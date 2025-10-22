import numpy as np
import time
from PIL import Image

from . import fringes, projector, display

# Daniel Weston
# 15/10/2025
# psydw2@nottingham.ac.uk

def main():
    # If you need to figure out what display the projector appears as, use this snippet
    display_handles = display.DisplayManager.get_display_handles()
    for handle in display_handles:
        print(display.Display(handle))

    # Use second display handle as default (not primary)
    proj = projector.DisplayProjector(display_handles[1])
    proj.resolution = (1280, 720) # width, height
    
    num_shifts = 3
    phases = np.linspace(0.0, 2.0 * np.pi, num_shifts, endpoint=False)

    num_stripes = 1.0
    rotation = 0.0 # Radians

    # Create some RGB fringe patterns
    rgb_patterns = np.asarray([
        fringes.CreateRGBFringePattern(proj.resolution, num_stripes, phase, rotation) for phase in phases
    ])

    # If you want to mask out a colour channel its fairly simple
    # rgb_patterns[..., 0] = 0.0 # No red
    rgb_patterns[..., 1] = 0.0 # No green
    rgb_patterns[..., 2] = 0.0 # No blue

    # You can also generate monochomatic greyscale fringes
    grey_patterns = np.asarray([
        fringes.CreateFringePattern(proj.resolution, num_stripes, phase, rotation) for phase in phases
    ])    

    # NOTE: If the resolution is different to what it is currently for the projector, you may want to put an artifical 
    # wait here of a few seconds as it will take some time to execute 
    # --- don't want to assume fringes are projected before the resolution change! :)
    show_fringes(proj, rgb_patterns, warmup_time=3.0)

    # If you wish to save some patterns to disk:
    output = "a\\directory\\somewhere\\changeme"
    for i, fp in enumerate(rgb_patterns):
        save_image(fp, f"{output}pattern{i}.bmp")

def after_project(shift):
    print(f"Projecting fringes with shift number {shift}")
    # Run any of your own updates here
    # e.g: take a picture with a camera
    pass


def show_fringes(proj, fringe_patterns, warmup_time=3.0):
    # Controls for consecutive projections
    projection_duration = 1.0 # seconds
    loop = True # Loop forver

    last_frame = time.time_ns() - (warmup_time * 1e9)
    i = 0
    while True:
        now = time.time_ns()

        if (now - last_frame) >= (projection_duration * 1e9):
            if i == len(fringe_patterns): # Check if finished
                if not loop: break
                i = 0

            # Project the fringe pattern
            proj.project(fringe_patterns[i])

            i += 1

            after_project(i)            

            last_frame = now

        proj.gui_update()


def save_image(img, path):
    img = Image.fromarray((img * 255.0).astype(np.uint8))
    img.save(path)

if __name__ == "__main__":
    main()