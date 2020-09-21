import argparse
import configparser
import time
import statistics
import pytooth.btnetwork
from itertools import product
import time
import ast
import multiprocessing
import json

def f(adv_no, sc_no, scannerType, iterationNumber, simulationLength, advertisingInterval, dataInterval, stopAdvertising):
    
    network = pytooth.btnetwork.BTNetwork()
    network.addScanners(sc_no, scannerType, backoffType="BTBackoff")
    network.addAdvertisers(adv_no, advertisingInterval, dataInterval, stopAdvertising)
    start_time = time.time()
    print(adv_no, sc_no, iterationNumber, simulationLength, scannerType, advertisingInterval, stopAdvertising)
    if not(stopAdvertising is True and scannerType == "Passive"):
        network.evaluateNetwork(simulationLength)
    execution_time = time.time() - start_time

    row = {}
    row["numberOfAdvertisers"] = adv_no
    row["numberOfScanners"] = sc_no
    row["scannerType"] = scannerType
    row["iterationNumber"] = iterationNumber
    row["simulationLength"] = simulationLength//1000
    row["advertisingInterval"] = advertisingInterval//1000
    row["dataInterval"] = dataInterval//1000
    row["stopAdvertising"] = stopAdvertising
    row["executionTime"] = execution_time

    if stopAdvertising is True and scannerType == "Passive":
        return row

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
        if stopAdvertising is True:
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

    return row

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="PyTooth: Python BT analyser")

    parser.add_argument("--inputCfg", help="input config file", default="example_network.ini")

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.inputCfg)

    parameters = config["BTNETWORK"]
    adv_list = ast.literal_eval(parameters["NoOfAdvertisers"])
    scanner_list = ast.literal_eval(parameters["NoOfScanners"])
    scanner_type = parameters["ScannerType"].split()
    no_of_iterations = ast.literal_eval(parameters["NoOfIterations"])
    no_of_iterations = range(no_of_iterations)
    advertising_interval_list = ast.literal_eval(parameters["AdvertisingInterval"])
    data_interval_list = ast.literal_eval(parameters["DataInterval"])
    no_of_cores = ast.literal_eval(parameters["NoOfCores"])
    simulationLength = ast.literal_eval(parameters["SimulationLength"])
    stop_advertising = [True, False]
    output_filename = parameters["OutputFilename"]

    if type(scanner_list) is int:
        scanner_list = [scanner_list]

    if type(advertising_interval_list) is int:
        advertising_interval_list = [advertising_interval_list]

    if type(data_interval_list) is int:
        data_interval_list = [data_interval_list]

    if type(simulationLength) is int:
        simulationLength = [simulationLength]

    sim_parameters = product(adv_list, scanner_list, scanner_type, no_of_iterations, simulationLength, advertising_interval_list, data_interval_list, stop_advertising)
    results = []
    with multiprocessing.Pool(processes=no_of_cores) as pool:
        results = pool.starmap(f, sim_parameters)

    with open(output_filename, 'w') as f:
        json.dump(dict(parameters), f, ensure_ascii=False, indent=4)
        json.dump(results, f, ensure_ascii=False, indent=4)