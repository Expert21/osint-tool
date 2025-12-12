
import logging
import shutil
import requests
import docker
from typing import Dict, List, Any
from src.core.config_manager import ConfigManager

logger = logging.getLogger(__name__)

# Installation hints for native tools
TOOL_INSTALL_HINTS = {
    "sherlock": "pip install sherlock-project",
    "theharvester": "pip install theHarvester",
    "holehe": "pip install holehe",
    "phoneinfoga": "See https://github.com/sundowndev/phoneinfoga#installation",
    "subfinder": "go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
    "ghunt": "pip install ghunt",
    "h8mail": "pip install h8mail"
}

class HermesDoctor:
    """
    Diagnostic tool for Hermes OSINT.
    Checks system requirements, connectivity, and tool availability.
    """
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.results = {
            "docker": False,
            "internet": False,
            "config": False,
            "native_tools": {}
        }

    def check_docker(self) -> bool:
        """Check if Docker is available and running."""
        try:
            client = docker.from_env()
            client.ping()
            self.results["docker"] = True
            return True
        except Exception as e:
            logger.debug(f"Docker check failed: {e}")
            self.results["docker"] = False
            return False

    def check_internet(self) -> bool:
        """Check internet connectivity."""
        try:
            requests.get("https://google.com", timeout=5)
            self.results["internet"] = True
            return True
        except Exception:
            self.results["internet"] = False
            return False

    def check_config(self) -> bool:
        """Check if configuration is valid."""
        try:
            # Just try to load default config
            self.config_manager.load_config('default')
            self.results["config"] = True
            return True
        except Exception:
            self.results["config"] = False
            return False

    def check_native_tools(self) -> Dict[str, bool]:
        """Check for presence of native tools."""
        # Check all tools that have plugins
        tools = list(TOOL_INSTALL_HINTS.keys())
        for tool in tools:
            self.results["native_tools"][tool] = shutil.which(tool) is not None
        return self.results["native_tools"]

    def run_diagnostics(self) -> Dict[str, Any]:
        """Run all checks and return results."""
        logger.info("Running system diagnostics...")
        self.check_docker()
        self.check_internet()
        self.check_config()
        self.check_native_tools()
        return self.results

    def print_report(self):
        """Print a formatted report of the diagnostics."""
        print("\n=== Hermes Doctor Report ===\n")
        
        # Docker
        status = "[OK] Available" if self.results["docker"] else "[X] Not Available"
        print(f"Docker: {status}")
        if not self.results["docker"]:
            print("  -> Ensure Docker Desktop is installed and running.")
            
        # Internet
        status = "[OK] Connected" if self.results["internet"] else "[X] Disconnected"
        print(f"Internet: {status}")
        
        # Config
        status = "[OK] Valid" if self.results["config"] else "[X] Invalid"
        print(f"Configuration: {status}")
        
        # Native Tools
        print("\nNative Tools:")
        for tool, available in self.results["native_tools"].items():
            status = "[OK] Installed" if available else "[X] Not Found"
            print(f"  - {tool}: {status}")
            if not available and tool in TOOL_INSTALL_HINTS:
                print(f"      Install: {TOOL_INSTALL_HINTS[tool]}")
            
        print("\n============================")
