import win32api
import win32con

class Display():
    def __init__(self, handle):
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
    def position(self):
        devmode = win32api.EnumDisplaySettings(self.__handle.DeviceName, win32con.ENUM_REGISTRY_SETTINGS)

        return devmode.Position_x, devmode.Position_y

    def __str__(self):
        w, h = self.resolution
        freq = self.refresh_rate

        return f'Display <{self.__handle.DeviceName}> Resolution: {w}x{h}, Refresh Rate: {freq} hz'

class DisplayManager:
    def __init__(self):
        pass

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