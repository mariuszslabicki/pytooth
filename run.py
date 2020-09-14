import pytooth.btnetwork

network = pytooth.btnetwork.BTNetwork()

network.addScanners(1, backoffType="BTBackoff")
network.addAdvertisers(1, advertising_interval=100000, data_interval=1000000, stop_advertising=True)

network.evaluateNetwork(40000000)

print(network.advertisers[0].number_of_sent_adv_events)
print(network.advertisers[0].number_of_delivered_adv_events)
print(network.advertisers[0].number_of_sent_data_values)
print(network.advertisers[0].number_of_delivered_data_values)
print(network.advertisers[0].number_of_sent_req_by_scanner)
print(network.advertisers[0].number_of_received_req)
print(network.advertisers[0].number_of_transmitted_resp)
print(network.advertisers[0].number_of_delivered_resp)
print(network.advertisers[0].when_delivered_data)
print(network.scanners[0].upperLimitHistory)