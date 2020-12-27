from connectivity import get_aci_token
from credentials import credentials
import json
import requests
import csv
from datetime import datetime
from prettytable import PrettyTable
from pprint import pprint

TODAYS_DATE = datetime.today().strftime('%Y-%m-%d')


def get_fault_details(aci_cookie, apic_ip,req_date):
    ######### GET Fault instances ##############
    # GET EP details
    
    url = f'{apic_ip}/api/node/class/topology/pod-1/faultRecord.json?order-by=faultRecord.created|desc&query-target-filter=and(wcard(faultRecord.created, "{req_date}"))'
    
    
    headers = {
        'cache-control': "no-cache"
    }

    get_response = requests.get(
        url, headers=headers, cookies=aci_cookie, verify=False).json()

    return get_response

def save_to_csv(list_of_all_data):
    
    keys = list_of_all_data[0].keys()
    
    with open('faults_history_data.csv', 'w', newline='')  as output_file:
    
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list_of_all_data)

    print('\n' + '-'*30)    
    print("File has been saved!!!")
    print('-'*30 + '\n')

def print_results(data):
    for row in data:
        
        print("="*211)
        print(f"\nSeverity : {row['severity']}")
        print(f"Code : {row['fault_code']}")
        print(f"Creation date : {row['creation_date']}")
        print(f"Creation time : {row['creation_time']}")
        print(f"description  : {row['description']}")
        print(f"cause : {row['cause']}")
        print(f"Affected object  : {row['affected']}")
        print("\n")
    print(f"Total number of records are {len(data)}\n" )

def get_processed_data(get_fault_details_result):

    fields = ['code', 'created','descr','severity','cause','affected']
    data = []

    for endpoints in get_fault_details_result['imdata']:
        for endpoint_data in endpoints['faultRecord'].items():
            line_dict={}
            for field in fields:
                line_dict[field] = endpoint_data[1][field]
            data.append(line_dict)

    processed_data = list()

    for row in data:
        
        c_splitted_date_time = row['created'].split('T')
        
        c_date = c_splitted_date_time[0]
        c_time = c_splitted_date_time[1].split('+')[0]

                
        code = row['code']
        description = row['descr']
        severity = row['severity']
        affected = row['affected']
        cause = row['cause']
                
        temp_dict = {'creation_date':c_date,'creation_time':c_time,'fault_code':code,'description':description,'severity':severity,'cause':cause,'affected':affected}

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

def main(req_date):
    
    

    if not req_date:
        exit()  

    aci_cookie = get_aci_token(
        credentials["username"], credentials["password"], credentials["apic_ip"])
    get_fault_details_result = get_fault_details(aci_cookie, credentials["apic_ip"],req_date)
    
    get_data = get_processed_data(get_fault_details_result)
    
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
                                    'Filter by severity',
                                    'Filter by time',
                                    'Filter by cause',
                                    'Filter by description',
                                    'Filter by affected object',
                                    'Filter by fault code',
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
                    filter_value1 = input("\nEnter Severity(critical,major,minor,warning): ")
                    filter_type1='severity'
                    get_filtered_data_func(filter_value1,filter_type1,get_data) 
                
                elif subops1 == '3':
                    
                    filter_value1 = input("\nCreation time (HH:MM:SS): ")
                    filter_type1='creation_time'
                    get_filtered_data_func(filter_value1,filter_type1,get_data) 

                elif subops1 == '4':
                    
                    filter_value1 = input("\nEnter string to search in cause: ")
                    filter_type1='cause'
                    get_filtered_data_func(filter_value1,filter_type1,get_data)                 

                elif subops1 == '5':
                    filter_value1 = input("\nEnter string to search in description: ")
                    filter_type1='description'
                    get_filtered_data_func(filter_value1,filter_type1,get_data)
                
                elif subops1 == '6':
                    filter_value1 = input("\nEnter string to search in affected object: ")
                    filter_type1='affected'
                    get_filtered_data_func(filter_value1,filter_type1,get_data)

                elif subops1 == '7':
                    filter_value1 = input("\nEnter fault code: ")
                    filter_type1='fault_code'
                    get_filtered_data_func(filter_value1,filter_type1,get_data)    
        
        
        elif main_operation == '2':
            save_to_csv(get_data)
if __name__ == '__main__':
    main()
          
