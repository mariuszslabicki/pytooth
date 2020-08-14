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
        self.msg_log = []
        self.advertisers = []
        self.scanners = []

    def addScanners(self, number, backoffType=None):
        for i in range(number):
            self.scanners.append(pytooth.scanner.Scanner(i+10000, self.env, self.events_list, self.msg_log, self, backoffType))

    def addAdvertisers(self, number):
        for i in range(number):
            self.advertisers.append(pytooth.advertiser.Advertiser(i, self.env, self.events_list, self.msg_log, self))

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
        with open(filename, 'w', newline='') as vcdfile:
            with vcd.VCDWriter(vcdfile, timescale='1 us', date='today') as writer:
                adv_vars = []
                for i in range(len(self.advertisers)):
                    dev_name = "adv" + str(i)
                    adv_vars.append(writer.register_var('BTNetwork', dev_name, 'string', size=64))
                sc_vars = []
                for i in range(len(self.scanners)):
                    dev_name = "sc" + str(i)
                    sc_vars.append(writer.register_var('BTNetwork', dev_name, 'string', size=64))
                for event in self.events_list:
                    if event[0] == "ADV":
                        dev_id = event[1]
                        dev_name = "adv" + str(dev_id)
                        stateName = str(pytooth.advertiser.AdvState[event[4][9:]])[9:]
                        if str(event[5]) != "":
                            stateName += "_" + str(event[5][1:])
                        writer.change(adv_vars[dev_id], event[2], stateName)

                    if event[0] == "SC":
                        dev_id = event[1]
                        dev_name = "sc" + str(dev_id)
                        stateName = str(pytooth.scanner.ScannerState[event[4][13:]])[13:]
                        if str(event[5]) != "":
                            stateName += "_" + str(event[5][1:])
                        writer.change(sc_vars[dev_id], event[2], stateName)

    def printMsgLog(self):
        for entry in self.msg_log:
            print(entry)

    def saveMsgLogToFile(self, filename):
        with open(filename, 'w', newline='') as csvfile:
            csvfile = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            csvfile.writerow(["timestamp", "tx/rx", "logger_id", "src_id", "dst_id", "pkt_type", "channel", "data_id", "counter_id"])
            for msg in self.msg_log:
                csvfile.writerow(msg)