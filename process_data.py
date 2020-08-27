import csv
import matplotlib as mpl
mpl.use('agg')
import matplotlib.pyplot as plt 

measures = {}

execution_time = {}
delivered_data = {}
delivered_packets = {}

def process_execution_time(row):
    if row[measures["advNo"]] not in execution_time:
        execution_time[row[measures["advNo"]]] = []
    execution_time[row[measures["advNo"]]].append(float(row[measures["execution_time"]]))

def process_delivered_data(row):
    if row[measures["advNo"]] not in delivered_data:
        delivered_data[row[measures["advNo"]]] = []
    delivered_data[row[measures["advNo"]]].append(float(row[measures["mean(rcv_data_per_device)"]]))

def process_delivered_packets(row):
    if row[measures["advNo"]] not in delivered_packets:
        delivered_packets[row[measures["advNo"]]] = []
    delivered_packets[row[measures["advNo"]]].append(float(row[measures["mean(rcv_packets_per_device)"]]))

with open('output.csv', newline='') as csvfile:
    resultsreader = csv.reader(csvfile, delimiter='\t', quotechar='|')
    header = next(resultsreader)
    for i in range(len(header[:-1])):
        measures[header[i]] = i
    print(measures)
    for row in resultsreader:
        process_execution_time(row)
        process_delivered_data(row)
        process_delivered_packets(row)

fig = plt.figure(1, figsize=(12, 8))
ax = fig.add_subplot(111)
times_sorted = []
for no in execution_time.keys():
    times_sorted.append(execution_time[no])
bp = ax.boxplot(times_sorted)
ax.set_xticklabels(execution_time.keys())
ax.set_title('Execution time')
ax.set_xlabel('Number of ADV devices')
ax.set_ylabel('seconds')
fig.savefig('execution_time.png', bbox_inches='tight')
plt.close()

fig = plt.figure(1, figsize=(12, 8))
ax = fig.add_subplot(111)
data_sorted = []
for no in delivered_data.keys():
    data_sorted.append(delivered_data[no])
bp = ax.boxplot(data_sorted)
ax.set_xticklabels(delivered_data.keys())
ax.set_title('Delivered data')
ax.set_xlabel('Number of ADV devices')
ax.set_ylabel('Mean received data units per device')
fig.savefig('delivered_data.png', bbox_inches='tight')
plt.close()

fig = plt.figure(1, figsize=(12, 8))
ax = fig.add_subplot(111)
packets_sorted = []
for no in delivered_packets.keys():
    packets_sorted.append(delivered_packets[no])
bp = ax.boxplot(packets_sorted)
ax.set_xticklabels(delivered_packets.keys())
ax.set_title('Delivered data')
ax.set_xlabel('Number of ADV devices')
ax.set_ylabel('Mean received packets per device')
fig.savefig('delivered_packages.png', bbox_inches='tight')
plt.close()
