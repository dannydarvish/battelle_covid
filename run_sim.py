from person import Person
from sim import Sim
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import animation
from tqdm import tqdm
from numpy.random import rand
import sys

try:
    name = sys.argv[1]
    transm_prob = float(sys.argv[2])
    dr = float(sys.argv[3])
    rt = float(sys.argv[4])
    if len(sys.argv) > 5:
        quarantine_rate = float(sys.argv[5])
    else:
        quarantine_rate = None
    if len(sys.argv) > 6:
        print_ = True
    else:
        print_ = False
except(IndexError):
    sys.exit('Usage: python run_sym.py name transm_prob death_rate recovery_time quarantine_rate')

people = []
for i in range(14):
    for j in range(14):
        pos = [1.0/15 * i + 1.0/15, 1.0/15 * j + 1.0/15]
        theta = 2*np.pi*np.random.rand()
        vel = [np.cos(theta), np.sin(theta)]
        rad = 0.01
        person = Person(pos, vel, radius = rad)
        people.append(person)
people[0].health = 'sick'
if quarantine_rate is not None:
    for ind, person in enumerate(people):
        if rand() < quarantine_rate and ind != 0:
            person.quarantined = True
sim = Sim([0,1,0,1], people, name=sys.argv[1], transm_prob=transm_prob,
          death_rate=dr, recovery_time=rt)

sim.write_state_to_file('states')
skip = 1
while sim.total_sick > 0:
    sim.proceed(skip)
    sim.write_state_to_file('states')
    if print_:
        print(sim.total_sick)
sim.end()
