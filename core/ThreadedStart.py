import sys
from queue import Queue
from threading import Thread
import time

import core.XSSRequest as xss
import core.SQLiRequest as sqli
import core.SSRFRequest as ssrf

endpoints_file = ""
params_file = ""
output_file = ""

verbose = False
recursive = False
filtered_params = False

collect_input_types = ""

discord_hook = ""

number_of_threads = 1
auth_cookie = {}
reflected_requests = []
filtered_params_array = []

burp_collab = ""

hidden_input_types = []
hidden_collected_index = []

get_reflected_param = []
post_reflected_param = []

get_false_param = []
post_false_param = []

thread_array = []

mode = 0

endpointIndex = -1

queue = Queue()


class DownloadWorker(Thread):

    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue
        self.id = 0

    def run(self):
        global endpointIndex
        print("THREAD ID RUNNING: " + str(self.id))
        while True:
            time.sleep(0.25)
            endpoint = self.queue.get()
            endpointIndex += 1
            try:
                if mode == 0:
                    try:
                        xss.sendGETEndpointRequests(endpoint, endpointIndex, auth_cookie, self.id)
                    except Exception as e:
                        print("Thread: " + str(self.id) + "(EXCEPTION endpoint abandoned: " + endpoint)
                        print("Due to: " + str(e))
                        self.queue.task_done()
                elif mode == 1:
                    try:
                        xss.sendPOSTEndpointRequests(endpoint, endpointIndex, auth_cookie, self.id)
                    except Exception as e:
                        print("Thread: " + str(self.id) + "(EXCEPTION endpoint abandoned: " + endpoint)
                        print("Due to: " + str(e))
                        self.queue.task_done()
                elif mode == 2:
                    try:
                        xss.sendGETEndpointRequests(endpoint, endpointIndex, auth_cookie, self.id)
                        print("[SWITCHING TO POST REQUESTS]")
                        xss.sendPOSTEndpointRequests(endpoint, endpointIndex, auth_cookie, self.id)
                    except Exception as e:
                        print("Thread: " + str(self.id) + "(EXCEPTION endpoint abandoned: " + endpoint)
                        print("Due to: " + str(e))
                        self.queue.task_done()
                elif mode == 3:
                    xss.sendXSSTesting(endpoint, endpointIndex, auth_cookie)
                elif mode == 4:
                    try:
                        if not sqli.sql_error_detector(endpoint, endpointIndex, auth_cookie):
                            sqli.sql_timebase_detector(endpoint, endpointIndex, auth_cookie)
                    except Exception as e:
                        print("Thread: " + str(self.id) + "(EXCEPTION endpoint abandoned: " + endpoint)
                        print("Due to: " + str(e))
                        self.queue.task_done()
                elif mode == 5:
                    try:
                        ssrf.testSSRFGET(endpoint, endpointIndex, auth_cookie, self.id)
                        ssrf.testSSRFPOST(endpoint, endpointIndex, auth_cookie, self.id)
                    except Exception as e:
                        print("Thread: " + str(self.id) + "(EXCEPTION endpoint abandoned: " + endpoint)
                        print("Due to: " + str(e))
                        self.queue.task_done()
            finally:
                self.queue.task_done()
                print("HERE FINISHED: " + str(self.id))


def start():
    global queue
    global number_of_threads
    print(f'Started with ' + str(number_of_threads) + ' threads')
    for x in range(number_of_threads):
        worker = DownloadWorker(queue)
        worker.daemon = True
        worker.id = x
        worker.start()
        thread_array.append(worker)
    print(len(thread_array))
    f = open(endpoints_file, "r")
    for line in f.readlines():
        endpoint = line.replace("\n", "")
        get_reflected_param.append('false')
        get_false_param.append('false')
        post_reflected_param.append('false')
        post_false_param.append('false')
        hidden_collected_index.append('false')
        queue.put(endpoint)
    queue.join()


def main():
    global thread_array
    beg = time.perf_counter()
    xss.parseParams(params_file)
    sqli.parseParams(params_file)
    ssrf.parseParams(params_file)
    if mode == 0:
        print("[STARTED GET ONLY SCAN]")
    elif mode == 1:
        print("[STARTED POST ONLY SCAN]")
    elif mode == 2:
        print("[STARTED GET/POST SCAN]")
    elif mode == 3:
        print("[STARTED XSS SCAN]")
    elif mode == 4:
        print("[STARTED SQLI SCAN]")
    elif mode == 5:
        if burp_collab == "":
            print("Please specify a burp collaborator link using -bc for this mode to work.")
            sys.exit()
        else:
            print("[STARTED SSRF SCAN]")
    start()
    finish = time.perf_counter()
    #if output_file != "":
        #with open(output_file, "w") as txt_file:
            #for url in reflected_requests:
                #txt_file.write(url + "\n")
    #if collect_input_types != "":
        #with open(collect_input_types, "w") as txt_file:
            #for input in hidden_input_types:
                #txt_file.write(input + "\n")
    print(f'Finished in  {round(finish - beg, 2)} seconds.')


if __name__ == "__main__":
    main()
