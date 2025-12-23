import numpy as np
import time

from pathlib import Path
from PIL import Image

from . import fringes, projector

# Daniel Weston
# 16/12/2025
# psydw2@nottingham.ac.uk

class Program:
    def __init__(self, proj: projector.DisplayProjector):
        # Use second display handle as default (not primary)
        self.proj = proj

        self.__patterns = None
        self.__pattern_index = None

    def run(self, patterns):
        self.__captured_imgs = []

        self.__patterns = patterns

        self.proj.add_on_init_callback(self.on_init)
        self.proj.add_on_draw_callback(self.on_draw)

        success = self.proj.show()

        # Remove callbacks
        self.proj.remove_on_draw_callback(self.on_draw)
        self.proj.remove_on_init_callback(self.on_init)

        return self.__captured_imgs if success else None

    def gamma_calibrate(self, num_intensities=64):
        self.__captured_imgs = []

        self.__pattern_index = 0
        w, h = proj.resolution

        self.__patterns = np.asarray([
            np.ones(shape=(h, w, 3), dtype=np.float32) * intensity
            for intensity in np.linspace(0.0, 1.0, num_intensities, endpoint=True)
        ])

        # Add callbacks
        self.proj.add_on_draw_callback(self.on_draw)
        self.proj.add_on_init_callback(self.on_init)

        success = self.proj.show()

        # Remove callbacks
        self.proj.remove_on_draw_callback(self.on_draw)
        self.proj.remove_on_init_callback(self.on_init)

        return self.__captured_imgs if success else None


    def on_draw(self):
        # # #
        # Could take camera picture here, would be synchronised with projector
        # # #
        
        if self.__pattern_index == len(self.__patterns):
            self.proj.finished = True
            return

        # Project the fringe pattern
        self.proj.set_img(self.__patterns[self.__pattern_index])

        self.__pattern_index += 1

    def on_init(self):
        self.__pattern_index = 0

        self.proj.set_img(self.__patterns[self.__pattern_index])
        self.__pattern_index += 1

if __name__ == "__main__":
    # Make a DisplayProjector
    proj = projector.DisplayProjector(resolution=(1280, 720), display_num=0, warmup_time=3.0)
    program = Program(proj)

    # Complete gamma calibration if required
    # gamma_imgs = program.gamma_calibrate(64)


    # Create some fringes
    num_shifts = 16     # Number of phase shifts
    num_stripes = 1.0   # Number of stripes (for the whole image)
    rotation = 0.0      # Stripe rotation (orientation)

    # Create some RGB fringe patterns
    patterns = np.asarray([
        fringes.create_rgb_pattern(proj.resolution, num_stripes, phase, rotation)
        for phase in np.linspace(0.0, 2.0 * np.pi, num_shifts, endpoint=False)
    ])

    # Show fringes at 30fps, loop forever, return camera images
    camera_imgs = program.run(patterns)
    

    # Show red fringes green and blue channels zero'd), loop forever, return camera images
    patterns[..., 1] = 0.0 # No green channel
    patterns[..., 2] = 0.0 # No blue channel
    camera_imgs = program.run(patterns) 


    # If you want to save any patterns/images, you can use the save_image function
    path = Path("some/path/somewhere")
    for i, pattern in enumerate(patterns):
        uint_pattern = (pattern * 255).astype(np.uint8)
        img = Image.fromarray(uint_pattern)
        # img.save(path / f"pattern{i}.png")