# -----------------------------------------------------------------------------
# Hermes OSINT - V2.0 Alpha
# This project is currently in an alpha state.
# -----------------------------------------------------------------------------

from typing import List, Dict, Any
import logging
from src.orchestration.docker_manager import DockerManager
from src.orchestration.execution_strategy import (
    ExecutionStrategy,
    DockerExecutionStrategy,
    NativeExecutionStrategy,
    HybridExecutionStrategy
)
from src.orchestration.adapters.sherlock_adapter import SherlockAdapter
from src.orchestration.adapters.theharvester_adapter import TheHarvesterAdapter
from src.orchestration.adapters.h8mail_adapter import H8MailAdapter
from src.orchestration.adapters.holehe_adapter import HoleheAdapter
from src.orchestration.adapters.phoneinfoga_adapter import PhoneInfogaAdapter
from src.orchestration.adapters.subfinder_adapter import SubfinderAdapter
from src.orchestration.adapters.searxng_adapter import SearxngAdapter
from src.orchestration.adapters.photon_adapter import PhotonAdapter
from src.orchestration.adapters.exiftool_adapter import ExiftoolAdapter

logger = logging.getLogger(__name__)

class WorkflowManager:
    """
    Manages sequential execution of OSINT tools.
    """

    def __init__(self, cleanup_images: bool = False, execution_mode: str = "docker"):
        """
        Initialize WorkflowManager.
        
        Args:
            cleanup_images: If True, remove Docker images after execution (OPSEC mode)
            execution_mode: Execution mode - "docker", "native", or "hybrid"
        """
        self.docker_manager = DockerManager()
        self.cleanup_images = cleanup_images
        
        # Initialize execution strategy based on mode
        if execution_mode == "docker":
            self.execution_strategy = DockerExecutionStrategy(self.docker_manager)
        elif execution_mode == "native":
            self.execution_strategy = NativeExecutionStrategy()
        elif execution_mode == "hybrid":
            docker_strategy = DockerExecutionStrategy(self.docker_manager)
            native_strategy = NativeExecutionStrategy()
            self.execution_strategy = HybridExecutionStrategy(docker_strategy, native_strategy)
        else:
            raise ValueError(f"Invalid execution mode: {execution_mode}")
        
        # Initialize all adapters with the execution strategy
        self.adapters = {
            "sherlock": SherlockAdapter(self.execution_strategy),
            "theharvester": TheHarvesterAdapter(self.execution_strategy),
            "h8mail": H8MailAdapter(self.execution_strategy),
            "holehe": HoleheAdapter(self.execution_strategy),
            "phoneinfoga": PhoneInfogaAdapter(self.execution_strategy),
            "subfinder": SubfinderAdapter(self.execution_strategy),
            "searxng": SearxngAdapter(self.docker_manager),  # Service-based, needs DockerManager
            "photon": PhotonAdapter(self.execution_strategy),
            "exiftool": ExiftoolAdapter(self.execution_strategy)
        }

    def execute_workflow(self, workflow_name: str, target: str) -> Dict[str, Any]:
        """
        Execute a predefined workflow.
        
        Args:
            workflow_name: Name of the workflow (e.g., 'domain_intel')
            target: Initial target (domain or username)
            
        Returns:
            Aggregated results
        """
        results = {
            "workflow": workflow_name,
            "target": target,
            "steps": []
        }
        
        if workflow_name == "domain_intel":
            self._run_domain_intel(target, results)
        elif workflow_name == "username_check":
            self._run_username_check(target, results)
        else:
            raise ValueError(f"Unknown workflow: {workflow_name}")
            
        return results

    def _run_domain_intel(self, target: str, results: Dict[str, Any]):
        """
        Workflow: theHarvester -> h8mail
        1. Find emails associated with domain.
        2. Check found emails for breaches.
        """
        # Step 1: theHarvester
        logger.info(f"Starting step 1: theHarvester for {target}")
        harvester_results = self.adapters["theharvester"].execute(target, {})
        results["steps"].append(harvester_results)
        
        emails = harvester_results.get("emails", [])
        logger.info(f"Found {len(emails)} emails")
        
        # Step 2: h8mail (for each email found)
        # Note: In a real scenario, we might batch this or limit it.
        breach_results = []
        for email in emails:
            logger.info(f"Starting step 2: h8mail for {email}")
            h8_result = self.adapters["h8mail"].execute(email, {})
            breach_results.append(h8_result)
            
        results["steps"].append({
            "tool": "h8mail_batch",
            "results": breach_results
        })

    def _run_username_check(self, target: str, results: Dict[str, Any]):
        """
        Workflow: Sherlock
        1. Check username across platforms.
        """
        # Step 1: Sherlock
        logger.info(f"Starting step 1: Sherlock for {target}")
        sherlock_results = self.adapters["sherlock"].execute(target, {})
        results["steps"].append(sherlock_results)

    def _run_tool(self, tool_name: str, target: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper to run a tool with pre-flight checks and error handling.
        """
        if tool_name not in self.adapters:
            logger.warning(f"Tool {tool_name} not found in adapters.")
            return {"error": "Tool not found"}
            
        adapter = self.adapters[tool_name]
        
        if not adapter.can_run():
            logger.warning(f"Skipping {tool_name}: Tool not available (check installation/docker)")
            return {"skipped": True, "reason": "Not available"}
            
        try:
            logger.info(f"Running {tool_name} for {target}...")
            return adapter.execute(target, config)
        except Exception as e:
            logger.error(f"{tool_name} failed: {e}")
            return {"error": str(e)}

    def run_all_tools(
        self, 
        target: str, 
        target_type: str, 
        domain: str = None, 
        email: str = None, 
        phone: str = None,
        stealth_mode: bool = False,
        username_variations: List[str] = None
    ) -> Dict[str, Any]:
        """
        Run all applicable tools based on target type and provided inputs.
        """
        results = {
            "target": target,
            "target_type": target_type,
            "tool_results": {}
        }
        
        from src.core.input_validator import InputValidator

        # Common config for all adapters
        tool_config = {
            "stealth_mode": stealth_mode
        }

        # Tools for Individuals
        if target_type == "individual":
            # Sherlock (Username)
            # Special handling for variations
            if "sherlock" in self.adapters:
                adapter = self.adapters["sherlock"]
                if adapter.can_run():
                    try:
                        logger.info(f"Running Sherlock for {target}...")
                        sherlock_res = adapter.execute(target, tool_config)
                        
                        # Variations check
                        if username_variations:
                            logger.info(f"Running Sherlock for {len(username_variations)} variations...")
                            sherlock_res["variations"] = []
                            for variant in username_variations:
                                try:
                                    var_res = adapter.execute(variant, tool_config)
                                    if var_res.get("results"):
                                        sherlock_res["variations"].append({
                                            "variant": variant,
                                            "results": var_res.get("results")
                                        })
                                except Exception as e:
                                    logger.warning(f"Sherlock variation {variant} failed: {e}")
                        
                        results["tool_results"]["sherlock"] = sherlock_res
                    except Exception as e:
                        logger.error(f"Sherlock failed: {e}")
                        results["tool_results"]["sherlock"] = {"error": str(e)}
                else:
                    logger.warning("Skipping Sherlock: Tool not available")
                    results["tool_results"]["sherlock"] = {"skipped": True, "reason": "Not available"}

            # Holehe (Email)
            if email:
                results["tool_results"]["holehe"] = self._run_tool("holehe", email, tool_config)
            
            # PhoneInfoga (Phone)
            if phone:
                results["tool_results"]["phoneinfoga"] = self._run_tool("phoneinfoga", phone, tool_config)

        # Tools for Companies
        elif target_type == "company":
            # Determine domain
            target_domain = domain
            if not target_domain:
                try:
                    InputValidator.validate_domain(target)
                    target_domain = target
                except ValueError:
                    pass
            
            if target_domain:
                # Company tools
                company_tools = ["theharvester", "subfinder", "photon"]
                for tool in company_tools:
                    results["tool_results"][tool] = self._run_tool(tool, target_domain, tool_config)
            else:
                logger.warning("No valid domain provided for company tools.")

        return results
