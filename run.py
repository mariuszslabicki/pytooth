#!/usr/bin/env python3
# coding: utf-8

import configparser
import ast
import json
import pytooth.btnetwork
import fire

def get_setup(ini_file_name):
    config = configparser.ConfigParser()
    config.read(ini_file_name)
    parameters = config["BTNETWORK"]
    setup = {
        "adv_list" : ast.literal_eval(parameters["NoOfAdvertisers"]),
        "no_of_scanners" : ast.literal_eval(parameters["NoOfScanners"]),
        "scanner_type" : parameters["ScannerType"].split(),
        "advertising_interval" : ast.literal_eval(parameters["AdvertisingInterval"]),
        "data_interval" : ast.literal_eval(parameters["DataInterval"]),
        "simulation_length" : ast.literal_eval(parameters["SimulationLength"]),
        "stop_advertising" : ast.literal_eval(parameters["StopAdvertising"]),
        "number_of_cores" : ast.literal_eval(parameters["NoOfCores"])
    }
    return setup

def run_simulation(ini_file_name):
    s = get_setup(ini_file_name)
    network = pytooth.btnetwork.BTNetwork()
    network.addScanners(s["number_of_cores"], s["scanner_type"], backoffType="BTBackoff")
    network.addAdvertisers(s["no_of_scanners"], s["advertising_interval"], s["data_interval"], s["stop_advertising"])
    network.evaluateNetwork(s["simulation_length"])

    row = {}
    advertisers = []
    for advertiser in network.advertisers:
        new_dict = {}
        new_dict["advertiser_id"] = advertiser.id
        new_dict["number_of_sent_adv_events"] = advertiser.number_of_sent_adv_events
        new_dict["number_of_sent_adv_events"] = advertiser.number_of_sent_adv_events
        new_dict["number_of_delivered_adv_events"] = advertiser.number_of_delivered_adv_events
        new_dict["number_of_sent_finished_data_series"] = advertiser.number_of_sent_data_values
        new_dict["number_of_delivered_data"] = advertiser.number_of_delivered_data_values
        new_dict["number_of_sent_req_by_scanner"] = advertiser.number_of_sent_req_by_scanner
        new_dict["number_of_delivered_req"] = advertiser.number_of_received_req
        new_dict["number_of_sent_resp"] = advertiser.number_of_transmitted_resp
        new_dict["number_of_delivered_resp"] = advertiser.number_of_delivered_resp
        if s["stop_advertising"] is True:
            new_dict["when_delivered_data"] = advertiser.when_delivered_data

        advertisers.append(new_dict)

    row["advertisers"] = advertisers

    scanners = []

    for scanner in network.scanners:
        new_dict = {}
        new_dict["scanner_id"] = scanner.id
        new_dict["backoff_upperlimit_history"] = scanner.upperLimitHistory
        
        scanners.append(new_dict)

    row["scanners"] = scanners

    with open("output.json", 'w') as f:
        json.dump(row, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
  fire.Fire(run_simulation)


