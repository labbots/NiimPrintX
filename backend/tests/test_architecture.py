import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_printer_capability_domain_imports_no_outer_layers_or_frameworks():
    script = (
        "import sys; "
        "import niimstudio.domain.printer_capabilities; "
        "forbidden = ('niimstudio.cli', 'niimstudio.nimmy', 'click', 'PIL', 'bleak', 'loguru', 'rich'); "
        "assert not any(name == item or name.startswith(item + '.') for name in sys.modules for item in forbidden)"
    )

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
