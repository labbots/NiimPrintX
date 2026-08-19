import pytest

from niimstudio.nimmy.packet import NiimbotPacket, packet_to_int


@pytest.mark.parametrize(
    ("packet_type", "data"),
    [
        (0x01, b""),
        (0x40, b"\x0b"),
        (0x85, bytes(range(32))),
    ],
)
def test_packet_round_trip(packet_type, data):
    encoded = NiimbotPacket(packet_type, data).to_bytes()

    decoded = NiimbotPacket.from_bytes(encoded)

    assert decoded.type == packet_type
    assert decoded.data == data


@pytest.mark.parametrize(
    ("packet", "message"),
    [
        (b"\x55", "too short"),
        (b"\x54\x55\x01\x00\x01\xaa\xaa", "header"),
        (b"\x55\x55\x01\x00\x01\xaa\xab", "footer"),
        (b"\x55\x55\x01\x01\x01\xaa\xaa", "length"),
        (b"\x55\x55\x01\x00\x00\xaa\xaa", "checksum"),
    ],
)
def test_packet_rejects_malformed_input(packet, message):
    with pytest.raises(ValueError, match=message):
        NiimbotPacket.from_bytes(packet)


def test_packet_rejects_invalid_type():
    with pytest.raises(ValueError, match="type"):
        NiimbotPacket(256, b"")


def test_packet_rejects_oversized_payload():
    with pytest.raises(ValueError, match="255"):
        NiimbotPacket(1, bytes(256))


def test_packet_to_int_uses_big_endian_data():
    packet = NiimbotPacket(1, b"\x01\x02")

    assert packet_to_int(packet) == 258
