import os
import json
from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class PerformanceProfile:
    name: str
    display_name: str
    thermal_threshold_c: float
    sample_interval_ms: int
    auto_cache_clean: bool
    auto_clean_ram_pct: float
    description: str


DEFAULT_PROFILES: Dict[str, PerformanceProfile] = {
    "dev": PerformanceProfile(
        name="dev",
        display_name="Modo Developer (Equilibrado)",
        thermal_threshold_c=75.0,
        sample_interval_ms=1000,
        auto_cache_clean=True,
        auto_clean_ram_pct=85.0,
        description="Muestreo constante (1s), autolimpieza de RAM en 85% y umbral de 75°C para desarrollo fluido."
    ),
    "gaming": PerformanceProfile(
        name="gaming",
        display_name="Modo Gaming (Prioridad GPU/CPU)",
        thermal_threshold_c=78.0,
        sample_interval_ms=2000,
        auto_cache_clean=False,
        auto_clean_ram_pct=90.0,
        description="Muestreo reducido (2s) para minimizar latencia en juegos. Umbral térmico elevado a 78°C."
    ),
    "eco": PerformanceProfile(
        name="eco",
        display_name="Modo Eco / Stealth (Enfriamiento Máximo)",
        thermal_threshold_c=70.0,
        sample_interval_ms=1500,
        auto_cache_clean=True,
        auto_clean_ram_pct=75.0,
        description="Umbral conservador a 70°C. Mantiene la CPU fría y la RAM libre de fragmentación."
    )
}


class ProfileManager:
    """
    Manages loading, saving, and updating custom user profiles in ~/.config/nocturne-guardian/profiles.json
    """

    def __init__(self):
        self.config_dir = os.path.expanduser("~/.config/nocturne-guardian")
        self.config_path = os.path.join(self.config_dir, "profiles.json")
        self.profiles: Dict[str, PerformanceProfile] = dict(DEFAULT_PROFILES)
        self.load_profiles()

    def load_profiles(self):
        """Loads custom user profiles from JSON config file if present."""
        if not os.path.exists(self.config_path):
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for name, pdata in data.items():
                    self.profiles[name] = PerformanceProfile(**pdata)
        except Exception as err:
            print(f"[ProfileManager Error] Failed to load profiles: {err}")

    def save_profiles(self):
        """Saves current profiles to JSON file."""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            data = {name: asdict(prof) for name, prof in self.profiles.items()}
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as err:
            print(f"[ProfileManager Error] Failed to save profiles: {err}")

    def add_custom_profile(self, profile: PerformanceProfile):
        """Adds or updates a profile and saves config."""
        self.profiles[profile.name] = profile
        self.save_profiles()


PROFILES: Dict[str, PerformanceProfile] = ProfileManager().profiles
