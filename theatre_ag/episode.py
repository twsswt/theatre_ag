"""
@author twsswt
"""

class Episode(object):
    """
    An aggregation of the artifacts necessary (clock, cast and directions) to perform a simulation.
    """

    def __init__(self, clock, cast, directions):
        self.clock = clock
        self.cast = cast
        self.directions = directions

    def perform(self):
        self.cast.improvise(self.directions)
        self.clock.start()
        self.cast.start()
        self.clock.wait_for_last_tick()
