import random
from pytooth import packet

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

    def main_loop(self):
        counter = 0
        while True:
            yield self.env.timeout(random.expovariate(0.01))
            for channel in range(37, 40):
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

                # if channel != 39:
                    # yield self.env.process(self.standby())
                yield self.env.process(self.standby())
                self.packets_sent += 1

            counter += 1
            if counter == 4:
                break
    
    def transmit(self, pkt, channel):
        now = self.env.now
        self.network.beginTransmissionToScanners(pkt)
        yield self.env.timeout(0.176)
        self.network.finishTransmissionToScanners(pkt)
        if channel == 37:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch37', Description='Transmit'))
        if channel == 38:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch38', Description='Transmit'))
        if channel == 39:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch39', Description='Transmit'))

    def switch(self):
        yield self.env.timeout(0.150)

    def listen(self, channel):
        now = self.env.now
        yield self.env.timeout(0.06)
        if channel == 37:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch37', Description='Listen'))
        if channel == 38:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch38', Description='Listen'))
        if channel == 39:
            self.events_list.append(dict(Task=self.id, Start=now, Finish=self.env.now, Resource='ch39', Description='Listen'))

    def standby(self):
        yield self.env.timeout(4)

    def receive_packet(self):
        print("Cos odebralem")
        self.action.interrupt()
        yield self.env.timeout(0.1)
        