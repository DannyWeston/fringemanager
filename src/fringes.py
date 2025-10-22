import numpy as np

def CreateFringePattern(resolution, num_stripes, phase=0.0, rotation=0.0):
    ''' 
        resolution: (width, height) in integer pixels\n
        num_stripes: float for total number of oscillations\n
        phase: float in radians for signal phase shift\n
        rotation: float in radians for orientation of fringes\n
    '''

    w, h = resolution

    xs, ys = np.meshgrid(
        np.linspace(0.0, 1.0, w, dtype=np.float32), 
        np.linspace(0.0, 1.0, h, dtype=np.float32),
    )

    pixels = xs * np.cos(rotation) - ys * np.sin(rotation)

    # I(x, y) = cos(2 * pi * f * x - phi)
    fringes = np.cos((num_stripes * pixels * 2.0 * np.pi) - phase, dtype=np.float32)

    # Normalise [-1..1] to [0..1]
    fringes = (fringes + 1.0) / 2.0

    return fringes

def CreateRGBFringePattern(resolution, num_stripes, phase=0.0, rotation=0.0):
    ''' 
        resolution: (width, height) in integer pixels\n
        num_stripes: float for total number of oscillations\n
        phase: float in radians for signal phase shift\n
        rotation: float in radians for orientation of fringes\n
    '''
    
    temp = np.dstack([CreateFringePattern(resolution, num_stripes, phase, rotation)] * 3)
    return temp