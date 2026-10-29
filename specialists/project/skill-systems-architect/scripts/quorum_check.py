#!/usr/bin/env python3
"""Check which node, failure-domain and QDevice losses a vote-based cluster (corosync/Proxmox style) survives with quorum.

Usage: just quorum examples/quorum.json (or: <venv python> scripts/quorum_check.py <cluster.json>)
Reads at most 1 MiB and 64 nodes; prints JSON; never writes or connects.
Quorum = floor(total votes / 2) + 1. A QDevice adds 1 vote on an even node count and N-1 votes on an odd one (Proxmox pvecm).
Exit 0: every required scenario keeps quorum, 1: a required scenario loses it, 2: invalid input.
"""

import argparse
import json
import sys
import time
from pathlib import Path

MAX_BYTES = 1024 * 1024
MAX_NODES = 64


def quorum(total):
  """Votes needed for quorum.

  Args:
    total: Total configured votes.
  Returns:
    floor(total / 2) + 1.
  """
  return total // 2 + 1


def check_cluster(data):
  """Evaluate every single-node, single-domain and QDevice loss, and the required ones.

  Args:
    data: Parsed JSON with schema_version, nodes, optional qdevice and must_survive.
  Returns:
    Pair of (result dictionary, findings list).
  Raises:
    ValueError: When the schema or a reference is invalid.
  """
  allowed = {"schema_version", "nodes", "qdevice", "must_survive"}
  if not isinstance(data, dict) or not {"schema_version", "nodes"} <= set(data) or set(data) - allowed:
    raise ValueError(f"expected schema_version and nodes, optionally qdevice and must_survive; got {sorted(data) if isinstance(data, dict) else data}")
  if type(data["schema_version"]) is not int or data["schema_version"] != 1:
    raise ValueError("schema_version must be integer 1")
  nodes = data["nodes"]
  if not isinstance(nodes, list) or not 1 <= len(nodes) <= MAX_NODES:
    raise ValueError(f"nodes must contain 1..{MAX_NODES} entries")
  votes, domains = {}, {}
  for node in nodes:
    if not isinstance(node, dict) or set(node) - {"id", "domain", "votes"} or not {"id", "domain"} <= set(node):
      raise ValueError("each node is {id, domain, optional votes}")
    if not isinstance(node["id"], str) or node["id"] in votes or not isinstance(node["domain"], str):
      raise ValueError("node id must be a unique string and domain a string")
    count = node.get("votes", 1)
    if type(count) is not int or not 1 <= count <= 255:
      raise ValueError(f"{node['id']}: votes must be an integer 1..255")
    votes[node["id"]] = count
    domains.setdefault(node["domain"], []).append(node["id"])
  qdevice = data.get("qdevice")
  qdevice_votes, findings = 0, []
  if qdevice is not None:
    if not isinstance(qdevice, dict) or set(qdevice) != {"domain"} or not isinstance(qdevice["domain"], str):
      raise ValueError("qdevice is {domain}")
    qdevice_votes = 1 if len(nodes) % 2 == 0 else len(nodes) - 1
    if len(nodes) % 2 == 1:
      findings.append(f"QDevice on an odd node count holds {qdevice_votes} votes; Proxmox discourages it (if it fails, no further node may fail)")
  total = sum(votes.values()) + qdevice_votes
  needed = quorum(total)

  def survives(lost_nodes, lose_qdevice):
    """Report whether the remaining votes reach quorum.

    Args:
      lost_nodes: Node ids that are down.
      lose_qdevice: Whether the QDevice is also unreachable.
    Returns:
      Pair of (remaining votes, quorate flag).
    """
    remaining = sum(count for node, count in votes.items() if node not in lost_nodes)
    if qdevice is not None and not lose_qdevice:
      remaining += qdevice_votes
    return remaining, remaining >= needed

  scenarios = {"none": (set(), False)}
  scenarios.update({f"node:{node}": ({node}, False) for node in votes})
  for domain, members in domains.items():
    scenarios[f"domain:{domain}"] = (set(members), qdevice is not None and qdevice["domain"] == domain)
  if qdevice is not None:
    scenarios["qdevice"] = (set(), True)
  required = data.get("must_survive", [])
  if not isinstance(required, list) or any(not isinstance(name, str) for name in required):
    raise ValueError("must_survive is a list of scenario names")
  # A combined scenario joins single ones with "+", e.g. "domain:rack-a+qdevice": the union of what each part takes down.
  for name in required:
    if "+" in name and name not in scenarios:
      parts = name.split("+")
      unknown = [part for part in parts if part not in scenarios]
      if unknown:
        raise ValueError(f"unknown scenario part(s) {unknown}; known: {sorted(scenarios)}")
      scenarios[name] = (set().union(*(scenarios[part][0] for part in parts)), any(scenarios[part][1] for part in parts))
  rows = []
  for name, (lost, lose_qdevice) in scenarios.items():
    remaining, ok = survives(lost, lose_qdevice)
    rows.append({"scenario": name, "remaining_votes": remaining, "quorate": ok})
  results = {row["scenario"]: row["quorate"] for row in rows}
  for name in required:
    if name not in results:
      raise ValueError(f"unknown scenario {name!r}; known: {sorted(results)}")
    if not results[name]:
      findings.append(f"{name}: cluster loses quorum ({needed} of {total} votes needed)")
  if not results["none"]:
    findings.append("cluster is not quorate with everything up")
  return {"total_votes": total, "quorum": needed, "qdevice_votes": qdevice_votes, "scenarios": rows}, findings


def main():
  """Read the bounded JSON input and print the scenario table.

  Args:
    None.
  Returns:
    Integer process exit code.
  """
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument("input", type=Path)
  args = parser.parse_args()
  started = time.perf_counter()
  try:
    with args.input.open("rb") as handle:
      raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
      raise ValueError("input exceeds 1 MiB")
    result, findings = check_cluster(json.loads(raw))
  except (OSError, ValueError, TypeError, UnicodeError) as error:
    print(json.dumps({"status": "invalid", "error": str(error)}))
    return 2
  failed = [finding for finding in findings if "loses quorum" in finding or "not quorate" in finding]
  result.update(
    {
      "status": "findings" if failed else ("warnings" if findings else "pass"),
      "findings": findings,
      "elapsed_seconds": round(time.perf_counter() - started, 6),
      "limits": "Votes only: quorum is necessary, not sufficient. Fencing, storage, capacity and corosync latency (<5 ms) decide whether guests actually run.",
    }
  )
  print(json.dumps(result, indent=2))
  return 1 if failed else 0


if __name__ == "__main__":
  sys.exit(main())
