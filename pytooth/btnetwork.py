import simpy
from datetime import datetime
import plotly.figure_factory as ff
import numpy as np
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
            scanner.beginReception(pkt)
        for advertiser in self.advertisers:
            if pkt.type == packet.PktType.ADV_SCAN_IND and pkt.src_id == advertiser.id:
                continue
            advertiser.beginReception(pkt)

    def endReceptionInDevices(self, pkt):
        for scanner in self.scanners:
            scanner.endReception(pkt)
        for advertiser in self.advertisers:
            if pkt.type == packet.PktType.ADV_SCAN_IND and pkt.src_id == advertiser.id:
                continue
            advertiser.endReception(pkt)

    def drawTimeline(self):
        colors = {
        'ch37_free': 'rgb(147,194,208)',
        'ch37_msg': 'rgb(86,140,40)',
        'ch38_free': 'rgb(212,92,89)',
        'ch38_msg': 'rgb(180,47,43)',
        'ch39_free': 'rgb(100,137,211)',
        'ch39_msg': 'rgb(33,83,184)',
        'noise': 'rgb(105,105,105)'}

        for event in self.events_list:
            event["Start"] = datetime.fromtimestamp(event["Start"]/1000.0)
            event["Finish"] = datetime.fromtimestamp(event["Finish"]/1000.0)


        num_tick_labels = np.linspace(start = 0, stop = 10, num = 11, dtype = int)
        date_ticks = [datetime.fromtimestamp(31536000+x*24*3600).strftime("%Y-%d-%m") for x in num_tick_labels]

        # print(len(events_map))

        fig = ff.create_gantt(self.events_list, colors=colors, index_col='Resource', show_colorbar=True, group_tasks=True, title="BT Eval")
        fig.layout.xaxis.update({
                'tickvals' : date_ticks,
                'ticktext' : num_tick_labels
                })
        fig.show()