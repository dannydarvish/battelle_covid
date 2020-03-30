import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import sys
from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
## for Palatino and other serif fonts use:
#rc('font',**{'family':'serif','serif':['Palatino']})
rc('text', usetex=True)

if len(sys.argv) > 1:
    os.chdir(sys.argv[1])

peaks = []
# start by just plotting number infected vs time
# plot one for each quarantine rate
qrs = ['0.0', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8']
for qr in qrs:
    df = pd.read_csv('tp0.5_dr0.05_rt2_qr%s_n196/0/states/stats.csv' % qr)
    peaks.append(df.sick.max())
    plt.plot(df.time, df.sick, label=r'$F_q=$' + qr)
    leg =plt.legend()
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.ylabel(r'\rm{Number sick}', fontsize=16)
    plt.xlabel(r'\rm{Time}', fontsize=16)
    for lh in leg.legendHandles:
        lh._legmarker.set_markersize(5)
    plt.xlim((0,12))
    plt.ylim((0,196))
    plt.savefig('plots/curves/qr%s.png' % qr, bbox_inches='tight', dpi=400)
plt.clf()
plt.plot([float(f) for f in qrs], peaks, '.')
plt.ylabel(r'\rm{Peak number sick}')
plt.xlabel(r'$F_q$')
plt.savefig('plots/peaks.png', bbox_inches='tight', dpi=400)
# plot total deaths vs death rate for a fixed quarantine rate
drs = ['0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.625', '0.65', '0.675', '0.7', '0.8']
n_dead = []
for dr in drs:
    df = pd.read_csv('tp1.0_dr%s_rt0.5_qr0.0_n196/states/stats.csv' % dr)
    n_dead.append(df.dead.iloc[-1])
plt.clf()
plt.plot([float(f) for f in drs], n_dead, '.')
plt.ylabel(r'\rm{Total fatalities}', fontsize=16) 
plt.xlabel(r'\rm{Case fatality rate}', fontsize=16)
plt.savefig('plots/total_deaths.png', dpi=400)
# plot total deaths vs. quarantine rate for a fixed death rate