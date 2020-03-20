import simpy
import pytooth.btnetwork
from datetime import datetime
import plotly.figure_factory as ff
import numpy as np

env = simpy.Environment()
events_map = []

network = pytooth.btnetwork.BTNetwork(env, events_map)

network.addScanners(1)
network.addAdvertisers(2)

env.run(10000)

# print(ps.received / (ps.received + ps.lost))

colors = {'Tx': 'rgb(220, 0, 0)',
        'Switch': (1, 0.9, 0.16),
        'Rx': 'rgb(0, 255, 100)',
        'Standby': 'rgb(0, 0, 200)'}

for event in network.events_map:
    event["Start"] = datetime.fromtimestamp(event["Start"]/1000.0)
    event["Finish"] = datetime.fromtimestamp(event["Finish"]/1000.0)


num_tick_labels = np.linspace(start = 0, stop = 10, num = 11, dtype = int)
date_ticks = [datetime.fromtimestamp(31536000+x*24*3600).strftime("%Y-%d-%m") for x in num_tick_labels]

# print(len(events_map))

fig = ff.create_gantt(events_map, colors=colors, index_col='Resource', show_colorbar=True, group_tasks=True, title="BT Eval")
fig.layout.xaxis.update({
        'tickvals' : date_ticks,
        'ticktext' : num_tick_labels
        })
fig.show()