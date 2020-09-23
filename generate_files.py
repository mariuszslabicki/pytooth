#!/usr/bin/env python3
# coding: utf-8

import configparser
import pytooth.btnetwork
from itertools import product
import ast
import os
import fire

def f(adv_no, sc_no, scannerType, iterationNumber, simulationLength, advertisingInterval, dataInterval, stopAdvertising):
    
    network = pytooth.btnetwork.BTNetwork()
    network.addScanners(sc_no, scannerType, backoffType="BTBackoff")
    network.addAdvertisers(adv_no, advertisingInterval, dataInterval, stopAdvertising)
    start_time = time.time()
    print(adv_no, sc_no, iterationNumber, simulationLength, scannerType, advertisingInterval, stopAdvertising)
    if scannerType == "Active" and stopAdvertising is False:
        return "Skip: Scanner active and stop advertising is False"
    if scannerType == "Passive" and stopAdvertising is True:
        return "Skip: Scanner passive and stop advertising is True"
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


def tupe_to_str(tup):
    tup = [str(x) for x in tup]
    s = '_'.join(tup)
    return s


def get_dir_name(tup):
    #tup = next(sim_parameters)
    s = tupe_to_str(tup)
    return s


def create_dir(tup):
    path = os.getcwd()
    path = os.path.join(path, get_dir_name(tup))
    
    try:
      os.mkdir(path)
    except OSError:
        print ("Creation of the directory %s failed, is it exist?" % path)
    else:
        print ("Successfully created the directory %s " % path)
    return path


def write_ini(path, tup):
    f_name = os.path.join(path, "network.ini")
    cfgfile = open(f_name, 'w')
    write_config = configparser.ConfigParser()
    write_config.add_section("BTNETWORK")
    write_config.set("BTNETWORK","NoOfAdvertisers",str(tup[0]))
    write_config.set("BTNETWORK","NoOfScanners",str(tup[1]))
    write_config.set("BTNETWORK","ScannerType",str(tup[2]))
    #write_config.set("BTNETWORK","NoOfIterations",)
    write_config.set("BTNETWORK","SimulationLength", str(tup[4]))
    write_config.set("BTNETWORK","AdvertisingInterval", str(tup[5]))
    write_config.set("BTNETWORK","DataInterval", str(tup[6]))
    #write_config.set("BTNETWORK","OutputFilename","Jane")

    write_config.write(cfgfile)
    cfgfile.close()


def prepare_config(main_ini_file_name):
    config = configparser.ConfigParser()
    config.read(main_ini_file_name)
    parameters = config["BTNETWORK"]
    adv_list = ast.literal_eval(parameters["NoOfAdvertisers"])
    scanner_list = ast.literal_eval(parameters["NoOfScanners"])
    scanner_type = parameters["ScannerType"].split()
    no_of_iterations = ast.literal_eval(parameters["NoOfIterations"])
    no_of_iterations = range(no_of_iterations)
    advertising_interval_list = ast.literal_eval(parameters["AdvertisingInterval"])
    data_interval_list = ast.literal_eval(parameters["DataInterval"])
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
    
    return sim_parameters


def prepare_simulation(main_ini_file_name="simulations/art_bullet1.ini"):
    sim_parameters = prepare_config(main_ini_file_name)

    for i in sim_parameters: 
        path = create_dir(i)
        write_ini(path, i)
        print(path)
        print("DONE")





if __name__ == '__main__':
  fire.Fire(prepare_simulation)







