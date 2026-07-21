### Copyright 2020
### Riverbed Technology, inc
### Get group alert data for given groups

### This script uses ExampleInput/group_alert_request_input.txt

### group_alert_request_input.txt ###
### grpname

# Resources used:
# /swarm/NETIM_NETWORK_METRIC_DATA_SERVICE/api/v1/network-metric-data
# /api/netim/v1/groups/
# /api/netim/v1/alert-profiles

'''
Usage: 
python3 get_top_n_metrics.py https://10.46.250.62:8543 INTERFACE IFC_ERRORS InPackets top 1000 1000
python3 get_top_n_metrics.py https://10.23.25.62:8543 DEVICE CPU_UTIL cpuUtil bottom 200 100 devices_with_least_cpu_util.json
'''

import sys
import urllib3
import requests
from requests.auth import HTTPBasicAuth
import json
import time
from utils import utils
from utils import metric_data_utils
import random

def get_topn_metric_data(session, resource_url, obj_type, metric_class, metric_field, top_bottom, top_bottom_n, limit):
    
    # obtain topn metrics per day for the last week
    days = [0, 1, 2, 3, 4, 5, 6]
    day_in_msecs = 24*60*60*1000

    resp_dict = {}
    for day in days:
        print(f"Obtaining topn metrics for {'current day' if day == 0 else 'yesterday' if day == 1 else str(day)+ ' days back'}")
        
        endTime = int(time.time()*1000) - day * day_in_msecs
        startTime = endTime - (day+1) * day_in_msecs
        
        topn_metric_request_data = {
            "searchType" : "topbottomn", 
            "type" : obj_type, 
            "startTime" : startTime, 
            "endTime" : endTime,
            "metricClass" : metric_class,
            "metric" : metric_field,
            "top" : top_bottom.strip().lower() == 'top',
            "n" : top_bottom_n,
            "timeWindowAlgo" : "avg",
            "limit": limit,
            "offset": 0,
            "pageSize": limit,
            "legacy": False,
        }

        resp_dict[day] = perform_objects_resource_get_op(session, resource_url, topn_metric_request_data)

    return resp_dict

@utils.report_time_taken
def perform_objects_resource_get_op(session, resource_url, topn_metric_request_data):
    # https://localhost:8543/api/netim/v1/objects
    resp = session.get(resource_url, verify=False, params=topn_metric_request_data)
    return resp

def process_topn_metric_data(resource_url, resp_dict):

    json_dict = {}
    for (day, resp) in resp_dict.items():
        key = 'current day' if day == 0 else 'yesterday' if day == 1 else str(day)+ ' days back'
        if resp is not None: 
            if resp.status_code >= 200 and resp.status_code < 300:
                json_dict[key] = json.loads(resp.text)
            else:
                print(f"Unable to retrieve resource. Status code: {resp.status_code}")
        else:
            print(f"Unable to retrieve resource from URL: {resource_url}")

    return json_dict


def usage():
    '''
    Usage: python3 get_top_n_metrics.py [netim_url] [obj_type] [metric_class] [metric_field] [top|bottom] [topn] [limit]
    '''
    print("Usage: python3 get_top_n_metrics.py netim_url obj_type metric_class metric_field top|bottom topn limit [output_filename]")
    print()
    print("For instance:")
    print("python3 get_top_n_metrics.py https://10.23.25.62:8543 INTERFACE IFC_ERRORS InPackets top 1000 1000")
    print("\twrites top n metric obtained to ExampleOutput/topn_metric_data_example_output.txt")
    print("python3 get_top_n_metrics.py https://10.23.25.62:8543 DEVICE CPU_UTIL cpuUtil bottom 200 100 devices_with_least_cpu_util.txt")
    print("\twrites top n metric obtained to devices_with_least_cpu_util.txt (in current directory)")
    return

def main():
    '''
    Usage: python3 get_top_n_metrics.py [netim_url] [obj_type] [metric_class] [metric_field] [top|bottom] [topn] [limit] [output_filename]
    '''

    if len(sys.argv) <= 7:
        usage()
        return

    base_url, obj_type, metric_class, metric_field, top_bottom, top_bottom_n, limit = sys.argv[1:8]
    
    # https://localhost:8543/api/netim/v1/objects
    resource_url = base_url + "/api/netim/v1/objects"
    
    session = utils.get_session()
    
    resp_dict = get_topn_metric_data(session, resource_url, obj_type, metric_class, 
        metric_field, top_bottom, top_bottom_n, limit)
    topn_metric_dict = process_topn_metric_data(resource_url, resp_dict) 

    outfilepath = sys.argv[8] if len(sys.argv) > 8 else "ExampleOutput/topn_metric_data_example_output.txt"

    utils.write_metric_data_to_file(topn_metric_dict, outfilepath)
    
    session.close()

if __name__ == '__main__':
    main()