# -----------------------------------------------------------------------------
# Hermes OSINT - V2.0 Alpha
# This project is currently in an alpha state.
# -----------------------------------------------------------------------------

from typing import Dict, Any
from src.orchestration.interfaces import ToolAdapter
from src.orchestration.docker_manager import DockerManager
from src.core.input_validator import InputValidator

class Sublist3rAdapter(ToolAdapter):
    def __init__(self, docker_manager: DockerManager):
        self.docker_manager = docker_manager
        self.image = "aboul3la/sublist3r"

    def execute(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run Sublist3r against a domain.
        
        Args:
            target: Domain name
            config: Configuration dictionary
            
        Returns:
            Parsed results from Sublist3r
        """
        # SECURITY: Validate domain
        try:
            InputValidator.validate_domain(target)
        except ValueError as e:
            raise ValueError(f"Invalid domain: {e}")
        
        # Use list format to prevent shell injection
        command = ["-d", target, "-n"] # -n for no color
        output = self.docker_manager.run_container(self.image, command)
        return self.parse_results(output)

    def parse_results(self, output: str) -> Dict[str, Any]:
        """
        Parse Sublist3r output.
        """
        subdomains = []
        lines = output.splitlines()
        capture = False
        
        for line in lines:
            if "Total Unique Subdomains Found" in line:
                capture = False
                continue
            
            # Sublist3r usually prints subdomains plainly at the end or throughout
            # We'll look for lines that look like subdomains
            clean_line = line.strip()
            if clean_line and "." in clean_line and not " " in clean_line and not clean_line.startswith(("-", "[", "Error")):
                 subdomains.append(clean_line)
        
        return {"tool": "sublist3r", "results": subdomains, "raw_output": output}
