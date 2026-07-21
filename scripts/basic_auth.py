### Copyright 2020
### Riverbed Technology, inc

# This is an example of basic authentication
# This script will log in to NetIM core, retrieve up to 100 devices, then output 
# the device data to the basic_auth_example_output.txt file in the current working directory. 

# For an example of GET calls with batching see get_devices.py
# This script can be run directly and accepts one optional parameter to set the base URL and port
# Uses the following resource:
# https://localhost:8543/api/netim/v1/devices

'''
Usage: 
python3 basic_auth.py
python3 basic_auth.py https://10.46.250.62:8543
'''

import sys
import urllib3
import requests
from requests.auth import HTTPBasicAuth
from utils import utils

def main():
    session = requests.session()
    headers = {'Content-type': 'application/json'}
    
    # For basic authentication you should provide the log in information to the session
    session.auth = HTTPBasicAuth("admin", "admin")
    session.headers.update(headers)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    base_url = "https://localhost:8543"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    # Update session headers with cookie from login url
    resp = session.get(base_url+"/api/netim/v1/rpc/login", verify=False)

    file_handle = open('ExampleOutput/basic_auth_example_output.txt', 'w+')
    file_handle.write(str(resp.headers))
    
    session.close()

if __name__ == '__main__':
    main()