import random
import simpy
from enum import Enum
from pytooth import packet
import pytooth.constants as const

class AdvState(Enum):
    IDLE = 1
    TX_ADV = 2
    TX_SCAN_RESP = 3
    RX = 4
    DETECT = 5
    INIT_DELAY = 6
    RADIO_START_DELAY = 7
    RADIO_SWITCH_DELAY1 = 8
    STANDBY_DELAY = 9
    POSTPROCESSING_DELAY = 10
    RADIO_SWITCH_DELAY2 = 11

class Advertiser(object):
    def __init__(self, id, env, events_list, network):
        self.id = id
        self.env = env
        self.packets_sent = 0
        self.action = env.process(self.main_loop())
        self.received_packet = None
        self.receiving_now = False
        self.ongoing_receptions = {37:0, 38:0, 39:0}
        self.events_list = events_list
        self.network = network
        self.state = AdvState.INIT_DELAY
        self.beginAt = 100*self.id + 100
        self.channel = 37
        self.receptionInterrupted = False
        self.debug_mode = False
        self.number_of_transmitted_adv = 0
        self.number_of_received_req = 0
        self.number_of_transmitted_resp = 0

    def main_loop(self):
        counter = 0
        while True:
            if self.state == AdvState.INIT_DELAY:
                self.debug_info("begin")
                self.save_event("begin")
                yield self.env.timeout(const.T_init_delay)
                self.debug_info("end")
                self.save_event("end")
                self.state = AdvState.RADIO_START_DELAY

            if self.state == AdvState.RADIO_START_DELAY:
                self.debug_info("begin")
                self.save_event("begin")
                yield self.env.timeout(const.T_radio_start_delay)
                self.debug_info("end")
                self.save_event("end")
                self.state = AdvState.TX_ADV

            if self.state == AdvState.TX_ADV:
                self.debug_info("begin")
                self.save_event("begin")
                pkt = packet.Packet(self.id, channel = self.channel, type=packet.PktType.ADV_SCAN_IND)
                yield self.env.process(self.transmit(pkt))
                self.number_of_transmitted_adv += 1
                self.debug_info("end")
                self.save_event("end")
                self.state = AdvState.RADIO_SWITCH_DELAY1
                
            if self.state == AdvState.RADIO_SWITCH_DELAY1:
                self.debug_info("begin")
                self.save_event("begin")
                yield self.env.timeout(const.T_ifs_advertiser)
                self.debug_info("end")
                self.save_event("end")
                self.state = AdvState.DETECT

            if self.state == AdvState.DETECT:
                self.debug_info("begin")
                self.save_event("begin")
                try:
                    yield self.env.process(self.detect(self.channel))
                    self.debug_info("end")
                    self.save_event("end")
                    if self.channel == 39:
                        self.state = AdvState.POSTPROCESSING_DELAY
                        self.channel = 37
                    else:
                        self.state = AdvState.STANDBY_DELAY
                        self.channel += 1
                except simpy.Interrupt:
                    self.debug_info("break")
                    self.save_event("break")
                    self.state = AdvState.RX

            if self.state == AdvState.POSTPROCESSING_DELAY:
                self.debug_info("begin")
                self.save_event("begin")
                yield self.env.timeout(const.T_postprocessing_delay)
                self.debug_info("end")
                self.save_event("end")
                self.state = AdvState.IDLE
            
            if self.state == AdvState.STANDBY_DELAY:
                self.debug_info("begin")
                self.save_event("begin")
                yield self.env.timeout(const.T_standby_delay)
                self.debug_info("end")
                self.save_event("end")
                self.state = AdvState.RADIO_START_DELAY

            if self.state == AdvState.IDLE:
                self.debug_info("begin")
                self.save_event("begin")
                yield self.env.timeout(1000)
                self.debug_info("end")
                self.save_event("end")
                self.state = AdvState.INIT_DELAY

            if self.state == AdvState.RX:
                self.debug_info("begin")
                self.save_event("begin")
                self.receptionInterrupted = False
                yield self.env.process(self.receive(self.receiving_packet))
                if self.receptionInterrupted == False:
                    self.number_of_received_req += 1
                    self.state = AdvState.RADIO_SWITCH_DELAY2
                else:
                    if self.channel == 39:
                        self.state = AdvState.POSTPROCESSING_DELAY
                        self.channel = 37
                    else:
                        self.state = AdvState.STANDBY_DELAY
                        self.channel += 1
            
            if self.state == AdvState.RADIO_SWITCH_DELAY2:
                self.debug_info("begin")
                self.save_event("begin")
                yield self.env.timeout(const.T_ifs_advertiser)
                self.debug_info("end")
                self.save_event("end")
                self.state = AdvState.TX_SCAN_RESP
                continue

            if self.state == AdvState.TX_SCAN_RESP:
                self.debug_info("begin")
                self.save_event("begin")
                pkt = packet.Packet(self.id, channel = self.channel, type=packet.PktType.SCAN_RSP)
                yield self.env.process(self.transmit(pkt))
                self.number_of_transmitted_resp += 1
                self.debug_info("end")
                self.save_event("end")
                if self.channel == 39:
                    self.state = AdvState.POSTPROCESSING_DELAY
                    self.channel = 37
                else:
                    self.state = AdvState.STANDBY_DELAY
                    self.channel += 1
                continue

            counter += 1
    
    def beginReception(self, packet):
        if self.channel == packet.channel:
            self.ongoing_receptions[self.channel] += 1
            if self.state == AdvState.DETECT and self.ongoing_receptions[self.channel] == 1:
                self.receiving_packet = packet
                self.action.interrupt("begin_reception")
            if self.state == AdvState.RX:
                self.receptionInterrupted = True

    def endReception(self, packet):
        if self.channel == packet.channel:
            self.ongoing_receptions[self.channel] -= 1

    def transmit(self, pkt):
        self.network.beginReceptionInDevices(pkt)
        if pkt.type == packet.PktType.ADV_SCAN_IND:
            yield self.env.timeout(const.T_advind)
        if pkt.type == packet.PktType.SCAN_RSP:
            yield self.env.timeout(const.T_scanresp)
        self.network.endReceptionInDevices(pkt)

    def detect(self, channel):
        yield self.env.timeout(const.T_detect)

    def listen(self, channel):
        yield self.env.timeout(const.T_scanreq)

    def standby(self):
        # yield self.env.timeout(random.expovariate(0.01))
        yield self.env.timeout(4000)

    def receive(self, packet):
        yield self.env.timeout(300) # how long should it wait for packet, interrupted if packet is received

    def debug_info(self, state):
        if self.debug_mode is True:
            channel = ""
            if self.state is AdvState.DETECT or self.state is AdvState.TX_ADV or self.state is AdvState.TX_SCAN_RESP or self.state is AdvState.RX:
                channel = " " + str(self.channel)
            if state == "begin":
                print("ADV", self.id, str(self.state) + channel, "\t\t\t\tbegin\t", self.env.now)
            if state == "end":
                print("ADV", self.id, str(self.state) + channel, "\t\t\t\tend\t", self.env.now)
            if state == "break":
                print("ADV", self.id, str(self.state) + channel, "\t\t\t\tbreak\t", self.env.now)

    def save_event(self, text):
        channel = ""
        if self.state is AdvState.DETECT or self.state is AdvState.TX_ADV or self.state is AdvState.TX_SCAN_RESP or self.state is AdvState.RX:
            channel = " " + str(self.channel)
        self.events_list.append(["ADV", self.id, self.env.now, text, str(self.state), channel])