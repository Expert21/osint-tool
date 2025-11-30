# -----------------------------------------------------------------------------
# Hermes OSINT - V2.0 Alpha
# This project is currently in an alpha state.
# -----------------------------------------------------------------------------

from typing import Dict, Any
import re
from src.orchestration.interfaces import ToolAdapter
from src.orchestration.docker_manager import DockerManager
from src.core.input_validator import InputValidator

class HoleheAdapter(ToolAdapter):
    def __init__(self, docker_manager: DockerManager):
        self.docker_manager = docker_manager
        self.image = "megadose/holehe"

    def execute(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run Holehe against an email address.
        
        Args:
            target: Email to check
            config: Configuration dictionary
            
        Returns:
            Parsed results from Holehe
        """
        # SECURITY: Validate email format
        if not InputValidator.validate_email(target):
             raise ValueError(f"Invalid email address: {target}")
        
        # Use list format to prevent shell injection
        command = [target, "--only-used", "--no-color"]
        output = self.docker_manager.run_container(self.image, command)
        return self.parse_results(output)

    def parse_results(self, output: str) -> Dict[str, Any]:
        """
        Parse Holehe output.
        """
        results = []
        for line in output.splitlines():
            if "[+]" in line:
                # Format: [+] Service
                service = line.replace("[+]", "").strip()
                results.append({"service": service, "status": "used"})
        
        return {"tool": "holehe", "results": results, "raw_output": output}
