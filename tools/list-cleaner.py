import sys
import os
import argparse

filename = ""
output = ""

urls = []

def readFile():
    global filename
    global urls
    with open(filename) as f:
        for line in f.readlines():
            split = line.split(": ")
            urls.append(split[1])
    writeFile()


def writeFile():
    global output
    global urls
    with open(output, 'w') as w:
        for url in urls:
            w.write(url)

def main():
    global filename
    global output
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", help="Input of burp traffic xml file")
    parser.add_argument("-o", help="File path to output for cleaned list")
    args = parser.parse_args()
    if not args.i:
        print("You need to specify a txt file at -i for your endpoints you want to clean.")
        sys.exit(0)
    if not os.path.isfile(args.i):
        print('The path specified does not exist for your input file')
        sys.exit()
    if not args.o:
        print("Please set the output for your cleaned file using -o")
        sys.exit()
    if os.path.isfile(args.o):
        print('A file already exists at this location, try another name.')
        sys.exit()
    filename = args.i
    output = args.o
    readFile()


if __name__ == '__main__':
    main()