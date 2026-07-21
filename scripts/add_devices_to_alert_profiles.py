### Copyright 2020
### Riverbed Technology, inc
### This is an example of retrieving all devices, reading in a map of sysname to alert profile name, and adding those devices to the profile
### Profile names and sysnames are read from add_devices_to_alert_profile.txt

# This script can be run directly and accepts one optional parameter to set the base URL and port
# Resources used:
# https://<base_url:port>/api/netim/v1/devices
# https://<base_url:port>/api/netim/v1/alert-profiles

'''
Usage: 
python3 add_devices_to_alert_profiles.py
python3 add_devices_to_alert_profiles.py https://10.46.250.62:8543
'''

import sys
from utils import utils

test_output = False

def add_to_alert_profiles(base_url, alert_profile_sysname_map, session, test=False):
    alert_profiles_url = base_url + "/api/netim/v1/alert-profiles"
    sysname_to_access_id_map = utils.get_device_access_id_map(base_url, session)
    utils.add_devices_to_profiles(alert_profiles_url, alert_profile_sysname_map, sysname_to_access_id_map, session, test)

def main():
    base_url = utils.get_base_url(sys.argv)
    session = utils.get_session()
    
    alert_profile_sysname_map = utils.read_map_from_file("ExampleInput/add_devices_to_alert_profiles.txt")
    add_to_alert_profiles(base_url, alert_profile_sysname_map, session, test_output)
    
    session.close()

if __name__ == '__main__':
    main()