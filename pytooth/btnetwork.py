import csv
import simpy
from datetime import datetime
import pytooth.advertiser
import pytooth.scanner
from pytooth import packet

class BTNetwork(object):
    def __init__(self):
        self.env = simpy.Environment()
        self.events_list = []
        self.advertisers = []
        self.scanners = []

    def addScanners(self, number):
        for i in range(number):
            self.scanners.append(pytooth.scanner.Scanner(i, self.env, self.events_list, self))

    def addAdvertisers(self, number):
        for i in range(number):
            self.advertisers.append(pytooth.advertiser.Advertiser(i, self.env, self.events_list, self))

    def evaluateNetwork(self, time=10000):
        self.env.run(time)

    def beginReceptionInDevices(self, pkt):
        for scanner in self.scanners:
            if pkt.type == packet.PktType.SCAN_REQ and pkt.src_id == scanner.id:
                continue
            scanner.beginReception(pkt)
        for advertiser in self.advertisers:
            if pkt.type == packet.PktType.ADV_SCAN_IND and pkt.src_id == advertiser.id:
                continue
            if pkt.type == packet.PktType.SCAN_RSP and pkt.src_id == advertiser.id:
                continue
            advertiser.beginReception(pkt)

    def endReceptionInDevices(self, pkt):
        for scanner in self.scanners:
            if pkt.type == packet.PktType.SCAN_REQ and pkt.src_id == scanner.id:
                continue
            scanner.endReception(pkt)
        for advertiser in self.advertisers:
            if pkt.type == packet.PktType.ADV_SCAN_IND and pkt.src_id == advertiser.id:
                continue
            if pkt.type == packet.PktType.SCAN_RSP and pkt.src_id == advertiser.id:
                continue
            advertiser.endReception(pkt)

    def saveEventListCSV(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            eventsFile = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for event in self.events_list:
                eventsFile.writerow(event)