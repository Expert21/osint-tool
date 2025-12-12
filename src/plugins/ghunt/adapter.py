
from typing import Dict, Any, List
import json
import re
import logging
from src.orchestration.interfaces import ToolAdapter
from src.orchestration.execution_strategy import ExecutionStrategy
from src.core.entities import ToolResult, Entity

logger = logging.getLogger(__name__)

class GhuntAdapter(ToolAdapter):
    def __init__(self, execution_strategy: ExecutionStrategy):
        self.execution_strategy = execution_strategy
        self.tool_name = "ghunt"

    def can_run(self) -> bool:
        """
        Check if Ghunt is available.
        Uses the execution strategy to check tool availability.
        """
        return self.execution_strategy.is_available(self.tool_name)

    def execute(self, target: str, config: Dict[str, Any]) -> ToolResult:
        """
        Run Ghunt against an email.
        CMD: ghunt email <email>
        
        Ghunt V2 output is rich text. We capture stdout and parse it.
        """
        # Construct command
        command = ["email", target]
        
        try:
            output = self.execution_strategy.execute(self.tool_name, command, config)
            return self.parse_results(output, target)
        except Exception as e:
            error_msg = str(e)
            # Make error message more actionable
            if "not found" in error_msg.lower():
                error_msg = "GHunt not installed. Install with: pip install ghunt"
            logger.error(f"Ghunt execution failed: {error_msg}")
            return ToolResult(tool="ghunt", error=error_msg)

    def _strip_ansi(self, text: str) -> str:
        """Remove ANSI escape codes from text."""
        ansi_pattern = re.compile(r'\x1b\[[0-9;]*m|\x1b\[[0-9;]*[A-Za-z]')
        return ansi_pattern.sub('', text)

    def parse_results(self, output: str, target: str) -> ToolResult:
        """
        Parse Ghunt output.
        Extracts Gaia ID, services, and other profile information.
        """
        # Clean the output by removing ANSI codes
        clean_output = self._strip_ansi(output)
        
        # Check for explicit failure
        if "[-] Target not found" in clean_output or "Target not found" in clean_output:
            logger.info("GHunt: Target not found")
            return ToolResult(tool="ghunt", entities=[], raw_output=clean_output)
        
        entities = []
        metadata = {}
        
        # Extract Gaia ID
        gaia_match = re.search(r'Gaia ID\s*:\s*(\d+)', clean_output)
        if gaia_match:
            metadata["gaia_id"] = gaia_match.group(1)
        
        # Extract Email (should be the target, but verify)
        email_match = re.search(r'Email\s*:\s*([^\s\n]+@[^\s\n]+)', clean_output)
        if email_match:
            metadata["email"] = email_match.group(1)
        
        # Extract Last profile edit
        edit_match = re.search(r'Last profile edit\s*:\s*([^\n]+)', clean_output)
        if edit_match:
            metadata["last_edit"] = edit_match.group(1).strip()
        
        # Extract User types
        user_types = re.findall(r'- (GOOGLE_[A-Z_]+)', clean_output)
        if user_types:
            metadata["user_types"] = user_types
        
        # Extract Google services
        services = []
        services_match = re.search(r'Activated Google services\s*:(.*?)(?:\n\n|\n🎮|\Z)', clean_output, re.DOTALL)
        if services_match:
            service_lines = services_match.group(1).strip().split('\n')
            for line in service_lines:
                line = line.strip()
                if line.startswith('-'):
                    services.append(line[1:].strip())
        if services:
            metadata["google_services"] = services
        
        # Extract profile picture URL
        pic_match = re.search(r'(https://lh3\.googleusercontent\.com/[^\s\n]+)', clean_output)
        if pic_match:
            metadata["profile_picture"] = pic_match.group(1)
        
        # Check if we found any profile data
        if metadata.get("gaia_id") or metadata.get("email") or services:
            entities.append(Entity(
                type="profile",
                value=metadata.get("email", target),
                source="ghunt",
                metadata=metadata
            ))
            logger.info(f"GHunt: Found profile for {target} (Gaia ID: {metadata.get('gaia_id', 'unknown')})")
        else:
            logger.warning(f"GHunt: Could not parse profile data from output")
        
        return ToolResult(tool="ghunt", entities=entities, raw_output=clean_output)

