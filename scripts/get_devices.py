### Copyright 2020
### Riverbed Technology, inc
### This is an example of retrieving all devices in batches and writing them to a file

# This script can be called directly and does not use any parameters
# Resource used:
# https://localhost:8543/api/netim/v1/devices

'''
Usage: 
python3 get_devices.py
python3 get_devices.py https://10.46.250.62:8543
'''

import sys
from utils import utils
import json

def get_all_devices(base_url, session):
    return utils.get_all_devices(base_url, session)

def write_devices_to_file(url, filename, session):
    with open(filename,'w+',encoding = 'utf-8') as file_handle:
        # https://localhost:8543/api/netim/v1/devices/
        json_dict = get_all_devices(url, session)
        file_handle.write(json.dumps(json_dict, indent=4))

def main():
    base_url = utils.get_base_url(sys.argv)
    session = utils.get_session()
    
    write_devices_to_file(base_url, "ExampleOutput/get_devices_example_output.txt", session)
    
    session.close()

if __name__ == '__main__':
    main()