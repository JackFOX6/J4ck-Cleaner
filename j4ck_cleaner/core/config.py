import os
import json
from typing import Dict, Any, List

DEFAULT_PROTECTED_WHITELIST: List[str] = [
    "steam", "steamwebhelper", "proton", "wine", "java", "zomboid",
    "niri", "noctalia-shell", "kitty", "warp", "windsurf", "antigravity",
    "code", "vesktop", "discord", "obsidian", "firefox", "chromium",
    "pulseaudio", "pipewire", "wireplumber", "sddm", "Xorg", "Xwayland"
]

DEFAULT_SETTINGS: Dict[str, Any] = {
    "language": "es",
    "active_profile": "dev",
    "autostart_enabled": True,
    "autostart_method": "both",  # "desktop", "systemd", "both"
    "stealth_notifications": True,
    "sample_interval_ms": 1000,
    "thermal_threshold_c": 75.0,
    "protected_whitelist": DEFAULT_PROTECTED_WHITELIST
}


class SettingsManager:
    """
    Manages loading, saving, and autostart configuration for ~/.config/nocturne-guardian/settings.json
    """

    def __init__(self):
        self.config_dir = os.path.expanduser("~/.config/nocturne-guardian")
        self.settings_path = os.path.join(self.config_dir, "settings.json")
        self.settings: Dict[str, Any] = dict(DEFAULT_SETTINGS)
        self.load_settings()

    def load_settings(self):
        """Load user settings from JSON file if available, with .bak fallback."""
        if not os.path.exists(self.settings_path):
            bak_path = self.settings_path + ".bak"
            if os.path.exists(bak_path):
                self.settings_path = bak_path

        if not os.path.exists(self.settings_path):
            self.save_settings()
            return

        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                loaded = json.load(f)
                self.settings.update(loaded)
        except Exception as err:
            print(f"[SettingsManager Error] Failed to load settings.json: {err}")

    def save_settings(self):
        """Atomic save settings to JSON file with .bak backup."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            tmp_path = self.settings_path + ".tmp"
            bak_path = self.settings_path + ".bak"

            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)

            if os.path.exists(self.settings_path):
                os.replace(self.settings_path, bak_path)
            os.replace(tmp_path, self.settings_path)
            os.chmod(self.settings_path, 0o600)
        except Exception as err:
            print(f"[SettingsManager Error] Failed to save settings.json: {err}")

    def reset_to_defaults(self):
        """Reset settings to factory default state and save."""
        self.settings = dict(DEFAULT_SETTINGS)
        self.save_settings()

    def get_whitelist(self) -> List[str]:
        """Returns active whitelist of protected application names."""
        return self.settings.get("protected_whitelist", DEFAULT_PROTECTED_WHITELIST)

    def add_to_whitelist(self, app_name: str):
        """Adds an app name to the protection whitelist."""
        clean_name = app_name.strip().lower()
        if clean_name and clean_name not in self.settings["protected_whitelist"]:
            self.settings["protected_whitelist"].append(clean_name)
            self.save_settings()

    def remove_from_whitelist(self, app_name: str):
        """Removes an app name from the protection whitelist."""
        clean_name = app_name.strip().lower()
        if clean_name in self.settings["protected_whitelist"]:
            self.settings["protected_whitelist"].remove(clean_name)
            self.save_settings()

    def configure_autostart(self, enable: bool):
        """
        Configures dual autostart: Desktop Autostart (~/.config/autostart/)
        AND Systemd User Service (~/.config/systemd/user/).
        """
        self.settings["autostart_enabled"] = enable
        self.save_settings()

        # 1. Desktop Autostart (~/.config/autostart/nocturne-guardian.desktop)
        autostart_dir = os.path.expanduser("~/.config/autostart")
        desktop_auto_file = os.path.join(autostart_dir, "nocturne-guardian.desktop")
        
        if enable:
            try:
                os.makedirs(autostart_dir, exist_ok=True)
                content = """[Desktop Entry]
Name=J4ck Cleaner
Comment=AMD APU Thermal & RAM Optimization Suite
Exec=j4ck-cleaner
Icon=nocturne-guardian
Terminal=false
Type=Application
Categories=System;Monitor;
X-GNOME-Autostart-enabled=true
"""
                with open(desktop_auto_file, "w", encoding="utf-8") as f:
                    f.write(content)
            except Exception as err:
                print(f"[SettingsManager Autostart Error] Desktop autostart failed: {err}")
        else:
            if os.path.exists(desktop_auto_file):
                os.remove(desktop_auto_file)

        # 2. Systemd User Service (~/.config/systemd/user/nocturne-guardian.service)
        systemd_dir = os.path.expanduser("~/.config/systemd/user")
        service_file = os.path.join(systemd_dir, "nocturne-guardian.service")

        if enable:
            try:
                os.makedirs(systemd_dir, exist_ok=True)
                service_content = """[Unit]
Description=J4ck Cleaner Thermal & System Optimization Daemon
After=graphical-session.target

[Service]
Type=simple
ExecStart=/home/j4ck/.local/bin/j4ck-cleaner
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
"""
                with open(service_file, "w", encoding="utf-8") as f:
                    f.write(service_content)
            except Exception as err:
                print(f"[SettingsManager Systemd Error] Systemd user service failed: {err}")
        else:
            if os.path.exists(service_file):
                os.remove(service_file)


# Global settings manager instance
settings_mgr = SettingsManager()
