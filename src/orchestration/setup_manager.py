
import logging
from typing import Dict, Callable, Optional
import sys
from src.core.secrets_manager import SecretsManager

logger = logging.getLogger(__name__)

class SetupManager:
    """
    Manages interactive setup for tools.
    Supports modular registration of setup handlers.
    """
    
    def __init__(self):
        self.secrets_manager = SecretsManager()
        self.setup_handlers: Dict[str, Callable[[], None]] = {}
        
        # Register default handlers
        self.register_handler("ghunt", self._setup_ghunt)

    def register_handler(self, tool_name: str, handler: Callable[[], None]):
        """Register a setup handler for a tool."""
        self.setup_handlers[tool_name] = handler

    def run_setup(self, tool_name: Optional[str] = None):
        """Run setup for all tools or a specific tool."""
        if tool_name:
            if tool_name in self.setup_handlers:
                print(f"\\n--- Setting up {tool_name} ---")
                self.setup_handlers[tool_name]()
            else:
                logger.error(f"No setup handler found for {tool_name}")
        else:
            print("\\n=== Hermes Tool Setup ===")
            print("Select a tool to configure:")
            tools = list(self.setup_handlers.keys())
            for i, name in enumerate(tools, 1):
                print(f"{i}. {name}")
            print("0. Exit")
            
            try:
                choice = input("\\nEnter choice: ")
                if choice == "0":
                    return
                idx = int(choice) - 1
                if 0 <= idx < len(tools):
                    tool = tools[idx]
                    self.run_setup(tool)
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Invalid input.")

    def _setup_ghunt(self):
        """Setup handler for Ghunt."""
        print("Ghunt requires authentication (Google cookies).")
        print("This setup will run 'ghunt login' natively.")
        print("Ensure 'ghunt' is installed in your PATH.")
        
        try:
            import subprocess
            subprocess.run(["ghunt", "login"], check=True)
            print("\\n[+] Ghunt setup completed successfully.")
        except FileNotFoundError:
            print("\\n[!] 'ghunt' command not found. Please install it: pip install ghunt")
        except subprocess.CalledProcessError:
            print("\\n[!] Ghunt login failed.")
        except Exception as e:
            print(f"\\n[!] Unexpected error: {e}")
