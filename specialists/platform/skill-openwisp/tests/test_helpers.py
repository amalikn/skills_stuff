"""Offline tests for the promoted helpers in scripts/: identity and time conversions, the read-only probe on recorded output, the registry
comparison, the health mirror plan and the alert-policy converger (synthetic data only)."""

from __future__ import annotations

import contextlib
import importlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
_identity = importlib.import_module("openwisp_identity")
OpenWispProbe = importlib.import_module("openwisp_probe").OpenWispProbe
backfill_time, device_name, from_hardware_id = _identity.backfill_time, _identity.device_name, _identity.from_hardware_id
normalise_mac, to_hardware_id = _identity.normalise_mac, _identity.to_hardware_id
_registry = importlib.import_module("openwisp_registry")
_mirror = importlib.import_module("openwisp_health_mirror")
_alerts = importlib.import_module("openwisp_alert_policy")


class Identity(unittest.TestCase):
    UUID = "11111111-2222-3333-4444-555555555555"

    def test_hardware_id_round_trip_fits_32(self):
        hw = to_hardware_id(self.UUID)
        self.assertEqual(hw, "11111111222233334444555555555555")
        self.assertEqual(len(hw), 32)
        self.assertEqual(from_hardware_id(hw), self.UUID)

    def test_bad_hardware_id_rejected(self):
        for bad in ("", "xyz", self.UUID, "1" * 31):
            with self.assertRaises(ValueError):
                from_hardware_id(bad)

    def test_mac_notations_normalise(self):
        for raw in ("AA-BB-CC-DD-EE-0F", "aabb.ccdd.ee0f", "AA:BB:CC:DD:EE:0F"):
            self.assertEqual(normalise_mac(raw), "aa:bb:cc:dd:ee:0f")
        self.assertIsNone(normalise_mac("aa:bb"))
        self.assertIsNone(normalise_mac(None))

    def test_device_name_made_valid(self):
        self.assertEqual(device_name("SITE_AP 01__x"), "SITE-AP-01-x")
        self.assertEqual(device_name("a_.b"), "a.b")
        with self.assertRaises(ValueError):
            device_name("___")
        with self.assertRaises(ValueError):
            device_name("x" * 64)

    def test_backfill_time_is_utc_and_rejects_naive(self):
        local = datetime(2026, 10, 5, 11, 30, tzinfo=timezone(timedelta(hours=10)))
        self.assertEqual(backfill_time(local), "05-10-2026_01:30:00.000000")
        with self.assertRaises(ValueError):
            backfill_time(datetime(2026, 10, 5, 1, 30))


def recorded(stdout: str):
    return lambda cmd: subprocess.CompletedProcess(cmd, 0, stdout=stdout, stderr="")


class Probe(unittest.TestCase):
    def test_workers_counts_replying_nodes(self):
        five = json.dumps({f"{n}@host": {"ok": "pong"} for n in ("celery", "network", "firmware_upgrader", "monitoring", "monitoring_checks")})
        self.assertTrue(OpenWispProbe(recorded(five)).workers("c").healthy)
        none = OpenWispProbe(recorded("Error: No nodes replied within time constraint\n")).workers("c")
        self.assertFalse(none.healthy)
        self.assertIn("none replied", none.detail)

    def test_freshness_flags_old_point(self):
        out = json.dumps({"results": [{"series": [{"columns": ["time", "reachable"], "values": [["2026-09-28T07:34:45Z", 1]]}]}]})
        now = datetime(2026, 10, 5, 7, 34, 45, tzinfo=timezone.utc)
        stale = OpenWispProbe(recorded(out)).freshness("i", now=now)
        self.assertFalse(stale.healthy)
        self.assertEqual(stale.data["age"], 7 * 86400)
        self.assertTrue(OpenWispProbe(recorded(out)).freshness("i", now=now - timedelta(days=7) + timedelta(minutes=5)).healthy)
        self.assertFalse(OpenWispProbe(recorded("")).freshness("i").healthy)

    def test_settings_compares_and_hides_secret_values(self):
        out = "PROBE " + json.dumps({"A": True, "B": "__UNSET__", "SECRET_KEY": "real"})
        f = OpenWispProbe(recorded(out)).settings(["c1"], {"A": True, "B": 1, "SECRET_KEY": "other"})
        self.assertFalse(f.healthy)
        self.assertIn("B = '__UNSET__'", f.detail)
        self.assertIn("SECRET_KEY = <differs>", f.detail)
        self.assertNotIn("real", f.detail)


def shell(stdout: str = "", returncode: int = 0, stderr: str = "", calls: list | None = None):
    """A recorded Django-shell runner; `calls` collects (program, stdin)."""
    def run(program, stdin=None):
        if calls is not None:
            calls.append((program, stdin))
        return subprocess.CompletedProcess(["shell"], returncode, stdout=stdout, stderr=stderr)
    return run


HW1, HW2, HW3 = "a" * 32, "b" * 32, "c" * 32


class Registry(unittest.TestCase):
    OUT = (f"some django warning\nR {HW1} AA-BB-CC-DD-EE-01 192.0.2.10 ap one\n"
           f"R {HW2} - - ap-two\nR {HW3} aa:bb:cc:dd:ee:03 198.51.100.7 ap-three\n")

    def test_parse_keeps_names_with_spaces_and_dash_means_none(self):
        devs = _registry.read_registered(shell(self.OUT))
        self.assertEqual([d.name for d in devs], ["ap one", "ap-two", "ap-three"])
        self.assertEqual((devs[1].mac, devs[1].management_ip), (None, None))

    def test_empty_read_raises_with_output_tail(self):
        with self.assertRaises(_registry.RegistryReadError) as ctx:
            _registry.read_registered(shell("", 1, "Traceback: OperationalError"))
        self.assertIn("OperationalError", str(ctx.exception))

    def test_compare_normalises_macs_and_skips_absent_fields(self):
        dev = _registry.RegisteredDevice(HW1, "AA-BB-CC-DD-EE-01", "192.0.2.10", "x")
        rec = _registry.SourceRecord("x", frozenset({"aa:bb:cc:dd:ee:01", "aa:bb:cc:dd:ee:99"}), "192.0.2.10")
        self.assertEqual(_registry.compare(dev, rec), [])
        self.assertEqual(_registry.compare(dev, _registry.SourceRecord("x")), [])
        no_ip = _registry.RegisteredDevice(HW1, "AA-BB-CC-DD-EE-01", None, "x")
        self.assertEqual(_registry.compare(no_ip, _registry.SourceRecord("x", frozenset(), "192.0.2.11")), [])

    def test_mismatches_name_both_fields_in_read_order(self):
        records = {HW1: _registry.SourceRecord("one", frozenset({"aa:bb:cc:dd:ee:02"}), "192.0.2.11"),
                   HW2: _registry.SourceRecord("two", frozenset({"aa:bb:cc:dd:ee:04"}), "198.51.100.1"),
                   HW3: _registry.SourceRecord("three", frozenset({"AABB.CCDD.EE03"}), "198.51.100.7")}
        bad = _registry.find_mismatches(_registry.read_registered(shell(self.OUT)), records.__getitem__, source="SoT")
        self.assertEqual(bad, ["one: MAC AA-BB-CC-DD-EE-01 is not one of SoT's; management IP 192.0.2.10, SoT 192.0.2.11",
                               "two: MAC - is not one of SoT's"])

    def test_lookup_errors_propagate(self):
        with self.assertRaises(KeyError):
            _registry.find_mismatches(_registry.read_registered(shell(self.OUT)), {}.__getitem__)

    def test_django_shell_command_and_stdin(self):
        with mock.patch.object(_registry.subprocess, "run", return_value="done") as run:
            self.assertEqual(_registry.django_shell("ctr", timeout=7)("print(1)", "{}"), "done")
        run.assert_called_once_with(["docker", "exec", "-i", "ctr", "python", "manage.py", "shell", "-c", "print(1)"],
                                    input="{}", capture_output=True, text=True, timeout=7)


class HealthMirror(unittest.TestCase):
    U1, U2, U3 = (str(__import__("uuid").UUID(hex=h)) for h in (HW1, HW2, HW3))

    def test_read_health_keys_and_failure_rules(self):
        out = f"H {HW1} ok\nH {HW2} critical\nnoise\n"
        self.assertEqual(_mirror.read_health(shell(out)), {self.U1: "ok", self.U2: "critical"})
        self.assertEqual(_mirror.read_health(shell(out, 1)), {self.U1: "ok", self.U2: "critical"})
        self.assertEqual(_mirror.read_health(shell(out), key=str.upper), {HW1.upper(): "ok", HW2.upper(): "critical"})
        with self.assertRaises(_mirror.HealthReadError):
            _mirror.read_health(shell("", 1, "boom"))
        self.assertEqual(_mirror.read_health(shell("", 0)), {})

    def test_plan_writes_only_changes_and_clears_unregistered(self):
        wanted = {self.U1: "ok", self.U2: "critical"}
        current = {self.U1: "ok", self.U2: "problem", self.U3: "ok"}
        plan = _mirror.plan_mirror(wanted, current, "h", "s", "T")
        self.assertEqual(plan.changes, [{"id": self.U2, "custom_fields": {"h": "critical", "s": "T"}}])
        self.assertEqual(plan.cleared, [{"id": self.U3, "custom_fields": {"h": None, "s": None}}])
        self.assertEqual(plan.patch_body(), plan.changes + plan.cleared)
        self.assertEqual(plan.summary("T"), 'T registered=2 {"critical": 1, "ok": 1} changed=1 cleared=1')
        self.assertEqual(plan.change_lines(), [f"  {self.U2}: problem -> critical"])

    def test_unchanged_run_plans_nothing_and_new_device_shows_dash(self):
        self.assertEqual(_mirror.plan_mirror({self.U1: "ok"}, {self.U1: "ok"}, "h", "s", "T").patch_body(), [])
        plan = _mirror.plan_mirror({self.U1: "unknown"}, {}, "h", "s", "T")
        self.assertEqual(plan.change_lines(), [f"  {self.U1}: - -> unknown"])


class _FakeAlert:
    def __init__(self, object_id, configuration, threshold, tolerance, is_active):
        self.metric = type("M", (), {"object_id": object_id, "configuration": configuration})()
        self.threshold, self.tolerance, self.is_active = threshold, tolerance, is_active
        self.saved = False

    def full_clean(self):
        pass

    def save(self):
        self.saved = True


class AlertPolicyTests(unittest.TestCase):
    DOC = {"defaults": {"ping": {"threshold": 1, "tolerance": 0, "reason": "doc only"}, "cpu": {"threshold": 90, "tolerance": 5}},
           "families": {"ap": {"cpu": {"threshold": 95, "is_active": False}}, "empty": None}}

    def policy(self):
        return _alerts.AlertPolicy.from_dict(self.DOC, classes_key="families")

    def test_policy_strips_documentation_and_layers_overrides(self):
        p = self.policy()
        self.assertEqual(p.defaults["ping"], {"threshold": 1, "tolerance": 0})
        self.assertEqual(p.wanted("ap")["cpu"], {"threshold": 95, "tolerance": 5, "is_active": False})
        self.assertEqual(p.wanted(None), p.wanted("unknown-class"))
        self.assertEqual(p.wanted("empty"), p.wanted(None))
        self.assertEqual(_alerts.AlertPolicy.from_dict(None).wanted("ap"), {})
        self.assertEqual(_alerts.AlertPolicy.from_dict(self.DOC).classes, {}, "classes_key defaults to `classes`")

    def test_offline_plan_skips_unresolved_and_missing_metrics(self):
        devices = {HW1: "pk1", HW2: "pk2", HW3: "pk3"}
        rows = {"pk1": {"cpu": {"threshold": 90, "tolerance": 5, "is_active": True}, "ping": {"threshold": 1, "tolerance": 0, "is_active": True}},
                "pk2": {"cpu": {"threshold": 90, "tolerance": 5, "is_active": True}}}
        plan = _alerts.plan_differences(self.policy(), devices, {HW1: None, HW2: "ap"}, rows)
        self.assertEqual(plan, [("SAME", HW1, "ping", {}), ("SAME", HW1, "cpu", {}),
                                ("WOULD", HW2, "cpu", {"threshold": (90, 95), "is_active": (True, False)})])

    def _exec(self, apply, rows):
        swapper = type(sys)("swapper")
        objects = mock.Mock()
        objects.select_related.return_value.filter.return_value = rows
        swapper.load_model = lambda app, model: type("AS", (), {"objects": objects})
        conv = _alerts.AlertSettingsConverger(self.policy(), {HW1: "pk1", HW2: "pk2", HW3: "pk3"}, {HW1: None, HW2: "ap"})
        buf = io.StringIO()
        with mock.patch.dict(sys.modules, {"swapper": swapper}), mock.patch.object(sys, "stdin", io.StringIO(json.dumps(conv.plan(apply)))), \
                contextlib.redirect_stdout(buf):
            exec(_alerts.program(apply), {})
        return conv, buf.getvalue()

    def rows(self):
        return [_FakeAlert("pk1", "cpu", 90, 5, True), _FakeAlert("pk1", "ping", 1, 0, True), _FakeAlert("pk2", "cpu", 90, 5, True)]

    def test_server_program_matches_offline_planner_and_dry_run_cannot_write(self):
        self.assertNotIn("save()", _alerts.program(False))
        self.assertIn("save()", _alerts.program(True))
        rows = self.rows()
        conv, out = self._exec(False, rows)
        self.assertEqual(conv.unresolved, [HW3])
        counts, lines = conv.parse(out)
        self.assertEqual(counts, {"SAME": 2, "WOULD": 1, "CHANGE": 0})
        self.assertEqual(lines, [f'WOULD {HW2} cpu {{"threshold": [90, 95], "is_active": [true, false]}}'])
        self.assertFalse(any(r.saved for r in rows))
        offline = _alerts.plan_differences(conv.policy, {HW1: "pk1", HW2: "pk2", HW3: "pk3"}, conv.classes,
                                           {"pk1": {"cpu": {"threshold": 90, "tolerance": 5, "is_active": True},
                                                    "ping": {"threshold": 1, "tolerance": 0, "is_active": True}},
                                            "pk2": {"cpu": {"threshold": 90, "tolerance": 5, "is_active": True}}})
        self.assertEqual(sorted((t, hw, c) for t, hw, c, _ in offline), sorted((l.split()[0], l.split()[1], l.split()[2]) for l in out.splitlines()))

    def test_apply_program_writes_custom_values_only_on_differences(self):
        rows = self.rows()
        _, out = self._exec(True, rows)
        self.assertIn(f"CHANGE {HW2} cpu", out)
        self.assertEqual([r.saved for r in rows], [False, False, True])
        self.assertEqual((rows[2].custom_threshold, rows[2].custom_tolerance, rows[2].is_active), (95, 5, False))

    def test_converge_passes_plan_and_reports_shell_failure(self):
        calls = []
        conv = _alerts.AlertSettingsConverger(self.policy(), {HW1: "pk1"}, {HW1: "ap"})
        counts, lines, error = conv.converge(shell(f"SAME {HW1} ping\nWOULD {HW1} cpu {{}}\n", calls=calls))
        self.assertEqual((counts["SAME"], counts["WOULD"], lines, error), (1, 1, [f"WOULD {HW1} cpu {{}}"], None))
        self.assertEqual(json.loads(calls[0][1])["apply"], False)
        self.assertNotIn("save()", calls[0][0])
        _, _, error = conv.converge(shell("", 1, "x" * 600 + "Traceback end"))
        self.assertTrue(error.endswith("Traceback end"))
        self.assertEqual(len(error), 500)

    def test_read_device_pks(self):
        self.assertEqual(_alerts.read_device_pks(shell(f"D {HW1} pk1\nnoise\n")), {HW1: "pk1"})
        self.assertEqual(_alerts.read_device_pks(shell("", 1, "down")), {})


class Governance(unittest.TestCase):
    """scripts/check_governance.py ("check_governance") is the pack's governance gate; it runs here so `just test` covers it."""

    PACK = Path(__file__).resolve().parents[1]

    def _run(self, root: Path) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(root / "scripts" / "check_governance.py")], capture_output=True, text=True, check=False)

    def test_governance_claims_hold(self):
        result = self._run(self.PACK)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_broken_reference_fails_the_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "pack"
            shutil.copytree(self.PACK, copy, ignore=shutil.ignore_patterns(".git", "documents", "graphify-out", ".ai-context"))
            with (copy / "README.md").open("a", encoding="utf-8") as fh:
                fh.write("\nSee `references/does-not-exist.md`.\n")
            result = self._run(copy)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("does-not-exist.md", result.stdout)


if __name__ == "__main__":
    unittest.main()
