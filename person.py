import numpy as np

class Person:
    '''A circle which represents a person in the simulation.'''
    radius = 1 # Static variable, since every circle should have the same radius. Default is 1.
    def __init__(self, pos, vel, health = 'healthy', radius = 1, quarantined=False):
        self._pos = np.array(pos)
        self._vel = np.array(vel)
        if health == 'healthy' or health == 'sick' or health == 'recovered':
            self._health = health
        else:
            raise RuntimeError('A Person.health can only be \'healthy\', \'sick\', or \'recovered\'.')
        self.time_spent_sick = 0
        self.radius = radius
        self._quarantined = quarantined
        if quarantined:
            self._vel = np.array([0.0, 0.0])

    @property
    def pos(self):
        return self._pos
    @pos.setter
    def pos(self, pos):
        self._pos = np.array(pos)
    
    @property
    def vel(self):
        return self._vel
    @vel.setter
    def vel(self, vel):
        self._vel = np.array(vel)
        if self._quarantined:
            self._vel = np.array([0.0, 0.0])

    @property
    def speed(self):
        return np.linalg.norm(self._vel)

    @property
    def health(self):
        return self._health
    @health.setter
    def health(self, health):
        if health == 'healthy' or health == 'sick' or health == 'recovered':
            self._health = health
        else:
            raise RuntimeError('A Person.health can only be \'healthy\', \'sick\', or \'recovered\'.')

    @property
    def quarantined(self):
        return self._quarantined
    @quarantined.setter
    def quarantined(self, quarantined):
        self._quarantined = quarantined
        if quarantined:
            self.vel = [0.0, 0.0]