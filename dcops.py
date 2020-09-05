#!/usr/bin/env python3.8

from get_ep_details4 import main as ep
from get_fault_details_v2 import main as fd

def main():
    
    print('#'*50)
    print('Welcome to Data Center Operations Application')
    print('#'*50)
    print('\n')

    while True:

        print('1 : Endpoint related')
        print('2 : Faults details')
        print('0 : Exit')
        main_operation = input('\nChoose number to select type of operation : ')

        if main_operation == '0':
            break
        if main_operation == '1':
            
            ep()

        if main_operation == '2':
            
            fd()
            

if __name__ == '__main__':
    main()
