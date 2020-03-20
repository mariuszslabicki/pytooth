import random
import simpy
from pytooth import packet

class Advertiser(object):
    def __init__(self, env, id, scanners_list, events_map):
        self.id = id
        self.env = env
        self.scanners_list = scanners_list
        self.packets_sent = 0
        self.action = env.process(self.main_loop())  # starts the run() method as a SimPy process
        self.received_packet = False
        self.receiving_now = False
        self.events_map = events_map

    def main_loop(self):
        counter = 0
        while True:
            yield self.env.timeout(random.expovariate(0.01))
            for channel in range(37, 40):
                pkt = packet.Packet(self.id, window_id = channel)
                
                yield self.env.process(self.transmit(pkt))

                yield self.env.process(self.switch())

                self.receiving_now = True
                # try:
                #     yield self.env.process(self.listen())
                # except simpy.Interrupt:
                #     print("Odbieram wiadomosc")
                yield self.env.process(self.listen())
                self.receiving_now = False

                # if channel != 39:
                    # yield self.env.process(self.standby())
                yield self.env.process(self.standby())
                self.packets_sent += 1

            counter += 1
            if counter == 4:
                break
    
    def transmit(self, pkt):
        print(str(self.env.now) + " Wchodze w stan transmit")
        now = self.env.now
        # self.scanner.begin_reception(pkt)
        yield self.env.timeout(0.176)
        # self.scanner.end_reception(pkt)
        self.events_map.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='Tx', Description='Transmit'))
        print(str(self.env.now) + " Wychodze ze stanu transmit")

    def switch(self):
        print(str(self.env.now) + "Wchodze w stan switch")
        now = self.env.now
        yield self.env.timeout(0.150)
        self.events_map.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='Switch', Description='Switch'))
        print(str(self.env.now) + "Wychodze ze stanu switch")

    def listen(self):
        print(str(self.env.now) + "Wchodze w stan listen")
        now = self.env.now
        yield self.env.timeout(0.05)
        self.events_map.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='Rx', Description='Listen'))
        print(str(self.env.now) + "Wychodze ze stanu listen")

    def standby(self):
        print(str(self.env.now) + "Wchodze w stan standby")
        # now = self.env.now
        yield self.env.timeout(4)
        # self.events_map.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='Standby'))
        print(str(self.env.now) + "Wychodze ze stanu standby")

    def receive_packet(self):
        self.action.interrupt()
        yield self.env.timeout(0.1)
        