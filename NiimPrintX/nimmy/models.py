"""Shared printer model metadata for CLI and UI."""

# Models that use B1-style 7-byte PrintStart + 6-byte SetPageSize (niimbluelib B1 task).
B1_PROTOCOL_MODELS = frozenset({"b1", "b21_c2b"})

# Models that need 6-byte SetPageSize (rows, cols, copies). B21S prints blank with 4-byte.
PAGE_SIZE_6B_MODELS = frozenset({"b21s", "b21s_c2b", "b21", "d101", "b1", "b21_c2b"})

# BLE advertisement name matching: longer / more specific keys first.
MODEL_NAME_MATCHERS = {
    "b21s": lambda n: n.startswith("b21s"),
    # Accept classic B21 and B21S when user selects b21 (same printhead family).
    "b21": lambda n: n.startswith("b21"),
    "b18": lambda n: n.startswith("b18"),
    "b1": lambda n: n.startswith("b1") and not n.startswith(("b18", "b21")),
    "d11_h": lambda n: n.startswith("d11") or "d11" in n,
    "d110": lambda n: n.startswith("d110") or n.startswith("d11"),
    "d11": lambda n: n.startswith("d11"),
    "d101": lambda n: n.startswith("d101"),
}

CLI_MODELS = ("b1", "b18", "b21", "b21s", "d11", "d11_h", "d110", "d101")

PRINTHEAD_WIDTH = {
    "b1": 384,
    "b18": 384,
    "b21": 384,
    "b21s": 384,
    "d11": 240,
    "d11_h": 240,
    "d110": 240,
    "d101": 240,
}


def matches_model(device_name: str, model: str) -> bool:
    if not device_name:
        return False
    name = device_name.lower().strip()
    model = (model or "").lower()
    matcher = MODEL_NAME_MATCHERS.get(model)
    if matcher:
        return matcher(name)
    # Fallback: prefix match, but avoid b1 matching b21
    if model == "b1":
        return name.startswith("b1") and not name.startswith(("b18", "b21"))
    if model == "b21":
        # Prefer exact B21, but also accept B21S so users can print with -m b21
        return name.startswith("b21")
    return name.startswith(model)


def uses_b1_protocol(model: str) -> bool:
    return (model or "").lower() in B1_PROTOCOL_MODELS


def uses_page_size_6b(model: str) -> bool:
    """B21S (and several others) require SetPageSize with copies count or print blank."""
    return (model or "").lower() in PAGE_SIZE_6B_MODELS
