#!/usr/bin/env python3.8

import datetime

from get_ep_details import main as ep
from get_fault_details import main as fd
from get_faults_history import main as fh
from get_events_history import main as eh
from get_sfp_details import main as sd
from get_rogue_eps import main as re

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
        print('0 : Exit')
        main_operation = input('\nChoose number to select type of operation : ')

        if main_operation == '0':
            break
        if main_operation == '1':
            
            ep()

        if main_operation == '2':
            
            print('1 : Current Faults')
            print('2 : Faults History')
            print('0 : Exit')

            faults_ops = input('\nChoose number to select type of operation : ')

            if faults_ops == '0':
                break

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

        if main_operation == '3':

            print('1 : Events History')
            
            print('0 : Exit')

            events_ops = input('\nChoose number to select type of operation : ')

            if events_ops == '0':
                break

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
                break
            
            if inventory_ops == '1':
                sd()
        
        if main_operation == '5':

            print('1 : Get Rogue EPs')
            
            print('0 : Exit')

            rogue_ops = input('\nChoose number to select type of operation : ')

            if rogue_ops == '0':
                break
            
            if rogue_ops == '1':
                re()
if __name__ == '__main__':
    main()
