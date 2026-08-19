import subprocess
import sys
import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_console_help_runs_without_loading_tkinter():
    script = (
        "import sys; "
        "from niimstudio.cli.command import niimbot_cli; "
        "niimbot_cli.main(args=['--help'], prog_name='niimstudio', standalone_mode=False); "
        "assert 'tkinter' not in sys.modules"
    )

    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Print labels and query Niimbot printers" in result.stdout


def test_production_dependencies_exclude_legacy_gui_stack():
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as pyproject_file:
        pyproject = tomllib.load(pyproject_file)

    dependencies = {name.lower() for name in pyproject["tool"]["poetry"]["dependencies"]}

    assert dependencies.isdisjoint({"appdirs", "convert", "devtools", "pycairo", "wand"})


def test_backend_uses_niimstudio_src_layout():
    with (PROJECT_ROOT / "pyproject.toml").open("rb") as pyproject_file:
        pyproject = tomllib.load(pyproject_file)

    assert pyproject["tool"]["poetry"]["packages"] == [{"include": "niimstudio", "from": "src"}]
    assert (PROJECT_ROOT / "src" / "niimstudio").is_dir()
    assert not (PROJECT_ROOT.parent / "NiimStudio").exists()


def test_legacy_ui_is_not_part_of_console_source_tree():
    assert not list((PROJECT_ROOT / "src" / "niimstudio" / "ui").glob("**/*.py"))
    assert not (PROJECT_ROOT / "spec_files" / "ui_app").exists()
