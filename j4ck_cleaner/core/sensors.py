import os
import glob
import time
from typing import Dict, List, Any
from PySide6.QtCore import QThread, Signal
import psutil


from j4ck_cleaner.core.config import settings_mgr


class SystemSensorThread(QThread):
    """
    Background worker thread for sampling CPU temperature, GPU metrics, memory, frequency, 
    and system metrics asynchronously to keep the UI at 60 FPS.
    """
    metrics_updated = Signal(dict)

    def __init__(self, sample_interval_ms: int = 1000, parent=None):
        super().__init__(parent)
        self.sample_interval_ms = sample_interval_ms
        self._running = True

    def stop(self):
        """Stop sampling worker safely."""
        self._running = False

    def get_cpu_temperature(self) -> float:
        """
        Reads CPU temperature in degrees Celsius across AMD k10temp, amdgpu,
        lm-sensors, or Linux sysfs.
        """
        temp = 0.0
        # Try psutil sensors_temperatures first
        try:
            sensors = psutil.sensors_temperatures()
            if sensors:
                for chip_name in ["k10temp", "zenpower", "coretemp", "amdgpu", "acpitz"]:
                    if chip_name in sensors and sensors[chip_name]:
                        for entry in sensors[chip_name]:
                            if entry.current and entry.current > 0:
                                return float(entry.current)
                for entries in sensors.values():
                    for entry in entries:
                        if entry.current and entry.current > 0:
                            return float(entry.current)
        except Exception:
            pass

        # Fallback to sysfs reading directly
        try:
            for i in range(10):
                sysfs_path = f"/sys/class/hwmon/hwmon{i}/temp1_input"
                if os.path.exists(sysfs_path):
                    with open(sysfs_path, "r") as f:
                        val = int(f.read().strip())
                        if val > 1000:
                            return float(val / 1000.0)
                        elif val > 0:
                            return float(val)
        except Exception:
            pass

        return temp

    def get_gpu_metrics(self) -> Dict[str, Any]:
        """
        Reads GPU temperature (°C), VRAM usage, and power consumption (Watts) 
        across AMDGPU sysfs, lm-sensors, or sysfs DRM nodes.
        """
        gpu_info = {
            "gpu_temp": 0.0,
            "gpu_power_w": 0.0,
            "vram_used_gb": 0.0,
            "vram_total_gb": 0.0,
            "vram_percent": 0.0
        }

        # 1. Try AMDGPU sysfs vram & power
        try:
            amdgpu_vram_used = glob.glob("/sys/class/drm/card*/device/mem_info_vram_used")
            amdgpu_vram_total = glob.glob("/sys/class/drm/card*/device/mem_info_vram_total")
            
            if amdgpu_vram_used and amdgpu_vram_total:
                with open(amdgpu_vram_used[0], "r") as f_used, open(amdgpu_vram_total[0], "r") as f_total:
                    used_b = int(f_used.read().strip())
                    total_b = int(f_total.read().strip())
                    gpu_info["vram_used_gb"] = round(used_b / (1024 ** 3), 2)
                    gpu_info["vram_total_gb"] = round(total_b / (1024 ** 3), 2)
                    if total_b > 0:
                        gpu_info["vram_percent"] = round((used_b / total_b) * 100.0, 1)

            amdgpu_power = glob.glob("/sys/class/drm/card*/device/hwmon/hwmon*/power1_average")
            if amdgpu_power:
                with open(amdgpu_power[0], "r") as f_pwr:
                    val_uw = int(f_pwr.read().strip())
                    gpu_info["gpu_power_w"] = round(val_uw / 1000000.0, 1)
        except Exception:
            pass

        # 2. Try GPU Temperature from psutil sensors
        try:
            sensors = psutil.sensors_temperatures()
            if sensors and "amdgpu" in sensors:
                for entry in sensors["amdgpu"]:
                    if entry.current and entry.current > 0:
                        gpu_info["gpu_temp"] = float(entry.current)
                        break
        except Exception:
            pass

        # Fallback GPU temp if 0
        if gpu_info["gpu_temp"] == 0.0:
            gpu_info["gpu_temp"] = self.get_cpu_temperature()

        return gpu_info

    def get_top_processes(self, count: int = 5) -> List[Dict[str, Any]]:
        """Returns top memory/CPU processes for dashboard visibility."""
        procs = []
        try:
            for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
                try:
                    info = p.info
                    pid = info['pid']
                    name = info['name'] or 'unknown'
                    # Filter out system kernel daemons, PIDs <= 1000, and protected whitelist apps
                    whitelist = settings_mgr.get_whitelist()
                    name_lower = name.lower()
                    if pid <= 1000 or name.startswith('[') or name.startswith('kworker/') or any(w in name_lower for w in whitelist):
                        continue

                    mem_mb = (info['memory_info'].rss / (1024 * 1024)) if info['memory_info'] else 0
                    procs.append({
                        'pid': pid,
                        'name': name,
                        'cpu': info['cpu_percent'] or 0.0,
                        'mem_mb': round(mem_mb, 1),
                        'mem_pct': round(info['memory_percent'] or 0.0, 1)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            procs.sort(key=lambda x: x['cpu'], reverse=True)
            return procs[:count]
        except Exception:
            return []

    def get_battery_metrics(self) -> Dict[str, Any]:
        """Reads battery state, percentage, and AC power status if available."""
        res = {"has_battery": False, "percent": 100, "plugged": True, "status_str": "🔌 Red CA"}
        try:
            bat = psutil.sensors_battery()
            if bat is not None:
                res["has_battery"] = True
                res["percent"] = int(bat.percent)
                res["plugged"] = bat.power_plugged
                if bat.power_plugged:
                    res["status_str"] = f"🔌 CA ({bat.percent}%)"
                else:
                    res["status_str"] = f"🔋 Batería ({bat.percent}%)"
        except Exception:
            pass
        return res

    def run(self):
        """Worker main loop."""
        psutil.cpu_percent(percpu=False)  # Initialize psutil cpu sampling
        
        while self._running:
            try:
                cpu_temp = self.get_cpu_temperature()
                cpu_total_pct = psutil.cpu_percent(percpu=False)
                cpu_cores_pct = psutil.cpu_percent(percpu=True)
                
                freq_info = psutil.cpu_freq()
                cpu_mhz = freq_info.current if freq_info else 0.0
                
                mem = psutil.virtual_memory()
                swap = psutil.swap_memory()
                gpu_metrics = self.get_gpu_metrics()
                bat_metrics = self.get_battery_metrics()
                
                metrics = {
                    "cpu_temp": round(cpu_temp, 1),
                    "cpu_usage": round(cpu_total_pct, 1),
                    "cpu_cores": cpu_cores_pct,
                    "cpu_freq_mhz": round(cpu_mhz, 0),
                    "ram_used_gb": round(mem.used / (1024 ** 3), 2),
                    "ram_total_gb": round(mem.total / (1024 ** 3), 2),
                    "ram_percent": round(mem.percent, 1),
                    "swap_used_gb": round(swap.used / (1024 ** 3), 2),
                    "swap_total_gb": round(swap.total / (1024 ** 3), 2),
                    "swap_percent": round(swap.percent, 1),
                    "gpu_temp": gpu_metrics["gpu_temp"],
                    "gpu_power_w": gpu_metrics["gpu_power_w"],
                    "vram_used_gb": gpu_metrics["vram_used_gb"],
                    "vram_total_gb": gpu_metrics["vram_total_gb"],
                    "vram_percent": gpu_metrics["vram_percent"],
                    "battery": bat_metrics,
                    "top_processes": self.get_top_processes(5),
                    "timestamp": time.time()
                }
                
                self.metrics_updated.emit(metrics)
            except Exception as err:
                print(f"[SensorThread Error] {err}")
                
            self.msleep(self.sample_interval_ms)
