#!/usr/bin/env python
# make KML of battery ages
# To get data:
# search Current Equipment in SIS, 
# Equipment Category: Battery
# Is Currently Installed: Yes
# in columns to display: add Epoch On Date
# sort by Epoch On Date
# download CSV file
# link below may work, but no guarantees
#https://anss-sis.scsn.org/sis/equipment/current/?catgids=31&istemplate=0&operatorids=1&isinstalled=1&o1=ondate&o1ad=a&o2ad=a&o3ad=a&o4ad=a&o5ad=a&displaycols=category&displaycols=manufacturer&displaycols=modelname&displaycols=serialnumber&displaycols=ondate&displaycols=inventory&displaycols=operatorcode&displaycols=project&displaycols=ownercode&displaycols=propertytag&displaycols=epochnotes&displaycols=isinstalled&displaycols=netcode&displaycols=lookupcode&displaycols=monname



from fastkml import kml
from fastkml import styles

import pandas as pd

import datetime as dt

import time



#kml_file = 'small_network_example.kml'
kml_file = 'N4_2020-09.kml'
#kml_file = 'US_2020-09.kml'
#kml_file = 'N4_2021-01.kml'
myfile = open(kml_file, 'r')
kmldoc = myfile.read()
k = kml.KML()
#k.from_string(kmldoc)
k.from_string(kmldoc.encode('utf-8'))



k_new = kml.KML()
doc_new = kml.Document()
k_new.append(doc_new)
f_new = kml.Folder(name='BattsOK')
doc_new.append(f_new)
f_old = kml.Folder(name='BattsOld')
doc_new.append(f_old)


features = list(k.features())
doc = features[0]

donut = 'http://maps.google.com/mapfiles/kml/shapes/donut.png'
#icon = styles.IconStyle(scale=5, color='7f0080ff', icon_href=donut) 
#newstyle = styles.Style(id='orange', styles=[icon])
#doc.append_style(newstyle)

# failed attempt at making one BalloonStyle for all
# I think this fails bc the original KML already has balloon styles defined
# I think I could get around this by creating new elements instead of modifying existing ones
# but for now we'll just edit the BalloonStyle already present for each station
# ns=None, id=None, bgColor=None, textColor=None, text=None, displayMode=None
#balloon_text = "<a href='https://anss-sis.scsn.org/sis/sites/monepoch/latest/?lookupcode_q=$[station]'>SIS</a><br> \
#               <a href='https://igskgacgvmweb01.cr.usgs.gov/rt/Search/Results.html?Query=%28+Subject+LIKE+%27$[station]%27+%29+AND+%28++Status+%3D+%27open%27+OR+Status+%3D+%27new%27+OR+Status+%3D+%27stalled%27+%29'>RT Tickets - Unresolved</a><br>"
#balloonstyle = styles.BalloonStyle(textColor='ff000000', text=balloon_text, displayMode="default")

color_dict = {'red': '7f0000ff',
              'orange': '7f0080ff', 
              'yellow': '7f00ffff',
              'green': '7f00ff00',
              'purple': '7fff00ff',
              'white': '7fffffff'}
for stylename, color in color_dict.items():
    icon = styles.IconStyle(scale=2, color=color, icon_href=donut) 
    newstyle = styles.Style(id=stylename, styles=[icon])
#    newstyle = styles.Style(id=stylename, styles=[icon, balloonstyle])
#    line = styles.LineStyle(color=color, width=2)
#    poly = styles.PolyStyle(color=color)
#    newstyle = styles.Style(id=stylename, styles=[icon, label, poly, line])
    doc_new.append_style(newstyle)



#doc.name='N4_battery_age'
netname = kml_file.split('_')[0]
doc.name=f'{netname}_battery_age'

for i in doc.features():

    print(i)


df = pd.read_csv('n4batts.csv', dtype={'lookupcode':'str'})
#df = pd.read_csv('all_asl_batts.csv', dtype={'lookupcode':'str'})
#df ['ondate'] = pd.to_datetime(df['ondate'], format='%Y-%m-%d (%j) %H:%M:%S') # format for CSV downloaded from SIS search results page
df ['ondate'] = pd.to_datetime(df['ondate'], format='%Y-%m-%dT%H:%M:%SZ') # format for results from SIS API without applying any date formatting
df.sort_values(by='ondate')

logfile = open('noinfo.txt', 'w')


label = styles.LabelStyle(scale=0.5, color='white')



for j in i.features():
    print(j.name)
    net = j.name.split('.')[0]
    sta = j.name.split('.')[1]
    df1 = df[df['lookupcode'] == sta]
    print(df1)
    print(len(df1))


    ext_data = kml.Data(name='station', value=sta) 
    ext_dat2 = kml.Data(name='network', value=net) 
    j.extended_data = kml.ExtendedData(elements=[ext_data, ext_dat2])

    if len(df1) == 0:
        logfile.write(j.name + '\n')
        battery_age_yr = 999
    else:
        battery_age = dt.datetime.utcnow() - df1['ondate'].drop_duplicates().iloc[0]
        battery_age_yr = battery_age.days/365

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
    j.description = f'Battery age: {battery_age_yr:.1f} yr'
    for style in j.styles():
        for s in style.styles():
#            print(s)
##            s.text = f"Battery age: {battery_age_yr:.1f} yr <br> <br> <a href='https://anss-sis.scsn.org/sis/sites/monepoch/latest/?lookupcode_q=$[station]'>SIS</a><br> <br> <a href='https://igskgacgvmweb01.cr.usgs.gov/rt/Search/Simple.html?q=$[station]'>RT Tickets</a><br> <br> <a href='https://igskgacgvmweb01.cr.usgs.gov/rt/Search/Results.html?Format=%27%3Cb%3E%3Ca+href%3D%22__WebPath__%2FTicket%2FDisplay.html%3Fid%3D__id__%22%3E__id__%3C%2Fa%3E%3C%2Fb%3E%2FTITLE%3A%23%27%2C%0A%27%3Cb%3E%3Ca+href%3D%22__WebPath__%2FTicket%2FDisplay.html%3Fid%3D__id__%22%3E__Subject__%3C%2Fa%3E%3C%2Fb%3E%2FTITLE%3ASubject%27%2C%0AStatus%2C%0AQueueName%2C%0AOwner%2C%0APriority%2C%0A%27__NEWLINE__%27%2C%0A%27__NBSP__%27%2C%0A%27%3Csmall%3E__Requestors__%3C%2Fsmall%3E%27%2C%0A%27__Created__%27%2C%0A%27%3Csmall%3E__CreatedRelative__%3C%2Fsmall%3E%27%2C%0A%27%3Csmall%3E__LastUpdatedRelative__%3C%2Fsmall%3E%27&Order=DESC%7CASC%7CASC%7CASC&OrderBy=LastUpdated%7C%7C%7C&Page=&Query=%28+Subject+LIKE+%27$[station]%27+%29+AND+%28++Status+%3D+%27open%27+OR+Status+%3D+%27new%27+OR+Status+%3D+%27stalled%27+%29&RowsPerPage=50&SavedChartSearchId=new&SavedSearchId='>RT Tickets - Unresolved</a><br>"

                      # <a href='https://anss-sis.scsn.org/sis/sites/monepoch/latest/?lookupcode_q=$[station]'>SIS</a><br> \
            s.text = f"Battery age: {battery_age_yr:.1f} yr <br>  \
                      <a href='https://anss-sis.scsn.org/sis/find/?lookup=$[station]'>SIS</a><br> \
                      <a href='https://igskgacgvmweb01.gs.doi.net/rt/Search/Results.html?Query=%28+Subject+LIKE+%27$[station]%27+%29+AND+%28++Status+%3D+%27open%27+OR+Status+%3D+%27new%27+OR+Status+%3D+%27stalled%27+%29'>RT Tickets - Unresolved</a><br> \
                      <a href='https://igskgacgvmweb01.gs.doi.net/rt/Search/Simple.html?q=$[station]'>RT Tickets - All</a><br> "
# N drive (not there yet...)
# example for a local file
#                      <a href='file:///Users/ewolin/Downloads/wolin_ridgecrest_cablefix.jpg'>N Drive</a><br>"

# all RT tickets (simple search by station):
#             

#    j.extended_data = 'hello'
#print(k.to_string(prettyprint=True))
        j._styles[0].append_style(label)

    if j.visibility == 0:
        f_new.append(j)
    else:
        f_old.append(j)

outfile = open(f'{doc.name}.kml', 'w')
#outfile.write(k.to_string(prettyprint=True))
outfile.write(k_new.to_string(prettyprint=True))
outfile.close()
print(f"wrote {doc.name}.kml")
