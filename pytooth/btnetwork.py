import pytooth.advertiser
import pytooth.scanner

class BTNetwork(object):
    def __init__(self, env, events_map):
        self.env = env
        self.events_map = events_map
        self.advertisers = []
        self.scanners = []

    def addScanners(self, number):
        for i in range(number):
            self.scanners.append(pytooth.scanner.Scanner(self.env, self.events_map, i))

    def addAdvertisers(self, number):
        for i in range(number):
            self.advertisers.append(pytooth.advertiser.Advertiser(self.env, i, self.scanners, self.events_map))