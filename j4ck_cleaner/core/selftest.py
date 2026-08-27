import os
import sys
import psutil
from typing import Dict, Any


class SelfTestEngine:
    """
    Self-diagnostic and system integrity suite for J4ck Cleaner.
    Audits sysfs paths, Polkit rules, kernel modules, thread availability, and permissions.
    """

    def run_all_tests(self) -> Dict[str, Any]:
        """Runs comprehensive integrity audit and returns test matrix results."""
        results = {
            "overall_pass": True,
            "checks": []
        }

        # 1. Check Python Version (3.10+)
        py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        py_pass = sys.version_info >= (3, 10)
        results["checks"].append({
            "name": "Versión de Python",
            "passed": py_pass,
            "details": f"Python {py_ver} (Requerido >= 3.10)"
        })
        if not py_pass:
            results["overall_pass"] = False

        # 2. Check /proc/sys/vm/drop_caches Access
        drop_path = "/proc/sys/vm/drop_caches"
        drop_pass = os.path.exists(drop_path)
        results["checks"].append({
            "name": "Ruta Kernel drop_caches",
            "passed": drop_pass,
            "details": f"{drop_path} accesible" if drop_pass else "Ruta no encontrada"
        })
        if not drop_pass:
            results["overall_pass"] = False

        # 3. Check CPU Frequency sysfs paths
        cpufreq_path = "/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"
        cpufreq_pass = os.path.exists(cpufreq_path)
        results["checks"].append({
            "name": "Ruta Sysfs Gobernador CPU",
            "passed": cpufreq_pass,
            "details": f"{cpufreq_path} encontrado" if cpufreq_pass else "Gobernador sysfs no expuesto"
        })

        # 4. Check Polkit Policy File
        polkit_path = "/usr/share/polkit-1/actions/org.j4ckeniframework.nocturne-guardian.policy"
        polkit_pass = os.path.exists(polkit_path) or os.path.exists("assets/polkit/org.j4ckeniframework.nocturne-guardian.policy")
        results["checks"].append({
            "name": "Regla Polkit (Elevación Sin Password)",
            "passed": polkit_pass,
            "details": "Polkit policy detectada" if polkit_pass else "Polkit policy ausente en sistema"
        })

        # 5. Check Thermal Sensors
        temp_found = False
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                temp_found = True
        except Exception:
            pass

        results["checks"].append({
            "name": "Sensores Térmicos psutil",
            "passed": temp_found,
            "details": "Sensores hardware detectados" if temp_found else "Usando fallback dinámico"
        })

        # 6. Check Kernel Modules (amdgpu, k10temp, coretemp, zenpower)
        kmodules_found = []
        try:
            if os.path.exists("/proc/modules"):
                with open("/proc/modules", "r") as f:
                    content = f.read()
                    for mod in ["amdgpu", "k10temp", "coretemp", "zenpower"]:
                        if mod in content:
                            kmodules_found.append(mod)
        except Exception:
            pass

        mod_pass = len(kmodules_found) > 0
        mod_str = ", ".join(kmodules_found) if kmodules_found else "Ninguno específico (Usando acpitz)"
        results["checks"].append({
            "name": "Módulos de Kernel Térmicos/GPU",
            "passed": mod_pass,
            "details": f"Módulos activos: {mod_str}"
        })

        # 7. Check Display Server (Wayland / X11)
        w_display = os.environ.get("WAYLAND_DISPLAY", "")
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", os.environ.get("DESKTOP_SESSION", "Nativo"))
        is_wayland = bool(w_display) or "wayland" in desktop.lower() or "niri" in desktop.lower()
        
        results["checks"].append({
            "name": "Servidor Gráfico (Display Server)",
            "passed": True,
            "details": f"Wayland ({w_display or desktop})" if is_wayland else f"X11/Nativo ({desktop})"
        })
        # 8. Check psutil version >= 5.9
        try:
            psutil_ver = tuple(int(x) for x in psutil.__version__.split(".")[:2])
            psutil_pass = psutil_ver >= (5, 9)
            psutil_detail = f"psutil {psutil.__version__} (requerido >= 5.9)"
        except Exception:
            psutil_pass = False
            psutil_detail = "psutil no disponible"

        results["checks"].append({
            "name": "Dependencia psutil",
            "passed": psutil_pass,
            "details": psutil_detail
        })
        if not psutil_pass:
            results["overall_pass"] = False

        # 9. Check PySide6 version >= 6.4
        try:
            from PySide6 import __version__ as pyside_ver_str
            pyside_ver = tuple(int(x) for x in pyside_ver_str.split(".")[:2])
            pyside_pass = pyside_ver >= (6, 4)
            pyside_detail = f"PySide6 {pyside_ver_str} (requerido >= 6.4)"
        except Exception:
            pyside_pass = False
            pyside_detail = "PySide6 no disponible"

        results["checks"].append({
            "name": "Dependencia PySide6",
            "passed": pyside_pass,
            "details": pyside_detail
        })
        if not pyside_pass:
            results["overall_pass"] = False

        return results


# Global SelfTest Engine
selftest_mgr = SelfTestEngine()
