from mock import Mock
from unittest import TestCase

from threading import Thread

from theatre_ag import Actor, AbstractClock


class ActorTestCase(TestCase):

    def setUp(self):

        self.clock = Mock(spec=AbstractClock)

        self.actor = Actor("alice", self.clock, person_time=2)

    def test_idle(self):

        self.actor.idle()
        self.clock.current_tick = 0
        self.actor.start()
        self.actor.shutdown()


        self.assertEquals(1, self.actor.person_time)

