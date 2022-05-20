#!/usr/bin/env python
# plot histograms of battery age
import pandas as pd
import matplotlib.pyplot as plt


# IMPORTANT NOTE: we use 'ondate' for now (Epoch start date) instead of install date
# This is because I had to adjust the install date of pre-2013 batteries to pass XML validation.
# (There were no N4 sites before 2013 - they were all TA - so some of the batteries were installed before the N4 even existed!!)
# For these batteries, the epoch on date is the actual date of install.
# (We could also parse the install year and month out of the serial number, but meh.)
# You can change this once all of the pre-2013 batteries have been replaced.
# In general it is more correct to use the installdate, but this works for now!
# (If we decided to start using epoch on dates to track when the batteries were purchased, rather than when they were installed, we'd definitely want to use install dates.)

df = pd.read_csv('n4batts.csv', dtype={'lookupcode':'str'})
#df = pd.read_csv('all_asl_batts.csv', dtype={'lookupcode':'str'})
df.sort_values(by='ondate')
df ['ondate'] = pd.to_datetime(df['ondate'], format='%Y-%m-%d (%j) %H:%M:%S')


# plot individual batteries
fig, ax = plt.subplots()
df['ondate'].groupby(df["ondate"].dt.year).count().plot(kind='bar', ax=ax)
ax.set_ylabel('# of batteries')
ax.set_xlabel('last battery swap')
plt.tight_layout()
fig.savefig('allbatts.png')

# group by station
df2 = df[['lookupcode', 'ondate']]
df3 = df2.drop_duplicates()

fig, ax = plt.subplots()
df3["ondate"].groupby(df3["ondate"].dt.year).count().plot(kind='bar', ax=ax)
ax.set_ylabel('# of stations')
ax.set_xlabel('last battery swap')
plt.tight_layout()
fig.savefig('n4batts_bystn.png')

fig, ax = plt.subplots()


print('------')
for f in df3.groupby(df3["ondate"].dt.year):
    print(f[1].reset_index(drop=True, inplace=True))
    print(f[0])
    color='black'
    yr=2022
    for i in range(len(f[1])): 
        if f[0] <= yr-7:
            color='red'
        elif f[0] < yr-5 and f[0] > yr-7:
            color='orange'
        else:
            color='green'
        ax.text(f[0], i, f[1].iloc[i]["lookupcode"], ha='center', va='bottom', color=color) 
#        print(ax.text(f[0], i, f[1].iloc[i]["lookupcode"])) 

ax.fill_between([2008,2023],[20,20],[30,30], color='grey', alpha=0.5)

ax.set_xlim(2008,2023)
#ax.set_ylim(0,35)
#ax.set_ylim(0,45)
ax.set_ylim(0,65)
ax.set_ylabel('# of stations')
ax.set_xlabel('last battery swap')
fig.set_size_inches(7,8)
plt.tight_layout()
fig.savefig('text.png')



for i,s in enumerate(df['lookupcode'].drop_duplicates()[:]): 
    print(i,s) 


