from person import Person
from sim import Sim
import os
import pandas as pd
from matplotlib.text import Text
import matplotlib.pyplot as plt
from matplotlib import animation
import sys

if len(sys.argv) > 1:
    os.chdir(sys.argv[1])

skip = 1
rad = 0.01
ls = os.listdir('states')
dfs = []
for fname in ls:
    if fname[:10] == 'sim_person':
        dfs.append(pd.read_csv('states/' + fname))
healths = [df['health'] for df in dfs]
colors = {'healthy': (0.0, 0.0, 1.0, 1), 'sick': (1.0, 0.0, 0.0, 1),
          'recovered': (0.0, 1.0, 0.0, 1), 'dead': (0.0, 0.0, 0.0, 0)}
n_frames = 0
for df in dfs:
    if len(df.index) > n_frames:
        n_frames = len(df.index)
n_frames = int(n_frames/skip)
fig = plt.figure()
fig.set_dpi(400)
fig.set_size_inches((9,6))
ax = fig.add_axes([0,0,0.75,1])
ax.xlim = (0,1)
ax.ylim = (0,1)
ax.tick_params(axis='both', which='both', bottom=False, top=False, left=False, right=False, labelbottom=False, labelleft=False)
patches = [plt.Circle((-10,-10),rad,fc='w') for i in dfs]
for patch in patches:
    ax.add_patch(patch)
text_healthy = plt.text(1.01,0.95,'Healthy:    ',fontsize=12,color=colors['healthy'])
text_sick = plt.text(1.01,0.9,'Sick:           ',fontsize=12,color=colors['sick'])
text_recovered = plt.text(1.01,0.85,'Recovered:  ',fontsize=12,color=colors['recovered'])
text_dead = plt.text(1.01,0.8,'Dead:       ',fontsize=12,color='k')
def update(t):
    num_dead = 0
    num_healthy = 0
    num_sick = 0
    num_recovered = 0
    for ind, patch in enumerate(patches):
        if t > len(dfs[ind].index) - 1:
            patch.set_fc(colors['dead'])
            patch.set_edgecolor(colors['dead'])
        if t < len(dfs[ind].index):
            patch.center = dfs[ind].iloc[t,1:3]
            patch.set_color(colors[dfs[ind].health.iloc[t]])
        if patch.get_fc() == colors['healthy']:
            num_healthy += 1
        elif patch.get_fc() == colors['sick']:
            num_sick += 1
        elif patch.get_fc() == colors['recovered']:
            num_recovered += 1
        elif patch.get_fc() == colors['dead']:
            num_dead += 1
    text_healthy.set_text('Healthy:   %i' % num_healthy)
    text_sick.set_text('Sick:          %i' % num_sick)
    text_recovered.set_text('Recovered: %i' % num_recovered)
    text_dead.set_text('Dead:      %i' % num_dead)
    return patches + [text_healthy, text_sick, text_recovered, text_dead]
anim = animation.FuncAnimation(fig, update, frames=n_frames, interval=1, blit=True)
anim.save('movie.mp4',fps=60,dpi=400)