import numpy as np
import time
from PIL import Image

from . import fringes, projector

# Daniel Weston
# 15/12/2025
# psydw2@nottingham.ac.uk

class Program:
    def __init__(self, proj: projector.OSDisplayProjector):
        # Use second display handle as default (not primary)
        self.proj = proj

        self.p_index = None
        self.loop = None
        self.pattern_time = None
        self.patterns = None

    def run(self, patterns, loop=False, pattern_time=1.0):
        self.p_index = 0
        self.loop = loop
        self.pattern_time = pattern_time

        self.patterns = patterns

        # We can show the fringes on the projector
        self.proj.add_frame_callback(self.on_frame_update)
        self.proj.show()

    def on_frame_update(self, last_update):
        now = time.time_ns()

        # # #
        # Could take camera picture here, would be synchronised with projector
        # # #

        if (last_update is None) or (now - last_update) >= (self.pattern_time * 1e9):
            # Check if not looping finished
            if (self.p_index == len(self.patterns)) and (not self.loop):
                self.proj.finished = True
                return

            # Project the fringe pattern
            self.proj.set_img(self.patterns[self.p_index])

            self.p_index = (self.p_index + 1) % len(self.patterns)

    @staticmethod
    def save_image(img, path):
        img = Image.fromarray(fringes.to_uint8(img))
        img.save(path)


if __name__ == "__main__":
    # Gather all of the supported displays, make a projector using the handle
    display_handles = projector.DisplayManager.get_display_handles()
    proj = projector.DisplayProjector(display_handles[0])
    proj.resolution = (1920, 1080) # width, height

    # Create some fringes
    num_shifts = 3
    phases = np.linspace(0.0, 2.0 * np.pi, num_shifts, endpoint=False)

    num_stripes = 1.0
    rotation = 0.0 # Radians

    # Create some RGB fringe patterns (convert to uint8 for DisplayProjector)
    patterns = np.asarray([
        fringes.to_uint8(fringes.create_rgb_pattern(proj.resolution, num_stripes, phase, rotation)) 
        for phase in phases
    ])

    # If you want to mask out a colour channel its fairly simple
    # rgb_patterns[..., 0] = 0.0 # No red
    patterns[..., 1] = 0.0 # No green
    patterns[..., 2] = 0.0 # No blue

    # You can also generate monochomatic greyscale fringes
    # self.patterns = np.asarray([
    #     fringes.create_pattern(self.proj.resolution, num_stripes, phase, rotation) for phase in phases
    # ])

    # Show the created fringes
    program = Program(proj)
    program.run(patterns, loop=True, pattern_time=1.0)