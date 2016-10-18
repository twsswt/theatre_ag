import unittest

from theatre_ag import ManualClock

from threading import Thread


class ClockTestCase(unittest.TestCase):

    def setUp(self):
        self.clock = ManualClock()
        self.condition = False

    def test_set_alarm(self):

        def run_method():
            self.clock.set_alarm(1)
            self.condition = True

        thread = Thread(target=run_method)
        thread.start()
        self.assertEquals(False, self.condition)
        self.clock.tick()
        thread.join()
        self.assertEquals(True, self.condition)


if __name__ == '__main__':
    unittest.main()
