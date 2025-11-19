import sys
import logging
from src.modules.domain_enum import run_domain_enumeration
from src.core.interactive import run_interactive_mode

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("OSINT_Tool")

def test_domain_enum():
    print("\n--- Testing Domain Enumeration ---")
    domain = "example.com"
    print(f"Running enumeration for: {domain}")
    
    # Run without bruteforce for speed
    results = run_domain_enumeration(domain, bruteforce=False)
    
    print(f"DNS Records Found: {list(results['dns_records'].keys())}")
    print(f"Subdomains Found: {len(results['subdomains'])}")
    if results['subdomains']:
        print(f"Sample Subdomains: {results['subdomains'][:5]}")

def test_interactive_wizard():
    print("\n--- Testing Interactive Wizard ---")
    print("Note: This requires user input. Since we are in a non-interactive test environment,")
    print("we will just instantiate the class to ensure it imports and initializes correctly.")
    
    from src.core.interactive import InteractiveWizard
    wizard = InteractiveWizard()
    print("InteractiveWizard class instantiated successfully.")

if __name__ == "__main__":
    test_domain_enum()
    test_interactive_wizard()
    print("\nPriority 3 Modules (Domain Enum & Interactive) created successfully.")
