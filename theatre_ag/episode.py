class Episode(object):

    def __init__(self, clock, cast, directions):
        self.clock = clock
        self.cast = cast
        self.directions = directions

    def perform(self):
        self.cast.improvise(self.directions)
        self.clock.start()
        self.cast.start()
        self.clock.wait_for_last_tick()
