#!/usr/bin/env python
# plot histograms of battery age
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt


# NOTE May 20 2022:
# this script still relies on the existence of n4batts.csv
# consider factoring out the part of battery2kml that calls the SIS API
# and use that for input to this script as well?


# IMPORTANT NOTE: we use 'ondate' for now (Epoch start date) instead of install date
# This is because I had to adjust the install date of pre-2013 batteries to pass XML validation.
# (There were no N4 sites before 2013 - they were all TA - so some of the batteries were installed before the N4 even existed!!)
# For these batteries, the epoch on date is the actual date of install.
# (We could also parse the install year and month out of the serial number, but meh.)
# You can change this once all of the pre-2013 batteries have been replaced.
# In general it is more correct to use the installdate, but this works for now!
# (If we decided to start using epoch on dates to track when the batteries were purchased, rather than when they were installed, we'd definitely want to use install dates.)

from sisutils import loginSIS, getEquipmentInstallations, extractBatteryInfo


# Send request to SIS API and parse returned text
token = loginSIS()

requesttext = getEquipmentInstallations(token, category="Battery", netcode="N4", isactive="y", pagesize="10000", sort="ondate")

outfile = extractBatteryInfo(requesttext)

#df = pd.read_csv('n4batts.csv', dtype={'lookupcode':'str'})
df = pd.read_csv(outfile, dtype={'lookupcode':'str'})
df.sort_values(by='ondate')

#dateformat = "%Y-%m-%d (%j) %H:%M:%S" # format if using CSV downloaded from SIS search results page
dateformat = "%Y-%m-%dT%H:%M:%SZ" # format for results written from SIS API without applying any date formatting
df ['ondate'] = pd.to_datetime(df['ondate'], format=dateformat)


# Some simple plots:
# plot individual batteries
fig, ax = plt.subplots()
df['ondate'].groupby(df["ondate"].dt.year).count().plot(kind='bar', ax=ax)
ax.set_ylabel('# of batteries')
ax.set_xlabel('last battery swap')
plt.tight_layout()
fig.savefig('allbatts.png')
print('saved allbatts.png')

# group by station
df2 = df[['lookupcode', 'ondate']]
df3 = df2.drop_duplicates()

fig, ax = plt.subplots()
df3["ondate"].groupby(df3["ondate"].dt.year).count().plot(kind='bar', ax=ax)
ax.set_ylabel('# of stations')
ax.set_xlabel('last battery swap')
plt.tight_layout()
fig.savefig('n4batts_bystn.png')
print('saved n4batts_bystn.png')

# Make fancier plot: histogram showing year of last battery swap at each station
fig, ax = plt.subplots()


print('------')
year_now = dt.datetime.utcnow()
year_int = int(dt.datetime.utcnow().strftime("%Y"))
for install_year, battlist in df3.groupby(df3["ondate"].dt.year):
    print(battlist.reset_index(drop=True, inplace=True))
    print(install_year)
    color='black'
    for i in range(len(battlist)): 
        install_dt = battlist.iloc[i]['ondate']
        battery_age = year_now - battlist.iloc[i]['ondate']
        battery_age_yr = battery_age.days/365
        if battery_age_yr >= 7:
            color='red'
        elif battery_age_yr > 5 and battery_age_yr < 7:
            color='orange'
        else:
            color='green'
        ax.text(install_year, i, battlist.iloc[i]["lookupcode"], ha='center', va='bottom', color=color) 


min_year = df3['ondate'].min().year


# Average number of batteries needed to replace each year: between 20 and 30

ax.fill_between([min_year,year_int+1],[20,20],[30,30], color='grey', alpha=0.1)

ax.set_xlim(min_year-1,year_int+1)
ax.set_ylim(0,65)
ax.set_ylabel('# of stations')
ax.set_xlabel('last battery swap')
fig.set_size_inches(7,8)
plt.tight_layout()
fig.savefig('text.png')
print('saved text.png')
