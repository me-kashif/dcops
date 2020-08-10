#!/usr/bin/env python3.8

"""
Author : Kashif Khan
This script helps to search Endpoint mac-address in following criteria.
1) Search single endpoint mac-address in the fabric. e.g (AA:BB:CC:DD:EE:FF)
2) List all endpoint mac-addresses from the fabric if specific mac-address will not be entered.

"""

from connectivity import get_aci_token
from credentials import credentials
import json
import requests
from pprint import pprint
from prettytable import PrettyTable 


def get_ep_details(aci_cookie, apic_ip,mac_addr=None):
    """ 
    Fetches EP details using API call

    Parameters:

    aci_cookie (dict): Session dictionary
    apic_ip (string): APIC controller ip address
    mac_address (string): (Optional) default is None. It searches specific mac-address

    Returns:
    dict: API response in JSON

    """

    if mac_addr:
        url = f'{apic_ip}/api/node/class/fvCEp.json?rsp-subtree=full&rsp-subtree-class=fvCEp,fvRsCEpToPathEp,fvIp,fvRsHyper,fvRsToNic,fvRsToVm&query-target-filter=wcard(fvCEp.mac,"{mac_addr}")'
    else:
        url = f'{apic_ip}/api/node/class/fvCEp.json?rsp-subtree=full&rsp-subtree-class=fvCEp,fvRsCEpToPathEp,fvIp,fvRsHyper,fvRsToNic,fvRsToVm'

    headers = {
        'cache-control': "no-cache"
    }

    get_response = requests.get(
        url, headers=headers, cookies=aci_cookie, verify=False).json()

    return get_response


if __name__ == '__main__':

    mac_addr = input("Enter full or part of mac address in format AA:BB:CC:DD:EE:FF or leave blank to show all results. : ")
    aci_cookie = get_aci_token(
        credentials["username"], credentials["password"], credentials["apic_ip"])
    get_ep_details_result = get_ep_details(aci_cookie, credentials["apic_ip"],mac_addr.upper())
    
    data = []
    fields = ['mac', 'ip','encap','dn','path']

    for each_ep in get_ep_details_result['imdata']:
        line_dict = {}
        for key,value in each_ep['fvCEp'].items():
        
            if isinstance (value,list):
                for each_tdn in value:
                    if each_tdn.get('fvRsCEpToPathEp'):
                        line_dict.update({'path':each_tdn['fvRsCEpToPathEp']['attributes']['tDn']})
            else:
                line_dict.update({'mac':value['mac']})
                line_dict.update({'ip':value['ip']})
                line_dict.update({'encap':value['encap']})
                line_dict.update({'dn':value['dn']})
                
        data.append(line_dict)

table = PrettyTable()
table.field_names = ['MAC Address','VLAN','Tenant','AP','EPG','Switch','Interface']

table.align['Interface'] = 'l'
table.align['MAC Address'] = 'l'
table.align['VLAN'] = 'l'
table.align['Tenant'] = 'l'
table.align['AP'] = 'l'
table.align['EPG'] = 'l'
table.align['Switch'] = 'l'

count = 0           #   To count number of interfaces where mac-address learnd  

for row in data:
    count += 1

    dn_splitted_list = row['dn'].split("/")
    tdn_splitted_list = row['path'].split("/")[2:]
    
    switch_splitted = tdn_splitted_list[0].split("-")[1:]
    tdn_splitted_list = tdn_splitted_list[1:]
    tdn_splitted_list = "/".join(tdn_splitted_list)
    interface_splitted = tdn_splitted_list.split("-")[1:]    

    mac = row['mac']
    vlan = row['encap'].lstrip("vlan-")
    tenant = dn_splitted_list[1].lstrip("tn-")
    ap = dn_splitted_list[2].lstrip("ap-")
    epg = dn_splitted_list[3].lstrip("epg-")
    switch = "-".join(switch_splitted)
    interface = "-".join(interface_splitted).strip("[]")
    
    table.add_row([mac,vlan,tenant,ap,epg,switch,interface])  # adds each mac address detail in table.

       
print(table)
print(f"Total number of interfaces where Endpoint mac-address learnd are {count}")


