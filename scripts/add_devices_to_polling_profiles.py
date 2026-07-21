### Copyright 2020
### Riverbed Technology, inc
### This is an example of adding devices to polling profiles
### Devices and profiles should be specified in the add_devices_to_polling_profile.txt file in the format
### "sysname","profile name"

# This script can be run directly and accepts one optional parameter to set the base URL and port
# https://<base_url:port>/api/netim/v1/polling-profiles
# https://<base_url:port>/api/netim/v1/devices

'''
Usage: 
python3 add_devices_to_polling_profiles.py
python3 add_devices_to_polling_profiles.py https://10.46.250.62:8543
'''

import sys
from utils import utils

test_output = False

def add_to_polling_profiles(base_url, polling_profile_sysname_map, session, test=False):
    polling_profiles_url = base_url + "/api/netim/v1/polling-profiles"
    sysname_to_access_id_map = utils.get_device_access_id_map(base_url, session)
    utils.add_devices_to_profiles(polling_profiles_url, polling_profile_sysname_map, sysname_to_access_id_map, session, test)

def main():
    base_url = utils.get_base_url(sys.argv)
    session = utils.get_session()
    
    polling_profile_sysname_map = utils.read_map_from_file("ExampleInput/add_devices_to_polling_profiles.txt")
    add_to_polling_profiles(base_url, polling_profile_sysname_map, session, test_output)
    
    session.close()

if __name__ == '__main__':
    main()