from typing import List, Dict, Any
import logging
from src.orchestration.docker_manager import DockerManager
from src.orchestration.adapters.sherlock_adapter import SherlockAdapter
from src.orchestration.adapters.theharvester_adapter import TheHarvesterAdapter
from src.orchestration.adapters.h8mail_adapter import H8MailAdapter
from src.orchestration.adapters.holehe_adapter import HoleheAdapter
from src.orchestration.adapters.phoneinfoga_adapter import PhoneInfogaAdapter
from src.orchestration.adapters.sublist3r_adapter import Sublist3rAdapter
from src.orchestration.adapters.photon_adapter import PhotonAdapter
from src.orchestration.adapters.exiftool_adapter import ExiftoolAdapter

logger = logging.getLogger(__name__)

class WorkflowManager:
    """
    Manages sequential execution of OSINT tools.
    """

    def __init__(self, cleanup_images: bool = False):
        """
        Initialize WorkflowManager.
        
        Args:
            cleanup_images: If True, remove Docker images after execution (OPSEC mode)
        """
        self.docker_manager = DockerManager()
        self.cleanup_images = cleanup_images
        self.adapters = {
            "sherlock": SherlockAdapter(self.docker_manager),
            "theharvester": TheHarvesterAdapter(self.docker_manager),
            "h8mail": H8MailAdapter(self.docker_manager),
            "holehe": HoleheAdapter(self.docker_manager),
            "phoneinfoga": PhoneInfogaAdapter(self.docker_manager),
            "sublist3r": Sublist3rAdapter(self.docker_manager),
            "photon": PhotonAdapter(self.docker_manager),
            "exiftool": ExiftoolAdapter(self.docker_manager)
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
