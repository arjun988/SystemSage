import platform
import os
if platform.system() == "Windows":
    try:
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        from comtypes import CLSCTX_ALL, CoInitialize, CoUninitialize
        from ctypes import cast, POINTER
    except ImportError as e:
        print(f"Error importing pycaw: {e}")

def adjust_volume(command):
    system = platform.system()
    print(f"Adjusting volume on {system} with command: {command}")
    if system == "Windows":
        try:
            # Initialize COM library
            CoInitialize()
            
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            current_volume = volume.GetMasterVolumeLevelScalar()
            if "increase" in command.lower() or "louder" in command.lower():
                volume.SetMasterVolumeLevelScalar(min(current_volume + 0.1, 1.0), None)
                return "Volume increased."
            elif "decrease" in command.lower() or "quieter" in command.lower():
                volume.SetMasterVolumeLevelScalar(max(current_volume - 0.1, 0.0), None)
                return "Volume decreased."
        except Exception as e:
            return f"Error adjusting volume on Windows: {e}"
        finally:
            # Uninitialize COM library
            CoUninitialize()
    elif system == "Linux":
        try:
            if "increase" in command.lower() or "louder" in command.lower():
                os.system("amixer -D pulse sset Master 10%+")
                return "Volume increased."
            elif "decrease" in command.lower() or "quieter" in command.lower():
                os.system("amixer -D pulse sset Master 10%-")
                return "Volume decreased."
        except Exception as e:
            return f"Error adjusting volume on Linux: {e}"
    return "Command not recognized for volume control."
