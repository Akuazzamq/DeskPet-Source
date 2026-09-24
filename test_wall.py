import unittest
from unittest.mock import patch
from behavior import Behavior, WALL_STATES
from pet_engine import PetEngine


class WallTests(unittest.TestCase):
    def test_sequence_all_skins_both_walls(self):
        for skin in PetEngine().pets:
            for direction in (-1, 1):
                pet = PetEngine()
                pet.set_skin(skin)
                b = Behavior(pet, 0)
                b.taskbar = True
                b.now = 20
                with patch.object(b.rng, 'random', return_value=0):
                    self.assertTrue(b.start_wall(direction))
                seen = []
                heights = []
                for step in range(1, 201):
                    b.tick(20 + step * .05, 0)
                    if not seen or seen[-1] != pet.state:
                        seen.append(pet.state)
                    heights.append(pet.wall_height)
                    if pet.state not in WALL_STATES:
                        break
                self.assertEqual(seen.count('climbing'), 2)
                self.assertEqual(seen.count('angry'), 2)
                self.assertEqual(b.wall_attempt, 2)
                self.assertEqual(pet.facing, -direction)
                self.assertGreaterEqual(max(heights), 25)
                self.assertLessEqual(max(heights), 45)
                self.assertEqual(pet.wall_height, 0)
                self.assertFalse(b.start_wall(direction), 'Cooldown must block another attempt')

    def test_interruption_sleep_and_disabled_wander(self):
        for interrupt in ('happy', 'held', 'sleep', 'wander'):
            pet = PetEngine()
            b = Behavior(pet, 0)
            b.taskbar = True
            b.now = 20
            b.start_wall(1)
            b.tick(20.7, 0)
            b.tick(21.2, 0)
            self.assertGreater(pet.wall_height, 0)
            if interrupt == 'sleep':
                b.tick(21.3, 180)
                self.assertEqual(pet.state, 'drowsy')
            elif interrupt == 'wander':
                b.wander = False
                b.tick(21.3, 0)
            else:
                b.interact(interrupt, 0 if interrupt == 'held' else 1.2)
            self.assertNotIn(pet.state, WALL_STATES)
            self.assertEqual(pet.wall_height, 0)

if __name__ == '__main__':
    unittest.main()
