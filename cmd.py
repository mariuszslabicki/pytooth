import argparse
import pytooth.btnetwork

parser = argparse.ArgumentParser(description="PyTooth: Python BT analyser")

parser.add_argument("advNo", type=int, help="number of advertisers", default=1)
parser.add_argument("scNo", type=int, help="number of scanners", default=1)

args = parser.parse_args()
