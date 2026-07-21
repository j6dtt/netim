### Copyright 2020
### Riverbed Technology, inc
### Utility functions used across the sample NetIM REST API usage examples

import sys
import urllib3
import requests
from requests.auth import HTTPBasicAuth
import json
import datetime

def get_all_devices(base_url, session):
    resource_url = base_url + "/api/netim/v1/devices"
    devices_json = get_complete_json_from_resource(resource_url, session)
    return devices_json

def get_all_device_interfaces(base_url, session, device_id):
    resource_url = base_url + "/api/netim/v1/devices/" + device_id + "/interfaces"
    device_interfaces_json = get_complete_json_from_resource(resource_url, session)
    return device_interfaces_json

def get_all_groups(base_url, session):
    resource_url = base_url + "/api/netim/v1/groups"
    groups_json = get_complete_json_from_resource(resource_url, session)
    return groups_json    

def get_all_monitoredpaths(base_url, session):
    resource_url = base_url + "/api/netim/v1/monitored-paths"
    paths_json = get_complete_json_from_resource(resource_url, session)
    return paths_json
    
def get_all_tests(base_url, session):
    resource_url = base_url + "/api/netim/v1/tests"
    tests_json = get_complete_json_from_resource(resource_url, session)
    return tests_json

def get_all_alert_profiles(base_url, session):
    resource_url = base_url + "/api/netim/v1/alert-profiles"
    profiles_json = get_complete_json_from_resource(resource_url, session)
    return profiles_json
    
def get_all_polling_profiles(base_url, session):
    resource_url = base_url + "/api/netim/v1/polling-profiles"
    profiles_json = get_complete_json_from_resource(resource_url, session)
    return profiles_json
    
def get_complete_json_from_resource(resource_url, session):
    json_dict = get_initial_json_from_resource(resource_url, session)
        
    if "meta" in json_dict:
        total = json_dict["meta"]["total"]
        next_offset = json_dict["meta"]["next_offset"]
        limit = json_dict["meta"]["limit"]
        while next_offset < total:
            json_dict_next_page = get_json_from_resource_page(resource_url, limit, next_offset, session)
            total_items = json_dict["items"]
            total_items.extend(json_dict_next_page["items"])
            json_dict["items"] = total_items
            
            #Total usually won't change, but there could be an edge case where a device is removed or added while we're still paging
            total = json_dict_next_page["meta"]["total"]
            next_offset = json_dict_next_page["meta"]["next_offset"]
            limit = json_dict_next_page["meta"]["limit"]
            json_dict["meta"] = json_dict_next_page["meta"]
    return json_dict

def get_json_from_resource(resource_url, session):
    json_dict = {}
    try:
        resp = session.get(resource_url, verify=False)
        # The response object is a conditional that evaluates to true for a successful response
        # but that includes codes in the 300 range. We shouldn't be getting redirected so
        # we're limiting the valid responses to the 200 range.
        if resp is not None: 
            if resp.status_code >= 200 and resp.status_code < 300:
                resp_text = resp.text
                json_dict = json.loads(resp_text)
            else:
                print(f"Unable to retrieve resource. Status code: {resp.status_code}")
        else:
            print(f"Unable to retrieve resource from URL: {resource_url}")
    except:
        print(f"Exception getting data from: {resource_url}")
    return json_dict

def get_initial_json_from_resource(resource_url, session):
    json_dict = get_json_from_resource(resource_url, session)
    return json_dict

def get_json_from_resource_page(resource_url, limit, offset, session):
    final_url = resource_url + "?limit=" + str(limit)+ "&offset=" + str(offset)
    json_dict = get_json_from_resource(final_url, session)
    return json_dict
    
def get_object_id_map(json_dict, id_property_name, name_attr1, name_attr2=None):
    obj_name_to_id_dict = dict()
    if (json_dict == None or 
        (name_attr1 == None and name_attr2 == None)):
        return obj_name_to_id_dict

    try:
        item_list = json_dict['items']
    except KeyError:
        return obj_name_to_id_dict  

    for item in item_list:
        try:
            netim_object_name = item[name_attr1]
        except:
            if (name_attr2 != None):
                netim_object_name = item[name_attr2]

        object_id = item[id_property_name]
        obj_name_to_id_dict[netim_object_name] = object_id
        
    return obj_name_to_id_dict

def get_anpname_id_map(base_url, session):
    json_dict = get_all_monitoredpaths(base_url, session)

    return get_object_id_map(json_dict, "id", 'name')

def get_testname_id_map(base_url, session):
    json_dict = get_all_tests(base_url, session)

    return get_object_id_map(json_dict, "id", 'name')

def get_groupname_id_map(base_url, session):
    json_dict = get_all_groups(base_url, session)

    return get_object_id_map(json_dict, "id", 'name')

def get_alert_profile_name_id_map(base_url, session):
    json_dict = get_all_alert_profiles(base_url, session)

    return get_object_id_map(json_dict, "id", 'name')

def get_device_interface_id_name_map(base_url, session, device_id):
    json_dict = get_all_device_interfaces(base_url, session, device_id)

    return get_object_id_map(json_dict, "name", 'id')

# Use the devices resource to generate a map from sys name to device id
def get_sysname_device_id_map(base_url, session):
    # https://localhost:8543/api/netim/v1/devices/
    json_dict = get_all_devices(base_url, session)

    return get_object_id_map(json_dict, "id", 'sysName', 'deviceName')
    
def get_device_access_id_map(base_url, session):
    # https://localhost:8543/api/netim/v1/devices/
    json_dict = get_all_devices(base_url, session)

    return get_object_id_map(json_dict, "deviceAccessInfoId", 'sysName', 'deviceName')

def get_session(username="admin", password="admin"):
    session = requests.session()
    headers = {'Content-type': 'application/json'}
    
    # For basic authentication you should provide the log in information to the session
    session.auth = HTTPBasicAuth(username, password)
    session.headers.update(headers)
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    return session
    
def get_base_url(argv):
    base_url = "https://localhost:8543"
    if len(argv) > 1:
        base_url = argv[1]
    return base_url
    
# Applies an operation to the mapped profiles and devices.
# Valid operations are "addDeviceAccessInfoIds" or "removeDeviceAccessInfoIds"
def patch_profiles(url, profile_json_dict, profile_sysname_map, sysname_to_access_id_map, operation, session, test):
    item_list = profile_json_dict['items']
    if test:
        print(f"Profile to device map: {str(profile_sysname_map)}")
    for item in item_list:

        profile_name = item["name"]
        if profile_name not in profile_sysname_map:
            continue

        if test:
            print("processing item: ", item)

        device_sysnames = profile_sysname_map[profile_name]
        device_access_info_ids = list()
        for device_sysname in device_sysnames:
            try:
                device_access_info_id = sysname_to_access_id_map[device_sysname]
                device_access_info_ids.append(device_access_info_id)
            except:
                continue
        if len(device_access_info_ids) == 0:
            continue
            
        profile_to_set = {
            "name" : profile_name, 
            "displayName": item["displayName"],
            "id": item["id"],
            operation: device_access_info_ids
        }
        
        profile_url = url + "/" + str(item["id"])
        if test:
            print(f"{str(datetime.datetime.now())}: Dry run of patch on {profile_url} with parameters {json.dumps(profile_to_set)}")
        else:
            resp = session.patch(profile_url, verify=False, data=json.dumps(profile_to_set))
            # The response object is a conditional that evaluates to true for a successful response
            # but that includes codes in the 300 range. We shouldn't be getting redirected so
            # we're limiting the valid responses to the 200 range.
            if resp is not None: 
                if resp.status_code < 200 or resp.status_code > 300:
                    print(f"Unable to patch profile {profile_url}. Status code: {resp.status_code}")
            else:
                print(f"Unable to patch profile {profile_url}. No response from server.")

def add_devices_to_profiles(url, profile_sysname_map, sysname_to_access_id_map, session, test):
    json_dict = get_initial_json_from_resource(url, session)
    patch_profiles(url, json_dict, profile_sysname_map, sysname_to_access_id_map, "addDeviceAccessInfoIds", session, test)
    if "meta" in json_dict:
        total = json_dict["meta"]["total"]
        next_offset = json_dict["meta"]["next_offset"]
        limit = json_dict["meta"]["limit"]
        while next_offset != total:
            json_dict = get_json_from_resource_page(url, limit, next_offset, session)
            patch_profiles(url, json_dict, profile_sysname_map, sysname_to_access_id_map, "addDeviceAccessInfoIds", session, test)
    
def remove_devices_from_profiles(url, profile_sysname_map, sysname_to_access_id_map, session, test):
    json_dict = get_initial_json_from_resource(url, session)
    patch_profiles(url, json_dict, profile_sysname_map, sysname_to_access_id_map, "removeDeviceAccessInfoIds", session, test)
    if "meta" in json_dict:
        total = json_dict["meta"]["total"]
        next_offset = json_dict["meta"]["next_offset"]
        limit = json_dict["meta"]["limit"]
        while next_offset != total:
            json_dict = get_json_from_resource_page(url, limit, next_offset, session)
            patch_profiles(url, json_dict, profile_sysname_map, sysname_to_access_id_map, "removeDeviceAccessInfoIds", session, test)

def read_list_from_file(file_path):
    fhandle = open(file_path)
    element_list = []
    for line in fhandle:
        stripped_line = line.strip()
        if stripped_line.startswith("#") or len(stripped_line) == 0 or line.isspace():
            continue
        else:
            element_list.append(stripped_line)
        
    fhandle.close()
    return element_list
    
# Reads a two column csv file and maps properties in the first column to the second column
# Example:
'''
device_name1,profile name1
device_name2,profile name1
device_name3,profile name2
'''
# The above would generate a dictionary mapping "profile name 1" to a list with device_name1 and device_name2
# and mapping "profile name2" to a list with device_name3.
def read_map_from_file(file_path):
    map = dict()
    with open(file_path) as flat_file:
        for line in flat_file:
            if line.startswith("#") or len(line) == 0 or line.isspace():
                continue
            line_list = line.strip().replace('"','').split(',')
            if line_list[1] in map:
                map[line_list[1]].append(line_list[0])
            else:
                map[line_list[1]] = [line_list[0]]
    return map

def write_metric_data_to_file(alerts_by_object_dict, filename):
    pretty_print_json_str = json.dumps(alerts_by_object_dict, indent=4)
    file_handle = open(filename, 'w+')
    file_handle.write(pretty_print_json_str)

import functools
def report_time_taken(func):
    from timeit import default_timer as timer

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = timer()
        result = func(*args, **kwargs)
        stop = timer()
        print(f"Time in function {func.__name__}: {stop - start}")
        return result
    return wrapper

def debug(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k,v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print(f"Calling {func.__name__}({signature})")
        result = func(*args, **kwargs)
        print(f"{func.__name__!r} returned {result!r}")
        return result
    return wrapper

def main():
    print("This library contains functions to access NetIM apis, read text files mapping devices to profiles, create a session to a NetIM, ...")

if __name__ == '__main__':
    main()