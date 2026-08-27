import os
import glob
import time
import logging
from datetime import datetime, timedelta


class SystemLogger:
    """
    Rotating daily logger with automatic 7-day hygiene cleanup.
    Saves event logs to ~/.config/nocturne-guardian/logs/
    """

    def __init__(self, retention_days: int = 7):
        self.retention_days = retention_days
        self.logs_dir = os.path.expanduser("~/.config/nocturne-guardian/logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        
        self.current_log_path = os.path.join(
            self.logs_dir, f"nocturne-guardian-{datetime.now().strftime('%Y-%m-%d')}.log"
        )
        self._setup_logger()
        self.cleanup_old_logs()

    def _setup_logger(self):
        self.logger = logging.getLogger("NocturneGuardian")
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.FileHandler(self.current_log_path, encoding="utf-8")
            formatter = logging.Formatter(
                "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def log(self, message: str, level: str = "info"):
        """Logs an event message."""
        if level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        else:
            self.logger.info(message)

    def cleanup_old_logs(self):
        """Purges log files older than retention_days for storage hygiene."""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            for log_file in glob.glob(os.path.join(self.logs_dir, "nocturne-guardian-*.log")):
                try:
                    file_time = datetime.fromtimestamp(os.path.getmtime(log_file))
                    if file_time < cutoff_date:
                        os.remove(log_file)
                except Exception:
                    continue
        except Exception as err:
            print(f"[Logger Error] Cleanup failed: {err}")


# Global logger instance
logger = SystemLogger()
