from urllib.parse import urlparse, parse_qs
import argparse
import sys
import os

params_filename = ""
burp_filename = ""
output = ""

params = []
endpoints = []
filtered_files = []

def get_params(url_value):
    url_data = urlparse(url_value)
    params_query = parse_qs(url_data.query)

    for param in params_query:
        if param not in params:
            params.append(param)

def loadFile(filename):
    global endpoints
    with open(filename) as f:
        for line in f.readlines():
            if params_filename:
                get_params(line)

            if checkDuplicates(line) or checkExcluded(line):
                continue
            else:
                endpoints.append(line.replace("\n", ""))
    
    writeFile(output, endpoints)

    if params_filename and params:
        writeFile(params_filename, params)


def writeFile(filename, endpoints):
    with open(filename, "w") as f:
        for endpoint in endpoints:
            f.write(endpoint + "\n")

def checkExcluded(line):
    global endpoints
    for ext in filtered_files:
        if ext in line:
            return True
    return False


def checkDuplicates(line):
    global endpoints
    for endpoint in endpoints:
        if "?" in line:
            test = line.split("?")
            if test[0] in endpoint:
                return True
        if ";" in line:
            test = line.split(";")
            if test[0] in endpoint:
                return True
    return False

def main():

    global burp_filename
    global output
    global filtered_files
    global params_filename

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="Input of HTTPX validated endpoints")
    parser.add_argument("-p", help="Retrieve all params from endpoints and store them")
    parser.add_argument("-o", help="File path to output for cleaned list")
    parser.add_argument("-ft", help="Filters out specified endpoint file types e.g. (.js,.css,.rtf)")
    args = parser.parse_args()

    if not args.i:
        print("You need to specify a txt file at -i for your endpoints you want to clean.")
        sys.exit(0)
    if not os.path.isfile(args.i):
        print('The path specified does not exist for your input file')
        sys.exit()
    if not args.p:
        print("You need to specify a txt file at -p to retrieve the params")
        sys.exit(0)
    if not args.o:
        print("Please set the output for your cleaned file using -o")
        sys.exit()
    if os.path.isfile(args.o):
        print('A file already exists at this location, try another name.')
        sys.exit()
    if os.path.isfile(args.p):
        print('A file already exists at this location for your params file, try another name.')
        sys.exit()
    
    if args.p:
        params_filename = args.p
    if args.ft:
        filtered_files = str(args.ft).split(",")

    burp_filename = args.i
    output = args.o
    loadFile(burp_filename)

if __name__ == '__main__':
    main()
