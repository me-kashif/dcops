#!/usr/bin/env python3.8

import datetime

from create_tenant  import main as tr
from get_ep_details import main as ep
from get_fault_details import main as fd
from get_faults_history import main as fh
from get_events_history import main as eh
from get_sfp_details import main as sd
from get_rogue_eps import main as re
from get_ep_static_bind import main as gesb
from get_audit_details import main as gad
from get_crc_errors import main as ce

def main():
    
    print('#'*50)
    print('Welcome to Data Center Operations Application')
    print('#'*50)
    print('\n')

    while True:

        print('1 : Endpoint related')
        print('2 : Faults related')
        print('3 : Events related')
        print('4 : Inventory related')
        print('5 : Rogue EP related')      
        print('6 : Tenants related')
        print('7 : Audit related')
        print('0 : Exit')
        main_operation = input('\nChoose number to select type of operation : ')

        if main_operation == '0':
            break
        if main_operation == '1':
            print('1 : Current Endpoints')
            print('2 : EPG static bindings')
            print('0 : Exit')

            ep_ops = input('\nChoose number to select type of operation : ')

            if ep_ops == '0':
                continue

            if ep_ops == '1':
                ep()

            if ep_ops == '2':
                gesb()
            

        if main_operation == '2':
            
            print('1 : Current Faults')
            print('2 : Faults History')
            print('3 : CRC Errors')
            print('0 : Exit')

            faults_ops = input('\nChoose number to select type of operation : ')

            if faults_ops == '0':
                continue

            if faults_ops == '1':
                fd()
            
            if faults_ops == '2':
                print("\n")
                regex = datetime.datetime.strptime
                try:
                    req_date = input("Enter required date to check faults history in this format yyyy-mm-dd : ")
                    assert regex(req_date,'%Y-%m-%d')
                except:
                    print("Incorrect date format , try again")
                    continue
            
                fh(req_date)
            if faults_ops == '3':
                         
                ce()

        if main_operation == '3':

            print('1 : Events History')
            
            print('0 : Exit')

            events_ops = input('\nChoose number to select type of operation : ')

            if events_ops == '0':
                continue

            if events_ops == '1':
                print("\n")
                regex = datetime.datetime.strptime
                try:
                    req_date = input("Enter required date to check faults history in this format yyyy-mm-dd : ")
                    assert regex(req_date,'%Y-%m-%d')
                except:
                    print("Incorrect date format , try again")
                    continue
            
                eh(req_date)
        
        if main_operation == '4':
            print('1 : All SFPs')
            
            print('0 : Exit')

            inventory_ops = input('\nChoose number to select type of operation : ')

            if inventory_ops == '0':
                continue
            
            if inventory_ops == '1':
                sd()
        
        if main_operation == '5':

            re()
        
        if main_operation == '6':

            tr()

        if main_operation == '7':

            print('1 : Audit ')
            
            print('0 : Exit')

            events_ops = input('\nChoose number to select type of operation : ')

            if events_ops == '0':
                continue

            if events_ops == '1':
                # print("\n")
                # regex = datetime.datetime.strptime
                # try:
                #     req_date = input("Enter required date to check faults history in this format yyyy-mm-dd : ")
                #     assert regex(req_date,'%Y-%m-%d')
                # except:
                #     print("Incorrect date format , try again")
                #     continue
            
                gad()
if __name__ == '__main__':
    main()
