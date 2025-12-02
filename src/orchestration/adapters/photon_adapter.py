# -----------------------------------------------------------------------------
# Hermes OSINT - V2.0 Alpha
# This project is currently in an alpha state.
# -----------------------------------------------------------------------------

from typing import Dict, Any
from src.orchestration.interfaces import ToolAdapter
from src.orchestration.execution_strategy import ExecutionStrategy
from src.core.input_validator import InputValidator
from src.core.url_validator import URLValidator


class PhotonAdapter(ToolAdapter):
    def __init__(self, execution_strategy: ExecutionStrategy):
        self.execution_strategy = execution_strategy
        self.tool_name = "photon"

    def can_run(self) -> bool:
        """Check if Photon is available."""
        return self.execution_strategy.is_available(self.tool_name)

    def execute(self, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run Photon against a URL.
        
        Args:
            target: URL or domain
            config: Configuration dictionary
            
        Returns:
            Parsed results from Photon
        """
        # SECURITY: Basic validation
        if not URLValidator.is_safe_url(target):
            raise ValueError(f"Invalid or unsafe URL: {target}")
            
        # Use list format to prevent shell injection
        command = ["-u", target, "--only-urls"]
        
        output = self.execution_strategy.execute(self.tool_name, command, config)
        return self.parse_results(output)

    def parse_results(self, output: str) -> Dict[str, Any]:
        """
        Parse Photon output.
        """
        # Photon saves to files, but also prints to stdout
        # We'll capture stdout for now
        urls = []
        for line in output.splitlines():
            if line.startswith("http"):
                urls.append(line.strip())
                
        return {"tool": "photon", "results": urls, "raw_output": output}
