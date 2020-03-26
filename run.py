import pytooth.btnetwork

network = pytooth.btnetwork.BTNetwork()

network.addScanners(1)
network.addAdvertisers(3)

network.evaluateNetwork()

network.scanners[0].print_summary()

network.drawTimeline()