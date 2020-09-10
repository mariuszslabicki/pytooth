import random
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
    SCAN_FOR_RESP = 12

class Scanner(object):
    def __init__(self, id, env, events_list, msg_log, network, backoff=None):
        self.env = env
        self.id = id
        self.received = 0
        self.lost = 0
        self.action = env.process(self.main_loop())
        self.events_list = events_list
        self.msg_log = msg_log
        self.channel = 37
        self.network = network
        self.state = ScannerState.SCAN
        self.receiving_packet = None
        self.adv_id = -1
        self.ongoing_receptions = {37:0, 38:0, 39:0}
        self.freq_change_time = None
        self.scan_started = False
        self.debug_mode = False
        self.number_of_received_adv = 0
        self.number_of_sent_req = 0
        self.backoff = backoff
        if self.backoff == "BTBackoff":
            self.backoffCount = 0
            self.upperLimit = 0
            self.valid_resp = 0
            self.invalid_resp = 0
        self.recv_seq_no = -1
        self.recv_copy_id = -1
        self.received_adv_data_values = {}
        self.received_adv_events = {}
        self.received_adv_packets = {}
        self.last_seen_adv_data = {}

    def main_loop(self):
        while True:
            if self.state == ScannerState.SCAN:
                # self.debug_info("begin")
                # self.save_event("begin")
                if self.scan_started is False:
                    self.freq_change_time = self.env.now + const.T_scanwindow   
                    self.scan_started = True
                    if self.backoff == "BTBackoff":
                        self.backoffCount = 1
                        self.upperLimit = 1
                try:
                    #TODO Czy to jest poprawny warunek
                    if self.freq_change_time > self.env.now:
                        yield self.env.process(self.scan(self.freq_change_time))
                    # self.debug_info("end")
                    # self.save_event("end")
                    self.state = ScannerState.FREQ_CHANGE_DELAY

                except simpy.Interrupt as i:
                    # self.debug_info("break")
                    # self.save_event("break")
                    if i.cause == "begin_reception":
                        self.state = ScannerState.RX
                    if i.cause == "end_reception":
                        self.state = ScannerState.ERROR_DECODING_DELAY

            if self.state == ScannerState.SCAN_FOR_RESP:
                # self.debug_info("begin")
                # self.save_event("begin")
                try:
                    yield self.env.process(self.scanForResp())
                    self.evaluateBackoff(receivedRSP=False)
                    if self.freq_change_time < self.env.now:
                        self.state = ScannerState.FREQ_CHANGE_DELAY
                    else:
                        self.state = ScannerState.SCAN
                
                except simpy.Interrupt as i:
                    # self.debug_info("break")
                    # self.save_event("break")
                    if i.cause == "begin_reception":
                        self.state = ScannerState.RX
                    if i.cause == "end_reception":
                        self.state = ScannerState.ERROR_DECODING_DELAY
                        self.evaluateBackoff(receivedRSP=False)


            if self.state == ScannerState.RX:
                # self.debug_info("begin")
                # self.save_event("begin")
                try:
                    yield self.env.process(self.receive())
                    # self.debug_info("end")
                    # self.save_event("end")
                    # self.save_pkt_to_log("Rx", self.receiving_packet)
                    if self.receiving_packet.type == packet.PktType.ADV_SCAN_IND:
                        self.recv_copy_id = self.receiving_packet.copy_id
                        self.recv_seq_no = self.receiving_packet.seq_no
                        if self.receiving_packet.src_id not in self.received_adv_data_values:
                            self.received_adv_data_values[self.receiving_packet.src_id] = 1
                            self.received_adv_packets[self.receiving_packet.src_id] = 1
                            self.last_seen_adv_data[self.receiving_packet.src_id] = self.recv_seq_no
                            self.network.advertisers[self.receiving_packet.src_id].number_of_delivered_adv_events = 1
                            self.network.advertisers[self.receiving_packet.src_id].number_of_delivered_data_values = 1
                        else:
                            self.received_adv_packets[self.receiving_packet.src_id] += 1
                            self.network.advertisers[self.receiving_packet.src_id].number_of_delivered_adv_events += 1
                            if self.last_seen_adv_data[self.receiving_packet.src_id] != self.recv_seq_no:
                                self.last_seen_adv_data[self.receiving_packet.src_id] = self.recv_seq_no
                                self.network.advertisers[self.receiving_packet.src_id].number_of_delivered_data_values += 1
                        self.state = ScannerState.DECODING_DELAY
                        if self.backoff == "BTBackoff" and self.backoffCount > 0:
                            self.backoffCount -= 1
                        if self.backoff == None or self.backoff == "BTBackoff" and self.backoffCount == 0:
                            self.state = ScannerState.T_IFS_DELAY1
                            self.adv_id = self.receiving_packet.src_id
                        if self.backoff == "BTBackoff" and self.backoffCount > 0:
                            self.state = ScannerState.DECODING_DELAY
                        self.receiving_packet = None
                        self.number_of_received_adv += 1

                    elif self.receiving_packet.type == packet.PktType.SCAN_RSP:
                        if self.receiving_packet.dst_id == self.id:
                            self.evaluateBackoff(receivedRSP=True)
                        self.network.advertisers[self.receiving_packet.src_id].number_of_delivered_resp += 1
                        self.state = ScannerState.DECODING_DELAY
                        self.receiving_packet = None

                except simpy.Interrupt as i:
                    # self.debug_info("break")
                    # self.save_event("break")
                    if i.cause == "begin_reception":
                        self.receiving_packet = None
                        self.state = ScannerState.SCAN

            if self.state == ScannerState.FREQ_CHANGE_DELAY:
                # self.debug_info("begin")
                # self.save_event("begin")
                yield self.env.timeout(const.T_freq_change_delay)
                self.scan_started = False
                self.channel += 1
                if self.channel == 40:
                    self.channel = 37
                # self.debug_info("end")
                # self.save_event("end")
                self.state = ScannerState.SCAN

            if self.state == ScannerState.T_IFS_DELAY1:
                # self.debug_info("begin")
                # self.save_event("begin")
                yield self.env.timeout(const.T_ifs_scanner)
                # self.debug_info("end")
                # self.save_event("end")
                self.state = ScannerState.TX

            if self.state == ScannerState.TX:
                # self.debug_info("begin")
                # self.save_event("begin")
                pkt = packet.Packet(src_id = self.id, dst_id=self.adv_id, channel = self.channel, 
                        type=packet.PktType.SCAN_REQ, seq_no=self.recv_seq_no, copy_id=self.recv_copy_id)
                yield self.env.process(self.transmit(pkt))
                self.network.advertisers[self.adv_id].number_of_sent_req_by_scanner += 1
                # self.save_pkt_to_log("Tx", pkt)
                self.number_of_sent_req += 1
                # self.debug_info("end")
                # self.save_event("end")
                if self.freq_change_time < self.env.now:
                    self.state = ScannerState.W_DELAY
                else:
                    self.state = ScannerState.T_IFS_DELAY2

            if self.state == ScannerState.T_IFS_DELAY2:
                # self.debug_info("begin")
                # self.save_event("begin")
                yield self.env.timeout(const.T_ifs_scanner)
                # self.debug_info("end")
                # self.save_event("end")
                self.state = ScannerState.SCAN_FOR_RESP

            if self.state == ScannerState.ERROR_DECODING_DELAY:
                # self.debug_info("begin")
                # self.save_event("begin")
                yield self.env.timeout(const.T_error_decoding_delay)
                # self.debug_info("end")
                # self.save_event("end")
                self.state = ScannerState.SCAN

            if self.state == ScannerState.DECODING_DELAY:
                # self.debug_info("begin")
                # self.save_event("begin")
                yield self.env.timeout(const.T_decod_delay)
                # self.debug_info("end")
                # self.save_event("end")
                self.state = ScannerState.SCAN

            if self.state == ScannerState.W_DELAY:
                # self.debug_info("begin")
                # self.save_event("begin")
                w_delay = const.T_scanreq + const.T_ifs_scanner + const.T_max_scan_resp
                yield self.env.timeout(w_delay)
                # self.debug_info("end")
                # self.save_event("end")
                self.state = ScannerState.MAX_DELAY

            if self.state == ScannerState.MAX_DELAY:
                # self.debug_info("begin")
                # self.save_event("begin")
                max_delay = max(const.T_decod_delay, const.T_freq_change_delay)
                yield self.env.timeout(max_delay)
                # self.debug_info("end")
                # self.save_event("end")
                self.state = ScannerState.SCAN

    def beginReception(self, packet):
        self.ongoing_receptions[packet.channel] += 1
        if self.channel == packet.channel:
            if self.state == ScannerState.SCAN and self.ongoing_receptions[self.channel] == 1:
                self.receiving_packet = packet
                self.action.interrupt("begin_reception")
            if self.state == ScannerState.SCAN_FOR_RESP and self.ongoing_receptions[self.channel] == 1:
                self.receiving_packet = packet
                self.action.interrupt("begin_reception")
            if self.state == ScannerState.RX:
                self.action.interrupt("begin_reception")

    def endReception(self, packet):
        self.ongoing_receptions[packet.channel] -= 1
        if self.channel == packet.channel:
            if self.state == ScannerState.SCAN and self.ongoing_receptions[self.channel] == 0:
                self.action.interrupt("end_reception")

    def scan(self, end_time):
        how_long = end_time - self.env.now
        yield self.env.timeout(how_long)

    def scanForResp(self):
        yield self.env.timeout(const.T_max_scan_resp)

    def transmit(self, pkt):
        self.network.beginReceptionInDevices(pkt)
        yield self.env.timeout(const.T_scanreq)
        self.network.endReceptionInDevices(pkt)

    def receive(self):
        if self.receiving_packet.type == packet.PktType.ADV_SCAN_IND:
            yield self.env.timeout(const.T_advind)
        elif self.receiving_packet.type == packet.PktType.SCAN_RSP:
            yield self.env.timeout(const.T_scanresp)

    def evaluateBackoff(self, receivedRSP):
        if receivedRSP is True:
            if self.backoff == "BTBackoff":
                self.valid_resp += 1
                self.invalid_resp = 0
                if self.valid_resp == 2:
                    self.upperLimit = self.upperLimit / 2
                    self.valid_resp = 0
                    if self.upperLimit < 1:
                        self.upperLimit = 1
                self.backoffCount = random.randint(1, self.upperLimit)
        if receivedRSP is False:
            if self.backoff == "BTBackoff":
                self.invalid_resp += 1
                self.valid_resp = 0
                if self.invalid_resp == 2:
                    self.upperLimit = self.upperLimit * 2
                    self.invalid_resp = 0
                    if self.upperLimit > 256:
                        self.upperLimit = 256
                self.backoffCount = random.randint(1, self.upperLimit)


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

    def save_pkt_to_log(self, txrx, pkt):
        if txrx == "Tx":
            self.msg_log.append([self.env.now, "Tx", self.id, pkt.src_id, pkt.dst_id, pkt.type, self.channel, pkt.seq_no, pkt.copy_id])
        if txrx == "Rx":
            self.msg_log.append([self.env.now, "Rx", self.id, pkt.src_id, pkt.dst_id, pkt.type, self.channel, pkt.seq_no, pkt.copy_id])
