import warnings
import lxml.html

import requests
import core.ParseParams as ParseParams
import core.ThreadedStart as ThreadedStart
from discord_webhook import DiscordWebhook, DiscordEmbed

endpoints = []
hidden_params = []

get_last_param = ""
post_last_param = ""

def checkParamInUrl(endpoint, param):
    if ("?" + param) in endpoint or ("&" + param) in endpoint:
        return True


def writeReflectedParamToFile(message):
    with open(ThreadedStart.output_file, "a") as file:
        file.write(str(message) + "\n")

def writeHiddenInputs(message):
    with open(ThreadedStart.collect_input_types, "a") as file:
        file.write(str(message + "\n"))

def parseParams(param_file):
    global hidden_params
    hidden_params = ParseParams.parseParams(param_file)


def sendDiscordMessage(message, message2):
    if ThreadedStart.discord_hook != "":
        hook = DiscordWebhook(url=ThreadedStart.discord_hook)
        embed = DiscordEmbed(title='[REFLECTION ALERT]', description='', color=242424)
        hook.add_embed(embed)
        embed.add_embed_field(name='URL:', value=message)
        if message2 != "":
            embed.add_embed_field(name='CODE SNIPPET:', value=message2)
        hook.execute()
    else:
        print(message)


def sendVerboseDiscordMessage(message1, message2, message3):
    if ThreadedStart.discord_hook != "":
        hook = DiscordWebhook(url=ThreadedStart.discord_hook)
        embed = DiscordEmbed(title='[REFLECTION ALERT]', description='', color=242424)
        hook.add_embed(embed)
        embed.add_embed_field(name='UNCLEAN URL:', value=message1)
        embed.add_embed_field(name='CLEAN URL', value=message2)
        embed.add_embed_field(name='CODE SNIPPET', value=message3)
        hook.execute()
    else:
        print(message1 + "\n" + message2 + "\n" + message3)


def sendGETEndpointRequests(endpoint, index, auth_cookie, thread_id):
    warnings.filterwarnings("ignore")
    global hidden_params
    global get_last_param
    endpoint = endpoint.replace("\n", "")
    i = 1
    count = 0
    url = ""
    print("thread id: " + str(thread_id) + ":" + str(endpoint))
    for param in hidden_params:
        count += 1
        param = param.replace("\n", "")

        if ThreadedStart.filtered_params:
            if ThreadedStart.filtered_params_array.count(param) > 0:
                continue

        if ThreadedStart.get_reflected_param[index] == 'true' and not ThreadedStart.recursive:
            if ThreadedStart.get_false_param[index] != 'true':
                new_url = url.split("?")
                sendDiscordMessage(
                    "[GET]: Has multiple reflective params beyond " + get_last_param + " that was found please manually inspect - " + str(
                        new_url[0]), "")
            break

        if i <= 1:
            if "?" in endpoint:
                if param in endpoint and checkParamInUrl(endpoint, param):
                    split_params = endpoint.split("?")
                    ggg = split_params[1].split("&")
                    for g in ggg:
                        jj = g.split("=")
                        if jj[0] == param:
                            if "zzxy" not in jj[1]:
                                jj[1] = "=zzxy" + str(i)
                                g = (jj[0] + jj[1])
                                url = split_params[0] + "?" + g
                                i += 1
                                for gg in ggg:
                                    zz = gg.split("=")
                                    if zz[0] not in url:
                                        url = url + "&" + gg
                else:
                    url = endpoint + "&" + param + "=zzxy" + str(i)
                    i += 1
            else:
                url = endpoint + "?" + param + "=zzxy" + str(i)
                i += 1
        else:
            if param in endpoint and checkParamInUrl(endpoint, param):
                split_params = endpoint.split("?")
                ggg = split_params[1].split("&")
                for g in ggg:
                    jj = g.split("=")
                    if jj[0] == param:
                        if "zzxy" not in jj[1]:
                            url = url.replace(g, param + "=zzxy" + str(i))
                            i += 1
            else:
                url = url + "&" + param + "=zzxy" + str(i)
                i += 1

        if i == 65:
            if str(auth_cookie) != "{}":
                response = requests.get(url, cookies=auth_cookie, verify=False)
            else:
                response = requests.get(url, verify=False)
            content = response.content
            if str(content).find("advancedsearch2.") > 0:
                return
            analyseGETRequests(url, str(content), index, auth_cookie)
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
            analyseGETRequests(url, str(content), index, auth_cookie)


def analyseGETRequests(url, content, index, cookie):
    warnings.filterwarnings("ignore")
    global get_last_param
    if "zzxy" in content:
        count = content.count("=zzxy")
        count1 = url.count("=zzxy")
        if count % count1 == 0 and count > 0:
            ThreadedStart.get_reflected_param[index] = 'true'
            ThreadedStart.get_false_param[index] = 'true'
        else:
            if content.count("zzxy") > 0:
                for i in range(0, 64):
                    skip = False
                    poi = "zzxy" + str(i)
                    if poi in content:
                        for j in range(0, 9):
                            filter_poi = poi + str(j)
                            if content.count(filter_poi) > 0:
                                skip = True
                                break
                        if not skip:
                            parsed_data = str(content[int(content.find(poi) - 100):int(content.find(poi)) + 100])
                            ThreadedStart.get_reflected_param[index] = 'true'
                            url_params = url.split(poi)
                            test_case = url_params[0] + "test1996"
                            base_url = url.split("?")
                            for k in range(0, 30):
                                finder = test_case[(test_case.find("=test1996") - k):test_case.find("=test1996") + 1]
                                if "&" in finder or "?" in finder:
                                    get_last_param = finder
                                    if "&" in finder:
                                        finder = finder.replace("&", "?")
                                    if not ThreadedStart.verbose:
                                        writeReflectedParamToFile("[GET REFLECTED PARAM]: " + base_url[0] + finder + poi)
                                        #sendDiscordMessage(("[GET]: " + base_url[0] + finder + poi), parsed_data)
                                        sendPayloadChars(base_url[0], finder, poi, cookie)
                                    else:
                                        sendVerboseDiscordMessage(url, (base_url[0] + finder + poi), parsed_data)
                                        writeReflectedParamToFile("[GET REFLECTED PARAM]: " + url)
                                        writeReflectedParamToFile("[GET REFLECTED PARAM CLEAN URL]: " + base_url[0] + finder + poi)
                                        writeReflectedParamToFile("[GET REFLECTED CODE SNIPPET]: " + parsed_data)
                                    break


def sendPOSTEndpointRequests(endpoint, index, auth_cookie, thread_id):
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
    for param in hidden_params:
        count += 1

        param = param.replace("\n", "")

        if ThreadedStart.filtered_params:
            if ThreadedStart.filtered_params_array.count(param) > 0:
                continue

        if ThreadedStart.post_reflected_param[index] == 'true' and not ThreadedStart.recursive:
            if ThreadedStart.post_false_param[index] != 'true':
                sendDiscordMessage(
                    "[POST]: Has multiple reflective params beyond " + post_last_param + " that was found please manually inspect - " + str(
                        endpoint), "")
            break

        test.append([param, 'zzxy' + str(i)])
        for product in test:
            vals['' + product[0]] = product[1]

        if i <= 1:
            url = url + param + "=zzxy" + str(i)
            i += 1
        else:
            url = url + "&" + param + "=zzxy" + str(i)
            i += 1

        if i == 65:
            if str(auth_cookie) != "{}":
                response = requests.post(endpoint, data=vals, cookies=auth_cookie, verify=False)
            else:
                response = requests.post(endpoint, data=vals, verify=False)
            content = response.content
            if str(content).find("advancedsearch2.") > 0:
                return
            analysePOSTRequests(endpoint, url, str(content), index, auth_cookie)
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
            analysePOSTRequests(endpoint, url, str(content), index, auth_cookie)


def analysePOSTRequests(endpoint, url, content, index, auth_cookie):
    warnings.filterwarnings("ignore")
    global post_last_param
    if "zzxy" in content:
        count = content.count("=zzxy")
        count1 = url.count("=zzxy")
        if count % count1 == 0 and count > 0:
            ThreadedStart.post_reflected_param[index] = 'true'
            ThreadedStart.post_false_param[index] = 'true'
        else:
            if content.count("zzxy") > 0:
                for i in range(0, 64):
                    skip = False
                    poi = "zzxy" + str(i)
                    if poi in content:
                        for j in range(0, 9):
                            filter_poi = poi + str(j)
                            if content.count(filter_poi) > 0:
                                skip = True
                                break
                        if not skip:
                            parsed_data = str(content[int(content.find(poi) - 100):int(content.find(poi)) + 100])
                            ThreadedStart.post_reflected_param[index] = 'true'
                            url_params = url.split(poi)
                            test_case = url_params[0] + "test"
                            for k in range(0, 30):
                                finder = test_case[(test_case.find("=test") - k):test_case.find("=test") + 1]
                                if "&" in finder or "?" in finder:
                                    post_last_param = finder
                                    if "&" in finder:
                                        finder = finder.replace("&", "?")
                                    if not ThreadedStart.verbose:
                                        writeReflectedParamToFile("[POST REFLECTED PARAM]: " + endpoint + finder + poi)
                                        #sendDiscordMessage(("[POST]: " + endpoint + finder + poi), parsed_data)
                                        sendPayloadChars(endpoint, finder, poi, auth_cookie)
                                    else:
                                        sendVerboseDiscordMessage(url, (endpoint + finder + poi), parsed_data)
                                        writeReflectedParamToFile("[POST REFLECTED PARAM]: " + endpoint)
                                        writeReflectedParamToFile("[POST REFLECTED PARAM CLEAN URL]: " + endpoint + finder + poi)
                                        writeReflectedParamToFile("[POST REFLECTED CODE SNIPPET]: " + parsed_data)
                                    break


def grabHiddenParameters(endpoint, content):
    htmltree = lxml.html.fromstring(content)
    try:
        for input_el in htmltree.xpath('//input'):
            name = input_el.attrib['name']
            writeHiddenInputs(str(endpoint) + " : " + str(name))
    except Exception as e:
        print('Collection exception: ' + str(e))


def sendXSSTesting(endpoint, auth_cookie):
    global hidden_params
    endpoint = endpoint.replace("\n", "")
    if str(auth_cookie) != "{}":
        response = requests.get(endpoint, cookies=auth_cookie, verify=False)
    else:
        response = requests.get(endpoint, verify=False)
    content = str(response.content)
    if "zzxy" in content:
        print("[TESTING POTENTIAL XSS]: " + endpoint, "")
        testXSS(endpoint)


def testXSS(url):
    test1 = url + '"> test'
    response1 = str(requests.get(test1).content)
    test2 = url + "'</script><script>test</script>"
    response2 = str(requests.get(test2).content)
    test3 = url + '"</script><script>test</script>'
    response3 = str(requests.get(test3).content)
    if '"> test' in response1:
        sendDiscordMessage("[CONFIRMED XSS]: " + test1, "")
        writeReflectedParamToFile("[CONFIRMED XSS]: " + url)
    elif "'</script><script>test</script>" in response2:
        sendDiscordMessage("[CONFIRMED XSS]: " + test2, "")
        writeReflectedParamToFile("[CONFIRMED XSS]: " + url)
    elif '"</script><script>test</script>' in response3:
        sendDiscordMessage("[CONFIRMED XSS]: " + test3, "")
        writeReflectedParamToFile("[CONFIRMED XSS]: " + url)


def sendPayloadChars(base, param, poi, cookie):
    payloads = ['">', "'>", "<>", "</", "<", ">"]
    #xss_payloads = ['"><img src=x>', "'><img src=x>", "<img src=x>", "</script>"]
    for payload in payloads:
        url = base + param + poi + payload
        response = requests.get(url, cookies=cookie)
        content = str(response.content)
        if str(response.status_code) == '403':
            vals = {}
            param = param.replace("?", "")
            param = param.replace("=", "")
            vals['' + param] = poi + payload
            response = requests.post(base, data=vals, cookies=cookie)
            content = str(response.content)
            if (poi + payload) in content:
                parsed_data = str(content[int(content.find(poi+payload) - 100):int(content.find(poi+payload)) + 100])
                print("[XSS POST]: " + url)
                writeReflectedParamToFile("[XSS POST]: " + url)
                sendDiscordMessage("[XSS POST]: " + url, parsed_data)
                #print("[XSS DATA]: " + parsed_data)
                #checkXSSPayload("post", xss_payloads, (base + param + poi), cookie)
                break
        elif (poi + payload) in content:
            print("[XSS GET]: " + url)
            parsed_data = str(content[int(content.find(poi + payload) - 100):int(content.find(poi + payload)) + 100])
            writeReflectedParamToFile("[XSS GET]: " + url)
            sendDiscordMessage("[XSS GET]: " + url, parsed_data)
            #print("[XSS DATA]: " + parsed_data)
            #checkXSSPayload("get", xss_payloads, (base + param + poi), cookie)
            break
        else:
            vals = {}
            param = param.replace("?", "")
            param = param.replace("=", "")
            vals['' + param] = poi + payload
            response = requests.post(base, data=vals, cookies=cookie)
            content = str(response.content)
            if (poi + payload) in content:
                parsed_data = str(content[int(content.find(poi + payload) - 100):int(content.find(poi + payload)) + 100])
                print("[XSS POST]: " + url)
                writeReflectedParamToFile("[XSS POST]: " + url)
                sendDiscordMessage("[XSS POST]: " + url, parsed_data)
                #print("[XSS DATA]: " + parsed_data)
                #checkXSSPayload("post", xss_payloads, (base + param + poi), cookie)
                break


# def checkXSSPayload(method, payloads, url, cookie):
#     for payload in payloads:
#         if method == "get":
#             url = url + payload
#             response = requests.get(url, cookies=cookie)
#             content = str(response.content)
#         elif method == "post":
#             vals = {}
#             param = param.replace("?", "")
#             param = param.replace("=", "")
#             #vals['' + param] = poi + xss
#             response = requests.post(base, data=vals, cookies=cookie)
#             content = str(response.content)
#             #if (poi + payload) in content:
#                 parsed_data = str(content[int(content.find(poi + payload) - 100):int(content.find(poi + payload)) + 100])
#                 print("[XSS CONF]: " + url)
#                 writeReflectedParamToFile("[XSS CONF]: " + url)
#                 sendDiscordMessage("[XSS CONF]: " + url, parsed_data)
