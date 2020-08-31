import pytooth.btnetwork

network = pytooth.btnetwork.BTNetwork()

network.addScanners(1, backoffType="BTBackoff")
network.addAdvertisers(1, 100000)

network.advertisers[0].beginAt = 100
# network.advertisers[0].time_to_next_packet = 250000
network.advertisers[0].use_random_delay = True

# network.advertisers[1].beginAt = 100
# network.advertisers[1].time_to_next_packet = 500000
# network.advertisers[1].use_random_delay = False

# network.scanners[0].debug_mode = True
# network.advertisers[0].debug_mode = True
# network.advertisers[1].debug_mode = True

network.evaluateNetwork(50000000)

# network.scanners[0].print_summary()

# network.drawTimeline()

network.printStatsNetwork()
network.printStatsPerDevice()
print(network.scanners[0].received_adv_packets)
print(network.scanners[0].received_adv_data_values)

# network.saveEventListCSV("1scanner_2advertisers.csv")
# network.saveEventListVCD("output.vcd")
# network.printMsgLog()
# network.saveMsgLogToFile("msg_log.csv")

print(network.advertisers[0].number_of_sent_data_values)
print(network.scanners[0].received_adv_data_values[0])
