import asyncio
from types import SimpleNamespace

import pytest
from click.testing import CliRunner
from PIL import Image

from niimstudio.cli import command
from niimstudio.nimmy.exception import PrinterException
from niimstudio.nimmy.printer import InfoEnum


def create_image(path, width=16, height=8):
    Image.new("1", (width, height), color=1).save(path)


def test_help_lists_console_commands():
    result = CliRunner().invoke(command.niimbot_cli, ["--help"])

    assert result.exit_code == 0
    assert "print" in result.output
    assert "info" in result.output


def test_print_prepares_image_and_clamps_density(tmp_path, monkeypatch):
    image_path = tmp_path / "label.png"
    create_image(image_path, width=20, height=10)
    captured = {}

    async def fake_print(model, density, image, quantity, vertical_offset, horizontal_offset):
        captured.update(
            model=model,
            density=density,
            size=image.size,
            pixel=image.getpixel((0, 0)),
            quantity=quantity,
            vertical_offset=vertical_offset,
            horizontal_offset=horizontal_offset,
        )

    monkeypatch.setattr(command, "_print", fake_print)

    result = CliRunner().invoke(
        command.niimbot_cli,
        [
            "print",
            "--model",
            "d11",
            "--density",
            "5",
            "--quantity",
            "2",
            "--rotate",
            "90",
            "--vo",
            "3",
            "--ho",
            "4",
            "--image",
            str(image_path),
        ],
    )

    assert result.exit_code == 0
    assert captured == {
        "model": "d11",
        "density": 3,
        "size": (10, 20),
        "pixel": 255,
        "quantity": 2,
        "vertical_offset": 3,
        "horizontal_offset": 4,
    }


@pytest.mark.parametrize(
    ("width", "height", "horizontal_offset", "vertical_offset", "expected_message"),
    [
        (240, 10, 1, 0, "allows 240px"),
        (10, 10, -10, 0, "horizontal offset removes the complete image"),
        (10, 10, 0, -10, "vertical offset removes the complete image"),
        (10, 10, 0, 65535, "height including offset exceeds 65535px"),
    ],
)
def test_print_rejects_invalid_effective_dimensions(
    tmp_path,
    width,
    height,
    horizontal_offset,
    vertical_offset,
    expected_message,
):
    image_path = tmp_path / "label.png"
    create_image(image_path, width=width, height=height)

    result = CliRunner().invoke(
        command.niimbot_cli,
        [
            "print",
            "--model",
            "d11",
            "--ho",
            str(horizontal_offset),
            "--vo",
            str(vertical_offset),
            "--image",
            str(image_path),
        ],
    )

    assert result.exit_code != 0
    assert expected_message in result.output


def test_print_rejects_non_positive_quantity(tmp_path):
    image_path = tmp_path / "label.png"
    create_image(image_path)

    result = CliRunner().invoke(
        command.niimbot_cli,
        ["print", "--quantity", "0", "--image", str(image_path)],
    )

    assert result.exit_code != 0
    assert "0 is not in the range" in result.output


def test_print_returns_non_zero_when_job_fails(tmp_path, monkeypatch):
    image_path = tmp_path / "label.png"
    create_image(image_path)

    async def failing_print(*args, **kwargs):
        raise PrinterException("printer unavailable")

    monkeypatch.setattr(command, "_print", failing_print)

    result = CliRunner().invoke(
        command.niimbot_cli,
        ["print", "--image", str(image_path)],
    )

    assert result.exit_code != 0
    assert "printer unavailable" in result.output


def test_info_runs_information_job(monkeypatch):
    captured = {}

    async def fake_info(model):
        captured["model"] = model

    monkeypatch.setattr(command, "_info", fake_info)

    result = CliRunner().invoke(command.niimbot_cli, ["info", "--model", "b21"])

    assert result.exit_code == 0
    assert captured == {"model": "b21"}


def test_print_job_disconnects_after_success(monkeypatch):
    fake_device = SimpleNamespace(name="D11", address="AA:BB")
    printer_instances = []

    async def fake_find_device(model):
        assert model == "d11"
        return fake_device

    class FakePrinter:
        def __init__(self, device):
            assert device is fake_device
            self.disconnected = False
            self.print_arguments = None
            printer_instances.append(self)

        async def connect(self):
            return True

        async def print_image(self, image, **kwargs):
            self.print_arguments = (image.size, kwargs)

        async def disconnect(self):
            self.disconnected = True

    monkeypatch.setattr(command, "find_device", fake_find_device)
    monkeypatch.setattr(command, "PrinterClient", FakePrinter)

    asyncio.run(command._print("d11", 3, Image.new("1", (8, 4)), 2, 1, -1))

    assert len(printer_instances) == 1
    assert printer_instances[0].disconnected is True
    assert printer_instances[0].print_arguments == (
        (8, 4),
        {
            "density": 3,
            "quantity": 2,
            "vertical_offset": 1,
            "horizontal_offset": -1,
        },
    )


def test_print_job_disconnects_after_failure(monkeypatch):
    fake_device = SimpleNamespace(name="D11", address="AA:BB")
    printer_instances = []

    async def fake_find_device(model):
        return fake_device

    class FakePrinter:
        def __init__(self, device):
            self.disconnected = False
            printer_instances.append(self)

        async def connect(self):
            return True

        async def print_image(self, image, **kwargs):
            raise PrinterException("paper out")

        async def disconnect(self):
            self.disconnected = True

    monkeypatch.setattr(command, "find_device", fake_find_device)
    monkeypatch.setattr(command, "PrinterClient", FakePrinter)

    with pytest.raises(PrinterException, match="paper out"):
        asyncio.run(command._print("d11", 3, Image.new("1", (8, 4)), 1, 0, 0))

    assert printer_instances[0].disconnected is True


def test_print_job_preserves_primary_error_when_disconnect_fails(monkeypatch):
    fake_device = SimpleNamespace(name="D11", address="AA:BB")

    async def fake_find_device(model):
        return fake_device

    class FakePrinter:
        def __init__(self, device):
            pass

        async def connect(self):
            return True

        async def print_image(self, image, **kwargs):
            raise PrinterException("paper out")

        async def disconnect(self):
            raise PrinterException("disconnect failed")

    monkeypatch.setattr(command, "find_device", fake_find_device)
    monkeypatch.setattr(command, "PrinterClient", FakePrinter)

    with pytest.raises(PrinterException, match="paper out"):
        asyncio.run(command._print("d11", 3, Image.new("1", (8, 4)), 1, 0, 0))


def test_info_queries_all_values_and_disconnects(monkeypatch, capsys):
    fake_device = SimpleNamespace(name="D110", address="AA:BB")
    printer_instances = []

    async def fake_find_device(model):
        assert model == "d110"
        return fake_device

    class FakePrinter:
        def __init__(self, device):
            self.requested = []
            self.disconnected = False
            printer_instances.append(self)

        async def connect(self):
            return True

        async def get_info(self, key):
            self.requested.append(key)
            return {
                InfoEnum.DEVICESERIAL: "0102",
                InfoEnum.SOFTVERSION: 1.23,
                InfoEnum.HARDVERSION: 4.56,
            }[key]

        async def disconnect(self):
            self.disconnected = True

    monkeypatch.setattr(command, "find_device", fake_find_device)
    monkeypatch.setattr(command, "PrinterClient", FakePrinter)

    asyncio.run(command._info("d110"))
    output = capsys.readouterr().out

    assert printer_instances[0].requested == [
        InfoEnum.DEVICESERIAL,
        InfoEnum.SOFTVERSION,
        InfoEnum.HARDVERSION,
    ]
    assert printer_instances[0].disconnected is True
    assert "Device Serial : 0102" in output
    assert "Software Version : 1.23" in output
    assert "Hardware Version : 4.56" in output
