"""Monotonic clocks, independent of pet animation and menu event loops."""
import math
import time


class TimeTools:
    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.mode = 'clock'
        self.duration = 25 * 60
        self.remaining = float(self.duration)
        self.deadline = None
        self.finished = False
        self.elapsed = 0.0
        self.started = None

    def start_timer(self, seconds):
        if seconds <= 0:
            raise ValueError('Timer duration must be positive')
        self.mode = 'timer'
        self.duration = int(seconds)
        self.remaining = float(seconds)
        self.deadline = self.clock() + seconds
        self.finished = False

    def tick(self):
        if self.deadline is not None:
            self.remaining = max(0, self.deadline - self.clock())
            if self.remaining == 0:
                self.deadline = None
                self.finished = True
                return True
        return False

    def toggle_timer(self):
        self.tick()
        if self.finished:
            return
        if self.deadline is None:
            self.deadline = self.clock() + self.remaining
        else:
            self.deadline = None

    def reset_timer(self):
        self.deadline = None
        self.remaining = float(self.duration)
        self.finished = False

    def toggle_stopwatch(self):
        self.mode = 'stopwatch'
        if self.started is None:
            self.started = self.clock()
        else:
            self.elapsed += self.clock() - self.started
            self.started = None

    def reset_stopwatch(self):
        self.elapsed = 0.0
        self.started = None

    def stopwatch_seconds(self):
        return self.elapsed + (self.clock() - self.started if self.started is not None else 0)

    @staticmethod
    def format_seconds(seconds):
        seconds = max(0, int(seconds))
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        return f'{hours:02}:{minutes:02}:{seconds:02}'

    def display(self):
        if self.mode == 'timer':
            remaining = max(0, self.deadline - self.clock()) if self.deadline is not None else self.remaining
            label = 'TIME UP' if self.finished else 'TIMER' if self.deadline is not None else 'TIMER PAUSED'
            return label, self.format_seconds(math.ceil(remaining))
        return ('STOPWATCH' if self.started is not None else 'STOPWATCH PAUSED',
                self.format_seconds(self.stopwatch_seconds()))
