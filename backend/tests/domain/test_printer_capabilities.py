from dataclasses import FrozenInstanceError
from decimal import Decimal

import pytest

from niimstudio.domain.printer_capabilities import (
    PRINTER_CAPABILITIES,
    LabelCapabilities,
    PixelBounds,
    PrintableBounds,
    PrinterCapabilities,
    PrinterFeature,
    PrintOrientation,
    UnknownPrinterModelError,
    get_printer_capabilities,
    is_label_compatible,
    printable_bounds_px,
)


def make_label(**overrides):
    values = {
        "label_id": "test-10x20",
        "display_name": "10 x 20 mm",
        "media_width_mm": Decimal("10"),
        "media_length_mm": Decimal("20"),
        "printable_bounds": PrintableBounds(
            left_mm=Decimal("0.25"),
            top_mm=Decimal("0.5"),
            width_mm=Decimal("3.8"),
            length_mm=Decimal("4.2"),
        ),
        "orientations": frozenset({PrintOrientation.NORMAL, PrintOrientation.CLOCKWISE_90}),
    }
    values.update(overrides)
    return LabelCapabilities(**values)


def make_printer(label=None, **overrides):
    label = label or make_label()
    values = {
        "model_id": "test",
        "display_name": "Test Printer",
        "discovery_prefixes": ("test",),
        "dpi_x": 254,
        "dpi_y": 127,
        "max_raster_width_px": 1000,
        "max_raster_length_px": 2000,
        "labels": (label,),
        "density_min": 1,
        "density_default": 2,
        "density_max": 3,
        "orientations": frozenset({PrintOrientation.NORMAL, PrintOrientation.CLOCKWISE_90}),
        "features": frozenset({PrinterFeature.THERMAL_TRANSFER}),
    }
    values.update(overrides)
    return PrinterCapabilities(**values)


@pytest.mark.parametrize(
    "bounds",
    [
        PrintableBounds(Decimal("0"), Decimal("0"), Decimal("10"), Decimal("20")),
        PrintableBounds(Decimal("1.25"), Decimal("2.5"), Decimal("8.75"), Decimal("17.5")),
    ],
)
def test_label_preserves_exact_physical_dimensions_and_printable_bounds(bounds):
    label = make_label(printable_bounds=bounds)

    assert label.media_width_mm == Decimal("10")
    assert label.media_length_mm == Decimal("20")
    assert label.printable_bounds == bounds


@pytest.mark.parametrize(
    "field",
    ["media_width_mm", "media_length_mm"],
)
@pytest.mark.parametrize("invalid_value", [Decimal("0"), Decimal("-0.1")])
def test_label_rejects_non_positive_media_dimensions(field, invalid_value):
    with pytest.raises(ValueError, match=field):
        make_label(**{field: invalid_value})


@pytest.mark.parametrize(
    "overrides",
    [
        {"label_id": ""},
        {"display_name": ""},
        {"orientations": frozenset()},
    ],
)
def test_label_rejects_missing_required_values(overrides):
    with pytest.raises(ValueError):
        make_label(**overrides)


@pytest.mark.parametrize(
    ("left_mm", "top_mm", "width_mm", "length_mm"),
    [
        (Decimal("-0.1"), Decimal("0"), Decimal("1"), Decimal("1")),
        (Decimal("0"), Decimal("-0.1"), Decimal("1"), Decimal("1")),
        (Decimal("0"), Decimal("0"), Decimal("0"), Decimal("1")),
        (Decimal("0"), Decimal("0"), Decimal("1"), Decimal("0")),
    ],
)
def test_printable_bounds_reject_invalid_origins_and_dimensions(left_mm, top_mm, width_mm, length_mm):
    with pytest.raises(ValueError):
        PrintableBounds(left_mm, top_mm, width_mm, length_mm)


@pytest.mark.parametrize(
    "bounds",
    [
        PrintableBounds(Decimal("9"), Decimal("0"), Decimal("2"), Decimal("1")),
        PrintableBounds(Decimal("0"), Decimal("19"), Decimal("1"), Decimal("2")),
    ],
)
def test_label_rejects_printable_rectangle_outside_media(bounds):
    with pytest.raises(ValueError, match="outside media"):
        make_label(printable_bounds=bounds)


def test_printer_preserves_typed_identity_and_capabilities():
    label = make_label()
    printer = make_printer(label)

    assert printer == PrinterCapabilities(
        model_id="test",
        display_name="Test Printer",
        discovery_prefixes=("test",),
        dpi_x=254,
        dpi_y=127,
        max_raster_width_px=1000,
        max_raster_length_px=2000,
        labels=(label,),
        density_min=1,
        density_default=2,
        density_max=3,
        orientations=frozenset({PrintOrientation.NORMAL, PrintOrientation.CLOCKWISE_90}),
        features=frozenset({PrinterFeature.THERMAL_TRANSFER}),
    )


@pytest.mark.parametrize(
    "overrides",
    [
        {"model_id": ""},
        {"display_name": ""},
        {"discovery_prefixes": ()},
        {"discovery_prefixes": ("",)},
        {"discovery_prefixes": ("test", "test")},
        {"dpi_x": 0},
        {"dpi_y": 0},
        {"max_raster_width_px": 0},
        {"max_raster_length_px": 0},
        {"labels": ()},
        {"orientations": frozenset()},
    ],
)
def test_printer_rejects_missing_or_non_positive_required_values(overrides):
    with pytest.raises(ValueError):
        make_printer(**overrides)


@pytest.mark.parametrize(
    ("minimum", "default", "maximum"),
    [(0, 1, 2), (2, 1, 3), (1, 4, 3)],
)
def test_printer_rejects_invalid_density_range(minimum, default, maximum):
    with pytest.raises(ValueError, match="density"):
        make_printer(density_min=minimum, density_default=default, density_max=maximum)


def test_capability_values_are_deeply_immutable():
    printer = make_printer()

    with pytest.raises(FrozenInstanceError):
        printer.dpi_x = 300
    with pytest.raises(AttributeError):
        printer.discovery_prefixes.append("alias")
    with pytest.raises(AttributeError):
        printer.labels[0].orientations.add(PrintOrientation.CLOCKWISE_180)
    with pytest.raises(AttributeError):
        printer.features.add(PrinterFeature.AUTOMATIC_LABEL_CALIBRATION)


def test_label_compatibility_requires_registered_label_and_shared_orientation():
    label = make_label()
    printer = make_printer(label)
    other_label = make_label(label_id="other")

    assert is_label_compatible(printer, label, PrintOrientation.NORMAL) is True
    assert is_label_compatible(printer, label, PrintOrientation.CLOCKWISE_180) is False
    assert is_label_compatible(printer, other_label, PrintOrientation.NORMAL) is False


def test_printable_bounds_conversion_uses_asymmetric_dpi_and_edge_rounding():
    label = make_label()
    printer = make_printer(label)

    assert printable_bounds_px(printer, label, PrintOrientation.NORMAL) == PixelBounds(3, 3, 38, 21)
    assert printable_bounds_px(printer, label, PrintOrientation.CLOCKWISE_90) == PixelBounds(153, 1, 42, 19)


def test_printable_bounds_conversion_transforms_opposite_edges_for_every_orientation():
    orientations = frozenset(PrintOrientation)
    label = make_label(orientations=orientations)
    printer = make_printer(label, orientations=orientations)

    assert printable_bounds_px(printer, label, PrintOrientation.CLOCKWISE_180) == PixelBounds(60, 77, 38, 21)
    assert printable_bounds_px(printer, label, PrintOrientation.CLOCKWISE_270) == PixelBounds(5, 30, 42, 19)


def test_label_compatibility_rejects_raster_wider_than_printer():
    label = make_label()
    printer = make_printer(label, max_raster_width_px=37)

    assert is_label_compatible(printer, label, PrintOrientation.NORMAL) is False


def test_label_compatibility_rejects_raster_longer_than_printer():
    label = make_label()
    printer = make_printer(label, max_raster_length_px=20)

    assert is_label_compatible(printer, label, PrintOrientation.NORMAL) is False


def test_printable_bounds_conversion_rejects_incompatible_selection():
    label = make_label()
    printer = make_printer(label)

    with pytest.raises(ValueError, match="not compatible"):
        printable_bounds_px(printer, label, PrintOrientation.CLOCKWISE_180)


def test_registry_contains_exact_approved_records_in_order():
    assert [printer.model_id for printer in PRINTER_CAPABILITIES] == [
        "b1",
        "b18",
        "b21",
        "d11",
        "d11_h",
        "d110",
    ]
    assert [
        (
            printer.model_id,
            printer.display_name,
            printer.discovery_prefixes,
            printer.dpi_x,
            printer.dpi_y,
            printer.max_raster_width_px,
            printer.max_raster_length_px,
            (printer.density_min, printer.density_default, printer.density_max),
            printer.features,
            tuple(label.label_id for label in printer.labels),
        )
        for printer in PRINTER_CAPABILITIES
    ] == [
        (
            "b1",
            "NIIMBOT B1",
            ("b1",),
            203,
            203,
            384,
            65535,
            (1, 3, 5),
            frozenset({PrinterFeature.NFC_LABEL_IDENTIFICATION}),
            ("b-50x30",),
        ),
        (
            "b18",
            "NIIMBOT B18",
            ("b18",),
            203,
            203,
            384,
            65535,
            (1, 3, 3),
            frozenset({PrinterFeature.THERMAL_TRANSFER}),
            ("b18-14x30",),
        ),
        (
            "b21",
            "NIIMBOT B21",
            ("b21",),
            203,
            203,
            384,
            65535,
            (1, 3, 5),
            frozenset(),
            ("b-50x30",),
        ),
        ("d11", "NIIMBOT D11", ("d11",), 203, 203, 240, 65535, (1, 3, 3), frozenset(), ("d-12x40",)),
        (
            "d11_h",
            "NIIMBOT D11_H",
            ("d11_h",),
            300,
            300,
            240,
            65535,
            (1, 3, 3),
            frozenset({PrinterFeature.AUTOMATIC_LABEL_CALIBRATION}),
            ("d-12x40",),
        ),
        ("d110", "NIIMBOT D110", ("d110",), 203, 203, 240, 65535, (1, 3, 3), frozenset(), ("d-12x40",)),
    ]


def test_registry_contains_exact_approved_label_geometry():
    labels = {label.label_id: label for printer in PRINTER_CAPABILITIES for label in printer.labels}

    assert labels == {
        "b-50x30": LabelCapabilities(
            label_id="b-50x30",
            display_name="50 x 30 mm",
            media_width_mm=Decimal("50"),
            media_length_mm=Decimal("30"),
            printable_bounds=PrintableBounds(Decimal("1"), Decimal("0"), Decimal("48"), Decimal("30")),
            orientations=frozenset(PrintOrientation),
        ),
        "b18-14x30": LabelCapabilities(
            label_id="b18-14x30",
            display_name="14 x 30 mm",
            media_width_mm=Decimal("14"),
            media_length_mm=Decimal("30"),
            printable_bounds=PrintableBounds(Decimal("1"), Decimal("0"), Decimal("12"), Decimal("30")),
            orientations=frozenset({PrintOrientation.NORMAL, PrintOrientation.CLOCKWISE_180}),
        ),
        "d-12x40": LabelCapabilities(
            label_id="d-12x40",
            display_name="12 x 40 mm",
            media_width_mm=Decimal("12"),
            media_length_mm=Decimal("40"),
            printable_bounds=PrintableBounds(Decimal("0"), Decimal("0"), Decimal("12"), Decimal("40")),
            orientations=frozenset({PrintOrientation.NORMAL, PrintOrientation.CLOCKWISE_180}),
        ),
    }


def test_registry_pixel_bounds_match_approved_examples():
    expected = {
        "b1": PixelBounds(8, 0, 384, 240),
        "b18": PixelBounds(8, 0, 96, 240),
        "b21": PixelBounds(8, 0, 384, 240),
        "d11": PixelBounds(0, 0, 96, 320),
        "d11_h": PixelBounds(0, 0, 142, 472),
        "d110": PixelBounds(0, 0, 96, 320),
    }

    assert {
        printer.model_id: printable_bounds_px(printer, printer.labels[0], PrintOrientation.NORMAL)
        for printer in PRINTER_CAPABILITIES
    } == expected


def test_registry_lookup_returns_canonical_record():
    assert get_printer_capabilities("d11_h") is PRINTER_CAPABILITIES[4]


@pytest.mark.parametrize("model_id", ["unknown", "D11_H", ""])
def test_registry_lookup_raises_specific_error_for_unknown_canonical_id(model_id):
    with pytest.raises(UnknownPrinterModelError, match=model_id or "''"):
        get_printer_capabilities(model_id)
