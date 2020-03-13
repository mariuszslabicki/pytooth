import random
from packet import Packet

class Advertiser(object):
    def __init__(self, env, id, scanner):
        self.id = id
        self.env = env
        self.scanner = scanner
        self.packets_sent = 0
        self.action = env.process(self.main_loop())  # starts the run() method as a SimPy process
        self.received_packet = False
        self.receiving_now = False

    def main_loop(self):
        while True:
            for channel in range(37, 40):
                pkt = Packet(self.id, window_id = channel)
                self.scanner.begin_reception(pkt)
                yield self.env.timeout(0.128)
                self.scanner.end_reception(pkt)

                yield self.env.timeout(0.159)

                self.receiving_now = True
                yield self.env.timeout(0.060)
                if self.received_packet is True:
                    yield self.env.timeout(0.07)    #zmienic na reception_length
                    self.receiving_now = False
                    break
                self.receiving_now = False

                if channel != 39:
                    yield self.env.timeout(0.281)

                self.packets_sent += 1

            yield self.env.timeout(random.expovariate(0.000001))