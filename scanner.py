class Scanner(object):
    def __init__(self, env):
        self.env = env
        self.received = 0
        self.lost = 0
        self.ongoing_receptions = {}
        self.action = env.process(self.main_loop())
        self.channel = None

    def main_loop(self):
        for channel in range(37, 40):
            self.channel = channel
            yield self.env.timeout(0.128)   #scan window length
            self.channel = None
            yield self.env.timeout(0.200)   #scan interval - scan window length

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