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

    def printStatsNetwork(self):
        self.number_of_transmitted_adv = 0
        self.number_of_received_adv = 0
        self.number_of_sent_req = 0
        self.number_of_received_req = 0
        self.number_of_transmitted_resp = 0
        for adv in self.advertisers:
            self.number_of_transmitted_adv += adv.number_of_transmitted_adv
            self.number_of_received_req += adv.number_of_received_req
            self.number_of_transmitted_resp += adv.number_of_transmitted_resp

        for sc in self.scanners:
            self.number_of_received_adv += sc.number_of_received_adv
            self.number_of_sent_req += sc.number_of_sent_req

        print("Number of transmitted adv", self.number_of_transmitted_adv)
        print("\t\t\t\tNumber of received adv", self.number_of_received_adv)
        print("\t\t\t\tNumber of sent req", self.number_of_sent_req)
        print("Number of received req", self.number_of_received_req)
        print("Number of transmitted resp", self.number_of_transmitted_resp)
    
    def printStatsPerDevice(self):
        for adv in self.advertisers:
            adv.print_stats()

    def saveEventListCSV(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            eventsFile = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            for event in self.events_list:
                eventsFile.writerow(event)

    def saveEventListVCD(self, filename):
        import vcd
        # from vcd import VCDWriter
        with open(filename, 'w', newline='') as vcdfile:
            with vcd.VCDWriter(vcdfile, timescale='1 ns', date='today') as writer:
                # counter_var = writer.register_var('a.b.c', 'counter', 'integer', size=8)
                # real_var = writer.register_var('a.b.c', 'x', 'real', init=1.23)
                # for timestamp, value in enumerate(range(10, 20, 2)):
                #     writer.change(counter_var, timestamp, value)
                # writer.change(real_var, 5, 3.21)
                advert0 = writer.register_var('adv0', 'adv0', 'string', size=64)
                for event in self.events_list:
                    if event[0] == "ADV":
                        stateName = str(pytooth.advertiser.AdvState[event[4][9:]])[9:]
                        print(stateName)
                        writer.change(advert0, event[2], stateName)
