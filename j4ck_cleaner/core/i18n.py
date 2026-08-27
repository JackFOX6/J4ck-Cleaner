import os
import json
from typing import Dict, Any


class I18nEngine:
    """
    Lightweight internationalization engine reading JSON locale files.
    Default language: Spanish (LATAM).
    """

    def __init__(self, default_lang: str = "es"):
        self.lang = default_lang
        self.locales_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "locales")
        self.translations: Dict[str, str] = {}
        self.load_language(self.lang)

    def load_language(self, lang_code: str):
        """Loads translation JSON for the given language code."""
        self.lang = lang_code
        file_path = os.path.join(self.locales_dir, f"{lang_code}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    self.translations = json.load(f)
            except Exception as err:
                print(f"[I18n Engine Error] Failed to load {lang_code}.json: {err}")

    def t(self, key: str, default: str = "") -> str:
        """Translates a key into the active language, falling back to default."""
        return self.translations.get(key, default or key)


# Global i18n instance
i18n = I18nEngine("es")
