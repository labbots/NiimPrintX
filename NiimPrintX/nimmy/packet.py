def packet_to_int(x):
    return int.from_bytes(x.data, "big")


class NiimbotPacket:
    CONNECT = 0xC1

    def __init__(self, type_, data):
        self.type = type_
        self.data = data

    @classmethod
    def from_bytes(cls, pkt):
        # Connect frames may include a leading 0x03 prefix
        if pkt and pkt[0] == 0x03:
            pkt = pkt[1:]
        assert pkt[:2] == b"\x55\x55"
        assert pkt[-2:] == b"\xaa\xaa"
        type_ = pkt[2]
        len_ = pkt[3]
        data = pkt[4 : 4 + len_]

        checksum = type_ ^ len_
        for i in data:
            checksum ^= i
        assert checksum == pkt[-3]

        return cls(type_, data)

    def to_bytes(self):
        checksum = self.type ^ len(self.data)
        for i in self.data:
            checksum ^= i
        frame = bytes(
            (0x55, 0x55, self.type, len(self.data), *self.data, checksum, 0xAA, 0xAA)
        )
        # Official app / niimbluelib prefix Connect with 0x03
        if self.type == self.CONNECT:
            return bytes((0x03,)) + frame
        return frame

    def __repr__(self):
        return f"<NiimbotPacket type={self.type} data={self.data}>"
