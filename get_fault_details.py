from connectivity import get_aci_token
from credentials import credentials
import json
import requests
from pprint import pprint
from prettytable import PrettyTable


def get_fault_details(aci_cookie, apic_ip ,fault_code=None):
    ######### GET Fault instances ##############
    # GET EP details
    print(fault_code)
    if fault_code:
        url = f'{apic_ip}api/node/class/faultInst.json?query-target-filter=and(eq(faultInst.code,"{fault_code}"))&order-by=faultInst.modTs|desc'
    else:
        url = f"{apic_ip}api/node/class/faultInst.json?&order-by=faultInst.modTs|desc"
    
    print(url)

    headers = {
        'cache-control': "no-cache"
    }

    get_response = requests.get(
        url, headers=headers, cookies=aci_cookie, verify=False).json()

    return get_response


if __name__ == '__main__':
    fault_code = input("Enter Fault code if you know or leave blank to show all faults result. : ")
    aci_cookie = get_aci_token(
        credentials["username"], credentials["password"], credentials["apic_ip"])
    get_fault_details_result = get_fault_details(aci_cookie, credentials["apic_ip"],fault_code)
    
    #pprint(get_fault_details_result)

    fields = ['code', 'created','lastTransition','descr','severity','subject','dn']
    data = []

for endpoints in get_fault_details_result['imdata']:
    for endpoint_data in endpoints['faultInst'].items():
        line_dict={}
        for field in fields:
            line_dict[field] = endpoint_data[1][field]
        data.append(line_dict)

# table = PrettyTable()
# table.field_names = ['code', 'created','lastTransition','severity','location']
for row in data:
    if row['severity'] =='critical' or row['severity'] =='major':
        # table.add_row([row['code'],row['created'].split(".")[0],row['lastTransition'].split(".")[0],row['severity'],row['dn']])
        print("-"*80)
        print(f"Severity is : {row['severity']}")
        print(f"Code : {row['code']}")
        print(f"Created on  : {row['created']}")
        print(f"Last transition on  : {row['lastTransition']}")
        print(f"description is  : {row['descr']}")
        print(f"DN is  : {row['dn']}")
        print("-"*80)
    

# print(table)