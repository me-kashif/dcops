from connectivity import get_aci_token
from credentials import credentials
import json
import requests
import csv
from datetime import datetime
import keyboard
import time
import sys

TODAYS_DATE = datetime.today().strftime('%Y-%m-%d')
current_time = datetime.now()
FW_MAC1 = 'aa:aa:aa:aa:aa:aa'
FW_MAC2 = 'bb:bb:bb:bb:bb:bb'


# only_current_time = current_time.now.strftime("%H:%M:%S")

def get_rogue_configs(aci_cookie, apic_ip):
    ######### GET rogue instances ##############
    # GET EP details
    
    url = f"{apic_ip}/api/node/mo/uni/infra/epCtrlP-default.json?rsp-subtree-include=full-deployment"
    
    
    headers = {
        'cache-control': "no-cache"
    }

    get_response = requests.get(
        url, headers=headers, cookies=aci_cookie, verify=False).json()

    return get_response

def configureRogueEpSetting(aci_cookie, apic_ip,setValue):
    """ 
    Fetches EP details using API call

    Parameters:

    aci_cookie (dict): Session dictionary
    apic_ip (string): APIC controller ip address
    mac_address (string): (Optional) default is None. It searches specific mac-address

    Returns:
    dict: API response in JSON

    """

    url = f'{apic_ip}/api/node/mo/uni/infra/epCtrlP-default.json'

    headers = {
        'cache-control': "no-cache"
    }

    payload = {"epControlP":{"attributes":{"dn":"uni/infra/epCtrlP-default","adminSt":f"{setValue}"},"children":[]}}
    
    get_response = requests.post(
        url, headers=headers, cookies=aci_cookie, verify=False,data=json.dumps(payload)).json()

    return get_response


def clearRogueEp(aci_cookie, apic_ip,nodeId):
    """ 
    Fetches EP details using API call

    Parameters:

    aci_cookie (dict): Session dictionary
    apic_ip (string): APIC controller ip address
    mac_address (string): (Optional) default is None. It searches specific mac-address

    Returns:
    dict: API response in JSON

    """

    url = f'{apic_ip}/api/node/mo/topology/pod-1/node-{nodeId}/sys/action.json'

    headers = {
        'cache-control': "no-cache"
    }

    payload = {"actionLSubj":{"attributes":{"dn":f"topology/pod-1/node-{nodeId}/sys/action/lsubj-[topology/pod-1/node-{nodeId}]","oDn":f"topology/pod-1/node-{nodeId}"},"children":[{"topSystemClearEpLTask":{"attributes":{"dn":f"topology/pod-1/node-{nodeId}/sys/action/lsubj-[topology/pod-1/node-{nodeId}]/topSystemClearEpLTask","adminSt":"start"},"children":[]}}]}}

    get_response = requests.post(
        url, headers=headers, cookies=aci_cookie, verify=False,data=json.dumps(payload)).json()

    return get_response

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
        print(f"Node ID : {row['node_id']}")
        print(f"VRF ID : {row['vrf_id']}")
        print(f"BD ID : {row['bd_id']}")
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
        dn_splitted = row['dn'].split('node-')[1].split('/')
        node_id,vrf_id,bd_id = dn_splitted[0],dn_splitted[2].split('vxlan-')[1].rstrip(']'),dn_splitted[3].split('vxlan-')[1].rstrip(']')

                
        mac = row['addr']
        flags = row['flags']
        ifId = row['ifId']
        dn = row['dn']
        prevIfInfo = row['prevIfInfo']
        status = row['status']
        
        
        temp_dict = {'mac':mac,'flags':flags,'ifId':ifId,'prevIfInfo':prevIfInfo,'status':status,'DN':dn,'creation_date':c_date,'creation_time':c_time,'node_id':node_id,'bd_id':bd_id,'vrf_id':vrf_id}

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
    
    # pprint(get_data)
    main_operations_list = ['Exit',
                            'Print Rogue EP details on screen',
                            'Clear Rogue EP from Leafs',
                            'Rogue EP Global Configs',
                            'Automatically detect and clear Rogue EP',
                            'Save data to CSV']    

    while True:
        
        for index,main_items in enumerate(main_operations_list,0):
            print(f"{index}: {main_items}")

        main_operation = input('\nChoose number to select type of operation : ')
        if main_operation == '0':
            break
        
        elif main_operation == '1':
            get_rogue_details_result = get_rogue_details(aci_cookie, credentials["apic_ip"])
    
            get_data = get_processed_data(get_rogue_details_result)
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
            nodeId = input("Enter Node ID to clear Rogue EP or 'q' quit: ")
            if nodeId:
                if nodeId == 'q' or int(nodeId) < 100 :
                    break
                response = clearRogueEp(aci_cookie,  credentials["apic_ip"],nodeId)
                print(f"\n{response}\n")
            else:
                break
        elif main_operation == '3':
            
            sub_operations1_list = ['Exit',
                                    'Display current configs',
                                    'Enable Rogue EP configs globally',
                                    'Disable Rogue EP configs globally',
                                   ]    

            while True:
                for index,sub_menu_items in enumerate(sub_operations1_list,0):
                    print(f"{index}: {sub_menu_items}")

                subops1 = input('\nChoose number to select type of operation : ')
                if subops1 == '0':
                    break

                elif subops1 == '1':
                    config_response = get_rogue_configs(aci_cookie, credentials["apic_ip"])
                    print(f"\nGlobal EP cofigures are {config_response['imdata'][0]['epControlP']['attributes']['adminSt']} now\n")
                elif subops1 == '2':
                    configureRogueEpSetting(aci_cookie, credentials["apic_ip"],"enabled")

                elif subops1 == '3':
                    configureRogueEpSetting(aci_cookie, credentials["apic_ip"],"disabled")

              
        elif main_operation == '4':
            get_rogue_details_result = get_rogue_details(aci_cookie, credentials["apic_ip"])
            get_data = get_processed_data(get_rogue_details_result)
            sub_operations1_list = ['Exit',
                                    'Clear REPs from all affected nodes',
                                    'Monitor & clear specific REP from leafs after 10 seconds interval or ctrl-c to exit',
                                    'Clear manually specific REP from all affected nodes',
                                   ]    

            while True:
                for index,sub_menu_items in enumerate(sub_operations1_list,0):
                    print(f"{index}: {sub_menu_items}")

                subops1 = input('\nChoose number to select type of operation : ')
                if subops1 == '0':
                    break

                elif subops1 == '1':
                    for each in get_data:
                        print(each['node_id'] , each['mac'] )
                        response = clearRogueEp(aci_cookie,  credentials["apic_ip"],each['node_id'])
                        print(f"\n{response}\n")
                    print("\n")

                elif subops1 == '2':
                                          
                    while True:
                        try:
                            aci_cookie1 = get_aci_token(credentials["username"], credentials["password"], credentials["apic_ip"])
                            get_rogue_details_result = get_rogue_details(aci_cookie1, credentials["apic_ip"])
                            get_data = get_processed_data(get_rogue_details_result)
                            print(f"{datetime.now()} ===> Checking if FW MAC {FW_MAC1} and {FW_MAC2} addresss are REP")
                            for each in get_data:
                                if (FW_MAC1 in each['mac'] or  FW_MAC2 in each['mac']): 
                                    response = f"{datetime.now()} {each['node_id']} , {each['mac']} detected\n"
                                    print(response)
                                    response = clearRogueEp(aci_cookie1,  credentials["apic_ip"],each['node_id'])
                                    print(f"\n{response}\n")
                                    
                                    result = f"{datetime.now()} Cleared REP {each['mac']} \n"
                                    print(result)

                                    with open('rep_logs.txt','a') as file:
                                            file.write(str(response))
                                            file.write(result)
                                   
                            time.sleep(60)   # check every after 60 seconds
                        except KeyboardInterrupt:
                            print("closed live monitoring gracefully")
                            break
                            
                elif subops1 == '3':
                    for each in get_data:
                        if (FW_MAC1 in each['mac'] or  FW_MAC2 in each['mac']): 

                            print(each['node_id'] , each['mac'] )
                            response = clearRogueEp(aci_cookie,  credentials["apic_ip"],each['node_id'])
                            print(f"\n{response}\n")
                    print("\n")

        elif main_operation == '5':
            get_rogue_details_result = get_rogue_details(aci_cookie, credentials["apic_ip"])
            get_data = get_processed_data(get_rogue_details_result)
            save_to_csv(get_data)

if __name__ == '__main__':
    main()
          
