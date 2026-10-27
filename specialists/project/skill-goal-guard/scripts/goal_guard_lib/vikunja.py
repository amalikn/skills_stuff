"""The Vikunja HTTP seam: the only module that talks to Vikunja (references/vikunja-integration.md). Standard library only.

Imported, not run. API v2 paths checked against the captured OpenAPI 3.1.0 of Vikunja v2.7.1
(documents/vikunja-2.7.1-20261027/openapi-v2.json): GET /info, GET /projects/{project}/tasks (PaginatedTask: items, page, per_page,
total, total_pages), GET /tasks/{task}, POST /projects/{project}/tasks, POST /tasks/{task}/relations (other_task_id, relation_kind).
Auth: bearer API token (APITokenAuth). Every call has the timeout from settings; the token is never logged or put in an error.

Reads are the default. The two write methods (create_task, create_relation) exist only for the clean-instance restore, which
gates them behind --apply in snapshot.restore; they are listed in code-map.toml write_gates.
"""

import json
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from typing import Protocol

from .errors import VikunjaAuthRejected, VikunjaConflict, VikunjaError, VikunjaNotFound, VikunjaUnreachable
from .settings import API_PATH, Settings

MAX_PAGES = 200  # a bound on pagination: 200 pages x the instance's page size (50 here) is far beyond one project


class Transport(Protocol):
  """Sends one HTTP request; tests pass a fake with the same call shape."""

  def __call__(self, method: str, url: str, headers: dict, body: bytes | None, timeout: float) -> tuple[int, bytes]:
    """Send a request.

    Args:
      method: HTTP method.
      url: full URL.
      headers: request headers.
      body: request body or None.
      timeout: seconds.

    Returns:
      (status, response body).
    """
    ...


def urllib_transport(method: str, url: str, headers: dict, body: bytes | None, timeout: float) -> tuple[int, bytes]:
  """Send one request with urllib.

  Args:
    method: HTTP method.
    url: full URL.
    headers: request headers.
    body: request body or None.
    timeout: seconds before giving up.

  Returns:
    (status, body) for any HTTP answer, including 4xx and 5xx.

  Raises:
    VikunjaUnreachable: no answer within the timeout, or the connection failed.
  """
  request = urllib.request.Request(url, data=body, method=method, headers=headers)
  try:
    with urllib.request.urlopen(request, timeout=timeout) as response:
      return response.status, response.read()
  except urllib.error.HTTPError as err:
    return err.code, err.read()
  except (urllib.error.URLError, TimeoutError, ConnectionError) as err:
    reason = getattr(err, "reason", err)
    raise VikunjaUnreachable(f"{method} {urllib.parse.urlsplit(url).path}: no answer ({reason})") from err


class Client:
  """A Vikunja API v2 client for one instance.

  Args:
    settings: resolved settings (URL, token, timeout); require_vikunja() is called here.
    transport: the HTTP sender; tests pass a fake.
  """

  def __init__(self, settings: Settings, transport: Callable = urllib_transport):
    """Bind the client to an instance.

    Args:
      settings: resolved settings.
      transport: the HTTP sender.

    Raises:
      ConfigError: URL or token not set.
    """
    settings.require_vikunja()
    self._base = settings.vikunja_url + API_PATH
    self._token = settings.vikunja_token
    self._timeout = settings.http_timeout
    self._send = transport

  def _call(self, method: str, path: str, query: dict | None = None, payload: dict | None = None) -> object:
    """Make one call and translate failures into GoalGuard errors.

    Args:
      method: HTTP method.
      path: API path under /api/v2, starting with "/".
      query: query parameters.
      payload: JSON body.

    Returns:
      The decoded JSON body.

    Raises:
      VikunjaAuthRejected: 401 or 403.
      VikunjaNotFound: 404.
      VikunjaConflict: 409 or 412.
      VikunjaError: any other non-2xx status, or a body that is not JSON.
      VikunjaUnreachable: no answer.
    """
    url = self._base + path + ("?" + urllib.parse.urlencode(query, doseq=True) if query else "")
    headers = {"Authorization": f"Bearer {self._token}", "Accept": "application/json"}
    body = None
    if payload is not None:
      headers["Content-Type"] = "application/json"
      body = json.dumps(payload).encode("utf-8")
    status, raw = self._send(method, url, headers, body, self._timeout)
    if status in (401, 403):
      raise VikunjaAuthRejected(f"{method} {path}: token rejected ({status}); check the token's permissions", status, path)
    if status == 404:
      raise VikunjaNotFound(f"{method} {path}: not found or not visible to this token", status, path)
    if status in (409, 412):
      raise VikunjaConflict(f"{method} {path}: concurrent change ({status}); re-read before writing", status, path)
    if not 200 <= status < 300:
      detail = _detail(raw)
      raise VikunjaError(f"{method} {path}: HTTP {status}{': ' + detail if detail else ''}", status, path)
    try:
      return json.loads(raw or b"null")
    except json.JSONDecodeError as err:
      raise VikunjaError(f"{method} {path}: answer is not JSON", status, path) from err

  def info(self) -> dict:
    """Read the instance information.

    Returns:
      The VikunjaInfos object (version, max_items_per_page, auth, ...).
    """
    return self._call("GET", "/info")

  def project_tasks(self, project_id: int) -> tuple[list[dict], dict]:
    """Read every task of one project, following pagination.

    Args:
      project_id: Vikunja project ID.

    Returns:
      (tasks, completeness): the raw Task objects, and {"total": int, "fetched": int, "pages": int, "complete": bool}.

    Raises:
      VikunjaError: any failed page (no partial list is returned).
    """
    tasks, page, total, pages = [], 1, None, 0
    while page <= MAX_PAGES:
      data = self._call("GET", f"/projects/{int(project_id)}/tasks", {"page": page})
      if not isinstance(data, dict):
        raise VikunjaError(f"GET /projects/{project_id}/tasks: expected a PaginatedTask object")
      items = data.get("items") or []
      tasks.extend(items)
      pages += 1
      total = data.get("total", total)
      total_pages = int(data.get("total_pages") or 1)
      if page >= total_pages or not items:
        break
      page += 1
    fetched = len(tasks)
    return tasks, {"total": total if total is not None else fetched, "fetched": fetched, "pages": pages, "complete": total in (None, fetched)}

  def task(self, task_id: int) -> dict:
    """Read one task.

    Args:
      task_id: Vikunja task ID.

    Returns:
      The task object (TaskReadOneBody), including related_tasks.
    """
    return self._call("GET", f"/tasks/{int(task_id)}")

  def create_task(self, project_id: int, task: dict) -> dict:
    """Create a task (restore only; the caller holds the --apply gate).

    Args:
      project_id: target Vikunja project ID.
      task: writable Task fields (title, description, done, priority, dates).

    Returns:
      The created Task, with its new id.
    """
    return self._call("POST", f"/projects/{int(project_id)}/tasks", payload=task)

  def create_relation(self, task_id: int, other_task_id: int, kind: str) -> dict:
    """Create a relation; Vikunja creates the inverse itself (OpenAPI TaskRelation.relation_kind).

    Args:
      task_id: base task ID.
      other_task_id: the other task ID.
      kind: relation kind, e.g. blocking or precedes.

    Returns:
      The created TaskRelation.
    """
    return self._call("POST", f"/tasks/{int(task_id)}/relations", payload={"other_task_id": int(other_task_id), "relation_kind": kind})


def _detail(raw: bytes) -> str:
  """Pull a short message out of a VikunjaErrorModel body.

  Args:
    raw: the response body.

  Returns:
    The title or detail text, at most 200 characters, or "" when there is none.
  """
  try:
    data = json.loads(raw)
  except json.JSONDecodeError, UnicodeDecodeError:
    return ""
  if not isinstance(data, dict):
    return ""
  return str(data.get("detail") or data.get("title") or data.get("message") or "")[:200]
