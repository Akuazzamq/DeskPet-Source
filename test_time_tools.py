import unittest
from time_tools import TimeTools
from behavior import Behavior
from pet_engine import PetEngine


class TimeTests(unittest.TestCase):
    def setUp(self):
        self.now = 0
        self.tools = TimeTools(lambda: self.now)

    def test_timer_pause_resume_completion_once(self):
        t = self.tools
        t.start_timer(60)
        self.now = 20
        t.toggle_timer()
        self.assertEqual(t.remaining, 40)
        self.now = 100
        self.assertFalse(t.tick())
        t.toggle_timer()
        self.now = 139.5
        self.assertEqual(t.display()[1], '00:00:01')
        self.now = 141
        self.assertTrue(t.tick())
        self.assertFalse(t.tick())
        self.assertEqual(t.display(), ('TIME UP', '00:00:00'))
        t.reset_timer()
        self.assertEqual(t.remaining, 60)
        self.assertFalse(t.finished)

    def test_clocks_run_independently_of_display(self):
        t = self.tools
        t.start_timer(60)
        t.toggle_stopwatch()
        self.now = 10
        t.toggle_stopwatch()
        self.now = 30
        self.assertEqual(t.stopwatch_seconds(), 10)
        t.toggle_stopwatch()
        t.mode = 'clock'
        self.now = 65
        self.assertTrue(t.tick())
        self.assertEqual(t.stopwatch_seconds(), 45)
        t.reset_stopwatch()
        self.assertEqual(t.stopwatch_seconds(), 0)

    def test_desktop_never_selects_walking(self):
        for skin in PetEngine().pets:
            b = Behavior(PetEngine(), 0)
            b.pet.set_skin(skin)
            b.rng.seed(42)
            for step in range(12000):
                b.tick(step * .05, 0)
                self.assertNotEqual(b.pet.state, 'walking')

if __name__ == '__main__':
    unittest.main()
