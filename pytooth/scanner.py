import simpy

class Scanner(object):
    def __init__(self, id, env, events_list, network):
        self.env = env
        self.id = id
        self.received = 0
        self.lost = 0
        self.ongoing_receptions = {}
        self.ongoing_transmission = False
        self.action = env.process(self.main_loop())
        self.channel = None
        self.events_list = events_list
        self.network = network

    def main_loop(self):
        while True:
            self.channel = 37
            end_window = self.env.now + 500
            while self.env.now < end_window:
                try:
                    yield self.env.process(self.listen(self.channel, end_window - self.env.now))
                except simpy.Interrupt:
                    continue

            self.channel = 38
            end_window = self.env.now + 500
            while self.env.now < end_window:
                try:
                    yield self.env.process(self.listen(self.channel, end_window - self.env.now))
                except simpy.Interrupt:
                    continue

            self.channel = 39
            end_window = self.env.now + 500
            while self.env.now < end_window:
                try:
                    yield self.env.process(self.listen(self.channel, end_window - self.env.now))
                except simpy.Interrupt:
                    continue

    def listen(self, channel, how_long):
        now = self.env.now
        yield self.env.timeout(how_long)
        if channel == 37:
            self.events_list.append(dict(Task="SCANNER", Start=now, Finish=self.env.now, Resource='ch37', Description='Listen'))
        if channel == 38:
            self.events_list.append(dict(Task="SCANNER", Start=now, Finish=self.env.now, Resource='ch38', Description='Listen'))
        if channel == 39:
            self.events_list.append(dict(Task="SCANNER", Start=now, Finish=self.env.now, Resource='ch39', Description='Listen'))

    def begin_reception(self, packet):
        self.ongoing_receptions[packet.src_id] = True
        self.action.interrupt()
        if self.channel == packet.channel:
            now = self.env.now
            self.events_list.append(dict(Task="SCANNER", Start=now, Finish=now+0.176, Resource='ch39', Description='Rx'))
        if len(self.ongoing_receptions) > 1:
            for key in self.ongoing_receptions:
                self.ongoing_receptions[key] = False

    def end_reception(self, packet):
        if self.ongoing_receptions[packet.src_id] == True and self.channel == packet.channel:
            self.received += 1
            self.sendRequestTo(packet.src_id)
        else:
            self.lost += 1
        del self.ongoing_receptions[packet.src_id]

    def sendRequestTo(self, src_id):
        now = self.env.now
        self.network.advertisers[src_id].receive_packet()
        self.events_list.append(dict(Task="SCANNER", Start=now+0.150, Finish=now+0.150+0.176, Resource='ch39', Description='Tx'))

    def print_summary(self):
        print("Received correct", self.received)
        print("Lost", self.lost)