import argparse
import time
import statistics
import pytooth.btnetwork
import time

parser = argparse.ArgumentParser(description="PyTooth: Python BT analyser")

parser.add_argument("--scNo", type=int, help="number of scanners", default=1)
parser.add_argument("--advNo", type=int, help="number of advertisers", default=1)
parser.add_argument("--simLen", type=int, help="Simulation length [s]", default=100)
parser.add_argument("--itNo", type=int, help="Iteration number", default=0)
parser.add_argument("--printHeader", type=bool, help="Print CSV header", default=False)

args = parser.parse_args()

if args.printHeader is True:
    print("scNo", end="\t")
    print("advNo", end="\t")
    print("itNo", end="\t")
    print("simLen", end="\t")
    print("execution_time", end="\t")
    print("sum(sent_data_per_device)", end="\t")
    print("sum(rcv_data_per_device)", end="\t")
    print("mean(sent_data_per_device)", end="\t")
    print("stdev(sent_data_per_device)", end="\t")
    print("mean(rcv_data_per_device)", end="\t")
    print("stdev(rcv_data_per_device)", end="\t")
    print("mean(sent_packets_per_device)", end="\t")
    print("stdev(sent_packets_per_device)", end="\t")
    print("mean(rcv_packets_per_device)", end="\t")
    print("stdev(rcv_packets_per_device)", end="\t")
    print()
    exit()

network = pytooth.btnetwork.BTNetwork()

# network.addScanners(args.scNo, backoffType="BTBackoff")
network.addScanners(args.scNo, backoffType=None)
network.addAdvertisers(args.advNo)

# network.scanners[0].debug_mode = True
# network.advertisers[0].debug_mode = True
# network.advertisers[1].debug_mode = True

start_time = time.time()
network.evaluateNetwork(args.simLen)
execution_time = time.time() - start_time

sent_data_per_device = []
rcv_data_per_device = []

sent_packets_per_device = []
rcv_packets_per_device = []

for advertiser in network.advertisers:
    sent_data = advertiser.sent_data
    received_data = len(network.scanners[0].received_adv_data[advertiser.id])
    sent_adv = advertiser.sent_adv
    received_packets = network.scanners[0].received_adv_packets[advertiser.id]

    sent_data_per_device.append(sent_data)
    rcv_data_per_device.append(received_data)
    sent_packets_per_device.append(sent_adv)
    rcv_packets_per_device.append(received_packets)

print(args.scNo, end="\t")
print(args.advNo, end="\t")
print(args.itNo, end="\t")
print(args.simLen, end="\t")
print(execution_time, end="\t")
print(sum(sent_data_per_device), end="\t")
print(sum(rcv_data_per_device), end="\t")
print(statistics.mean(sent_data_per_device), end="\t")
print(statistics.stdev(sent_data_per_device), end="\t")
print(statistics.mean(rcv_data_per_device), end="\t")
print(statistics.stdev(rcv_data_per_device), end="\t")
print(statistics.mean(sent_packets_per_device), end="\t")
print(statistics.stdev(sent_packets_per_device), end="\t")
print(statistics.mean(rcv_packets_per_device), end="\t")
print(statistics.stdev(rcv_packets_per_device), end="\t")
print()
# print(execution_time, sent_data + 1, received_data, received_packets)

