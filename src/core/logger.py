import logging
import sys
import re
from colorama import init, Fore, Style

init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: Fore.CYAN + "%(asctime)s - %(levelname)s - %(message)s" + Style.RESET_ALL,
        logging.INFO: Fore.GREEN + "%(asctime)s - %(levelname)s - %(message)s" + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + "%(asctime)s - %(levelname)s - %(message)s" + Style.RESET_ALL,
        logging.ERROR: Fore.RED + "%(asctime)s - %(levelname)s - %(message)s" + Style.RESET_ALL,
        logging.CRITICAL: Fore.RED + Style.BRIGHT + "%(asctime)s - %(levelname)s - %(message)s" + Style.RESET_ALL
    }

    SENSITIVE_PATTERNS = [
        (re.compile(r'(api[_-]?key|token|password|secret)["\']?\s*[:=]\s*["\']?([^"\'&\s]+)', re.I), r'\1=***REDACTED***'),
        (re.compile(r'([?&])(api[_-]?key|token|password)=([^&]+)', re.I), r'\1\2=***REDACTED***'),
        (re.compile(r'\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})\b'), r'***EMAIL***'),
        (re.compile(r'\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b'), r'***IP***'),
    ]

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%H:%M:%S")
        formatted = formatter.format(record)
        
        # Sanitize
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            formatted = pattern.sub(replacement, formatted)
            
        return formatted

def setup_logger():
    """
    Sets up the logger with colored output.
    """
    logger = logging.getLogger("OSINT_Tool")
    logger.setLevel(logging.INFO)
    
    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(ColoredFormatter())
    
    if not logger.handlers:
        logger.addHandler(ch)
        
    return logger
