import pytooth.btnetwork

network = pytooth.btnetwork.BTNetwork()

network.addScanners(1, backoffType="BTBackoff")
network.addAdvertisers(1, time_to_next_AE=100000, stop_advertising=True)

network.evaluateNetwork(500000000)

print(network.advertisers[0].number_of_sent_adv_packets)
print(network.advertisers[0].number_of_sent_adv_events)
print(network.advertisers[0].number_of_delivered_adv_events)
print(network.advertisers[0].number_of_sent_data_values)
print(network.advertisers[0].number_of_sent_req_by_scanner)
print(network.advertisers[0].number_of_received_req)
print(network.advertisers[0].number_of_transmitted_resp)
print(network.advertisers[0].number_of_delivered_resp)