import pytooth.btnetwork

network = pytooth.btnetwork.BTNetwork()

network.addScanners(1)
network.addAdvertisers(1)

network.scanners[0].debug_mode = True
network.advertisers[0].debug_mode = True
# network.advertisers[1].debug_mode = True

network.evaluateNetwork(10000)

# network.scanners[0].print_summary()

# network.drawTimeline()

network.printStats()

# network.saveEventListCSV("output.csv")
# network.saveEventListVCD("output.vcd")