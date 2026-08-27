import os
import json
import time
import platform
import subprocess
import psutil
from typing import Dict, Any, List
from j4ck_cleaner import __version__
from j4ck_cleaner.core.logger import logger

# Protected workloads (NEVER kill or restrict these)
PROTECTED_PROCESSES = {
    "steam", "steamwebhelper", "proton", "wine", "java", "zomboid",
    "niri", "noctalia-shell", "kitty", "warp", "windsurf", "antigravity",
    "code", "vesktop", "discord", "obsidian", "firefox", "chromium",
    "pulseaudio", "pipewire", "wireplumber", "sddm", "Xorg", "Xwayland"
}

# Thermal Slider Bounds (°C)
TEMP_MIN_SLIDER: int = 60   # Minimum configurable thermal threshold
TEMP_MAX_SLIDER: int = 90   # Maximum configurable thermal threshold


class SystemOptimizerEngine:
    """
    Core engine for non-destructive RAM cache cleaning, ZRAM compaction,
    diagnostics reporting, and thermal throttling management for legacy/heterogeneous Linux hardware.
    """

    def __init__(self, thermal_threshold_c: float = 76.0):
        self.thermal_threshold_c = thermal_threshold_c

    def set_thermal_threshold(self, temp_c: float):
        """Update thermal threshold trigger."""
        self.thermal_threshold_c = temp_c

    def clean_cache(self) -> Dict[str, Any]:
        """
        Flushes inactive pagecache, dentries, and inodes safely after filesystem sync.
        Does not close or affect running user applications.
        """
        results = {
            "success": False,
            "freed_mb": 0.0,
            "message": ""
        }

        try:
            mem_before = psutil.virtual_memory().used

            # Sync filesystems first to prevent any data loss
            subprocess.run(["sync"], check=True)

            # Drop caches via pkexec if non-root, or directly if root
            if os.geteuid() == 0:
                with open("/proc/sys/vm/drop_caches", "w") as f:
                    f.write("3\n")
                results["success"] = True
            else:
                cmd = ["pkexec", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                results["success"] = (proc.returncode == 0)

            # Perform safe ZRAM compaction if swap is active
            self.compact_zram_swap()

            mem_after = psutil.virtual_memory().used
            freed_bytes = max(0, mem_before - mem_after)
            results["freed_mb"] = round(freed_bytes / (1024 * 1024), 1)
            results["message"] = f"Limpieza de caché: {results['freed_mb']} MB liberados."
        except Exception as err:
            results["message"] = f"Error en limpieza de caché: {err}"
            results["success"] = False

        return results

    def compact_zram_swap(self) -> bool:
        """
        Safely compacts ZRAM / Swap if free physical RAM is greater than used Swap.
        Prevents system freezes by enforcing strict free memory buffer checks.
        """
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            if swap.used == 0:
                return True

            # Safety Check: Free RAM must be at least 1.5x Swap used to prevent freeze
            if mem.available < (swap.used * 1.5):
                return False

            # Compact zram via sysfs if zram is active
            zram_compact_paths = ["/sys/block/zram0/compact", "/sys/block/zram1/compact"]
            for zpath in zram_compact_paths:
                if os.path.exists(zpath):
                    if os.geteuid() == 0:
                        with open(zpath, "w") as f:
                            f.write("1\n")
                    else:
                        subprocess.run(["pkexec", "sh", "-c", f"echo 1 > {zpath}"], capture_output=True, timeout=3)
            return True
        except Exception:
            return False

    def generate_diagnostics_report(self) -> str:
        """
        Generates a 1-click JSON system diagnostic report in ~/.config/nocturne-guardian/system-diagnostics.json
        useful for attaching to GitHub issues or analyzing hardware health.
        """
        config_dir = os.path.expanduser("~/.config/nocturne-guardian")
        report_path = os.path.join(config_dir, "system-diagnostics.json")

        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            report_data = {
                "app_version": __version__,
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "system": {
                    "os": platform.system(),
                    "release": platform.release(),
                    "arch": platform.machine(),
                    "python_version": platform.python_version()
                },
                "hardware": {
                    "cpu_cores_logical": psutil.cpu_count(logical=True),
                    "cpu_cores_physical": psutil.cpu_count(logical=False),
                    "ram_total_gb": round(mem.total / (1024 ** 3), 2),
                    "ram_used_gb": round(mem.used / (1024 ** 3), 2),
                    "swap_total_gb": round(swap.total / (1024 ** 3), 2),
                    "swap_used_gb": round(swap.used / (1024 ** 3), 2)
                },
                "thermal_configuration": {
                    "thermal_threshold_c": self.thermal_threshold_c,
                    "protected_processes_count": len(PROTECTED_PROCESSES)
                }
            }

            os.makedirs(config_dir, exist_ok=True)
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(report_data, f, indent=4, ensure_ascii=False)

            return report_path
        except Exception as err:
            print(f"[Diagnostics Error] {err}")
            return ""

    def enforce_thermal_throttling(self, current_temp_c: float) -> Dict[str, Any]:
        """
        If current_temp_c >= thermal_threshold_c, deprioritizes non-essential 
        background processes (renice +10 / ionice idle) to relieve CPU core stress 
        while preserving all user games and active IDEs.
        """
        summary = {
            "triggered": False,
            "adjusted_processes": 0,
            "details": ""
        }

        if current_temp_c < self.thermal_threshold_c:
            summary["details"] = f"Temperatura ({current_temp_c}°C) por debajo del umbral ({self.thermal_threshold_c}°C)."
            return summary

        summary["triggered"] = True
        adjusted_count = 0

        for p in psutil.process_iter(['pid', 'name']):
            try:
                pid = p.info['pid']
                name = (p.info['name'] or '').lower()

                # Ignore kernel threads and protected processes
                if pid <= 1000 or any(prot in name for prot in PROTECTED_PROCESSES):
                    continue

                proc = psutil.Process(pid)
                # Lower CPU niceness (increase nice value to 10)
                if proc.nice() < 10:
                    proc.nice(10)
                    adjusted_count += 1
            except Exception:
                continue

        summary["adjusted_processes"] = adjusted_count
        summary["details"] = f"Umbral ({self.thermal_threshold_c}°C) alcanzado. Reajustada prioridad de {adjusted_count} procesos secundarios."
        logger.log(f"ALERTA TÉRMICA ({current_temp_c}°C): {summary['details']}", level="warning")
        return summary

    def get_current_governor(self) -> str:
        """Reads current CPU scaling governor from sysfs."""
        try:
            gov_file = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
            if os.path.exists(gov_file):
                with open(gov_file, "r") as f:
                    return f.read().strip()
        except Exception:
            pass
        return "desconocido"

    def set_cpu_governor(self, governor: str) -> bool:
        """Sets scaling governor across all CPU cores (performance, schedutil, powersave, ondemand)."""
        valid_govs = ["performance", "schedutil", "powersave", "ondemand"]
        clean_gov = governor.strip().lower()
        if clean_gov not in valid_govs:
            return False

        try:
            if os.geteuid() == 0:
                cmd = f"echo {clean_gov} | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
                subprocess.run(cmd, shell=True, check=True)
            else:
                cmd = f"pkexec sh -c 'echo {clean_gov} | tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor'"
                subprocess.run(cmd, shell=True, check=True)
            return True
        except Exception as err:
            print(f"[Governor Error] {err}")
            return False
