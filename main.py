import pymem
import pymem.process
import keyboard
import time
import os
import ctypes

# --- APP INFO ---
VERSION = "1.01"
GITHUB_URL = "https://github.com/Bableg/OutOfOre-AutoLeveler"

# --- CONFIGURATION ---
PROCESS_NAME = "OutOfOre-Win64-Shipping.exe"
KEYS = {"LEFT": 0x4B, "RIGHT": 0x4D, "UP": 0x48, "DOWN": 0x50} 

TOLERANCE_ANGLE = 0.15 
TOLERANCE_GPS = 5.0 

# --- MEMORY OFFSETS ---
BASE_GPS = 0x05901438
OFFSETS_GPS = [0xF8, 0x48, 0x50, 0xC0, 0x350, 0x260, 0x9C] 

BASE_ANGLE = 0x05CBAB60 
OFFSETS_ANGLE = [0x28, 0x600, 0x10, 0x260, 0xD4] 

user32 = ctypes.windll.user32

def send_key(scancode, duration):
    user32.keybd_event(0, scancode, 0x0008, 0)
    time.sleep(duration)
    user32.keybd_event(0, scancode, 0x0008 | 0x0002, 0)

def get_dynamic_hold(diff, is_gps=False):
    mult = 0.003 if is_gps else 0.04
    max_hold = 0.15 if is_gps else 0.12
    hold = abs(diff) * mult
    return max(0.02, min(hold, max_hold))

class AutoPilot:
    def __init__(self):
        self.pm = None
        self.module_base = None
        self.mode_list = ["OFF", "GPS_LEVEL", "FULL_AUTO", "SEMI_AUTO"]
        self.mode_idx = 0
        self.target_side = 0.0
        self.target_pitch = 0.0
        self.target_gps = 0.0
        self.last_valid_gps = 0.0

    def connect(self):
        try:
            self.pm = pymem.Pymem(PROCESS_NAME)
            self.module_base = pymem.process.module_from_name(self.pm.process_handle, PROCESS_NAME).lpBaseOfDll
            return True
        except: return False

    def get_addr(self, base_offset, offsets):
        try:
            addr = self.pm.read_longlong(self.module_base + base_offset)
            for offset in offsets[:-1]:
                addr = self.pm.read_longlong(addr + offset)
            return addr + offsets[-1]
        except: return None 

    def draw_ui(self, cur_s, cur_p, cur_g):
        mode = self.mode_list[self.mode_idx]
        print("\033[H", end="") 
        print("="*55)
        print(f" AUTOPILOT (BLADE CONTROL) v{VERSION:<6} | MODE: {mode:<7}")
        print(f" {GITHUB_URL}")
        print("="*55)
        print(f" [ROLL ANGLE]  Current: {cur_s:7.2f}  |  Target: {self.target_side:7.2f}")
        print(f" [PITCH ANGLE] Current: {cur_p:7.2f}  |  Target: {self.target_pitch:7.2f}")
        print(f" [GPS DEPTH]   Current: {int(cur_g):7}  |  Target: {int(self.target_gps):7}")
        print("-" * 55)
        print(" [ CONTROL GUIDE ]")
        if mode == "GPS_LEVEL":
            print(" F5 / F6 : Adjust Depth (+/- 5.0 cm)")
            print(" Num 5   : Sync Depth to Current Position")
        elif mode == "FULL_AUTO":
            print(" F5 / F6 : Adjust Pitch (+/- 0.05 deg)")
            print(" F7 / F8 : Adjust Roll  (+/- 0.05 deg)")
            print(" Num 5   : Reset Angles (Roll & Pitch) to 0.0")
        elif mode == "SEMI_AUTO":
            print(" F7 / F8 : Adjust Roll  (+/- 0.05 deg)")
            print(" Num 5   : Reset Roll Angle to 0.0")
        else:
            print(" Autopilot is OFF. Press F9 to switch modes.")
        print("-" * 55)
        print(" F9: Switch Mode | F4: Emergency OFF | ESC: Exit")
        print("="*55)

    def run(self):
        addr_base = self.get_addr(BASE_ANGLE, OFFSETS_ANGLE)
        addr_gps = self.get_addr(BASE_GPS, OFFSETS_GPS)

        if keyboard.is_pressed('f9'):
            self.mode_idx = (self.mode_idx + 1) % len(self.mode_list)
            if addr_base:
                try: 
                    self.target_side = 0.0
                    self.target_pitch = 0.0
                except: pass
            if addr_gps:
                try: self.target_gps = round(self.pm.read_float(addr_gps), -1)
                except: pass
            time.sleep(0.3)

        if keyboard.is_pressed('f4'):
            self.mode_idx = 0
            time.sleep(0.2)

        try:
            cur_s = self.pm.read_float(addr_base) if addr_base else 0.0
            cur_p = self.pm.read_float(addr_base + 4) if addr_base else 0.0
            raw_g = self.pm.read_float(addr_gps) if addr_gps else 0.0

            if raw_g != 0: self.last_valid_gps = raw_g
            cur_g = self.last_valid_gps

            self.draw_ui(cur_s, cur_p, cur_g)

            cur_mode = self.mode_list[self.mode_idx]
            if cur_mode != "OFF":
                if cur_mode == "GPS_LEVEL":
                    if keyboard.is_pressed('f5'): self.target_gps -= 5.0; time.sleep(0.05)
                    if keyboard.is_pressed('f6'): self.target_gps += 5.0; time.sleep(0.05)
                elif cur_mode == "FULL_AUTO":
                    if keyboard.is_pressed('f5'): self.target_pitch -= 0.05; time.sleep(0.1)
                    if keyboard.is_pressed('f6'): self.target_pitch += 0.05; time.sleep(0.1)

                if cur_mode in ["FULL_AUTO", "SEMI_AUTO"]:
                    if keyboard.is_pressed('f7'): self.target_side -= 0.05; time.sleep(0.1)
                    if keyboard.is_pressed('f8'): self.target_side += 0.05; time.sleep(0.1)

            if keyboard.is_pressed('5'):
                if cur_mode == "GPS_LEVEL":
                    self.target_gps = round(cur_g, -1)
                elif cur_mode in ["FULL_AUTO", "SEMI_AUTO"]:
                    self.target_side = 0.0
                    self.target_pitch = 0.0
                time.sleep(0.2)

            if cur_mode != "OFF":
                diff_s = cur_s - self.target_side
                if abs(diff_s) > TOLERANCE_ANGLE:
                    if diff_s > 0: send_key(KEYS["LEFT"], get_dynamic_hold(diff_s))
                    else: send_key(KEYS["RIGHT"], get_dynamic_hold(diff_s))

                if cur_mode == "GPS_LEVEL":
                    diff_g = cur_g - self.target_gps
                    if abs(diff_g) >= TOLERANCE_GPS:
                        if diff_g > 0: send_key(KEYS["DOWN"], get_dynamic_hold(diff_g, True))
                        else: send_key(KEYS["UP"], get_dynamic_hold(diff_g, True))
                
                elif cur_mode == "FULL_AUTO":
                    diff_p = cur_p - self.target_pitch
                    if abs(diff_p) > TOLERANCE_ANGLE:
                        if diff_p > 0: send_key(KEYS["DOWN"], get_dynamic_hold(diff_p))
                        else: send_key(KEYS["UP"], get_dynamic_hold(diff_p))

        except Exception:
            pass

os.system('cls')
bot = AutoPilot()
print("Searching for Out of Ore process...")
while not bot.connect(): time.sleep(1)
print(f"Connected! Autopilot v{VERSION} active.")

while True:
    bot.run()
    if keyboard.is_pressed('esc'): break