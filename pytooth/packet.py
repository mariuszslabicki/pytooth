from enum import Enum

class PktType(Enum):
    ADV_SCAN_IND = 1
    SCAN_REQ = 2
    SCAN_RSP = 3

class Packet(object):
    def __init__(self, src_id, dst_id, channel, type):
        self.src_id = src_id
        self.dst_id = dst_id
        self.channel = channel
        self.type = type