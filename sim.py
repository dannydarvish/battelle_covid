from person import Person
from barrier import Barrier
import numpy as np
from numpy import arccos, array, dot, pi, cross
from numpy.linalg import norm
from numpy.random import rand
import os
class Sim:
    '''The main class for the simulation.'''
    def __init__(self, walls, people, extra_barriers = None, name = None,
                 transm_prob = 1, death_rate = 0.1, recovery_time = 2):
        x1, x2, y1, y2 = walls
        self._barriers = 4*[None]
        self._barriers[0] = Barrier(np.array([x1, y1]), np.array([x1, y2]))
        self._barriers[1] = Barrier(np.array([x1, y2]), np.array([x2, y2]))
        self._barriers[2] = Barrier(np.array([x2, y2]), np.array([x2, y1]))
        self._barriers[3] = Barrier(np.array([x2, y1]), np.array([x1, y1]))
        self._people = people
        for person in people:
            assert(people[0].radius == person.radius)
        max_speed = 0
        for person in people:
            speed = norm(person.vel)
            if speed > max_speed:
                max_speed = speed
        self._delta_t = 0.5 * people[0].radius / max_speed
        self._transmission_prob = transm_prob
        self._death_rate = death_rate
        self._recovery_time = recovery_time
        self._total_healthy = 0
        self._total_sick = 0
        self._total_dead = 0
        self._total_recovered = 0
        self._R = 0
        for person in people:
            if person.health == 'healthy':
                self._total_healthy += 1
            elif person.health == 'sick':
                self._total_sick += 1
            elif person.health == 'recovered':
                self._total_sick += 1
        self._name = name
        self._time = 0
        if name is not None:
            if not os.path.isdir(name):
                try:
                    os.mkdir(name)
                except(FileNotFoundError):
                    os.makedirs(name, exist_ok=True)
            os.chdir(name)
        if not os.path.isdir('states'):
            os.mkdir('states')
        self._files = [open('states/sim_person_%i.csv' % i, 'w') for i in range(len(people))]
        self._files.append(open('states/stats.csv', 'w'))
        for f in self._files[:-1]:
            f.write('time,x,y,health,num_infected\n')
        self._files[-1].write('time,healthy,sick,recovered,dead,R\n')

    def proceed(self, n_steps = 1):
        for _ in range(n_steps):
            # Advance everything forward in time
            for person in self._people:
                if person.health == 'sick':
                    person.time_spent_sick += self._delta_t
            self.recover()
            for person in self._people:
                person.pos = person.pos + person.vel * self._delta_t
            kill_list = []
            for i, person_i in enumerate(self._people):
                for j, person_j in enumerate(self._people):
                    if i <= j:
                        continue
                    delta_r = person_i.pos - person_j.pos
                    # Double check that they are indeed moving toward each other
                    if delta_r @ delta_r < (person_i.radius + person_j.radius)**2 and \
                        (person_j.vel - person_i.vel) @ (person_j.pos - person_i.pos) < 0:
                        self.collide_people(person_i, person_j)
                        if person_i.health == 'sick' and person_j.health == 'healthy' and \
                            i not in kill_list and j not in kill_list:
                            if rand() < self._transmission_prob:
                                person_i.num_infected += 1
                                if rand() < self._death_rate:
                                    kill_list.append(j)
                                    self._total_healthy -= 1
                                    self._total_dead += 1
                                else:
                                    person_j.health = 'sick'
                                    self._total_sick += 1
                                    self._total_healthy -= 1
                        if person_i.health == 'healthy' and person_j.health == 'sick' and \
                            i not in kill_list and j not in kill_list:
                            if rand() < self._transmission_prob:
                                person_j.num_infected += 1
                                if rand() < self._death_rate:
                                    kill_list.append(i)
                                    self._total_healthy -= 1
                                    self._total_dead += 1
                                else:
                                    person_i.health = 'sick'
                                    self._total_sick += 1
                                    self._total_healthy -= 1
            self._people = np.delete(self._people, kill_list)
            for i in sorted(kill_list, reverse=True):
                self._files[i].close
                del self._files[i]
            
            for person in self._people:
                for barrier in self._barriers:
                    collision, nearest = self.detect_barrier_collision(person, barrier)
                    if collision:
                        self.collide_with_barrier(person, barrier, nearest)
            # Update R
            self._R = 0.0
            for person in self._people:
                self._R += person.num_infected
            self._R /= len(self._people)
            self._time += self._delta_t
    def write_state_to_file(self, dir=None):
        # Write current stats to file
        self._files[-1].write('%f,%d,%d,%d,%d,%d\n' %
                              (self._time, self._total_healthy, self._total_sick, 
                               self._total_recovered, self._total_dead, self._R))
        for ind, person in enumerate(self._people):
            self._files[ind].write('%f,%f,%f,%s,%d\n' %
                                   (self._time, person.pos[0], person.pos[1], person.health, person.num_infected))
        
    def collide_people(self, person1, person2):
        # In this special case of equal masses, we just swap the velocities.
        # For non-zero radius, this is strictly incorrect, but
        # the approximation speeds things up by reducing the need for
        # another projection.
        if person1.quarantined:
            person2.vel *= -1
        elif person2.quarantined:
            person1.vel *= -1
        else:
            v_temp = person1.vel
            person1.vel = person2.vel
            person2.vel = v_temp
    
    def collide_with_barrier(self, person, barrier, nearest):
        perp_hat = (nearest - person.pos)/np.linalg.norm(nearest - person.pos)
        v_perp = person.vel @ perp_hat * perp_hat
        person.vel -= 2*v_perp
        
    def detect_barrier_collision(self, person, barrier):
        # adapted from: https://gist.github.com/nim65s/5e9902cd67f094ce65b0
        A = barrier.start
        B = barrier.end
        P = person.pos
        if all(A == P) or all(B == P):
            dist = 0
        elif arccos(dot((P - A) / norm(P - A), (B - A) / norm(B - A))) > pi / 2:
            dist = norm(P - A)
            nearest = A
        elif arccos(dot((P - B) / norm(P - B), (A - B) / norm(A - B))) > pi / 2:
            dist = norm(P - B)
            nearest = B
        else:
            dist = norm(cross(A-B, A-P))/norm(B-A)
            nearest = B + (A-B)*((P-B)@(A-B)/((A-B)@(A-B)))
        if dist < person.radius:
            # ensure that the person is actually moving away from the barrier
            if (nearest - P) @ person.vel > 0:
                return True, nearest
        return False, nearest

    def recover(self):
        for person in self._people:
            if person.health == 'sick':
                if person.time_spent_sick > self._recovery_time:
                    person.health = 'recovered'
                    self._total_sick -= 1
                    self._total_recovered += 1
    
    def end(self):
        for f in self._files:
            f.close()

    @property
    def people(self):
        return self._people

    @property
    def time(self):
        return self._time
    
    @property
    def total_healthy(self):
        return self._total_healthy
    
    @property
    def total_sick(self):
        return self._total_sick

    @property
    def total_recovered(self):
        return self._total_recovered

    @property
    def total_dead(self):
        return self._total_dead
