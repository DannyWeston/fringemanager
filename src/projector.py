import platform
import time
import numpy as np

import contextlib
with contextlib.redirect_stdout(None):
    import pygame # Stupid library welcome message

from abc import ABC, abstractmethod

class IProjector(ABC):
    @abstractmethod
    def show(self, img):
        raise NotImplementedError
    
    @property
    @abstractmethod
    def resolution(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def refresh_rate(self):
        raise NotImplementedError

class DisplayProjector(IProjector):
    def __init__(self, resolution, refresh_rate=10.0, display_num=0, warmup_time=0.0):
        self.__num = display_num

        self.__on_draw_callbacks = []
        self.__on_init_callbacks = []

        self.finished = False
        self.__drawn = None
        self.__display = None

        self.__warmed_up = False
        
        self.__surface = None
        self.__clock = None

        self.__warmup_time = warmup_time
        self.__refresh_rate = refresh_rate
        
        pygame.init()
        self.__display = pygame.display.set_mode(resolution, pygame.SHOWN | pygame.NOFRAME | pygame.FULLSCREEN, display=self.__num)

    def set_img(self, img: np.ndarray):
        if img.dtype != np.uint8:
            img = (img * 255).astype(np.uint8)

        rot_img = np.rot90(img, k=3)
        self.__surface = pygame.surfarray.make_surface(rot_img)

        self.__drawn = False

    def show(self):
        self.finished = False
        self.__clock = pygame.time.Clock()

        self.__display = pygame.display.set_mode(self.resolution, pygame.SHOWN | pygame.NOFRAME | pygame.FULLSCREEN, display=self.__num)
        pygame.mouse.set_visible(False)
        pygame.display.set_window_position(self.offset)

        # Check if slpash screen needed for warmup
        if (not self.__warmed_up) and (0.0 < self.__warmup_time): 
            self.set_img(self.default_img)
            self.__draw()

            wait_start = time.time_ns()
            while True:
                if (self.__warmup_time * 1e9) < (time.time_ns() - wait_start): break

                self.__clock.tick(self.refresh_rate)

        self.__warmed_up = True

        for cb in self.__on_init_callbacks:
            cb()

        while not self.finished:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.finished = True
                    continue
            
            if self.__draw():
                for cb in self.__on_draw_callbacks:
                    cb()

            self.__clock.tick(self.refresh_rate)
        
        pygame.mouse.set_visible(True)
        self.__display = pygame.display.set_mode(self.resolution, pygame.HIDDEN | pygame.NOFRAME | pygame.FULLSCREEN, display=self.__num)


    def __draw(self):
        if not self.__drawn:
            self.__display.blit(self.__surface, (0, 0))

            pygame.display.update()

            self.__drawn = True

            return True
        
        return False

    @property
    def resolution(self):
        return pygame.display.get_window_size()

    @resolution.setter
    def resolution(self, value):
        self.__display = pygame.display.set_mode(value, pygame.SHOWN | pygame.NOFRAME, display=self.__num)
    
    @property
    def refresh_rate(self) -> float:
        return self.__refresh_rate

    @refresh_rate.setter
    def refresh_rate(self, value):
        self.__refresh_rate = value

    @property
    def offset(self):
        return pygame.display.get_window_position()

    @property
    def name(self) -> str:
        return platform.system()

    @property
    def default_img(self):
        w, h = self.resolution
        return np.ones(shape=(h, w, 3), dtype=np.uint8) * 255

    @property
    def warmup_time(self):
        return self.__warmup_time
    
    @warmup_time.setter
    def warmup_time(self, value):
        self.__warmup_time = value

    def add_on_draw_callback(self, cb):
        self.__on_draw_callbacks.append(cb)

    def remove_on_draw_callback(self, cb):
        self.__on_draw_callbacks.remove(cb)

    def add_on_init_callback(self, cb):
        self.__on_init_callbacks.append(cb)

    def remove_on_init_callback(self, cb):
        self.__on_init_callbacks.remove(cb)

    def __str__(self):
        w, h = self.resolution
        freq = self.refresh_rate

        return f'{self.name}Projector ({w}x{h}, {freq} hz)'