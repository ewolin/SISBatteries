# SISBatteries
Get battery info from SIS; make a KML and some plots to help with maintenance planning.

Users should download kml/N4BatteryAge_link.kml and open it in Google Earth.  This KML will sync with the linked file on a specified interval.

Running the code requires a SIS login and a Python environment with [fastkml](https://fastkml.readthedocs.io/en/latest/) installed.  I like to use conda for this.

The battery2kml.py script uses the SIS API to retrieve battery info. 

To supply your SIS login credentials: Create a copy of config.ini.example named config.ini. Enter your SIS username and password. This file will be read by battery2kml.py.

Battery info from SIS is added to the KML to produce an interactive map: 
![screenshot from Google Earth showing battery status KML](ExampleFiles/battery_map_example.jpg)



To-do: Update battplot.py to use the same call to the API!!  Right now it still relies on the existence of n4batts.csv.

battplot.py reads the same CSV and plots batteries by the year they were installed.
![histogram of year N4 batteries were installed](https://github.com/ewolin/SISBatteries/blob/main/ExampleFiles/text.png)




Old way of obtaining CSV file - obsolete now that the API request is working:

To get data:
 - search Current Equipment in SIS, 
 - Equipment Category: Battery
 - Is Currently Installed: Yes
 - in columns to display: add Epoch On Date
 - sort by Epoch On Date
 - download CSV file
 
 [SIS equipment search for N4 batteries, sorted by install date](https://anss-sis.scsn.org/sis/equipment/current/?page=4&catgids=31&istemplate=0&operatorids=1&isinstalled=1&netids=41&displaycols=category&displaycols=manufacturer&displaycols=modelname&displaycols=serialnumber&displaycols=ondate&displaycols=inventory&displaycols=operatorcode&displaycols=project&displaycols=ownercode&displaycols=propertytag&displaycols=epochnotes&displaycols=isinstalled&displaycols=netcode&displaycols=lookupcode&displaycols=monname&displaycols=installdate&o1=installdate&o1ad=a&o2=&o2ad=a&o3=&o3ad=a&o4=&o4ad=a&o5=&o5ad=a)
 
[another older link I had been using](https://anss-sis.scsn.org/sis/equipment/current/?catgids=31&istemplate=0&operatorids=1&isinstalled=1&o1=ondate&o1ad=a&o2ad=a&o3ad=a&o4ad=a&o5ad=a&displaycols=category&displaycols=manufacturer&displaycols=modelname&displaycols=serialnumber&displaycols=ondate&displaycols=inventory&displaycols=operatorcode&displaycols=project&displaycols=ownercode&displaycols=propertytag&displaycols=epochnotes&displaycols=isinstalled&displaycols=netcode&displaycols=lookupcode&displaycols=monname)
