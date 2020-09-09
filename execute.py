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

def f(adv_no, sc_no, iterationNumber, simulationLength, timeToNextAE, stopAdvertising):
    network = pytooth.btnetwork.BTNetwork()
    network.addScanners(sc_no, backoffType=None)
    network.addAdvertisers(adv_no, timeToNextAE, stopAdvertising)
    start_time = time.time()
    print(adv_no, sc_no, iterationNumber, simulationLength, timeToNextAE, stopAdvertising)
    network.evaluateNetwork(simulationLength)
    execution_time = time.time() - start_time

    row = {}
    row["adv_no"] = adv_no
    row["sc_no"] = sc_no
    row["iterationNumber"] = iterationNumber
    row["simulationLength"] = simulationLength
    row["timeToNextAE"] = timeToNextAE
    row["stopAdvertising"] = stopAdvertising
    row["execution_time"] = execution_time

    advertisers = []

    for advertiser in network.advertisers:
        new_dict = {}
        new_dict["advertiser_id"] = advertiser.id
        new_dict["number_of_sent_adv_events"] = advertiser.number_of_sent_adv_events
        new_dict["number_of_sent_adv_events"] = advertiser.number_of_sent_adv_events
        new_dict["number_of_delivered_adv_events"] = advertiser.number_of_delivered_adv_events
        new_dict["number_of_sent_data_values"] = advertiser.number_of_sent_data_values
        new_dict["number_of_sent_req_by_scanner"] = advertiser.number_of_sent_req_by_scanner
        new_dict["number_of_received_req"] = advertiser.number_of_received_req
        new_dict["number_of_transmitted_resp"] = advertiser.number_of_transmitted_resp
        new_dict["number_of_delivered_resp"] = advertiser.number_of_delivered_resp
        if stopAdvertising is True:
            new_dict["when_delivered_data"] = advertiser.when_delivered_data

        advertisers.append(new_dict)

    row["advertisers"] = advertisers

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
    no_of_iterations = ast.literal_eval(parameters["NoOfIterations"])
    no_of_iterations = range(no_of_iterations)
    time_to_next_AE_list = ast.literal_eval(parameters["TimeToNextAE"])
    no_of_cores = ast.literal_eval(parameters["NoOfCores"])
    stop_advertising = [True, False]
    output_filename = parameters["OutputFilename"]

    if type(scanner_list) is int:
        scanner_list = [scanner_list]

    if type(time_to_next_AE_list) is int:
        time_to_next_AE_list = [time_to_next_AE_list]

    simulationLength = ast.literal_eval(parameters["SimulationLength"])
    if type(simulationLength) is int:
        simulationLength = [simulationLength]

    parameters = product(adv_list, scanner_list, no_of_iterations, simulationLength, time_to_next_AE_list, stop_advertising)
    results = []
    with multiprocessing.Pool(processes=no_of_cores) as pool:
        results = pool.starmap(f, parameters)

    with open(output_filename, 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)