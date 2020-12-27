#!/usr/bin/env python3.8


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

    url = f'{apic_ip}/api/node/class/ethpmFcot.json?&order-by=ethpmFcot.modTs|desc'
    
    headers = {
        'cache-control': "no-cache"
    }

    get_response = requests.get(
        url, headers=headers, cookies=aci_cookie, verify=False).json()

    return get_response

def get_processed_data(get_sfp_details_result):

    data = []
    fields = ['typeName','guiName','guiPN','guiSN','state','dn']

    for endpoints in get_sfp_details_result['imdata']:
        for endpoint_data in endpoints['ethpmFcot'].items():
            line_dict={}
            for field in fields:
                line_dict[field] = endpoint_data[1][field]
            data.append(line_dict)

    
    processed_data = list()

    for row in data:
        
        dn_splitted_list_switch = row['dn'].split("/")  
        dn_splitted_list_interface = row['dn'].split("[") 

        at = row['typeName']
        gn = row['guiName']
        gpn = row['guiPN']
        gsn = row['guiSN']
        state = row['state']
        dn = row['dn']

        switch = dn_splitted_list_switch[2].split('-')[1]
        interface = dn_splitted_list_interface[1].split(']')[0]
        temp_dict = {'type':at,'sfpname':gn,'partnumber':gpn,'serialnumber':gsn,'state':state,'switch':switch,'interface':interface}

        processed_data.append(temp_dict)
    return processed_data

def print_details_onscreen(processed_data):

    table = PrettyTable()
    
    table.field_names = ['Type','SFP','Part#','SN#','state','Switch','interface']

    table.align['Type'] = 'l'
    table.align['SFP'] = 'l'
    table.align['Part#'] = 'l'
    table.align['SN#'] = 'l'
    table.align['state'] = 'l'
    table.align['Switch'] = 'l'
    table.align['interface'] = 'l'

    count = 0
    for each_row in processed_data:
        
        count += 1
        only_values = [values for values in each_row.values()]
        table.add_row(only_values)  # adds each mac address detail in table.
        

    print(table)
    print(f"Total number of interfaces where SFP info learnd are {count}")

def get_filtered_data_func(filter_value,filter_type,get_data):

    get_filtered_data = [filtered_data
                        for filtered_data in get_data
                        if filter_value in filtered_data[filter_type]]
    print_details_onscreen(get_filtered_data)

def save_to_csv(list_of_all_data):
    
    keys = list_of_all_data[0].keys()
    
    with open('aci_sfp_data.csv', 'w', newline='')  as output_file:
    
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list_of_all_data)

    print('\n' + '-'*30)    
    print("File has been saved!!!")
    print('-'*30 + '\n')

def main():
    
    aci_cookie = get_aci_token(
        credentials["username"], credentials["password"], credentials["apic_ip"])
    get_sfp_details_result = get_ep_details(aci_cookie, credentials["apic_ip"])
    
    get_data = get_processed_data(get_sfp_details_result)
        
    main_operations_list = ['Exit',
                            'Print SFP details on screen',
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
                                    'Filter by switch',
                                    'Filter by Type',
                                    'Filter by SFP name',
                                    'Filter by SFP part number',
                                    'Filter by SFP serial',
                                    'Filter by SFP state',
                                    'Filter by switch interface',
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
                    filter_value = input("Enter Type: ")
                    filter_type='type'
                    get_filtered_data_func(filter_value,filter_type,get_data)                  
            
                elif subops1 =='4':
                    filter_value = input("Enter SFP Name: ")
                    filter_type='sfpname'
                    get_filtered_data_func(filter_value,filter_type,get_data)
                    
                elif subops1 =='5':
                    filter_value = input("Enter SFP Part Number: ")
                    filter_type='partnumber'
                    get_filtered_data_func(filter_value,filter_type,get_data)
                                
                elif subops1 =='6':
                    filter_value = input("Enter SFP Serial Number: ")
                    filter_type='serialnumber'
                    get_filtered_data_func(filter_value,filter_type,get_data)
                    
                elif subops1 =='7':
                    filter_value = input("Enter SFP state: ")
                    filter_type='state'
                    get_filtered_data_func(filter_value,filter_type,get_data)

                elif subops1 =='8':
                    filter_value = input("Enter SFP interface: ").upper()
                    filter_type='interface'
                    get_filtered_data_func(filter_value,filter_type,get_data)

        elif main_operation == '2':
            save_to_csv(get_data)
                    
if __name__ == '__main__':
    main()
        


