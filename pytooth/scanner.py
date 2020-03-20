class Scanner(object):
    def __init__(self, env, events_map, id):
        self.env = env
        self.id = id
        self.received = 0
        self.lost = 0
        self.ongoing_receptions = {}
        self.action = env.process(self.main_loop())
        self.channel = None
        self.events_map = events_map

    def main_loop(self):
        while True:
            self.channel = 37
            now = self.env.now
            yield self.env.timeout(500)   #scan window length
            self.events_map.append(dict(Task="SCANNER", Start=now, Finish=self.env.now, Resource='Tx', Description='Tx'))
            self.channel = 38
            now = self.env.now
            yield self.env.timeout(500)   #scan window length
            self.events_map.append(dict(Task="SCANNER", Start=now, Finish=self.env.now, Resource='Switch', Description='Switch'))
            self.channel = 39
            now = self.env.now
            yield self.env.timeout(500)   #scan window length
            self.events_map.append(dict(Task="SCANNER", Start=now, Finish=self.env.now, Resource='Rx', Description='Rx'))

    def begin_reception(self, packet):
        self.ongoing_receptions[packet.src_id] = True
        if len(self.ongoing_receptions) > 1:
            for key in self.ongoing_receptions:
                self.ongoing_receptions[key] = False

    def end_reception(self, packet):
        if self.ongoing_receptions[packet.src_id] == True:
            self.received += 1
        else:
            self.lost += 1
        del self.ongoing_receptions[packet.src_id]