from connectivity import get_aci_token
from credentials import credentials
import json
import requests
import csv
from datetime import datetime

TODAYS_DATE = datetime.today().strftime('%Y-%m-%d')


def get_fault_details(aci_cookie, apic_ip):
    ######### GET Fault instances ##############
    # GET EP details
    
    url = f"{apic_ip}api/node/class/faultInst.json?&order-by=faultInst.modTs|desc"
    
    
    headers = {
        'cache-control': "no-cache"
    }

    get_response = requests.get(
        url, headers=headers, cookies=aci_cookie, verify=False).json()

    return get_response

def save_to_csv(list_of_all_data):
    
    keys = list_of_all_data[0].keys()
    
    with open('fault_data.csv', 'w', newline='')  as output_file:
    
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
        print(f"Last transition date : {row['last_transition_date']}")
        print(f"Last transition time : {row['last_transition_time']}")
        print(f"description  : {row['description']}")
        print(f"Affected object  : {row['DN']}")
        print("\n")
    print(f"Total number of records are {len(data)}\n" )

def get_processed_data(get_fault_details_result):

    fields = ['code', 'created','lastTransition','descr','severity','subject','dn']
    data = []

    for endpoints in get_fault_details_result['imdata']:
        for endpoint_data in endpoints['faultInst'].items():
            line_dict={}
            for field in fields:
                line_dict[field] = endpoint_data[1][field]
            data.append(line_dict)

    processed_data = list()

    for row in data:
        
        c_splitted_date_time = row['created'].split('T')
        lt_splitted_date_time = row['lastTransition'].split('T')

        c_date = c_splitted_date_time[0]
        c_time = c_splitted_date_time[1]

        lt_date = lt_splitted_date_time[0]
        lt_time = lt_splitted_date_time[1]
        
        code = row['code']
        description = row['descr']
        severity = row['severity']
        dn = row['dn']
        
        temp_dict = {'last_transition_time':lt_time,'last_transition_date':lt_date,'fault_code':code,'description':description,'severity':severity,'DN':dn,'creation_date':c_date,'creation_time':c_time}

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
    get_fault_details_result = get_fault_details(aci_cookie, credentials["apic_ip"])
    
    get_data = get_processed_data(get_fault_details_result)
    # pprint(get_data)
    main_operations_list = ['Exit',
                            'Print Faults details on screen',
                            'Recent faults by creation date',
                            'Recent faults by last transaction date',
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
                                    'Filter by creation date & time',
                                    'Filter by last transition date & time',
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
                    filter_value1 = input("\nCreation date (YYYY-MM-DD): ")
                    filter_type1='creation_date'

                    filter_value2 = input("\nCreation time (HH:MM:SS): ")
                    filter_type2='creation_time'
                    get_filtered_data_func(filter_value1,filter_type1,get_data,filter_value2,filter_type2) 

                elif subops1 == '4':
                    filter_value1 = input("\nLast transition date (YYYY-MM-DD): ")
                    filter_type1='last_transition_date'

                    filter_value2 = input("\nLast transition time (HH:MM:SS): ")
                    filter_type2='last_transition_time'
                    get_filtered_data_func(filter_value1,filter_type1,get_data,filter_value2,filter_type2) 
                
                elif subops1 == '5':
                    filter_value1 = input("\nEnter string to search in description: ")
                    filter_type1='description'
                    get_filtered_data_func(filter_value1,filter_type1,get_data)
                
                elif subops1 == '6':
                    filter_value1 = input("\nEnter string to search in affected object: ")
                    filter_type1='DN'
                    get_filtered_data_func(filter_value1,filter_type1,get_data)

                elif subops1 == '7':
                    filter_value1 = input("\nEnter fault code: ")
                    filter_type1='fault_code'
                    get_filtered_data_func(filter_value1,filter_type1,get_data)    
        
        elif main_operation == '2':
                    filter_value1 = TODAYS_DATE
                    filter_type1='creation_date'

                    get_filtered_data_func(filter_value1,filter_type1,get_data)

        elif main_operation == '3':
                    filter_value1 = TODAYS_DATE
                    filter_type1='last_transition_date'

                    get_filtered_data_func(filter_value1,filter_type1,get_data)

        elif main_operation == '4':
            save_to_csv(get_data)
if __name__ == '__main__':
    main()
          
