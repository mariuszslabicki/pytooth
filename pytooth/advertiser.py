import random
import simpy
from enum import Enum
from pytooth import packet
import pytooth.constants as const

class AdvState(Enum):
    TX = 1
    TIFS = 2
    RX = 3
    DETECT = 4
    NOISE = 5
    IDLE = 6
    INIT = 7

class Advertiser(object):
    def __init__(self, id, env, events_list, network):
        self.id = id
        self.env = env
        self.packets_sent = 0
        self.action = env.process(self.main_loop())
        self.received_packet = None
        self.receiving_now = False
        self.events_list = events_list
        self.network = network
        self.state = AdvState.INIT
        self.beginAt = 100*self.id + 100
        self.channel = 37
        self.debug_mode = False
        self.time_to_end_rx = 0

    def main_loop(self):
        counter = 0
        while True:
            if self.state == AdvState.INIT:
                self.debug_info("begin")
                yield self.env.timeout(self.beginAt)
                self.debug_info("end")
                self.state = AdvState.IDLE

            if self.state == AdvState.IDLE:
                self.debug_info("begin")
                yield self.env.process(self.standby())
                self.debug_info("end")
                self.state = AdvState.TX

            if self.state == AdvState.TX:
                self.debug_info("begin")
                pkt = packet.Packet(self.id, channel = self.channel, type=packet.PktType.ADV_SCAN_IND)
                yield self.env.process(self.transmit(pkt, self.channel))
                self.debug_info("end")
                self.state = AdvState.TIFS
                
            if self.state == AdvState.TIFS:
                self.debug_info("begin")
                yield self.env.process(self.switch())
                self.debug_info("end")
                self.state = AdvState.DETECT

            if self.state == AdvState.DETECT:
                self.debug_info("begin")
                try:
                    yield self.env.process(self.detect(self.channel))
                    if self.channel == 39:
                        self.debug_info("end")
                        self.state = AdvState.IDLE
                        self.channel = 37
                    else:
                        self.debug_info("end")
                        self.state = AdvState.IDLE
                        self.channel += 1
                except simpy.Interrupt:
                    self.debug_info("break")
                    self.state = AdvState.RX
                    break

            if self.state == AdvState.RX:
                self.debug_info("begin")
                self.receiving_now = True
                try:
                    yield self.env.process(self.receive(self.channel))
                    self.state = AdvState.IDLE
                    self.debug_info("end")
                except simpy.Interrupt:
                    self.state = AdvState.NOISE
                    self.time_to_end_rx = 0.1
                    self.debug_info("break")
                    break

            if self.state == AdvState.NOISE:
                self.debug_info("begin")
                try:
                    yield self.env.process(self.wait_noise(self.time_to_end_rx))
                    self.state = AdvState.IDLE
                    self.debug_info("end")
                except simpy.Interrupt:
                    self.state = AdvState.NOISE
                    self.time_to_end_rx = 0.1
                    self.debug_info("break")
                    break

            counter += 1
    
    def deliver(self, packet):
        if self.state == AdvState.NOISE:
            self.action.interrupt()
        if self.state == AdvState.RX:
            self.action.interrupt()
        if self.state == AdvState.DETECT and self.channel == packet.channel:
            self.receiving_packet = packet
            self.action.interrupt()

    def transmit(self, pkt, channel):
        now = self.env.now
        self.state = AdvState.TX
        yield self.env.timeout(const.T_advind)
        self.network.deliverPacket(pkt)
        if channel == 37:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch37_msg', Description='Transmit'))
        if channel == 38:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch38_msg', Description='Transmit'))
        if channel == 39:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch39_msg', Description='Transmit'))

    def switch(self):
        self.state = AdvState.TIFS
        yield self.env.timeout(const.T_ifs)

    def detect(self, channel):
        now = self.env.now
        yield self.env.timeout(const.T_detect)
        if channel == 37:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch37_free', Description='Listen'))
        if channel == 38:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch38_free', Description='Listen'))
        if channel == 39:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch39_free', Description='Listen'))

    def listen(self, channel):
        yield self.env.timeout(const.T_scanreq)

    def wait_noise(self, time_to_end):
        yield self.env.timeout(time_to_end)

    def standby(self):
        self.state = AdvState.IDLE
        # yield self.env.timeout(random.expovariate(0.01))
        yield self.env.timeout(4000)

    def receive(self, packet):
        self.action.interrupt()
        yield self.env.timeout(0.1)

    def debug_info(self, state):
        if self.debug_mode is True:
            channel = ""
            if self.state is AdvState.DETECT or self.state is AdvState.TX or self.state is AdvState.RX:
                channel = " " + str(self.channel)
            if state == "begin":
                print("ADV", self.id, "State", str(self.state) + channel, "\t\tbegin\t", self.env.now)
            if state == "end":
                print("ADV", self.id, "State", str(self.state) + channel, "\t\tend\t", self.env.now)
        