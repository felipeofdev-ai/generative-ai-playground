import importlib.util
from pathlib import Path


def load_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, Path(path))
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod


def test_backpressure_signals():
    mod = load_module("runtime-control/backpressure.py", "backpressure")
    ctl = mod.BackpressureController(threshold=100)
    assert ctl.should_reject(80) is False
    assert ctl.should_reject(120) is True
    assert ctl.scaling_signal(160) == "scale_up_urgent"


def test_immutable_audit_chain():
    mod = load_module("governance/immutable_audit.py", "immutable_audit")
    trail = mod.ImmutableAuditTrail()
    trail.append("inference", {"tenant": "t1"})
    trail.append("policy_decision", {"allowed": True})
    assert trail.verify_chain() is True
