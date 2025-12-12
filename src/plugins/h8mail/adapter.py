
from typing import Dict, Any
import json
import logging
from src.orchestration.interfaces import ToolAdapter
from src.orchestration.execution_strategy import ExecutionStrategy
from src.core.entities import ToolResult, Entity

logger = logging.getLogger(__name__)

class H8MailAdapter(ToolAdapter):
    """
    Adapter for h8mail (Email Breach Hunting).
    """

    def __init__(self, execution_strategy: ExecutionStrategy):
        self.execution_strategy = execution_strategy
        self.tool_name = "h8mail"

    def can_run(self) -> bool:
        """Check if h8mail is available."""
        return self.execution_strategy.is_available(self.tool_name)

    def execute(self, target: str, config: Dict[str, Any]) -> ToolResult:
        """
        Execute h8mail against the target email.
        
        Args:
            target: Email address to check
            config: Configuration dictionary (e.g., API keys)
            
        Returns:
            ToolResult containing the structured findings
        """
        # Construct command
        # -t: target
        # -j: json output (if supported, otherwise we parse stdout)
        # --loose: loose search (optional, maybe configurable)
        
        # Use /dev/stdout for output to ensure JSON is captured in the logs
        # and to satisfy the requirement for an argument to --json.
        output_file = "/dev/stdout"
        
        command = ["-t", target, "--json", output_file]
        
        # STEALTH: Use local breach compilation only, no external API calls
        if config.get("stealth_mode", False):
            command.append("--local")
        
        # Add API keys if provided in config
        # h8mail uses a config file usually, but can take some via CLI or env
        # For this MVP, we'll assume basic execution or env vars passed via DockerManager
        
        try:
            logger.info(f"Executing h8mail for {target}")
            output = self.execution_strategy.execute(self.tool_name, command, config)
            
            return self.parse_results(output)
            
        except Exception as e:
            logger.error(f"h8mail execution failed: {e}")
            return ToolResult(tool="h8mail", error=str(e))

    def parse_results(self, output: str) -> ToolResult:
        """
        Parse h8mail output.
        """
        import re
        entities = []
        
        # Strip ANSI color codes
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean_output = ansi_escape.sub('', output)
        
        try:
            # Look for JSON objects in the cleaned output
            # Matches { ... } with minimal assumption about content
            json_pattern = re.compile(r'\{.*\}')
            
            for line in clean_output.splitlines():
                line = line.strip()
                match = json_pattern.search(line)
                if match:
                    json_str = match.group(0)
                    try:
                        data = json.loads(json_str)
                        
                        # Handle "target" format: {"targets": [{"target": "...", "data": []}]}
                        if "targets" in data:
                            for target_data in data["targets"]:
                                if "breach" in target_data:
                                     # handle breach list if present
                                     pass
                                # Check 'data' field which might contain breach info
                                if "data" in target_data and isinstance(target_data["data"], list):
                                     for breach_item in target_data["data"]:
                                         entities.append(Entity(
                                             type="breach",
                                             value=str(breach_item),
                                             source="h8mail",
                                             metadata=target_data
                                         ))
                        
                        # Handle direct breach format (older versions or different flags)
                        if "target" in data and "breach" in data:
                             # data["breach"] can be a list or string
                             breaches = data.get("breach", [])
                             if isinstance(breaches, list):
                                 for breach in breaches:
                                     entities.append(Entity(
                                         type="breach",
                                         value=str(breach),
                                         source="h8mail",
                                         metadata=data
                                     ))
                             else:
                                 entities.append(Entity(
                                     type="breach",
                                     value=str(breaches),
                                     source="h8mail",
                                     metadata=data
                                 ))

                    except json.JSONDecodeError:
                        continue
                        
        except Exception as e:
            logger.warning(f"Failed to parse h8mail output: {e}")
            
        return ToolResult(
            tool="h8mail",
            entities=entities,
            raw_output=clean_output # Return cleaned output for better readability
        )
