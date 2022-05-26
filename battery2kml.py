#!/usr/bin/env python
# Use SIS API to get info on N4 battery installations
# make KML showing battery ages

import time
import json
import requests
import configparser


from fastkml import kml
from fastkml import styles
from io import StringIO

import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt



from sisutils import loginSIS, getEquipmentInstallations, extractBatteryInfo


# Send request to SIS API and parse returned text
token = loginSIS()

requesttext = getEquipmentInstallations(token, category="Battery", netcode="N4", isactive="y", pagesize="10000", sort="ondate")

outfile = extractBatteryInfo(requesttext)




#############
# Read KML file containing list of N4 stations
# did we have to edit this header like we did for the RT kml? don't remember.
# shouldn't need to change the list of N4 sites - unlikely we will add or close any in the near future.
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

#df = pd.read_csv('n4batts.csv', dtype={'lookupcode':'str'})

df = pd.read_csv(outfile, dtype={'lookupcode':'str'})
outfile.close()
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

# Write info to text balloon and create link to SIS page for station
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

# Create image file - legend
# for image overlay
fig, ax = plt.subplots(figsize=(1.5,1))
ax.text(0.2,0.8, 'Battery Age', color='black', transform=ax.transAxes, va='center', weight='bold')
labels = ['≤5 years old', '5-7 years old', '≥7 years old' ]
colors = ['green', 'orange', 'red']
n = 1
for label, color in zip(labels, colors):
    y = n * 0.2
    ax.text(0.3,y, label, color=color, transform=ax.transAxes, va='center')
    ax.plot(0.15,y,marker='o',markersize=10,mfc=color, transform=ax.transAxes, mec='lightgray') 
    ax.plot(0.15,y,marker='o',markersize=5,mfc='white', mec='lightgray', transform=ax.transAxes) 
    n += 1
ax.set_axis_off()
fig.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
fig.savefig('kml/legend.png')

#############
# Write new KML file 
outfile = open(f'{doc_new.name}.kml', 'w')
# As of May 2022, the fastkml library does not support creating or writing ScreenOverlay objects
# so to include a legend, we'll just insert the appropriate xml string
# right before the end of the Document...
# modified from https://developers.google.com/kml/documentation/kmlreference?csw=1#screenoverlay
#outfile.write(k_new.to_string(prettyprint=True))
outstring = k_new.to_string(prettyprint=True)
start, end = outstring.split("</Document>")
overlay_string = '''
<ScreenOverlay id="ScreenOverlay001">
	<name>Legend</name>
	<Icon>
	<href>legend.png</href>
	</Icon>
	<overlayXY x="0" y="1" xunits="fraction" yunits="fraction"/>
	<screenXY x="0" y="1" xunits="fraction" yunits="fraction"/>
	<rotation>0</rotation>
	<size x="0" y="0" xunits="pixels" yunits="pixels"/>
</ScreenOverlay> '''
start += (overlay_string)
start += ("\n</Document>\n</kml>\n")
outfile.write(start)


outfile.close()
print(f"wrote {doc_new.name}.kml")
