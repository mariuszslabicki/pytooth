import pytooth.btnetwork

network = pytooth.btnetwork.BTNetwork()

network.addScanners(1, backoffType="BTBackoff")
network.addAdvertisers(1, time_to_next_AE=100000, stop_advertising=True)

network.evaluateNetwork(500000000)

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
