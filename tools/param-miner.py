import argparse
import os
import sys

params = []

parser = argparse.ArgumentParser()
parser.add_argument("-e", help="The path to your endpoints file")
parser.add_argument("-o", help="File path to output for results")
args = parser.parse_args()

if not args.e:
    print("You need to specify a txt file at -e for your endpoints you want to scan.")
    sys.exit(0)

if not args.o:
    print("You need to specify a txt file at -o for your parameters output.")
    sys.exit(0)

if not os.path.isfile(args.e):
    print('The path specified does not exist for you endpoints file.')
    sys.exit(0)

if os.path.isfile(args.o):
    print('This output file already exists please try again.')
    sys.exit(0)

def readEndpoints():
    global params
    with open(args.e) as file:
        for line in file:
            endpoint = line
            if "?" in endpoint:
                param_list = line.split("?")
                if "&" in endpoint:
                    params_list = param_list[1].split("&")
                    for p in params_list:
                        test = p.split("=")
                        if not checkDuplicates(test[0]):
                            params.append(test[0])
                else:
                    test = param_list[1].split("=")
                    if not checkDuplicates(test[0]):
                        params.append(test[0])
    writeEndpoints()

def writeEndpoints():
    global params
    with open(args.o, "w") as file:
        for param in params:
            file.write(param + "\n")

def checkDuplicates(param):
    global params
    for fuck in params:
        if fuck == param:
            return True

readEndpoints()