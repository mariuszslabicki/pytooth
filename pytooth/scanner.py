import simpy
from enum import Enum

class ScannerState(Enum):
    LISTEN = 1
    RX = 2
    TX = 3
    IDLE = 4
    SWITCH = 5
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
        self.channel = None
        self.events_list = events_list
        self.network = network
        self.state = ScannerState.LISTEN
        self.receiving_packet = None
        self.debug_mode = False

    def main_loop(self):
        while True:
            if self.state == ScannerState.LISTEN:
                self.debug_info()
                self.channel = 37
                begin = self.env.now
                end_window = self.env.now + 500
                while self.env.now < end_window:
                    try:
                        yield self.env.process(self.scan(self.channel, end_window - self.env.now))
                    except simpy.Interrupt:
                        self.state = ScannerState.RX
                        break
                self.events_list.append(dict(Task="SCANNER", Start=begin, Finish=self.env.now, Resource='ch37_free', Description='Listen'))

            if self.state == ScannerState.RX:
                self.debug_info()
                start = self.env.now
                try:
                    yield self.env.process(self.receive())
                    self.state = ScannerState.LISTEN
                except simpy.Interrupt:
                    self.state = ScannerState.NOISE
                self.events_list.append(dict(Task="SCANNER", Start=start, Finish=self.env.now, Resource='ch37_msg', Description='Rx'))

            if self.state == ScannerState.NOISE:
                self.debug_info()
                start = self.env.now
                try:
                    yield self.env.process(self.processInterference())
                    self.state = ScannerState.LISTEN
                except simpy.Interrupt:
                    self.state = ScannerState.NOISE
                self.events_list.append(dict(Task="SCANNER", Start=start, Finish=self.env.now, Resource='noise', Description='Interference'))


    def deliver(self, packet):
        if self.state == ScannerState.NOISE:
            self.action.interrupt()
        if self.state == ScannerState.RX:
            self.action.interrupt()
        if self.state == ScannerState.LISTEN and self.channel == packet.channel:
            self.receiving_packet = packet
            self.action.interrupt()

    def scan(self, channel, how_long):
        self.state = ScannerState.LISTEN
        yield self.env.timeout(how_long)

    def processInterference(self):
        self.ongoing_transmissions += 1
        yield self.env.timeout(0.176)
        self.lost += 1
        self.ongoing_transmissions -= 1

    def receive(self):
        self.ongoing_transmissions += 1
        yield self.env.timeout(0.176)
        if self.ongoing_transmissions == 1 and self.channel == self.receiving_packet.channel:
            self.received += 1
            self.ongoing_transmissions = 0
        else:
            self.lost += 1

    def print_summary(self):
        print("Scanner: Received correct", self.received)
        print("Scanner: Lost", self.lost)

    def debug_info(self):
        if self.debug_mode is True:
            print("SC State", self.state, "at", self.env.now)