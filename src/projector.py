import tkinter
import numpy as np
import time

from abc import ABC, abstractmethod
from PIL import Image, ImageTk
from .display import Display

class IProjector(ABC):
    @abstractmethod
    def project(self, img):
        raise NotImplementedError

class DisplayProjector(Display, IProjector):
    def __init__(self, handle):
        super().__init__(handle)

        self.__post_project_cbs = []

        self.__root = tkinter.Tk()
        self.__root.configure(background='black')

        w, h = self.resolution
        x, y = self.position

        self.__root.geometry(f"{w}x{h}+{x}+{y}")
        self.__root.overrideredirect(1)

        # Create canvas that fills the entire window
        self.__canvas = tkinter.Canvas(self.__root, background='black', highlightthickness=0)
        self.__canvas.pack(fill='both', expand=True)

        self.__tk_img = None
        self.__img = self.__canvas.create_image(0, 0, anchor='nw')

    def project(self, img):
        h, w, *_, = img.shape

        proj_w, proj_h = self.resolution

        if h != proj_h or w != proj_w:
            raise Exception(f"The fringes provided do not match projector's resolution (given: {w}x{h}, projector: {proj_w}x{proj_h})")
        
        proj_w, proj_h = self.resolution
        x, y = self.position

        self.__root.focus_set()
        self.__root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))

        img = (img * 255.0).astype(np.uint8)
        self.__tk_img = ImageTk.PhotoImage(Image.fromarray(img))
        self.__canvas.itemconfig(self.__img, image=self.__tk_img)
        self.__root.geometry(f"{w}x{h}+{x}+{y}")

    def gui_update(self):
        # Don't run any code after this point
        self.__root.update()
        self.__root.update_idletasks()

        time.sleep(float(1.0 / self.refresh_rate)) # Not accurate as not synced with interrupt! Be warned!

    def add_project_callback(self, cb):
        self.__post_project_cbs.append(cb)

    def remove_project_callback(self, cb):
        self.__post_project_cbs.remove(cb)

    def __str__(self):
        w, h = self.resolution
        freq = self.refresh_rate

        return f'DisplayProjector <{self.__handle.DeviceName}> Resolution: {w}x{h}, Refresh Rate: {freq} hz'