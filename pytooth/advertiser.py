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
    BEGIN_FSM = 12

class Advertiser(object):
    def __init__(self, id, env, events_list, msg_log, network, advertising_interval, data_interval, stop_advertising=False):
        self.id = id
        self.env = env
        self.packets_sent = 0
        self.action = env.process(self.main_loop())
        self.received_packet = None
        self.receiving_now = False
        self.ongoing_receptions = {37:0, 38:0, 39:0}
        self.events_list = events_list
        self.msg_log = msg_log
        self.network = network
        self.state = AdvState.BEGIN_FSM
        self.init_delay_start_time = None
        self.advertising_interval = advertising_interval
        self.data_interval = data_interval
        self.stop_advertising = stop_advertising
        self.request_received = False
        self.use_random_delay = True
        self.channel = 37
        self.receptionInterrupted = False
        self.debug_mode = False
        self.scanner_id = -1
        self.adv_copy_id = 0
        self.seq_no = 0
        self.number_of_sent_adv_packets = 0
        self.number_of_sent_adv_events = 0
        self.number_of_delivered_adv_events = 0
        self.number_of_sent_data_values = 0
        self.number_of_delivered_data_values = 0
        self.number_of_sent_req_by_scanner = 0
        self.number_of_received_req = 0
        self.number_of_transmitted_resp = 0
        self.number_of_delivered_resp = 0
        self.when_delivered_data = {}
        self.recv_seq_no = -1
        self.recv_copy_id = -1
        self.end_of_data_interval = None
        self.end_of_idle = None

    def main_loop(self):
        while True:
            if self.state == AdvState.BEGIN_FSM:
                random_delay = random.randint(0, self.data_interval)
                yield self.env.timeout(random_delay)
                self.end_of_data_interval = self.env.now + self.data_interval
                self.end_of_idle = self.env.now + self.advertising_interval
                self.state = AdvState.INIT_DELAY

            if self.state == AdvState.INIT_DELAY:
                self.init_delay_start_time = self.env.now
                yield self.env.timeout(const.T_init_delay)
                self.state = AdvState.RADIO_START_DELAY

            if self.state == AdvState.RADIO_START_DELAY:
                yield self.env.timeout(const.T_radio_start_delay)
                self.state = AdvState.TX_ADV

            if self.state == AdvState.TX_ADV:
                pkt = packet.Packet(src_id = self.id, dst_id=-1, channel = self.channel, 
                        type=packet.PktType.ADV_SCAN_IND, seq_no=self.seq_no, copy_id=self.adv_copy_id)
                yield self.env.process(self.transmit(pkt))
                self.number_of_sent_adv_packets += 1
                if self.channel == 39:
                    self.number_of_sent_adv_events += 1
                self.state = AdvState.RADIO_SWITCH_DELAY1
                
            if self.state == AdvState.RADIO_SWITCH_DELAY1:
                yield self.env.timeout(const.T_ifs_advertiser)
                self.state = AdvState.DETECT

            if self.state == AdvState.DETECT:
                try:
                    yield self.env.process(self.detect(self.channel))
                    if self.channel == 39:
                        self.state = AdvState.POSTPROCESSING_DELAY
                        self.channel = 37
                    else:
                        self.state = AdvState.STANDBY_DELAY
                        self.channel += 1
                except simpy.Interrupt:
                    self.state = AdvState.RX

            if self.state == AdvState.POSTPROCESSING_DELAY:
                yield self.env.timeout(const.T_postprocessing_delay)
                self.state = AdvState.IDLE
            
            if self.state == AdvState.STANDBY_DELAY:
                yield self.env.timeout(const.T_standby_delay)
                self.state = AdvState.RADIO_START_DELAY

            if self.state == AdvState.IDLE:
                yield self.env.timeout(self.end_of_idle - self.env.now)
                if self.use_random_delay is True:
                    random_shift = random.randint(0, 10000)
                else:
                    random_shift = 0
                self.end_of_idle += self.advertising_interval + random_shift

                if self.env.now >= self.end_of_data_interval:
                    if self.request_received is False or self.stop_advertising is False:
                        self.number_of_sent_data_values += 1
                    self.request_received = False
                    self.adv_copy_id = 0
                    self.seq_no += 1
                    self.end_of_data_interval = self.end_of_data_interval + self.data_interval
                else:
                    self.adv_copy_id += 1
                if self.request_received is False or self.stop_advertising is False:
                    self.state = AdvState.INIT_DELAY
                else:
                    self.state = AdvState.IDLE

            if self.state == AdvState.RX:
                self.receptionInterrupted = False
                yield self.env.process(self.receive(self.receiving_packet))
                if self.receptionInterrupted == False and self.receiving_packet.dst_id == self.id:
                    self.request_received = True
                    if self.stop_advertising is True:
                        self.number_of_sent_data_values += 1
                    if self.receiving_packet.copy_id+1 not in self.when_delivered_data:
                        self.when_delivered_data[self.receiving_packet.copy_id+1] = 1
                    else:
                        self.when_delivered_data[self.receiving_packet.copy_id+1] += 1
                    self.number_of_received_req += 1
                    self.state = AdvState.RADIO_SWITCH_DELAY2
                    self.scanner_id = self.receiving_packet.src_id
                    self.recv_copy_id = self.receiving_packet.copy_id
                    self.recv_seq_no = self.receiving_packet.seq_no
                else:
                    if self.channel == 39:
                        self.state = AdvState.POSTPROCESSING_DELAY
                        self.channel = 37
                    else:
                        self.state = AdvState.STANDBY_DELAY
                        self.channel += 1
            
            if self.state == AdvState.RADIO_SWITCH_DELAY2:
                yield self.env.timeout(const.T_ifs_advertiser)
                self.state = AdvState.TX_SCAN_RESP
                continue

            if self.state == AdvState.TX_SCAN_RESP:
                pkt = packet.Packet(src_id = self.id, dst_id = self.scanner_id, channel = self.channel, 
                        type=packet.PktType.SCAN_RSP, seq_no=self.recv_seq_no, copy_id=self.recv_copy_id)
                yield self.env.process(self.transmit(pkt))
                self.number_of_transmitted_resp += 1
                if self.stop_advertising is True and self.request_received is True and self.channel == 39:
                    self.state = AdvState.IDLE
                    self.channel = 37
                else:
                    if self.channel == 39:
                        self.state = AdvState.POSTPROCESSING_DELAY
                        self.channel = 37
                    else:
                        self.state = AdvState.STANDBY_DELAY
                        self.channel += 1
                continue

    
    def beginReception(self, packet):
        self.ongoing_receptions[packet.channel] += 1
        if self.channel == packet.channel:
            if self.state == AdvState.DETECT and self.ongoing_receptions[self.channel] == 1:
                self.receiving_packet = packet
                self.action.interrupt("begin_reception")
            if self.state == AdvState.RX:
                self.receptionInterrupted = True

    def endReception(self, packet):
        self.ongoing_receptions[packet.channel] -= 1

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

    def receive(self, rcv_packet):
        if self.receiving_packet.type == packet.PktType.ADV_SCAN_IND:
            yield self.env.timeout(const.T_advind)
        elif self.receiving_packet.type == packet.PktType.SCAN_RSP:
            yield self.env.timeout(const.T_scanresp)
        elif self.receiving_packet.type == packet.PktType.SCAN_REQ:
            yield self.env.timeout(const.T_scanreq)

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

    def print_stats(self):
        print("ADV:", self.id, "\tADV", self.number_of_sent_adv_packets, "\tREQ", self.number_of_received_req, "\tRESP", self.number_of_transmitted_resp)

    def save_pkt_to_log(self, txrx, pkt):
        if txrx == "Tx":
            self.msg_log.append([self.env.now, "Tx", self.id, pkt.src_id, pkt.dst_id, pkt.type, self.channel, pkt.seq_no, pkt.copy_id])
        if txrx == "Rx":
            self.msg_log.append([self.env.now, "Rx", self.id, pkt.src_id, pkt.dst_id, pkt.type, self.channel, pkt.seq_no, pkt.copy_id])
