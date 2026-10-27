"""An in-memory fake of the Vikunja API v2 endpoints Goal Guard uses, as a transport for vikunja.Client.

Imported by the tests, not run. Shapes follow the captured OpenAPI of v2.7.1 (PaginatedTask, Task, TaskRelation); it creates the
inverse relation itself, as the real server's relation_kind description says. Safety: memory only.
"""

import json
import urllib.parse

from helpers import lib

INVERSE = {
  "blocking": "blocked",
  "blocked": "blocking",
  "precedes": "follows",
  "follows": "precedes",
  "subtask": "parenttask",
  "parenttask": "subtask",
  "related": "related",
  "duplicateof": "duplicates",
  "duplicates": "duplicateof",
  "copiedto": "copiedfrom",
  "copiedfrom": "copiedto",
}


class FakeVikunja:
  """Holds projects and tasks and answers HTTP calls.

  Args:
    per_page: page size, like the instance's max_items_per_page.
  """

  def __init__(self, per_page: int = 2):
    """Start empty.

    Args:
      per_page: page size.
    """
    self.per_page = per_page
    self.tasks: dict[int, dict] = {}
    self.next_id = 500
    self.calls: list[tuple[str, str]] = []

  def settings(self):
    """Return settings pointing a Client at this fake.

    Returns:
      Settings with a fake URL and token.
    """
    return lib("settings").load({"GG_VIKUNJA_URL": "http://fake", "GG_VIKUNJA_TOKEN": "tk_test_value"})

  def client(self):
    """Return a Client bound to this fake.

    Returns:
      vikunja.Client.
    """
    return lib("vikunja").Client(self.settings(), transport=self)

  def __call__(self, method: str, url: str, headers: dict, body: bytes | None, timeout: float) -> tuple[int, bytes]:
    """Answer one request.

    Args:
      method: HTTP method.
      url: full URL.
      headers: request headers.
      body: JSON body or None.
      timeout: seconds (unused by the fake).

    Returns:
      (status, JSON body).
    """
    parts = urllib.parse.urlsplit(url)
    path = parts.path.removeprefix("/api/v2")
    query = urllib.parse.parse_qs(parts.query)
    self.calls.append((method, path))
    seg = path.strip("/").split("/")
    if headers.get("Authorization") != "Bearer tk_test_value":
      return 401, b'{"title": "unauthorized"}'
    if path == "/info":
      return 200, json.dumps({"version": "v2.7.1", "max_items_per_page": self.per_page}).encode()
    if method == "GET" and seg[0] == "projects" and seg[2] == "tasks":
      items = sorted((t for t in self.tasks.values() if t["project_id"] == int(seg[1])), key=lambda t: t["id"])
      page = int(query.get("page", ["1"])[0])
      chunk = [self._view(t) for t in items[(page - 1) * self.per_page : page * self.per_page]]
      pages = max(1, -(-len(items) // self.per_page))
      return 200, json.dumps({"items": chunk, "page": page, "per_page": self.per_page, "total": len(items), "total_pages": pages}).encode()
    if method == "POST" and seg[0] == "projects" and seg[2] == "tasks":
      data = json.loads(body)
      self.next_id += 1
      task = {"id": self.next_id, "project_id": int(seg[1]), "related": {}, "priority": 0, "done": False, **data}
      self.tasks[task["id"]] = task
      return 201, json.dumps(self._view(task)).encode()
    if method == "GET" and seg[0] == "tasks":
      task = self.tasks.get(int(seg[1]))
      return (200, json.dumps(self._view(task)).encode()) if task else (404, b'{"title": "not found"}')
    if method == "POST" and seg[0] == "tasks" and seg[2] == "relations":
      data = json.loads(body)
      a, b, kind = int(seg[1]), int(data["other_task_id"]), data["relation_kind"]
      if b in self.tasks[a]["related"].get(kind, []):
        return 409, b'{"title": "relation exists"}'
      self.tasks[a]["related"].setdefault(kind, []).append(b)
      self.tasks[b]["related"].setdefault(INVERSE[kind], []).append(a)
      return 201, json.dumps({"task_id": a, "other_task_id": b, "relation_kind": kind}).encode()
    return 404, b'{"title": "no route"}'

  def _view(self, task: dict) -> dict:
    """Render a stored task as the API returns it.

    Args:
      task: the stored task.

    Returns:
      The Task object with related_tasks expanded to small task objects.
    """
    out = {k: v for k, v in task.items() if k != "related"}
    out["related_tasks"] = {k: [{"id": i, "project_id": self.tasks[i]["project_id"]} for i in ids] for k, ids in task["related"].items()}
    return out
