#!/usr/bin/env python3
"""
J4ck Cleaner - Open Source System & Thermal Optimizer
Main application entry point with CLI shortcut support.
"""

import sys
import os
import argparse
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

# Ensure package is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from j4ck_cleaner.core.optimizer import SystemOptimizerEngine
from j4ck_cleaner.core.profiles import ProfileManager
from j4ck_cleaner.ui.dashboard import J4ckCleanerWindow


def main():
    parser = argparse.ArgumentParser(
        description="J4ck Cleaner v1.2.5 - System & Thermal Optimizer for Linux (J4ckENI Framework)"
    )
    parser.add_argument("--clean", action="store_true", help="Ejecuta Turbo Clean & Cooldown instantáneo desde CLI y sale.")
    parser.add_argument("--report", action="store_true", help="Genera reporte de diagnóstico de sistema en JSON y sale.")
    parser.add_argument("--test", action="store_true", help="Ejecuta auto-diagnóstico de integridad de sistema y sale.")
    parser.add_argument("--info", action="store_true", help="Imprime estado rápido de CPU °C y RAM GB en 1 línea y sale.")
    parser.add_argument("--profile", type=str, choices=["dev", "gaming", "eco"], help="Cambia el perfil activo por defecto.")
    
    args, unknown = parser.parse_known_args()

    # Instant CLI Clean Mode
    if args.clean:
        optimizer = SystemOptimizerEngine()
        res = optimizer.clean_cache()
        print(f"[J4ck Cleaner CLI] {res['message']}")
        sys.exit(0)

    # Instant CLI Report Mode
    if args.report:
        optimizer = SystemOptimizerEngine()
        rpt_path = optimizer.generate_diagnostics_report()
        print(f"📊 [J4ck Cleaner CLI] Reporte generado en: {rpt_path}")
        sys.exit(0)

    # Instant CLI Test Mode
    if args.test:
        from j4ck_cleaner.core.selftest import selftest_mgr
        res = selftest_mgr.run_all_tests()
        print("🔍 [J4ck Cleaner CLI] Auto-Diagnóstico de Integridad:")
        for check in res["checks"]:
            status = "✓ PASS" if check["passed"] else "✗ WARN"
            print(f"  [{status}] {check['name']}: {check['details']}")
        sys.exit(0 if res["overall_pass"] else 1)

    # Instant CLI Info Mode (1-line status for Waybar/scripts)
    if args.info:
        import psutil
        from j4ck_cleaner.core.sensors import SystemSensorThread
        sensor = SystemSensorThread()
        temp = sensor.get_cpu_temperature()
        mem = psutil.virtual_memory()
        ram_used = mem.used / (1024 ** 3)
        ram_total = mem.total / (1024 ** 3)
        print(f"🛡️ J4ck Cleaner | CPU: {temp:.1f}°C | RAM: {ram_used:.1f}/{ram_total:.1f} GB ({mem.percent:.0f}%)")
        sys.exit(0)

    # Force Wayland native backend & software rendering optimization on Linux
    os.environ["QT_QPA_PLATFORM"] = "wayland;xcb"
    os.environ["QT_QUICK_BACKEND"] = "software"
    
    app = QApplication(sys.argv)
    app.setApplicationName("J4ck Cleaner")
    app.setOrganizationName("J4ckENIFramework")

    window = J4ckCleanerWindow()
    
    if args.profile:
        window.switch_profile(args.profile)
        
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
