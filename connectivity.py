import json
import requests
import urllib3
from credentials import credentials

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_aci_token(username, password, apic_ip):
    """
    Arguments: 
      payload = username password to generate token
      url = APIC URL

    returns:
      token cookie

    """
    url = f'{apic_ip}/api/aaaLogin.json'
    payload = {
        "aaaUser": {
            "attributes": {
                "name": username,
                "pwd": password
            }
        }
    }

    headers = {
        'Content-Type': "application/json"
    }

    response = requests.post(url, data=json.dumps(
        payload), headers=headers, verify=False).json()

    # print(json.dumps(response, indent=2, sort_keys=True))

    # PARSE TOKEN AND SET COOKIE

    token = response['imdata'][0]['aaaLogin']['attributes']['token']
    cookie = {}
    cookie['APIC-cookie'] = token

    return cookie


if __name__ == '__main__':

    token_cookies = get_aci_token(
        credentials["username"], credentials["password"], credentials["apic_ip"])
    print(token_cookies)
