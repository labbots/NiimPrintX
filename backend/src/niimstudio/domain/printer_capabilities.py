"""Immutable printer capability domain values.

All printer and label data is loaded from the sibling ``printers.toml`` file.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from enum import StrEnum
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_MILLIMETRES_PER_INCH = Decimal("25.4")
_MAX_RASTER_LENGTH_PX = 65535

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class PrintOrientation(StrEnum):
    NORMAL = "normal"
    CLOCKWISE_90 = "clockwise_90"
    CLOCKWISE_180 = "clockwise_180"
    CLOCKWISE_270 = "clockwise_270"


class PrinterFeature(StrEnum):
    NFC_LABEL_IDENTIFICATION = "nfc_label_identification"
    THERMAL_TRANSFER = "thermal_transfer"
    AUTOMATIC_LABEL_CALIBRATION = "automatic_label_calibration"


# ---------------------------------------------------------------------------
# Value types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class PrintableBounds:
    left_mm: Decimal
    top_mm: Decimal
    width_mm: Decimal
    length_mm: Decimal

    def __post_init__(self) -> None:
        _require_non_negative_decimal("left_mm", self.left_mm)
        _require_non_negative_decimal("top_mm", self.top_mm)
        _require_positive_decimal("width_mm", self.width_mm)
        _require_positive_decimal("length_mm", self.length_mm)


@dataclass(frozen=True, slots=True)
class LabelCapabilities:
    label_id: str
    display_name: str
    media_width_mm: Decimal
    media_length_mm: Decimal
    printable_bounds: PrintableBounds
    orientations: frozenset[PrintOrientation]

    def __post_init__(self) -> None:
        object.__setattr__(self, "orientations", frozenset(self.orientations))
        if not self.label_id:
            raise ValueError("label_id must not be empty")
        if not self.display_name:
            raise ValueError("display_name must not be empty")
        _require_positive_decimal("media_width_mm", self.media_width_mm)
        _require_positive_decimal("media_length_mm", self.media_length_mm)
        if not self.orientations:
            raise ValueError("orientations must not be empty")
        if (
            self.printable_bounds.left_mm + self.printable_bounds.width_mm > self.media_width_mm
            or self.printable_bounds.top_mm + self.printable_bounds.length_mm > self.media_length_mm
        ):
            raise ValueError("printable bounds are outside media")


@dataclass(frozen=True, slots=True)
class PrinterCapabilities:
    model_id: str
    display_name: str
    discovery_prefixes: tuple[str, ...]
    dpi_x: int
    dpi_y: int
    max_raster_width_px: int
    max_raster_length_px: int
    labels: tuple[LabelCapabilities, ...]
    density_min: int
    density_default: int
    density_max: int
    orientations: frozenset[PrintOrientation]
    features: frozenset[PrinterFeature]

    def __post_init__(self) -> None:
        object.__setattr__(self, "discovery_prefixes", tuple(self.discovery_prefixes))
        object.__setattr__(self, "labels", tuple(self.labels))
        object.__setattr__(self, "orientations", frozenset(self.orientations))
        object.__setattr__(self, "features", frozenset(self.features))
        if not self.model_id:
            raise ValueError("model_id must not be empty")
        if not self.display_name:
            raise ValueError("display_name must not be empty")
        if not self.discovery_prefixes or any(not prefix for prefix in self.discovery_prefixes):
            raise ValueError("discovery_prefixes must contain non-empty values")
        if len(set(self.discovery_prefixes)) != len(self.discovery_prefixes):
            raise ValueError("discovery_prefixes must be unique")
        if self.dpi_x <= 0:
            raise ValueError("dpi_x must be positive")
        if self.dpi_y <= 0:
            raise ValueError("dpi_y must be positive")
        if self.max_raster_width_px <= 0:
            raise ValueError("max_raster_width_px must be positive")
        if self.max_raster_length_px <= 0:
            raise ValueError("max_raster_length_px must be positive")
        if not self.labels:
            raise ValueError("labels must not be empty")
        if not self.orientations:
            raise ValueError("orientations must not be empty")
        if self.density_min <= 0 or not self.density_min <= self.density_default <= self.density_max:
            raise ValueError("density values must be positive and ordered")


@dataclass(frozen=True, slots=True)
class PixelBounds:
    left_px: int
    top_px: int
    width_px: int
    height_px: int


# ---------------------------------------------------------------------------
# Error type
# ---------------------------------------------------------------------------


class UnknownPrinterModelError(LookupError):
    def __init__(self, model_id: str) -> None:
        super().__init__(f"Unknown printer model {model_id!r}")
        self.model_id = model_id


# ---------------------------------------------------------------------------
# Pure functions
# ---------------------------------------------------------------------------


def is_label_compatible(
    printer: PrinterCapabilities,
    label: LabelCapabilities,
    orientation: PrintOrientation,
) -> bool:
    """Return whether a printer can render the selected label and orientation."""
    if label not in printer.labels or orientation not in printer.orientations or orientation not in label.orientations:
        return False
    bounds = _convert_bounds(printer, label, orientation)
    return bounds.width_px <= printer.max_raster_width_px and bounds.height_px <= printer.max_raster_length_px


def printable_bounds_px(
    printer: PrinterCapabilities,
    label: LabelCapabilities,
    orientation: PrintOrientation,
) -> PixelBounds:
    """Convert compatible physical printable bounds to edge-rounded pixels."""
    if not is_label_compatible(printer, label, orientation):
        raise ValueError(f"Label {label.label_id!r} and orientation {orientation.value!r} are not compatible")
    return _convert_bounds(printer, label, orientation)


def get_printer_capabilities(model_id: str) -> PrinterCapabilities:
    """Look up a capability record by its canonical model ID."""
    for printer in PRINTER_CAPABILITIES:
        if printer.model_id == model_id:
            return printer
    raise UnknownPrinterModelError(model_id)


# ---------------------------------------------------------------------------
# Conversion helpers
# ---------------------------------------------------------------------------


def _require_non_negative_decimal(name: str, value: Decimal) -> None:
    if not value.is_finite() or value < 0:
        raise ValueError(f"{name} must be a finite non-negative decimal")


def _require_positive_decimal(name: str, value: Decimal) -> None:
    if not value.is_finite() or value <= 0:
        raise ValueError(f"{name} must be a finite positive decimal")


def _convert_bounds(
    printer: PrinterCapabilities,
    label: LabelCapabilities,
    orientation: PrintOrientation,
) -> PixelBounds:
    left_mm, top_mm, width_mm, height_mm = _oriented_bounds(label, orientation)
    left_px = _millimetres_to_pixels(left_mm, printer.dpi_x)
    top_px = _millimetres_to_pixels(top_mm, printer.dpi_y)
    right_px = _millimetres_to_pixels(left_mm + width_mm, printer.dpi_x)
    bottom_px = _millimetres_to_pixels(top_mm + height_mm, printer.dpi_y)
    return PixelBounds(left_px, top_px, right_px - left_px, bottom_px - top_px)


def _oriented_bounds(
    label: LabelCapabilities,
    orientation: PrintOrientation,
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    bounds = label.printable_bounds
    if orientation is PrintOrientation.NORMAL:
        return bounds.left_mm, bounds.top_mm, bounds.width_mm, bounds.length_mm
    if orientation is PrintOrientation.CLOCKWISE_90:
        return (
            label.media_length_mm - (bounds.top_mm + bounds.length_mm),
            bounds.left_mm,
            bounds.length_mm,
            bounds.width_mm,
        )
    if orientation is PrintOrientation.CLOCKWISE_180:
        return (
            label.media_width_mm - (bounds.left_mm + bounds.width_mm),
            label.media_length_mm - (bounds.top_mm + bounds.length_mm),
            bounds.width_mm,
            bounds.length_mm,
        )
    return (
        bounds.top_mm,
        label.media_width_mm - (bounds.left_mm + bounds.width_mm),
        bounds.length_mm,
        bounds.width_mm,
    )


def _millimetres_to_pixels(millimetres: Decimal, dpi: int) -> int:
    return int((millimetres * dpi / _MILLIMETRES_PER_INCH).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def _load_registry() -> tuple[PrinterCapabilities, ...]:
    """Load printer capabilities from the sibling printers.toml file."""
    toml_path = Path(__file__).parent / "printers.toml"
    with toml_path.open("rb") as f:
        data = tomllib.load(f)

    # Build label lookup by label_id.
    label_registry: dict[str, LabelCapabilities] = {}
    for raw_label in data["labels"]:
        label = _parse_label(raw_label)
        label_registry[label.label_id] = label

    # Build printer capabilities, resolving label references.
    printers: list[PrinterCapabilities] = []
    for raw_printer in data["printers"]:
        printers.append(_parse_printer(raw_printer, label_registry))

    return tuple(printers)


def _parse_label(raw: dict[str, Any]) -> LabelCapabilities:
    raw_bounds = raw["printable_bounds"]
    bounds = PrintableBounds(
        left_mm=Decimal(raw_bounds["left_mm"]),
        top_mm=Decimal(raw_bounds["top_mm"]),
        width_mm=Decimal(raw_bounds["width_mm"]),
        length_mm=Decimal(raw_bounds["length_mm"]),
    )
    return LabelCapabilities(
        label_id=raw["label_id"],
        display_name=raw["display_name"],
        media_width_mm=Decimal(raw["media_width_mm"]),
        media_length_mm=Decimal(raw["media_length_mm"]),
        printable_bounds=bounds,
        orientations=frozenset(PrintOrientation(o) for o in raw["orientations"]),
    )


def _parse_printer(raw: dict[str, Any], label_registry: dict[str, LabelCapabilities]) -> PrinterCapabilities:
    labels = tuple(label_registry[lid] for lid in raw["labels"])
    return PrinterCapabilities(
        model_id=raw["model_id"],
        display_name=raw["display_name"],
        discovery_prefixes=tuple(raw["discovery_prefixes"]),
        dpi_x=raw["dpi_x"],
        dpi_y=raw["dpi_y"],
        max_raster_width_px=raw["max_raster_width_px"],
        max_raster_length_px=raw.get("max_raster_length_px", _MAX_RASTER_LENGTH_PX),
        labels=labels,
        density_min=raw["density_min"],
        density_default=raw["density_default"],
        density_max=raw["density_max"],
        orientations=frozenset(PrintOrientation(o) for o in raw["orientations"]),
        features=frozenset(PrinterFeature(f) for f in raw["features"]),
    )


# ---------------------------------------------------------------------------
# Module-level constant
# ---------------------------------------------------------------------------

PRINTER_CAPABILITIES: tuple[PrinterCapabilities, ...] = _load_registry()
