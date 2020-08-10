import pytooth.btnetwork

network = pytooth.btnetwork.BTNetwork()

network.addScanners(1)
network.addAdvertisers(2)

network.scanners[0].debug_mode = True
# network.advertisers[0].debug_mode = True
# network.advertisers[1].debug_mode = True

network.evaluateNetwork(1000000)

# network.scanners[0].print_summary()

# network.drawTimeline()

network.printStatsNetwork()
network.printStatsPerDevice()

# network.saveEventListCSV("output.csv")
# network.saveEventListVCD("output.vcd")