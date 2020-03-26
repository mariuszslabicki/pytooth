import random
from enum import Enum
from pytooth import packet

class AdvState(Enum):
    TX = 1
    SWITCH = 2
    RX = 3
    IDLE = 4

class Advertiser(object):
    def __init__(self, id, env, events_list, network):
        self.id = id
        self.env = env
        self.packets_sent = 0
        self.action = env.process(self.main_loop())
        self.received_packet = False
        self.receiving_now = False
        self.events_list = events_list
        self.network = network
        self.state = AdvState.IDLE
        self.beginAt = 0.1*self.id

    def main_loop(self):
        counter = 0
        while True:
            yield self.env.timeout(self.beginAt)
            for channel in range(37, 38):
                pkt = packet.Packet(self.id, channel = channel)
                
                yield self.env.process(self.transmit(pkt, channel))

                yield self.env.process(self.switch())

                self.receiving_now = True
                # try:
                #     yield self.env.process(self.listen())
                # except simpy.Interrupt:
                #     print("Odbieram wiadomosc")
                yield self.env.process(self.listen(channel))
                self.receiving_now = False

                yield self.env.process(self.standby())
                self.packets_sent += 1
            yield self.env.timeout(random.expovariate(0.01))
            counter += 1
            if counter == 1:
                break
    
    def transmit(self, pkt, channel):
        now = self.env.now
        self.state = AdvState.TX
        self.network.deliverPacket(pkt)
        yield self.env.timeout(0.176)
        if channel == 37:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch37', Description='Transmit'))
        if channel == 38:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch38', Description='Transmit'))
        if channel == 39:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch39', Description='Transmit'))

    def switch(self):
        self.state = AdvState.SWITCH
        yield self.env.timeout(0.150)

    def listen(self, channel):
        now = self.env.now
        self.state = AdvState.RX
        yield self.env.timeout(0.06)
        if channel == 37:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch37', Description='Listen'))
        if channel == 38:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch38', Description='Listen'))
        if channel == 39:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch39', Description='Listen'))

    def standby(self):
        self.state = AdvState.IDLE
        yield self.env.timeout(4)

    def receive(self, packet):
        print("Cos odebralem")
        self.action.interrupt()
        yield self.env.timeout(0.1)
        