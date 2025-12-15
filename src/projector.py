import platform
import time
import numpy as np
import tkinter

from abc import ABC, abstractmethod
from PIL import Image, ImageTk

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

class OSDisplayProjector(IProjector):
    def __init__(self):
        self.__frame_update_cbs = []

        self.__finished = False
        self.__last_update = None

        self.__root = tkinter.Tk()
        self.__root.configure(background='black')

        self.__root.overrideredirect(1)
        self.__root.config(cursor='none')

        # Create canvas that fills the entire window
        self.__canvas = tkinter.Canvas(self.__root, background='black', highlightthickness=0)
        self.__canvas.pack(fill='both', expand=True)

        self.__img = self.__canvas.create_image(0, 0, anchor='nw')
        self.__tk_img = None

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def offset(self):
        raise NotImplementedError
    
    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError
    
    def set_img(self, img):
        self.__last_update = time.time_ns()
        self.__finished = False
        
        h, w, *_, = img.shape
        proj_w, proj_h = self.resolution

        if (w, h) != self.resolution: # Must be same resolution
            raise Exception(f"Image shape does not match resolution")

        if img.dtype != np.uint8: # Must be uint8
            raise Exception(f"Image dtype must be in np.uint8 format ({img.dtype} provided)")

        if h != proj_h or w != proj_w:
            raise Exception(f"The fringes provided do not match projector's resolution (given: {w}x{h}, projector: {proj_w}x{proj_h})")
        
        proj_w, proj_h = self.resolution

        self.__tk_img = ImageTk.PhotoImage(Image.fromarray(img))
        self.__canvas.itemconfig(self.__img, image=self.__tk_img)
    
    @property
    def finished(self):
        return self.__finished

    def show(self):
        self.__finished = False
        
        w, h = self.resolution
        x, y = self.offset

        self.__root.geometry(f"{w}x{h}+{x}+{y}")

        self.__root.bind("<Escape>", self.__on_finish)
        self.__root.deiconify()
        self.__root.focus_force()

        while not self.__finished:
            w, h = self.resolution
            x, y = self.offset
            
            self.__root.geometry(f"{w}x{h}+{x}+{y}")

            self.__root.update()
            self.__root.update_idletasks()

            time.sleep(float(1.0 / self.refresh_rate)) # Not accurate as not synced with interrupt! Be warned!

            for cb in self.__frame_update_cbs:
                cb(self.__last_update)

        self.__cleanup()

    def add_frame_callback(self, cb):
        self.__frame_update_cbs.append(cb)

    def remove_frame_callback(self, cb):
        self.__frame_update_cbs.remove(cb)

    def __on_finish(self, e):
        self.__finished = True

    def __cleanup(self):
        self.__last_update = None
        self.__root.unbind("<Escape>")
        self.__root.withdraw()

    def __str__(self):
        w, h = self.resolution
        freq = self.refresh_rate

        return f'{self.name}Projector ({w}x{h}, {freq} hz)'

if platform.system() == 'Linux':
    
    class DisplayManager:
        @staticmethod
        def get_display_handles():
            return []

    class DisplayProjector(OSDisplayProjector):
        def __init__(self):
            super().__init__()

        @property
        def name(self):
            return "Linux"
        
elif platform.system() == "Windows":
    import win32api
    import win32con

    class DisplayManager:
        @staticmethod
        def get_display_handles():
            i = 0
            monitors = []

            while True:
                try:
                    device = win32api.EnumDisplayDevices(None, i, 0)

                    if device.StateFlags & win32con.DISPLAY_DEVICE_ATTACHED_TO_DESKTOP:
                        monitors.append(device)

                except: return monitors

                i += 1

    class DisplayProjector(OSDisplayProjector):
        def __init__(self, handle):
            super().__init__()

            self.__handle = handle

        @property
        def resolution(self):
            devmode = win32api.EnumDisplaySettings(self.__handle.DeviceName, win32con.ENUM_REGISTRY_SETTINGS)

            return devmode.PelsWidth, devmode.PelsHeight

        @resolution.setter
        def resolution(self, value):
            ''' TODO '''
            w, h = value

            devmode = win32api.EnumDisplaySettings(self.__handle.DeviceName, win32con.ENUM_REGISTRY_SETTINGS)
            devmode.PelsWidth = w
            devmode.PelsHeight = h
            devmode.Fields = win32con.DM_PELSWIDTH | win32con.DM_PELSHEIGHT

            result = win32api.ChangeDisplaySettingsEx(self.__handle.DeviceName, devmode, win32con.CDS_UPDATEREGISTRY | win32con.CDS_RESET) 

            if result != win32con.DISP_CHANGE_SUCCESSFUL:
                raise Exception(f"Could not change resolution to {w}x{h} for Display <{self.__handle.DeviceName}>")
            
            return self
        
        @property
        def refresh_rate(self):
            ''' TODO '''
            devmode = win32api.EnumDisplaySettings(self.__handle.DeviceName, win32con.ENUM_REGISTRY_SETTINGS)

            return devmode.DisplayFrequency
        
        @refresh_rate.setter
        def refresh_rate(self, value:int):
            ''' TODO: Implement working solution - not Currently Supported! '''
            raise NotImplementedError

            # devmode = win32api.EnumDisplaySettings(self.__handle.DeviceName, win32con.ENUM_REGISTRY_SETTINGS)

            # devmode.DisplayFrequency = value
            # devmode.Fields = win32con.DM_DISPLAYFREQUENCY

            # result = win32api.ChangeDisplaySettingsEx(self.__handle.DeviceName, devmode, win32con.CDS_UPDATEREGISTRY | win32con.CDS_RESET)

            # if result != win32con.DISP_CHANGE_SUCCESSFUL:
            #     raise Exception(f"Could not change refresh rate to {value} hz for Display <{self.__handle.DeviceName}>")
            
            # return self

        @property
        def offset(self):
            devmode = win32api.EnumDisplaySettings(self.__handle.DeviceName, win32con.ENUM_REGISTRY_SETTINGS)

            return devmode.Position_x, devmode.Position_y

        @property
        def name(self):
            return "Windows"