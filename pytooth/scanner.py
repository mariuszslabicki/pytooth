import simpy
from enum import Enum
from pytooth import packet
import pytooth.constants as const

class ScannerState(Enum):
    SCAN = 1
    RX = 2
    TIFS = 3
    TX = 4
    IDLE = 5
    NOISE = 6

class Scanner(object):
    def __init__(self, id, env, events_list, network):
        self.env = env
        self.id = id
        self.received = 0
        self.lost = 0
        self.ongoing_receptions = {}
        self.ongoing_transmissions = 0
        self.action = env.process(self.main_loop())
        self.channel = 37
        self.events_list = events_list
        self.network = network
        self.state = ScannerState.SCAN
        self.receiving_packet = None
        self.endtime_scan = None
        self.replying = False
        self.debug_mode = False
        self.temp_to_remove = 0

    def main_loop(self):
        while True:
            if self.state == ScannerState.SCAN:
                self.debug_info("begin")
                self.endtime_scan = self.env.now + const.T_scanwindow

                try:
                    yield self.env.process(self.scan(self.channel, self.endtime_scan))
                    self.debug_info("end")
                    self.state = ScannerState.IDLE

                except simpy.Interrupt:
                    self.debug_info("break")
                    self.state = ScannerState.RX
                    break

            if self.state == ScannerState.RX:
                self.debug_info("begin")
                try:
                    yield self.env.process(self.receive())
                    self.debug_info("end")
                    if self.receiving_packet.type == packet.PktType.ADV_SCAN_IND:
                        self.state = ScannerState.TIFS
                        self.receiving_packet = None
                except simpy.Interrupt:
                    self.state = ScannerState.NOISE

            if self.state == ScannerState.TIFS:
                self.debug_info("begin")
                yield self.env.timeout(const.T_ifs)
                self.debug_info("end")
                if self.replying is True:
                    self.state = ScannerState.TX
                if self.replying is False:
                    self.state = ScannerState.SCAN

            if self.state == ScannerState.TX:
                self.debug_info("begin")
                pkt = packet.Packet(self.id, channel = self.channel, type=packet.PktType.SCAN_REQ)
                self.transmit(pkt)
                self.replying = False
                self.debug_info("end")
                self.state = ScannerState.TIFS

            if self.state == ScannerState.IDLE:
                self.debug_info("begin")
                yield self.env.process(self.idle(const.T_scaninterval - const.T_scanwindow))
                self.channel += 1
                if self.channel > 39:
                    self.channel = 37
                self.debug_info("end")
                self.state = ScannerState.SCAN

            # if self.state == ScannerState.NOISE:
            #     self.debug_info()
            #     start = self.env.now
            #     try:
            #         yield self.env.process(self.processInterference())
            #         self.state = ScannerState.LISTEN
            #     except simpy.Interrupt:
            #         self.state = ScannerState.NOISE
            #     self.events_list.append(dict(Task="SCANNER", Start=start, Finish=self.env.now, Resource='noise', Description='Interference'))


    def deliver(self, packet):
        if self.state == ScannerState.NOISE:
            self.action.interrupt()
        if self.state == ScannerState.RX:
            self.action.interrupt()
        if self.state == ScannerState.SCAN and self.channel == packet.channel:
            self.receiving_packet = packet
            self.action.interrupt()

    def scan(self, channel, end_time):
        how_long = self.endtime_scan - self.env.now
        yield self.env.timeout(how_long)

    def idle(self, how_long):
        yield self.env.timeout(how_long)

    def transmit(self, pkt):
        yield self.env.timeout(const.T_scanreq)
        self.network.deliverPacket(pkt)

    def processInterference(self):
        self.ongoing_transmissions += 1
        yield self.env.timeout(0.176)
        self.lost += 1
        self.ongoing_transmissions -= 1

    def receive(self):
        self.ongoing_transmissions += 1
        yield self.env.timeout(const.T_advind)
        if self.ongoing_transmissions == 1 and self.channel == self.receiving_packet.channel:
            self.received += 1
            self.ongoing_transmissions = 0
        else:
            self.lost += 1

    def print_summary(self):
        print("Scanner: Received correct", self.received)
        print("Scanner: Lost", self.lost)

    def debug_info(self, state):
        if self.debug_mode is True:
            channel = ""
            if self.state is ScannerState.SCAN or self.state is ScannerState.TX or self.state is ScannerState.RX:
                channel = " " + str(self.channel)
            if state == "begin":
                print("SC", self.id, "State", str(self.state) + channel, "\t\tbegin\t", self.env.now)
            if state == "end":
                print("SC", self.id, "State", str(self.state) + channel, "\t\tend\t", self.env.now)
            if state == "break":
                print("SC", self.id, "State", str(self.state) + channel, "\t\tbreak\t", self.env.now)
            if state == "continue":
                print("SC", self.id, "State", str(self.state) + channel, "\t\tcontinue\t", self.env.now)