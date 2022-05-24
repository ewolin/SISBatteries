#!/usr/bin/env python

import json
import requests
import configparser

from io import StringIO

def loginSIS():
   #############
    # Read config file with login info
    config = configparser.ConfigParser()
    config.read('config.ini')
    un =  config['RT']['user']
    pw =  config['RT']['pwd']
    payload = {'username': un,   
               'password': pw,}   # do not save this in the file, read it from a protected config file. 
    #############
    
    #############
    # Log into SIS
    sisinstance = 'sis' # will be "sis" in case of production 
    baseurl = 'https://anss-sis.scsn.org/{0}'.format(sisinstance)
    loginurl = '{0}/api/v1/token/auth'.format(baseurl)
    print(loginurl)
    r = requests.post(loginurl, data=payload)#, verify=False)
    r.raise_for_status()    # Check if response is valid. Handle error
    #print ('response:', r.json())
    token = r.json()['token']
    #print ('token:', token)
    ############# 
    return(token)


def getEquipmentInstallations(token, category="Battery", netcode="*", isactive="y", pagesize="10000", sort="ondate"):
    #############
    # Build and send request
    # Set the token in the request header
    sisinstance = 'sis' # will be "sis" in case of production 
    baseurl = 'https://anss-sis.scsn.org/{0}'.format(sisinstance)
    auth_header = {"Authorization": "Bearer {0}".format(token),}
    params = {
        "category": category,
        "netcode": netcode,
        "isactive": isactive,
        "page[size]": pagesize,
        "sort": sort
    }
    
    # Send request to a SIS webservice endpoint.
    url = '{0}/api/v1/equipment-installations'.format(baseurl)
    r = requests.get(url, headers=auth_header, params=params, verify=False)
    r.raise_for_status()
    print ('\n', r.text)
    return(r.text)
#############

def extractBatteryInfo(requesttext):
    #############
    # Parse returned text, then
    # loop over returned text to create a table of battery serial number, net and station code, and installation date
    j = json.loads(requesttext)
    
    #outfile = open('n4batts.csv', 'w')
    outfile = StringIO()
    outfile.write('serialnumber,netcode,lookupcode,ondate\n')
    for one_install in j['data']:
        for equip in j['included']: 
            if equip['type'] == 'Equipment' and equip['id'] == one_install['relationships']['equipment']['data']['id']: 
                e = equip
        for site in j['included']: 
            if site['type'] == 'SiteEpoch' and site['id'] == one_install['relationships']['siteepoch']['data']['id']: 
                s = site
        print(e['attributes']['serialnumber'], s['attributes']['netcode'], s['attributes']['lookupcode'], one_install['attributes']['ondate'])
        outfile.write(f"{e['attributes']['serialnumber']},{s['attributes']['netcode']},{s['attributes']['lookupcode']},{one_install['attributes']['ondate']}\n")
    outfile.seek(0)
    return outfile
    #############

