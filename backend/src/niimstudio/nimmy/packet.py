PACKET_HEADER = b"\x55\x55"
PACKET_FOOTER = b"\xaa\xaa"
PACKET_OVERHEAD = 7
MAX_PAYLOAD_LENGTH = 255


def packet_to_int(packet: "NiimbotPacket") -> int:
    return int.from_bytes(packet.data, "big")


class NiimbotPacket:
    def __init__(self, type_: int, data: bytes):
        if not 0 <= type_ <= 255:
            raise ValueError("Packet type must fit in one byte")
        if len(data) > MAX_PAYLOAD_LENGTH:
            raise ValueError("Packet payload must not exceed 255 bytes")
        self.type = type_
        self.data = data

    @classmethod
    def from_bytes(cls, packet: bytes) -> "NiimbotPacket":
        if len(packet) < PACKET_OVERHEAD:
            raise ValueError("Packet is too short")
        if packet[:2] != PACKET_HEADER:
            raise ValueError("Packet header is invalid")
        if packet[-2:] != PACKET_FOOTER:
            raise ValueError("Packet footer is invalid")

        type_ = packet[2]
        payload_length = packet[3]
        expected_length = payload_length + PACKET_OVERHEAD
        if len(packet) != expected_length:
            raise ValueError(f"Packet length is {len(packet)} bytes; expected {expected_length}")

        data = packet[4 : 4 + payload_length]
        checksum = type_ ^ payload_length
        for value in data:
            checksum ^= value
        if checksum != packet[-3]:
            raise ValueError("Packet checksum is invalid")
        return cls(type_, data)

    def to_bytes(self) -> bytes:
        checksum = self.type ^ len(self.data)
        for value in self.data:
            checksum ^= value
        return bytes((0x55, 0x55, self.type, len(self.data), *self.data, checksum, 0xAA, 0xAA))

    def __repr__(self) -> str:
        return f"<NiimbotPacket type={self.type} data={self.data}>"
