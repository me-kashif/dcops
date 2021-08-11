from connectivity import get_aci_token
from credentials import credentials
import json
import requests
import csv
from datetime import datetime
from prettytable import PrettyTable
from pprint import pprint
import time
import sys

TODAYS_DATE = datetime.today().strftime('%Y-%m-%d')


def get_crc_details(aci_cookie, apic_ip):
    ######### GET crc instances ##############
    # GET EP details
    
    url = f'{apic_ip}/api/node/class/eqptIngrCrcErrPkts5min.json?&order-by=eqptIngrCrcErrPkts5min.modTs|desc'
    
    
    headers = {
        'cache-control': "no-cache"
    }

    get_response = requests.get(
        url, headers=headers, cookies=aci_cookie, verify=False).json()

    return get_response

def save_to_csv(list_of_all_data):
    
    keys = list_of_all_data[0].keys()
    
    with open('crc_error_data.csv', 'w', newline='')  as output_file:
    
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list_of_all_data)

    print('\n' + '-'*30)    
    print("File has been saved!!!")
    print('-'*30 + '\n')

def print_results(data):
    table = PrettyTable()
    table.field_names = ['Node','Interface','CRC_Counts','FCS_Percentage','FCS_Rate']   # {'leaf': '403', 'interface': 'eth2/1', 'fcsCum': '0', 'fcsPerc': '0', 'fcsRate': '0.000000'}

    table.align['Leaf'] = 'l'
    table.align['Interface'] = 'l'
    table.align['CRC_Counts'] = 'l'
    table.align['FCS_Percentage'] = 'l'
    table.align['FCS_Rate'] = 'l'
    

    count = 0
    for each_row in data:
        
        count += 1
        only_values = [values for values in each_row.values()]
        table.add_row(only_values)  # adds each mac address detail in table.
        

    print(table)
    print(f"Total number of interfaces where Endpoint CRC Errors learnd are {count}")

def get_processed_data(get_crc_details_result):

    fields = ['dn', 'cnt','fcsCum','fcsRate','fcsRateAvg','fcsPer','repIntvStart','repIntvEnd']
    data = []

    for endpoints in get_crc_details_result['imdata']:
        for endpoint_data in endpoints['eqptIngrCrcErrPkts5min'].items():
            line_dict={}
            for field in fields:
                line_dict[field] = endpoint_data[1][field]
            data.append(line_dict)

    processed_data = list()

    for row in data:
        
        
        tdn_splitted_list = row['dn'].split("/")[2:]
        # # ['node-402', 'sys', 'phys-[eth1', '6]', 'CDeqptIngrCrcErrPkts5min']
        switch_splitted = tdn_splitted_list[0].split("-")[1]
        
        tdn_splitted_list = tdn_splitted_list[2:]
        
        
        if len(tdn_splitted_list) == 2 :
            interface_splitted = tdn_splitted_list[0].split("-")[1]
               
        else:
            tdn_splitted_list_first = tdn_splitted_list[0].split("-[")[1]
            tdn_splitted_list_last = tdn_splitted_list[1].strip("[]")

            interface_splitted = [tdn_splitted_list_first,tdn_splitted_list_last]
            interface_splitted = "/".join(interface_splitted)

        cnt = row['cnt']
        fcsCum = row['fcsCum']
        fcsPer = row['fcsPer']
        fcsRate = row['fcsRate']
        switch = switch_splitted
        interface = interface_splitted.strip("[]")
        temp_dict = {'leaf':switch,'interface':interface,'fcsCum':fcsCum,'fcsPerc':fcsPer,'fcsRate':fcsRate}

        processed_data.append(temp_dict)
    return processed_data

def get_filtered_data_func(filter_value1,filter_type1,get_data,filter_value2=None,filter_type2=None):

    if filter_type2:
        get_filtered_data = [filtered_data
                        for filtered_data in get_data
                        if (filter_value1 in filtered_data[filter_type1]) and (filter_value2 in filtered_data[filter_type2])]    
    
    else:
        get_filtered_data = [filtered_data
                        for filtered_data in get_data
                        if filter_value1 in filtered_data[filter_type1]]
    
    if not get_filtered_data:
        print("\n" + "*"*56 + "\n!!! incorrect input value or value not found.. Try again\n" + "*"*56 + "\n")

    print_results(get_filtered_data)

def main():
    
    

    aci_cookie = get_aci_token(
        credentials["username"], credentials["password"], credentials["apic_ip"])
    get_crc_details_result = get_crc_details(aci_cookie, credentials["apic_ip"])
    # print(get_crc_details_result)
    get_data = get_processed_data(get_crc_details_result)
    # print(get_data)
    main_operations_list = ['Exit',
                            'Print crcs details on screen',
                            'Live CRC erros',
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
                                    'Filter by node',
                                    'Filter by Interface',
                                 
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
                    filter_value1 = input("\nEnter Node Number: ")
                    filter_type1='leaf'
                    get_filtered_data_func(filter_value1,filter_type1,get_data) 
                
             
                elif subops1 == '3':
                    
                    filter_value1 = input("\nEnter Interface Number: ")
                    filter_type1='interface'
                    get_filtered_data_func(filter_value1,filter_type1,get_data)                 


        
        elif main_operation == '2':
                                          
                    while True:
                        try:
                            aci_cookie1 = get_aci_token(credentials["username"], credentials["password"], credentials["apic_ip"])
                            get_crc_details_result = get_crc_details(aci_cookie, credentials["apic_ip"])
                            # print(get_crc_details_result)
                            get_data = get_processed_data(get_crc_details_result)
                            print(f"{datetime.now()} ===> Checking live CRC errors every 30 seconds")
                            live_results = list()
                            for each in get_data:
                                
                                if each['fcsCum'] != '0' : 
                                    live_results.append(each)
                            print_results(live_results)        
                            time.sleep(30)   # check every after 60 seconds
                        except KeyboardInterrupt:
                            print("closed live monitoring gracefully")
                            break

        
        elif main_operation == '3':
            save_to_csv(get_data)

if __name__ == '__main__':
    main()
          
