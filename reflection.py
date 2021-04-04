import argparse
import os
import sys
import http.cookiejar as cookielib

import core.ThreadedStart as ThreadedStart

parser = argparse.ArgumentParser()
parser.add_argument("-e", help="The path to your endpoints file")
parser.add_argument("-p", help="The path to your params file")
parser.add_argument("--mode",
                    help="See README.md on github")
parser.add_argument("--cookie",
                    help="The value of your authentication cookie (e.g. ASPSESSIONIDCSRAABSA=JBLJINCDBGFOCIJBNIHEMLCJ)")
parser.add_argument("-t", help="The number of threads you want to use (default 1)")
parser.add_argument("--discord", help="Link to discord web-hooks for notifications")
parser.add_argument("-o", help="File path to output for results")
parser.add_argument("-v", help="-v on More detailed output, full URLs & reflected code snippets")
parser.add_argument("-rec",
                    help="-rec on (Provides recursive searching so if a reflective value is found it will continue to find more)")
parser.add_argument("-fp",
                    help="Filters out parameters from being used on the scan, use on global params across the site (e.g. -fp err,username)")
parser.add_argument("-hi",
                    help="-hi FILENAME (collects hidden input types from HTML source code and writes them to the specified file for either further scanning.)")
parser.add_argument("-bc",
                    help="-bc [BURP COLLABORATOR PAYLOAD] (tests for SSRF)")
args = parser.parse_args()

if args.cookie:
    cookie_array = str(args.cookie).split(";")
    cookies = dict(res[0] for res in cookielib.parse_ns_headers(cookie_array))
    print(cookies)
    ThreadedStart.auth_cookie = cookies

if args.t:
    ThreadedStart.number_of_threads = int(args.t)

if args.mode:
    ThreadedStart.mode = int(args.mode)

if not args.e:
    print("You need to specify a txt file at -e for your endpoints you want to scan.")
    sys.exit(0)

if not args.p:
    print("You need to specify a txt file at -p for your params you want to search.")
    sys.exit(0)

if not os.path.isfile(args.e):
    print('The path specified does not exist for you endpoints file')
    sys.exit()

if not os.path.isfile(args.p):
    print('The path specified does not exist for you params file')
    sys.exit()

if args.o:
    if os.path.isfile(args.o):
        print('A file already exists at this location, try another name.')
        sys.exit()
    else:
        ThreadedStart.output_file = args.o

if args.hi:
    if os.path.isfile(args.hi):
        print('A file already exists at this location, try another name.')
        sys.exit()
    else:
        ThreadedStart.collect_input_types = args.hi

if args.discord:
    ThreadedStart.discord_hook = args.discord

if args.v:
    ThreadedStart.verbose = True

if args.rec:
    ThreadedStart.recursive = True

if args.fp:
    filtered_params = str(args.fp).split(",")
    ThreadedStart.filtered_params_array = filtered_params
    ThreadedStart.filtered_params = True

if args.bc:
    ThreadedStart.burp_collab = args.bc

ThreadedStart.endpoints_file = args.e
ThreadedStart.params_file = args.p

ThreadedStart.main()
