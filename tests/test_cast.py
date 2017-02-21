import unittest

from mock import Mock

from theatre_ag import SynchronizingClock, Cast


class TeamTestCase(unittest.TestCase):

    def setUp(self):

        self.clock = Mock(spec=SynchronizingClock)

        self.tdd_development_team = Cast(self.clock)

    def test_add_member(self):
        self.tdd_development_team.add_member('alice')

        self.assertEqual(1, len(self.tdd_development_team.members))


if __name__ == '__main__':
    unittest.main()
