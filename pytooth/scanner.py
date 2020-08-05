import simpy
from enum import Enum
from pytooth import packet
import pytooth.constants as const

class ScannerState(Enum):
    SCAN = 1
    RX = 2
    TX = 3
    COLISION = 4
    T_IFS_DELAY1 = 5
    T_IFS_DELAY2 = 6
    W_DELAY = 7
    DECODING_DELAY = 8
    ERROR_DECODING_DELAY = 9
    MAX_DELAY = 10
    FREQ_CHANGE_DELAY = 11

class Scanner(object):
    def __init__(self, id, env, events_list, network):
        self.env = env
        self.id = id
        self.received = 0
        self.lost = 0
        self.action = env.process(self.main_loop())
        self.events_list = events_list
        self.channel = 37
        self.network = network
        self.state = ScannerState.SCAN
        self.receiving_packet = None
        self.ongoing_receptions = 0
        self.freq_change_time = None
        self.scan_started = False
        self.debug_mode = False

    def main_loop(self):
        while True:
            if self.state == ScannerState.SCAN:
                self.debug_info("begin")
                self.save_event("begin")
                if self.scan_started is False:
                    self.freq_change_time = self.env.now + const.T_scanwindow
                    self.scan_started = True

                try:
                    yield self.env.process(self.scan(self.channel, self.freq_change_time))
                    self.debug_info("end")
                    self.save_event("end")
                    self.state = ScannerState.FREQ_CHANGE_DELAY

                except simpy.Interrupt:
                    self.debug_info("break")
                    self.save_event("break")
                    self.state = ScannerState.RX

            if self.state == ScannerState.RX:
                self.debug_info("begin")
                self.save_event("begin")
                try:
                    yield self.env.process(self.receive())
                    print("Skonczylem odbior")
                    self.debug_info("end")
                    self.save_event("end")
                    if self.receiving_packet.type == packet.PktType.ADV_SCAN_IND:
                        self.state = ScannerState.T_IFS_DELAY1
                        self.receiving_packet = None
                except simpy.Interrupt as i:
                    self.debug_info("break")
                    self.save_event("break")
                    if i.cause == "begin_transmission":
                        self.state = ScannerState.COLISION


            if self.state == ScannerState.FREQ_CHANGE_DELAY:
                self.debug_info("begin")
                self.save_event("begin")
                yield self.env.timeout(const.T_freq_change_delay)
                self.scan_started = False
                self.channel += 1
                if self.channel == 40:
                    self.channel = 37
                self.debug_info("end")
                self.save_event("end")
                self.state = ScannerState.SCAN

            if self.state == ScannerState.T_IFS_DELAY1:
                self.debug_info("begin")
                self.save_event("begin")
                yield self.env.timeout(const.T_ifs_scanner)
                self.debug_info("end")
                self.save_event("end")
                self.state = ScannerState.TX

            if self.state == ScannerState.TX:
                self.debug_info("begin")
                self.save_event("begin")
                pkt = packet.Packet(self.id, channel = self.channel, type=packet.PktType.SCAN_REQ)
                yield self.env.process(self.transmit(pkt))
                self.debug_info("end")
                self.save_event("end")
                self.state = ScannerState.T_IFS_DELAY2

            if self.state == ScannerState.T_IFS_DELAY2:
                self.debug_info("begin")
                self.save_event("begin")
                yield self.env.timeout(const.T_ifs_scanner)
                self.debug_info("end")
                self.save_event("end")
                self.state = ScannerState.SCAN

            if self.state == ScannerState.COLISION:
                self.debug_info("begin")
                self.save_event("begin")
                try:
                    yield self.env.process(self.colide())
                    # self.debug_info("end")
                    # self.save_event("end")
                except simpy.Interrupt as i:
                    self.debug_info("break")
                    self.save_event("break")
                    if i.cause == "begin_reception":
                        print(self.ongoing_receptions)
                        self.state = ScannerState.COLISION
                    if i.cause == "end_reception":
                        print(self.ongoing_receptions)
                        if self.ongoing_receptions == 0:
                            self.state = ScannerState.SCAN
                        else:
                            self.state = ScannerState.COLISION

    def beginReception(self, packet):
        if self.channel == packet.channel:
            self.ongoing_receptions += 1
            if self.state == ScannerState.SCAN:
                self.receiving_packet = packet
                self.action.interrupt("begin_reception")
            if self.state == ScannerState.RX:
                self.action.interrupt("begin_reception")
            if self.state == ScannerState.COLISION:
                self.action.interrupt("begin_reception")

    def endReception(self, packet):
        if self.channel == packet.channel:
            self.ongoing_receptions -= 1
            # if self.state == ScannerState.RX:
            #     self.action.interrupt("end_reception")
            if self.state == ScannerState.COLISION:
                self.action.interrupt("end_reception")

    def scan(self, channel, end_time):
        how_long = end_time - self.env.now
        yield self.env.timeout(how_long)

    def transmit(self, pkt):
        self.network.beginReceptionInDevices(pkt)
        yield self.env.timeout(const.T_scanreq)
        self.network.endReceptionInDevices(pkt)

    def receive(self):
        if self.receiving_packet.type == packet.PktType.ADV_SCAN_IND:
            yield self.env.timeout(const.T_advind)

    def colide(self):
        yield self.env.timeout(100*const.T_advind)

    def print_summary(self):
        print("Scanner: Received correct", self.received)
        print("Scanner: Lost", self.lost)

    def debug_info(self, state):
        if self.debug_mode is True:
            channel = ""
            if self.state is ScannerState.SCAN or self.state is ScannerState.TX or self.state is ScannerState.RX:
                channel = " " + str(self.channel)
            if state == "begin":
                print("SC", self.id, str(self.state) + channel, "\t\t\t\tbegin\t", self.env.now)
            if state == "end":
                print("SC", self.id, str(self.state) + channel, "\t\t\t\tend\t", self.env.now)
            if state == "break":
                print("SC", self.id, str(self.state) + channel, "\t\t\t\tbreak\t", self.env.now)
            if state == "continue":
                print("SC", self.id, str(self.state) + channel, "\t\t\t\tcontinue\t", self.env.now)

    def save_event(self, text):
        channel = ""
        if self.state is ScannerState.SCAN or self.state is ScannerState.TX or self.state is ScannerState.RX:
            channel = " " + str(self.channel)
        self.events_list.append(["SC", self.id, self.env.now, text, str(self.state), channel])