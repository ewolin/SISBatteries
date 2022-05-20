#!/usr/bin/env python
# make KML of battery ages




from fastkml import kml
from fastkml import styles

import pandas as pd

import datetime as dt

import time
import json
import configparser
import requests
#from cryptography.fernet import Fernet


#def load_key():
#    """
#    Loads the key from the current directory named `key.key`
#    """
#    return open("key.key", "rb").read()


#authfile = open('sisauth.txt', 'rb')
#enc = authfile.read()
#authfile.close()
#
#key = load_key()
#print(key)
#f = Fernet(key)

#dec = f.decrypt(enc).decode().split()
#un = dec[0]
#pw = dec[1]

config = configparser.ConfigParser()
config.read('config.ini')
un =  config['RT']['user']
pw =  config['RT']['pwd']


payload = {'username': un,   
           'password': pw,}   # do not save this in the file, read it from a protected config file. 
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

#############
# Create and send request
# Set the token in the request header
auth_header = {"Authorization": "Bearer {0}".format(token),}

params = {
    "category": 'Battery',
#    "netcode":"US,NE,N4,IW",
    "netcode":"N4",
    "isactive":"y",
    "page[size]":10000,
    "sort":"ondate"
}

# Send request to a SIS webservice endpoint.
url = '{0}/api/v1/equipment-installations'.format(baseurl)
r = requests.get(url, headers=auth_header, params=params, verify=False)
r.raise_for_status()
print ('\n', r.text)
#############

#############
# Parse returned text, then
# loop over returned text to create a table of battery serial number, net and station code, and installation date
# maybe we could write this to a StringIO like object instead of to disk? can figure out later, this works for now
j = json.loads(r.text)

outfile = open('n4batts.csv', 'w')
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
outfile.close()
#############

#############
# Read KML file containing list of N4 stations
# did we have to edit this header like we did for the RT kml? don't remember.
kml_file = 'kml/N4_2020-09.kml'
myfile = open(kml_file, 'r')
kmldoc = myfile.read()
k = kml.KML()
k.from_string(kmldoc.encode('utf-8'))
features = list(k.features())
doc = features[0]
for i in doc.features(): # there should only be one Feature at this level - a Folder object, which in turn contains all of the station Features
    print(i)
#############


#############
# Create new KML document containing 2 subfolders
k_new = kml.KML()
doc_new = kml.Document()
k_new.append(doc_new)
f_new = kml.Folder(name='BattsOK')
doc_new.append(f_new)
f_old = kml.Folder(name='BattsOld')
doc_new.append(f_old)
netname = kml_file.split('_')[0]
doc_new.name=f'kml/N4_battery_age'
#############



#############
# Define styles: use an open circle (donut) so it works nicely with solid circles from RT KML
donut = 'http://maps.google.com/mapfiles/kml/shapes/donut.png'
color_dict = {'red': '7f0000ff',
              'orange': '7f0080ff', 
              'yellow': '7f00ffff',
              'green': '7f00ff00',
              'purple': '7fff00ff',
              'white': '7fffffff'}
for stylename, color in color_dict.items():
    icon = styles.IconStyle(scale=2, color=color, icon_href=donut) 
    newstyle = styles.Style(id=stylename, styles=[icon])
    doc_new.append_style(newstyle)
label = styles.LabelStyle(scale=0.5, color='white')
#############


#############
# Read list of battery info obtained from API (or, in previous versions, from CSV downloaded from SIS)
# Loop over features in KML, write info to pop-up balloon, and apply color scheme based on age

df = pd.read_csv('n4batts.csv', dtype={'lookupcode':'str'})
#dateformat = "%Y-%m-%d (%j) %H:%M:%S" # format if using CSV downloaded from SIS search results page
dateformat = "%Y-%m-%dT%H:%M:%SZ" # format for results written from SIS API without applying any date formatting
df ['ondate'] = pd.to_datetime(df['ondate'], format=dateformat)
df.sort_values(by='ondate')

# the one Folder in our KML contains a Feature for each station
for j in i.features():
    print(j.name)
    net = j.name.split('.')[0]
    sta = j.name.split('.')[1]
    df1 = df[df['lookupcode'] == sta]
    print(df1)
    print(len(df1))


# Some N4 sites were adopted by other agencies or universities, but continue running under the N4 net code.
# For these sites, we may not have battery info.  
# Color them white on the map and label appropriately.
    if len(df1) == 0:
        battery_age_yr = 999
        install_date = 'Unknown'
    else:
        battery_age = dt.datetime.utcnow() - df1['ondate'].drop_duplicates().iloc[0]
        battery_age_yr = battery_age.days/365
        install_date = df1['ondate'].drop_duplicates().iloc[0].strftime("%Y-%m-%d")

    if battery_age_yr > 900:
        color='white'
        j.styleUrl = 'white'
    elif battery_age_yr >= 7 and battery_age_yr < 900:
        color='red'
        j.styleUrl = 'red'
    elif battery_age_yr > 5 and battery_age_yr < 7:
        color='orange'
        j.styleUrl = 'orange'
    else:
        color='green'
        j.styleUrl = 'green'
        j.visibility = 0
    print(j.styleUrl, battery_age_yr)

    j.description = f"Battery age: {battery_age_yr:.1f} yr"
    for style in j.styles():
        for s in style.styles():
            s.text = f"<h2> {net}.{sta}</h2> \
                      Battery age: {battery_age_yr:.1f} yr <br>  \
                      Batteries installed: {install_date} <br> \
                      <a href='https://anss-sis.scsn.org/sis/find/?lookup={sta}'>SIS page for {net} {sta}</a><br> "
            s.text += f"<table width =\"200\"><tr><h2> </h2></tr>"
            s.text += "</table>"

# N drive: this works for Macs, but not sure how to make it Windows-compatible yet, so I won't write it out to the file. 
# example for a local file
#            s.text += f"<a href='file:///Volumes/aslcommon/Station Documents/N4_network/N4 Site Info/{sta}'>N4.{sta} on N Drive</a><br>"
#            s.text += "hint: if file browser window does not open, right-click and select Copy Link, then open in Finder, Windows Explorer, or a web browser<br>" 

        j._styles[0].append_style(label)

# Make old batteries (orange/red) visible by default; hide new batteries (green).
    if j.visibility == 0:
        f_new.append(j)
    else:
        f_old.append(j)
#############

#############
# Write new KML file and we're done!
outfile = open(f'{doc_new.name}.kml', 'w')
outfile.write(k_new.to_string(prettyprint=True))
outfile.close()
print(f"wrote {doc_new.name}.kml")
