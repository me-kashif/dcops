from connectivity import get_aci_token
from credentials import credentials
import json
import requests
import csv
from datetime import datetime

TODAYS_DATE = datetime.today().strftime('%Y-%m-%d')


def get_rogue_details(aci_cookie, apic_ip):
    ######### GET rogue instances ##############
    # GET EP details
    
    url = f"{apic_ip}/api/node/class/epmRogueMacEp.json?&order-by=epmRogueMacEp.modTs|desc"
    
    
    headers = {
        'cache-control': "no-cache"
    }

    get_response = requests.get(
        url, headers=headers, cookies=aci_cookie, verify=False).json()

    return get_response

def save_to_csv(list_of_all_data):
    
    keys = list_of_all_data[0].keys()
    
    with open('rogue_data.csv', 'w', newline='')  as output_file:
    
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(list_of_all_data)

    print('\n' + '-'*30)    
    print("File has been saved!!!")
    print('-'*30 + '\n')

def print_results(data):
    for row in data:
        
        print("="*211)
        print(f"\nMAC : {row['mac']}")
        print(f"Interface ID : {row['ifId']}")
        print(f"Flags : {row['flags']}")
        print(f"Creation date : {row['creation_date']}")
        print(f"Creation time : {row['creation_time']}")
        print(f"Status  : {row['status']}")
        print(f"Affected object  : {row['DN']}")
        print(f"Previous interface details : {row['prevIfInfo']}")
        print("\n")
    print(f"Total number of records are {len(data)}\n" )

def get_processed_data(get_rogue_details_result):

    fields = ['addr', 'createTs','flags','ifId','prevIfInfo','status','dn']
    data = []

    for endpoints in get_rogue_details_result['imdata']:
        for endpoint_data in endpoints['epmRogueMacEp'].items():
            line_dict={}
            for field in fields:
                line_dict[field] = endpoint_data[1][field]
            data.append(line_dict)

    processed_data = list()

    for row in data:
        
        c_splitted_date_time = row['createTs'].split('T')
        
        c_date = c_splitted_date_time[0]
        c_time = c_splitted_date_time[1].split('+')[0]

                
        mac = row['addr']
        flags = row['flags']
        ifId = row['ifId']
        dn = row['dn']
        prevIfInfo = row['prevIfInfo']
        status = row['status']
        
        
        temp_dict = {'mac':mac,'flags':flags,'ifId':ifId,'prevIfInfo':prevIfInfo,'status':status,'DN':dn,'creation_date':c_date,'creation_time':c_time}

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
    get_rogue_details_result = get_rogue_details(aci_cookie, credentials["apic_ip"])
    
    get_data = get_processed_data(get_rogue_details_result)
    # pprint(get_data)
    main_operations_list = ['Exit',
                            'Print Rogue EP details on screen',
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
                                    'Filter by mac address',
                                    'Filter by creation date & time',
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
                    filter_value = input("Enter MAC Address: ").upper()
                    filter_type='mac'
                    get_filtered_data_func(filter_value,filter_type,get_data)
                
                elif subops1 == '3':
                    filter_value1 = input("\nCreation date (YYYY-MM-DD): ")
                    filter_type1='creation_date'

                    filter_value2 = input("\nCreation time (HH:MM:SS): ")
                    filter_type2='creation_time'
                    get_filtered_data_func(filter_value1,filter_type1,get_data,filter_value2,filter_type2) 

                        
        elif main_operation == '2':
            save_to_csv(get_data)
if __name__ == '__main__':
    main()
          
