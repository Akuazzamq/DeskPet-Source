import math
from special_actions import SpecialActions
import random
import time


WALL_STATES = {'wall_look', 'climbing', 'slipping', 'landing', 'angry'}


class Behavior:
    """One owner for transitions; no delayed callbacks from previous states."""
    def __init__(self, pet, now=None):
        self.pet = pet
        self.specials = SpecialActions()
        self.rng = random.Random()
        self.now = time.monotonic() if now is None else now
        self.until = 0
        self.next_action = self.now + 5
        self.next_blink = self.now + 3
        self.next_tail = self.now + 2
        self.tail_left = 0
        self.near_since = None
        self.direction = 1
        self.paused = False
        self.sleep_enabled = True
        self.wander = True
        self.wake_grace = 0
        self.taskbar = False
        self.next_walk = self.now + 2
        self.next_climb = self.now + 12
        self.wall_started = self.now
        self.wall_attempt = 0
        self.wall_retries = 0
        self.wall_peak = 35

    def enter(self, state, duration=0):
        self.pet.set_state(state)
        self.wall_started = self.now
        self.pet.wall_progress = 0
        if state == 'drowsy':
            self.pet.sleep_progress = 0.0
        if state not in WALL_STATES:
            self.pet.wall_height = 0
        self.until = self.now + duration if duration else 0
        self.pet.ear_twitch = False
        if state in ('sleeping', 'drowsy', 'held'):
            self.tail_left = 0

    def interact(self, state='happy', duration=1.2):
        self.wake_grace = self.now + 5
        self.enter(state, duration)

    def start_wall(self, direction):
        if not self.taskbar or not self.wander or self.paused or self.now < self.next_climb:
            return False
        self.pet.facing = direction
        self.wall_attempt = 1
        self.wall_retries = int(self.rng.random() < (.7 if self.pet.get_pet_type() == 'fox' else .3))
        self.wall_peak = self.rng.randint(25, 45)
        self.next_climb = self.now + self.rng.uniform(35, 60)
        self.enter('wall_look', .6)
        return True

    def tick_wall(self):
        state = self.pet.state
        elapsed = self.now - self.wall_started
        duration = max(.001, self.until - self.wall_started)
        self.pet.wall_progress = min(1, elapsed / duration)
        self.pet.walk_phase = int(elapsed * 16) % 8
        self.pet.idle_frame = int(elapsed * 9) % 2
        if state == 'climbing':
            self.pet.wall_height = round(self.wall_peak * (min(1, elapsed / 1.25) ** .8))
        elif state == 'slipping':
            self.pet.wall_height = round(self.wall_peak * max(0, 1 - (elapsed / .45) ** 2))
        else:
            self.pet.wall_height = 0
        if self.now < self.until:
            return
        if state == 'wall_look':
            self.enter('climbing', 1.25)
        elif state == 'climbing':
            self.pet.wall_height = self.wall_peak
            self.enter('slipping', .45)
        elif state == 'slipping':
            self.pet.wall_height = 0
            self.enter('landing', .25)
        elif state == 'landing':
            self.enter('angry', 1.1)
        elif self.wall_retries:
            self.wall_retries -= 1
            self.wall_attempt += 1
            self.enter('wall_look', .45)
        else:
            self.pet.facing *= -1
            self.enter('groom' if self.pet.get_pet_type() == 'cat' else 'idle',
                       .9 if self.pet.get_pet_type() == 'cat' else 0)
            self.next_walk = self.now + 1
            self.next_action = self.now + 4

    def tick(self, now, idle_seconds, near=False, direction=0):
        self.now = now
        if self.paused:
            self.specials.last = now
            return
        self.pet.taskbar_effects = self.taskbar and self.wander
        self.pet.effect_phase = now
        if self.pet.get_pet_type() in ('duck', 'penguin'):
            # Independent eight-frame clock also animates held and happy poses.
            self.pet.animation_phase = int(now * 8) % 8
        state = self.pet.state
        if state == 'held':
            return
        sleeping = state in ('drowsy', 'sleeping')
        if sleeping and (idle_seconds < 180 or not self.sleep_enabled):
            self.enter('stretch', 1.5)
        elif self.sleep_enabled and idle_seconds >= 180 and now >= self.wake_grace:
            if not sleeping:
                self.enter('drowsy', 3)
            elif state == 'drowsy' and now >= self.until:
                self.enter('sleeping')
            self.pet.sleep_progress = min(1, max(0, (now - self.wall_started) / 3)) if self.pet.state == 'drowsy' else 1.0
            self.pet.breath_phase = (now % 3.6) / 3.6 * 2 * math.pi
            self.pet.idle_frame = int(now / 1.2) % 2
            return
        if self.pet.state in WALL_STATES:
            if not self.taskbar or not self.wander:
                self.enter('idle')
            else:
                self.tick_wall()
                return
        if self.specials.tick(self, now):
            return
        if self.until and now >= self.until:
            finished_state = self.pet.state
            self.enter('idle')
            # A blink is a brief overlay, not an activity that needs another rest.
            if finished_state != 'blink':
                self.next_action = now + self.rng.uniform(5, 11)
        self.pet.idle_frame = int(now / .7) % 2
        state = self.pet.state
        if state in ('idle', 'curious', 'happy', 'groom', 'sniff', 'look', 'walking'):
            if now >= self.next_tail:
                if not self.tail_left:
                    self.tail_left = self.rng.choice((4, 6, 8))
                self.pet.next_tail_frame()
                self.tail_left -= 1
                self.next_tail = now + (self.rng.uniform(.18, .28) if self.tail_left else self.rng.uniform(2, 5))
        self.pet.ear_twitch = state == 'look' and int(now * 5) % 2 == 0
        if state not in ('idle', 'curious'):
            return
        if near:
            if self.near_since is None:
                self.near_since = now
            if now - self.near_since < (5 if self.pet.get_pet_type() == 'fox' else 3):
                self.enter('curious')
                self.pet.set_curiosity(direction)
            else:
                self.enter('idle')
        else:
            self.near_since = None
            self.enter('idle')
        if self.taskbar and self.wander and now >= self.next_walk:
            self.enter('walking', 3)
            self.next_walk = now + 3
        elif now >= self.next_action:
            choices = ['look', 'sniff', 'groom'] if self.pet.get_pet_type() == 'fox' else ['groom', 'groom', 'look']
            if self.pet.get_pet_type() == 'rabbit':
                choices = ['sniff', 'sniff', 'look', 'groom']
            elif self.pet.get_pet_type() == 'gorilla':
                choices = ['look', 'groom', 'happy']
            elif self.pet.get_pet_type() == 'dog':
                choices = ['sniff', 'look', 'happy', 'groom']
            if self.taskbar and self.wander:
                choices.append('walking')
            self.direction = self.rng.choice((-1, 1))
            self.enter(self.rng.choice(choices), self.rng.uniform(1.5, 3))
        elif now >= self.next_blink:
            self.enter('blink', .16)
            self.next_blink = now + self.rng.uniform(3, 6)
