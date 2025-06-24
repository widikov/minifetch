#!/usr/bin/env python3

import os
import platform
import subprocess
import sys
import ctypes
import psutil
import re
from colorama import Fore, init

init()

class Config:
    ASCII_FILE = "custom.txt"
    ASCII_DIR = "ascii"
    
    TEXT_COLOR = Fore.WHITE
    RESET = Fore.RESET
    
    LABELS = {
        "user": "user",
        "os": "os",
        "host": "host",
        "kernel": "kernel",
        "uptime": "uptime",
        "cpu": "cpu",
        "gpu": "gpu",
        "memory": "memory",
    }
    
    COLOR_TAGS = {
        '{black}': Fore.BLACK,
        '{red}': Fore.RED,
        '{green}': Fore.GREEN,
        '{yellow}': Fore.YELLOW,
        '{blue}': Fore.BLUE,
        '{magenta}': Fore.MAGENTA,
        '{cyan}': Fore.CYAN,
        '{white}': Fore.WHITE,
        '{orange}': '\033[38;5;208m',
        '{reset}': Fore.RESET
    }


class ColorManager:
    
    @staticmethod
    def load_colors(ascii_path: str) -> tuple:
        try:
            with open(ascii_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
                
            if len(lines) >= 2:
                color1_tag = f"{{{lines[0].lower()}}}"
                color2_tag = f"{{{lines[1].lower()}}}"
                
                color1 = Config.COLOR_TAGS.get(color1_tag, Fore.WHITE)
                color2 = Config.COLOR_TAGS.get(color2_tag, Fore.WHITE)
                
                return color1, color2
        except:
            pass
        return None, None
    
    @staticmethod
    def parse_colored_ascii(line: str) -> str:
        colored_line = line
        for tag, color in Config.COLOR_TAGS.items():
            colored_line = colored_line.replace(tag, color)
        return colored_line + Config.RESET

# freebsd support soon i hope
class SystemInfoFetcher:    
    @staticmethod
    def get_username() -> str:
        return os.getlogin() if hasattr(os, 'getlogin') else os.environ.get('USER', 'Unknown')

    @staticmethod
    def get_hostname() -> str:
        return platform.node()

    @staticmethod
    def get_host_info() -> str:
        try:
            system = platform.system().lower()
            if system == 'linux':
                try:
                    with open('/sys/devices/virtual/dmi/id/product_name', 'r') as f:
                        return f.read().strip()
                except:
                    return "Unknown"
            elif system == 'darwin':
                return subprocess.getoutput("sysctl -n hw.model").strip() or "Unknown"
            else:
                output = subprocess.getoutput("wmic baseboard get product").strip()
                return output.replace('Product', '').strip() or "Unknown"
        except Exception:
            return "Unknown"

    @staticmethod
    def get_uptime() -> str:
        try:
            system = platform.system().lower()
            if system == 'linux' or system == 'darwin':
                with open('/proc/uptime', 'r') as f:
                    uptime_seconds = float(f.readline().split()[0])
                mins, sec = divmod(int(uptime_seconds), 60)
                hour, mins = divmod(mins, 60)
                days, hour = divmod(hour, 24)
            else:
                lib = ctypes.windll.kernel32
                t = lib.GetTickCount64()
                t = int(str(t)[:-3])
                mins, sec = divmod(t, 60)
                hour, mins = divmod(mins, 60)
                days, hour = divmod(hour, 24)
            
            uptime_str = ""
            if days > 0:
                uptime_str += f"{days}d "
            uptime_str += f"{hour:02}h {mins:02}m"
            return uptime_str
        except Exception:
            return "Unknown"

    @staticmethod
    def get_cpu_info() -> str:
        try:
            system = platform.system().lower()
            if system == 'linux':
                with open('/proc/cpuinfo', 'r') as f:
                    for line in f:
                        if 'model name' in line:
                            return line.split(':')[1].strip()
                return "Unknown"
            elif system == 'darwin':
                return subprocess.getoutput("sysctl -n machdep.cpu.brand_string").strip() or "Unknown"
            else:
                output = subprocess.getoutput("wmic cpu get name").strip()
                return output.replace('Name', '').strip() or "Unknown"
        except Exception:
            return "Unknown"

    @staticmethod
    def get_ram_info() -> str:
        try:
            total_ram = round(psutil.virtual_memory().total / (1024**3), 1)
            used_ram = round(psutil.virtual_memory().used / (1024**3), 1)
            return f"{used_ram}GB / {total_ram}GB"
        except Exception:
            return "Unknown"

    @staticmethod
    def get_gpu_info() -> str:
        try:
            system = platform.system().lower()
            if system == 'linux':
                try:
                    output = subprocess.getoutput("lspci | grep -i vga").strip()
                    if output:
                        return output.split(': ')[-1]
                    output = subprocess.getoutput("glxinfo | grep 'OpenGL renderer string'").strip()
                    if output:
                        return output.split(': ')[-1]
                    return "Unknown"
                except:
                    return "Unknown"
            elif system == 'darwin':
                output = subprocess.getoutput("system_profiler SPDisplaysDataType | grep Chipset").strip()
                return output.split(': ')[-1] if output else "Unknown"
            else:
                output = subprocess.getoutput("wmic path win32_videocontroller get name").strip()
                gpus = [line.strip() for line in output.split('\n') 
                       if line.strip() and not line.startswith('Name')]
                return ", ".join(gpus) if gpus else "Unknown"
        except Exception:
            return "Unknown"

    @staticmethod
    def get_os_info() -> str:
        try:
            system = platform.system()
            if system == 'Linux':
                try:
                    import distro
                    distro_name = distro.id()
                    return f"{distro.name()} {distro.version()}", distro_name
                except:
                    return f"Linux {platform.release()}", "linux"
            elif system == 'Darwin':
                version = platform.mac_ver()[0]
                return f"macOS {version}", "mac"
            else:
                version_map = {
                    '10': '10',
                    '11': '11'
                }
                release = platform.release()
                build = sys.getwindowsversion().build
                return f"Windows {version_map.get(release, release)} (Build {build})", "windows"
        except Exception:
            return platform.system() + " " + platform.release(), "unknown"

    @staticmethod
    def get_kernel_info() -> str:
        try:
            system = platform.system()
            if system == 'Linux':
                return platform.release()
            elif system == 'Darwin':
                return subprocess.getoutput("uname -r").strip()
            else:
                return platform.version()
        except Exception:
            return "Unknown"


class ASCIIArtLoader:    
    @staticmethod
    def get_ascii_file() -> str:
        script_dir = os.path.dirname(__file__)
        custom_path = os.path.join(script_dir, Config.ASCII_FILE)
        
        if os.path.exists(custom_path) and os.path.getsize(custom_path) > 0:
            return custom_path
        
        os_info, os_name = SystemInfoFetcher.get_os_info()
        possible_files = [
            f"{os_name}.txt",
        ]
        
        ascii_dir = os.path.join(script_dir, Config.ASCII_DIR)
        if os.path.exists(ascii_dir):
            for filename in possible_files:
                filepath = os.path.join(ascii_dir, filename)
                if os.path.exists(filepath):
                    return filepath
                
        return None 
    
    @staticmethod
    def load_ascii_art() -> tuple:
        ascii_path = ASCIIArtLoader.get_ascii_file()
        if not ascii_path:
            return [], 0, None, None
            
        try:
            with open(ascii_path, 'r', encoding='utf-8') as f:
                lines = [line.rstrip('\n') for line in f.readlines()]
                
            if len(lines) < 2:
                return [], 0, None, None
                
            color1, color2 = ColorManager.load_colors(ascii_path)
            if not color1 or not color2:
                return [], 0, None, None
                
            ascii_lines = lines[2:] if len(lines) > 2 else []
            
            colored_ascii = []
            max_width = 0
            
            for line in ascii_lines:
                colored_line = ColorManager.parse_colored_ascii(line)
                colored_ascii.append(colored_line)
                visible_length = len(re.sub(r'\x1b\[[0-9;]*m', '', colored_line))
                if visible_length > max_width:
                    max_width = visible_length
            
            return colored_ascii, max_width, color1, color2
            
        except:
            return [], 0, None, None


class SystemInfoDisplay:    
    def __init__(self):
        self.user = SystemInfoFetcher.get_username()
        self.hostname = SystemInfoFetcher.get_hostname()
        self.os, _ = SystemInfoFetcher.get_os_info()
        self.host = SystemInfoFetcher.get_host_info()
        self.kernel = SystemInfoFetcher.get_kernel_info()
        self.uptime = SystemInfoFetcher.get_uptime()
        self.cpu = SystemInfoFetcher.get_cpu_info()
        self.ram = SystemInfoFetcher.get_ram_info()
        self.gpu = SystemInfoFetcher.get_gpu_info()
        
    def generate_display(self) -> str:
        colored_ascii, ascii_width, color1, color2 = ASCIIArtLoader.load_ascii_art()
        
        if not color1 or not color2:
            info_lines = [
                f"{self.user}@{self.hostname}",
                f"{Config.LABELS['os']:9}{self.os}",
                f"{Config.LABELS['host']:9}{self.host}",
                f"{Config.LABELS['kernel']:9}{self.kernel}",
                f"{Config.LABELS['uptime']:9}{self.uptime}",
                f"{Config.LABELS['cpu']:9}{self.cpu}",
                f"{Config.LABELS['gpu']:9}{self.gpu}",
                f"{Config.LABELS['memory']:9}{self.ram}",
            ]
            return "\n" + "\n".join(info_lines)
        
        info_lines = [
            f"{color2}{self.user}{Config.TEXT_COLOR}@{color2}{self.hostname}",
            f"{color1}{Config.LABELS['os']:9}{Config.TEXT_COLOR}{self.os}",
            f"{color1}{Config.LABELS['host']:9}{Config.TEXT_COLOR}{self.host}",
            f"{color1}{Config.LABELS['kernel']:9}{Config.TEXT_COLOR}{self.kernel}",
            f"{color1}{Config.LABELS['uptime']:9}{Config.TEXT_COLOR}{self.uptime}",
            f"{color1}{Config.LABELS['cpu']:9}{Config.TEXT_COLOR}{self.cpu}",
            f"{color1}{Config.LABELS['gpu']:9}{Config.TEXT_COLOR}{self.gpu}",
            f"{color1}{Config.LABELS['memory']:9}{Config.TEXT_COLOR}{self.ram}",
        ]
        
        display_text = "\n"
        if colored_ascii:
            for i, (ascii_line, info_line) in enumerate(zip(colored_ascii, info_lines)):
                visible_ascii_length = len(re.sub(r'\x1b\[[0-9;]*m', '', ascii_line))
                padding = " " * (ascii_width - visible_ascii_length + 4)
                display_text += ascii_line + padding + info_line + "\n"
            
            for i in range(len(info_lines), len(colored_ascii)):
                display_text += colored_ascii[i] + "\n"
        else:
            display_text += "\n".join(info_lines) + "\n"
        
        return display_text


def main():
    system_display = SystemInfoDisplay()
    print(system_display.generate_display())

def entry_point():
    main()

if __name__ == "__main__":
    main()