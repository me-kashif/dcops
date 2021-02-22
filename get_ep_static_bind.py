#!/usr/bin/env python3.8

"""
Author : Kashif Khan
This script helps to search Endpoint in following criteria.
1: All results
2: Filter by Node ID
3: Filter by EPG
4: Filter by VLAN ID
5: Filter by Interface Name
6: Filter by Tenant Name
7: Filter by MAC Address

"""
# Imports block
from connectivity import get_aci_token
from credentials import credentials
import json
import requests
from pprint import pprint
from prettytable import PrettyTable 
import csv


def get_ep_details(aci_cookie, apic_ip):
    """ 
    Fetches EP details using API call

    Parameters:

    aci_cookie (dict): Session dictionary
    apic_ip (string): APIC controller ip address
    mac_address (string): (Optional) default is None. It searches specific mac-address

    Returns:
    dict: API response in JSON

    """

    url = f'{apic_ip}/api/node/class/fvRsPathAtt.json?&order-by=fvRsPathAtt.modTs|desc'

    headers = {
        'cache-control': "no-cache"
    }

    get_response = requests.get(
        url, headers=headers, cookies=aci_cookie, verify=False).json()

    return get_response

def get_processed_data(get_ep_details_result):

    data = []
    fields = ['encap', 'modTs','instrImedcy','dn','uid','tDn','mode']

    for each_ep in get_ep_details_result['imdata']:
        line_dict = {}
        for key,value in each_ep['fvRsPathAtt'].items():
        
            if isinstance (value,list):
                for each_tdn in value:
                    if each_tdn.get('fvRsCEpToPathEp'):
                        line_dict.update({'path':each_tdn['fvRsCEpToPathEp']['attributes']['tDn']})
            else:
                line_dict.update({'modTs':value['modTs']})
                line_dict.update({'uid':value['uid']})
                line_dict.update({'encap':value['encap']})
                line_dict.update({'dn':value['dn']})
                line_dict.update({'instrImedcy':value['instrImedcy']})
                line_dict.update({'tDn':value['tDn']})
                line_dict.update({'mode':value['mode']})
                
        data.append(line_dict)

    
    processed_data = list()

    for row in data:
        
        dn_splitted_list = row['dn'].split("/")   
        tdn_splitted_list = row['tDn'].split("/")[2:]   
        
        switch_splitted = tdn_splitted_list[0].split("-")[1:] 
        tdn_splitted_list = tdn_splitted_list[1:] 
        tdn_splitted_list = "/".join(tdn_splitted_list)
        interface_splitted = tdn_splitted_list.split("-")[1:]    

        last_change_at = row['modTs']
        uid = row['uid']

        if row['mode'] == 'regular':
            row['mode'] = 'Trunk'
        elif row['mode'] == 'native':
            row['mode'] = 'AccessDot1P'
        elif row['mode'] == 'untagged':
            row['mode'] = 'AccessUntagged'

        mode = row['mode']

        if row['instrImedcy'] == 'lazy':
            row['instrImedcy'] = 'on_demand'
        
        dep_mode = row['instrImedcy']
        vlan = row['encap'].lstrip("vlan-")
        tenant = dn_splitted_list[1].lstrip("tn-")
        ap = dn_splitted_list[2].lstrip("ap-")
        epg = dn_splitted_list[3].lstrip("epg-")
        switch = "-".join(switch_splitted)
        interface = "-".join(interface_splitted).strip("[]")
        temp_dict = {'tenant':tenant,'application_profile':ap,'epg':epg,'vlan':vlan,'mode':mode,'dep_mode':dep_mode,'switch':switch,'interface':interface,'last_change_at':last_change_at}

        processed_data.append(temp_dict)
    return processed_data

def print_details_onscreen(processed_data):

    table = PrettyTable()
    table.field_names = ['Tenant','AP','EPG','Vlan','Mode','Dep_mode','Switch','Interface','last_change_at']

    
    table.align['Tenant'] = 'l'
    table.align['AP'] = 'l'
    table.align['EPG'] = 'l'
    table.align['Vlan'] = 'l'
    table.align['Mode'] = 'l'
    table.align['Dep_mode'] = 'l'
    table.align['Switch'] = 'l'
    table.align['Interface'] = 'l'
    table.align['Tenant'] = 'l'
    table.align['last_change_at'] = 'l'

    count = 0
    for each_row in processed_data:
        
        count += 1
        only_values = [values for values in each_row.values()]
        table.add_row(only_values)  # adds each mac address detail in table.
        

    print(table)
    print(f"Total number of interfaces where Endpoint mac-address learnd are {count}")

def get_filtered_data_func(filter_value,filter_type,get_data):

    get_filtered_data = [filtered_data
                        for filtered_data in get_data
                        if filter_value in filtered_data[filter_type]]
    print_details_onscreen(get_filtered_data)

def save_to_csv(list_of_all_data):
    
    keys = list_of_all_data[0].keys()
    
    with open('ep_static_bind.csv', 'w', newline='')  as output_file:
    
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list_of_all_data)

    print('\n' + '-'*30)    
    print("File has been saved!!!")
    print('-'*30 + '\n')

def main():
    
    aci_cookie = get_aci_token(
        credentials["username"], credentials["password"], credentials["apic_ip"])
    get_ep_details_result = get_ep_details(aci_cookie, credentials["apic_ip"])
    
    get_data = get_processed_data(get_ep_details_result)
    
    main_operations_list = ['Exit',
                            'Print Endpoint details on screen',
                            'Save data to CSV']    

    while True:
        
        for index,main_items in enumerate(main_operations_list,0):
            print(f"{index}: {main_items}")

        main_operation = input('\nChoose number to select type of operation : ')
        if main_operation == '0':
            break
                
        elif main_operation == '1':
            sub_operations1_list = ['Exit',
                                    'All results',
                                    'Filter by Node ID',
                                    'Filter by EPG',
                                    'Filter by VLAN ID',
                                    'Filter by Interface Name',
                                    'Filter by Tenant Name',
                                    'Filter by Mode',
                                    ]    

            while True:
                for index,sub_menu_items in enumerate(sub_operations1_list,0):
                    print(f"{index}: {sub_menu_items}")

                subops1 = input('\nChoose number to select type of operation : ')
                if subops1 == '0':
                    break

                elif subops1 == '1':
                    print_details_onscreen(get_data) 

                elif subops1 =='2':
                    filter_value = input("Enter Node ID: ")
                    filter_type='switch'
                    if len(filter_value) != 3:
                        print('Wrong Node ID! try again')
                        continue
                    get_filtered_data_func(filter_value,filter_type,get_data)

                elif subops1 =='3':
                    filter_value = input("Enter EPG: ")
                    filter_type='epg'
                    get_filtered_data_func(filter_value,filter_type,get_data)                  
            
                elif subops1 =='4':
                    filter_value = input("Enter VLAN ID: ")
                    filter_type='vlan'
                    get_filtered_data_func(filter_value,filter_type,get_data)
                    
                elif subops1 =='5':
                    filter_value = input("Enter Interface ID: ")
                    filter_type='interface'
                    get_filtered_data_func(filter_value,filter_type,get_data)
                                
                elif subops1 =='6':
                    filter_value = input("Enter Tenant Name: ")
                    filter_type='tenant'
                    get_filtered_data_func(filter_value,filter_type,get_data)
                    
                elif subops1 =='7':
                    filter_value = input("Enter Mode (Trunk/AccessDot1P/AccessUntagged): ")
                    filter_type='mode'
                    get_filtered_data_func(filter_value,filter_type,get_data)

        elif main_operation == '2':
            save_to_csv(get_data)
                    
if __name__ == '__main__':
    main()
        


