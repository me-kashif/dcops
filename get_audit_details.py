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


def get_audit_details(aci_cookie, apic_ip):
    """ 
    Fetches EP details using API call

    Parameters:

    aci_cookie (dict): Session dictionary
    apic_ip (string): APIC controller ip address
    mac_address (string): (Optional) default is None. It searches specific mac-address

    Returns:
    dict: API response in JSON

    """

    url = f'{apic_ip}/api/node/class/aaaModLR.json?&order-by=aaaModLR.modTs|desc'

    headers = {
        'cache-control': "no-cache"
    }

    get_response = requests.get(
        url, headers=headers, cookies=aci_cookie, verify=False).json()

    return get_response

def get_processed_data(get_audit_details_result):

    fields = ['id', 'user','created','descr','trig','changeSet','dn','affected','cause','ind','txId']
    data = []

    for audits in get_audit_details_result['imdata']:
        for audit_data in audits['aaaModLR'].items():
            line_dict={}
            for field in fields:
                line_dict[field] = audit_data[1][field]
            data.append(line_dict)

    processed_data = list()

    for row in data:
        
        c_splitted_date_time = row['created'].split('T')
        # lt_splitted_date_time = row['modTs'].split('T')

        c_date = c_splitted_date_time[0]
        c_time = c_splitted_date_time[1]

             # 'id', 'user','created','descr','trig','changeSet','dn','affected','cause','ind','txId'
        id = row['id']
        description = row['descr']
        user = row['user']
        dn = row['dn']
        actionTrig = row['trig']
        changeSet = row['changeSet']
        affectedObject = row['affected']
        cause = row['cause']
        actionPerformed = row['ind']
        transactionId = row['txId']
        
        temp_dict = {'id':id,'transactionId':transactionId,'description':description,'user':user,'actionTrig':actionTrig,'actionPerformed':actionPerformed,'changeSet':changeSet,'dn':dn,'affectedObject':affectedObject,'cause':cause,'creation_date':c_date,'creation_time':c_time}

        processed_data.append(temp_dict)
    return processed_data

def print_details_onscreen(data):

    for row in data:
        
        print("="*211)
        print(f"\nID : {row['id']}")
        print(f"Transaction ID : {row['transactionId']}")
        print(f"Creation date : {row['creation_date']}")
        print(f"Creation time : {row['creation_time']}")
        print(f"Description : {row['description']}")
        print(f"change Set : {row['changeSet']}")
        print(f"Action Trigger  : {row['actionTrig']}")
        print(f"Action Performed  : {row['actionPerformed']}")
        print(f"Cause  : {row['cause']}")
        print(f"Affected object  : {row['affectedObject']}")
        print(f"DN  : {row['dn']}")
        print(f"user  : {row['user']}")
        print("\n")
    print(f"Total number of records are {len(data)}\n" )

def get_filtered_data_func(filter_value,filter_type,get_data):

    get_filtered_data = [filtered_data
                        for filtered_data in get_data
                        if filter_value in filtered_data[filter_type]]
    print_details_onscreen(get_filtered_data)

def save_to_csv(list_of_all_data):
    
    keys = list_of_all_data[0].keys()
    
    with open('Audit_data.csv', 'w', newline='')  as output_file:
    
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list_of_all_data)

    print('\n' + '-'*30)    
    print("File has been saved!!!")
    print('-'*30 + '\n')

def main():
    
    aci_cookie = get_aci_token(
        credentials["username"], credentials["password"], credentials["apic_ip"])
    get_audit_details_result = get_audit_details(aci_cookie, credentials["apic_ip"])
    
    # print(get_audit_details_result)
    get_data = get_processed_data(get_audit_details_result)
    # print(get_data)

    main_operations_list = ['Exit',
                            'Print Faults details on screen',
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
                                    'Filter by user',
                                    'Filter by time',
                                    'Filter by Action Performed',
                                    'Filter by description',
                                    'Filter by affected object',
                                    'Filter by ID',
                                    'Filter by DN',
                                    ]    

            while True:
                for index,sub_menu_items in enumerate(sub_operations1_list,0):
                    print(f"{index}: {sub_menu_items}")

                subops1 = input('\nChoose number to select type of operation : ')
                if subops1 == '0':
                    break

                elif subops1 == '1':
                    print_results(get_data)

                elif subops1 == '2':
                    filter_value1 = input("\nEnter usnername: ")
                    filter_type1='user'
                    get_filtered_data_func(filter_value1,filter_type1,get_data) 
                
                elif subops1 == '3':
                    
                    filter_value1 = input("\nCreation time (HH:MM:SS): ")
                    filter_type1='creation_time'
                    get_filtered_data_func(filter_value1,filter_type1,get_data) 

                elif subops1 == '4':
                    
                    filter_value1 = input("\nEnter string to search in Action Performed: ")
                    filter_type1='actionPerformed'
                    get_filtered_data_func(filter_value1,filter_type1,get_data)                 

                elif subops1 == '5':
                    filter_value1 = input("\nEnter string to search in description: ")
                    filter_type1='description'
                    get_filtered_data_func(filter_value1,filter_type1,get_data)
                
                elif subops1 == '6':
                    filter_value1 = input("\nEnter string to search in affected object: ")
                    filter_type1='affectedObject'
                    get_filtered_data_func(filter_value1,filter_type1,get_data)

                elif subops1 == '7':
                    filter_value1 = input("\nEnter id: ")
                    filter_type1='id'
                    get_filtered_data_func(filter_value1,filter_type1,get_data)

                elif subops1 == '8':
                    filter_value1 = input("\nEnter string to search in DN: ")
                    filter_type1='dn'
                    get_filtered_data_func(filter_value1,filter_type1,get_data)    
        
        
        elif main_operation == '2':
            save_to_csv(get_data)
if __name__ == '__main__':
    main()