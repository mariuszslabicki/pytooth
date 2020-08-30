import argparse
import configparser
import time
import statistics
import pytooth.btnetwork
from itertools import product
import time
import ast
import multiprocessing
import csv

def f(adv_no, sc_no, iterationNumber, simulationLength, timeToNextAE):
    network = pytooth.btnetwork.BTNetwork()
    network.addScanners(sc_no, backoffType=None)
    network.addAdvertisers(adv_no, timeToNextAE)
    start_time = time.time()
    print(adv_no, sc_no, iterationNumber, simulationLength, timeToNextAE)
    network.evaluateNetwork(simulationLength)
    execution_time = time.time() - start_time
    
    sent_data_per_device = []
    rcv_data_per_device = []

    sent_events_per_device = []
    rcv_events_per_device = []

    for advertiser in network.advertisers:
        sent_data_values = advertiser.number_of_sent_data_values
        received_data = network.scanners[0].received_adv_data_values[advertiser.id]
        sent_adv_events = advertiser.number_of_sent_adv_events
        received_events = network.scanners[0].received_adv_packets[advertiser.id]

        sent_data_per_device.append(sent_data_values)
        rcv_data_per_device.append(received_data)
        sent_events_per_device.append(sent_adv_events)
        rcv_events_per_device.append(received_events)
    result = []
    result.append(sc_no)
    result.append(adv_no)
    result.append(timeToNextAE)
    result.append(iterationNumber)
    result.append(simulationLength)
    result.append(execution_time)
    result.append(sum(sent_data_per_device))
    result.append(sum(rcv_data_per_device))
    result.append(statistics.mean(sent_data_per_device))
    result.append(statistics.stdev(sent_data_per_device))
    result.append(statistics.mean(rcv_data_per_device))
    result.append(statistics.stdev(rcv_data_per_device))
    result.append(statistics.mean(sent_events_per_device))
    result.append(statistics.stdev(sent_events_per_device))
    result.append(statistics.mean(rcv_events_per_device))
    result.append(statistics.stdev(rcv_events_per_device))
    return result

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

    if type(scanner_list) is int:
        scanner_list = [scanner_list]

    if type(time_to_next_AE_list) is int:
        time_to_next_AE_list = [time_to_next_AE_list]

    simulationLength = [parameters["SimulationLength"]]

    parameters = product(adv_list, scanner_list, no_of_iterations, simulationLength, time_to_next_AE_list)
    results = []
    with multiprocessing.Pool(processes=no_of_cores) as pool:
        results = pool.starmap(f, parameters)

    file = open("output.csv",'w') 

    separator = "\t"

    file.write("scNo" + separator)
    file.write("advNo" + separator)
    file.write("timeToNextAE" + separator)
    file.write("itNo" + separator)
    file.write("simLen" + separator)
    file.write("execution_time" + separator)
    file.write("sum(sent_data_per_device)" + separator)
    file.write("sum(rcv_data_per_device)" + separator)
    file.write("mean(sent_data_per_device)" + separator)
    file.write("stdev(sent_data_per_device)" + separator)
    file.write("mean(rcv_data_per_device)" + separator)
    file.write("stdev(rcv_data_per_device)" + separator)
    file.write("mean(sent_events_per_device)" + separator)
    file.write("stdev(sent_events_per_device)" + separator)
    file.write("mean(rcv_events_per_device)" + separator)
    file.write("stdev(rcv_events_per_device)" + separator)
    file.write("\n")

    wr = csv.writer(file, delimiter=separator)
    for result in results:
        wr.writerow(result)
    file.close