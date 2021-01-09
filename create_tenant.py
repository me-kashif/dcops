#!/usr/bin/env python3.8

"""
Author : Kashif Khan
This script helps to create tenant

"""
# Imports block
from connectivity import get_aci_token
from credentials import credentials
import json
import requests
from pprint import pprint
from prettytable import PrettyTable 
import csv


def create_tenant(aci_cookie, apic_ip,tName,tDescr=None):
    """ 
    Fetches EP details using API call

    Parameters:

    aci_cookie (dict): Session dictionary
    apic_ip (string): APIC controller ip address
    mac_address (string): (Optional) default is None. It searches specific mac-address

    Returns:
    dict: API response in JSON

    """

    url = f'{apic_ip}/api/node/mo/uni/tn-{tName}.json'

    headers = {
        'cache-control': "no-cache"
    }

    payload = {"fvTenant":{"attributes":{"dn":f"uni/tn-{tName}","descr":f"{tDescr}","name":f"{tName}","rn":f"tn-{tName}","status":"created"},"children":[]}}

    get_response = requests.post(
        url, headers=headers, cookies=aci_cookie, verify=False,data=json.dumps(payload)).json()

    return get_response

def delete_tenant(aci_cookie, apic_ip,tName,tDescr=None):
    """ 
    Fetches EP details using API call

    Parameters:

    aci_cookie (dict): Session dictionary
    apic_ip (string): APIC controller ip address
    mac_address (string): (Optional) default is None. It searches specific mac-address

    Returns:
    dict: API response in JSON

    """

    url = f'{apic_ip}/api/node/mo/uni/tn-{tName}.json'

    headers = {
        'cache-control': "no-cache"
    }

    payload = {"fvTenant":{"attributes":{"dn":f"uni/tn-{tName}","status":"deleted"},"children":[]}}

    get_response = requests.post(
        url, headers=headers, cookies=aci_cookie, verify=False,data=json.dumps(payload)).json()

    return get_response

def load_tenants(aci_cookie, apic_ip):
    """ 
    Fetches EP details using API call

    Parameters:

    aci_cookie (dict): Session dictionary
    apic_ip (string): APIC controller ip address
    mac_address (string): (Optional) default is None. It searches specific mac-address

    Returns:
    dict: API response in JSON

    """

    url = f'{apic_ip}/api/node/class/fvTenant.json?&order-by=fvTenant.modTs|desc'

    headers = {
        'cache-control': "no-cache"
    }

    get_response = requests.get( url, headers=headers, cookies=aci_cookie, verify=False).json()

    gPd = get_processed_data(get_response)

    return gPd
    
    




def get_processed_data(get_ep_details_result):
   
    data = []
    fields = ['descr', 'name','modTs','dn','uid']

    for each_ep in get_ep_details_result['imdata']:
        line_dict = {}
        for key,value in each_ep['fvTenant'].items():
        
            line_dict.update({'descr':value['descr']})
            line_dict.update({'name':value['name']})
            line_dict.update({'modTs':value['modTs']})
            line_dict.update({'dn':value['dn']})
            line_dict.update({'uid':value['uid']})

                
        data.append(line_dict)

    
    processed_data = list()

    for row in data:
        
        desc = row['descr']
        name = row['name']
        lastModTime =  row['modTs']
        DN =  row['dn']
        UID =  row['uid']
        
        temp_dict = {'name':name,'desc':desc,'lastModTime':lastModTime,'DN':DN,'UID':UID}

        processed_data.append(temp_dict)

    return processed_data

        

def print_details_onscreen(processed_data):

    table = PrettyTable()
    table.field_names = ['Name','Description','LastModTime','DN','UID']

    table.align['Name'] = 'l'
    table.align['Description'] = 'l'
    table.align['LastModTime'] = 'l'
    table.align['DN'] = 'l'
    table.align['UID'] = 'l'
    
    count = 0
    for each_row in processed_data:
        
        count += 1
        only_values = [values for values in each_row.values()]
        table.add_row(only_values)  # adds each mac address detail in table.
        

    print(table)
    print(f"Total number tenants are {count}")


def save_to_csv(list_of_all_data):
    
    keys = list_of_all_data[0].keys()
    
    with open('tenant_data.csv', 'w', newline='')  as output_file:
    
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list_of_all_data)

    print('\n' + '-'*30)    
    print("File has been saved!!!")
    print('-'*30 + '\n')

def main():
   
    aci_cookie = get_aci_token(
        credentials["username"], credentials["password"], credentials["apic_ip"])

        
    main_operations_list = ['Exit',
                            'Tenant Operations',
                            'Save data to CSV']    

    while True:
        
        for index,main_items in enumerate(main_operations_list,0):
            print(f"{index}: {main_items}")

        main_operation = input('\nChoose number to select type of operation : ')
        if main_operation == '0':
            break
                
        elif main_operation == '1':
            sub_operations1_list = ['Exit',
                                    'Display tenants',
                                    'Create tenants',
                                    'Remove tenants',
                                   ]    

            while True:
                for index,sub_menu_items in enumerate(sub_operations1_list,0):
                    print(f"{index}: {sub_menu_items}")

                subops1 = input('\nChoose number to select type of operation : ')
                if subops1 == '0':
                    break

                elif subops1 == '1':
                    gPd = load_tenants(aci_cookie, credentials["apic_ip"]) 
                    print_details_onscreen(gPd)

                elif subops1 =='2':
                    tName = input("Tenant name : ")
                    tDescr = input("Enter Tenant Description : ")
                    response = create_tenant(aci_cookie, credentials["apic_ip"],tName,tDescr)
                    if response:
                        print("\n !!!       Tenant created successfully     !!!!!\n")

                elif subops1 =='3':
                    tName = input("Tenant name : ")
                    response = delete_tenant(aci_cookie, credentials["apic_ip"],tName)
                    try:
                        if response['imdata'][0]['error']['attributes']['text']:
                            print(f"\n{response['imdata'][0]['error']['attributes']['text']}\n")
                    except:
                        print("\n Deleted\n")  
                              
            

        elif main_operation == '2':
            get_data1 = load_tenants(aci_cookie, credentials["apic_ip"]) 
            save_to_csv(get_data1)
                    
if __name__ == '__main__':
    main()
        


