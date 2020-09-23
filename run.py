#!/usr/bin/env python3
# coding: utf-8

import configparser
import ast
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
    #TODO
    #save output (file name is constat called "output.json")

if __name__ == '__main__':
  fire.Fire(run_simulation)


