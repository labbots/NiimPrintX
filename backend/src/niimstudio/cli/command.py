import asyncio
from collections.abc import Awaitable
from typing import TypeVar

import click
from PIL import Image

from niimstudio.cli.output import print_error, print_info, print_success
from niimstudio.nimmy.bluetooth import find_device
from niimstudio.nimmy.exception import PrinterException
from niimstudio.nimmy.logger_config import get_logger, logger_enable, setup_logger
from niimstudio.nimmy.printer import MAX_PROTOCOL_VALUE, InfoEnum, PrinterClient

MODEL_MAX_WIDTH_PX = {
    "b1": 384,
    "b18": 384,
    "b21": 384,
    "d11": 240,
    "d11_h": 240,
    "d110": 240,
}
MODEL_MAX_DENSITY = {
    "b1": 5,
    "b18": 3,
    "b21": 5,
    "d11": 3,
    "d11_h": 3,
    "d110": 3,
}
MODEL_CHOICES = tuple(MODEL_MAX_WIDTH_PX)

T = TypeVar("T")

setup_logger()
logger = get_logger()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "-v",
    "--verbose",
    count=True,
    default=0,
    help="Enable verbose logging",
)
def niimbot_cli(verbose: int) -> None:
    """Print labels and query Niimbot printers."""
    logger_enable(verbose)


@niimbot_cli.command("print")
@click.option(
    "-m",
    "--model",
    type=click.Choice(MODEL_CHOICES, case_sensitive=False),
    default="d11",
    show_default=True,
    help="Niimbot printer model",
)
@click.option(
    "-d",
    "--density",
    type=click.IntRange(1, 5),
    default=3,
    show_default=True,
    help="Print density",
)
@click.option(
    "-n",
    "--quantity",
    type=click.IntRange(1, MAX_PROTOCOL_VALUE),
    default=1,
    show_default=True,
    help="Print quantity",
)
@click.option(
    "--vo",
    "vertical_offset",
    type=int,
    default=0,
    show_default=True,
    help="Vertical offset in pixels",
)
@click.option(
    "--ho",
    "horizontal_offset",
    type=int,
    default=0,
    show_default=True,
    help="Horizontal offset in pixels",
)
@click.option(
    "-r",
    "--rotate",
    type=click.Choice(("0", "90", "180", "270")),
    default="0",
    show_default=True,
    help="Image rotation (clockwise)",
)
@click.option(
    "-i",
    "--image",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=str),
    required=True,
    help="Image path",
)
def print_command(
    model: str,
    density: int,
    rotate: str,
    image: str,
    quantity: int,
    vertical_offset: int,
    horizontal_offset: int,
) -> None:
    """Print an image with the selected printer settings."""
    try:
        prepared_image = prepare_image(
            image,
            model,
            rotate,
            horizontal_offset,
            vertical_offset,
        )
        effective_density = min(density, MODEL_MAX_DENSITY[model])
        _run_async(
            _print(
                model,
                effective_density,
                prepared_image,
                quantity,
                vertical_offset,
                horizontal_offset,
            )
        )
    except Exception as exception:
        logger.error("Print job failed: {}", exception)
        raise click.ClickException(str(exception)) from exception


def prepare_image(
    image_path: str,
    model: str,
    rotate: str,
    horizontal_offset: int,
    vertical_offset: int,
) -> Image.Image:
    """Load, rotate, and validate an image for a printer model."""
    with Image.open(image_path) as source_image:
        image = source_image.copy()

    if rotate != "0":
        image = image.rotate(-int(rotate), expand=True)

    effective_width = image.width + horizontal_offset
    effective_height = image.height + vertical_offset
    if effective_width <= 0:
        raise click.BadParameter(
            "horizontal offset removes the complete image",
            param_hint="--ho",
        )
    if effective_height <= 0:
        raise click.BadParameter(
            "vertical offset removes the complete image",
            param_hint="--vo",
        )
    if effective_height > MAX_PROTOCOL_VALUE:
        raise click.BadParameter(
            f"image height including offset exceeds {MAX_PROTOCOL_VALUE}px",
            param_hint="--image",
        )
    max_width_px = MODEL_MAX_WIDTH_PX[model]
    if effective_width > max_width_px:
        raise click.BadParameter(
            f"image width including offset is {effective_width}px; {model.upper()} allows {max_width_px}px",
            param_hint="--image",
        )
    return image


async def _print(
    model: str,
    density: int,
    image: Image.Image,
    quantity: int,
    vertical_offset: int,
    horizontal_offset: int,
) -> None:
    printer: PrinterClient | None = None
    primary_error: BaseException | None = None
    try:
        print_info("Starting print job")
        device = await find_device(model)
        printer = PrinterClient(device)
        if not await printer.connect():
            raise PrinterException(f"Failed to connect to {device.name or device.address}")
        print_info(f"Connected to {device.name or device.address}")
        await printer.print_image(
            image,
            density=density,
            quantity=quantity,
            vertical_offset=vertical_offset,
            horizontal_offset=horizontal_offset,
        )
        print_success("Print job completed")
    except BaseException as exception:
        primary_error = exception
        raise
    finally:
        if printer is not None:
            try:
                await printer.disconnect()
            except Exception as exception:
                if primary_error is None:
                    raise
                logger.warning("Failed to disconnect after print failure: {}", exception)


@niimbot_cli.command("info")
@click.option(
    "-m",
    "--model",
    type=click.Choice(MODEL_CHOICES, case_sensitive=False),
    default="d110",
    show_default=True,
    help="Niimbot printer model",
)
def info_command(model: str) -> None:
    """Display identifying information reported by a printer."""
    try:
        _run_async(_info(model))
    except Exception as exception:
        logger.error("Printer information query failed: {}", exception)
        print_error(exception)
        raise click.ClickException(str(exception)) from exception


async def _info(model: str) -> None:
    printer: PrinterClient | None = None
    primary_error: BaseException | None = None
    try:
        print_info("Niimbot Information")
        device = await find_device(model)
        printer = PrinterClient(device)
        if not await printer.connect():
            raise PrinterException(f"Failed to connect to {device.name or device.address}")
        device_serial = await printer.get_info(InfoEnum.DEVICESERIAL)
        software_version = await printer.get_info(InfoEnum.SOFTVERSION)
        hardware_version = await printer.get_info(InfoEnum.HARDVERSION)
        click.echo(f"Device Serial : {device_serial}")
        click.echo(f"Software Version : {software_version}")
        click.echo(f"Hardware Version : {hardware_version}")
    except BaseException as exception:
        primary_error = exception
        raise
    finally:
        if printer is not None:
            try:
                await printer.disconnect()
            except Exception as exception:
                if primary_error is None:
                    raise
                logger.warning("Failed to disconnect after information query failure: {}", exception)


def _run_async(awaitable: Awaitable[T]) -> T:
    return asyncio.run(awaitable)


if __name__ == "__main__":
    niimbot_cli()
