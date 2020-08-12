import pytooth.btnetwork

network = pytooth.btnetwork.BTNetwork()

network.addScanners(1, backoffType="BTBackoff")
network.addAdvertisers(2)

network.advertisers[0].beginAt = 100
network.advertisers[0].time_to_next_packet = 250000
network.advertisers[0].use_random_delay = False

network.advertisers[1].beginAt = 100
network.advertisers[1].time_to_next_packet = 500000
network.advertisers[1].use_random_delay = False

# network.scanners[0].debug_mode = True
# network.advertisers[0].debug_mode = True
# network.advertisers[1].debug_mode = True

network.evaluateNetwork(1000000)

# network.scanners[0].print_summary()

# network.drawTimeline()

network.printStatsNetwork()
network.printStatsPerDevice()

# network.saveEventListCSV("1scanner_2advertisers.csv")
network.saveEventListVCD("output.vcd")