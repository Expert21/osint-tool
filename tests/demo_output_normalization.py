#!/usr/bin/env python3
"""
Output Normalization Demo
Shows how Hermes normalizes outputs from different tools into a unified format
"""

import json
from src.orchestration.adapters.sherlock_adapter import SherlockAdapter
from src.orchestration.adapters.theharvester_adapter import TheHarvesterAdapter
from src.orchestration.adapters.h8mail_adapter import H8MailAdapter
from src.orchestration.docker_manager import DockerManager

def demo_individual_outputs():
    """Show how each tool's output is normalized."""
    
    print("=" * 80)
    print("INDIVIDUAL TOOL OUTPUT NORMALIZATION")
    print("=" * 80)
    
    # Create mock Docker manager for parsing demo
    dm = DockerManager()
    
    # 1. SHERLOCK OUTPUT
    print("\n📱 SHERLOCK (Username Enumeration)")
    print("-" * 80)
    
    sherlock = SherlockAdapter(dm)
    
    # Simulate Sherlock's raw output
    raw_sherlock_output = """
[*] Checking username johndoe on:
[+] Instagram: https://www.instagram.com/johndoe
[+] Twitter: https://twitter.com/johndoe
[+] GitHub: https://github.com/johndoe
[-] Facebook: Not Found
[+] Reddit: https://www.reddit.com/user/johndoe
"""
    
    sherlock_normalized = sherlock.parse_results(raw_sherlock_output)
    
    print("Raw output (excerpt):")
    print("  [+] Instagram: https://www.instagram.com/johndoe")
    print("  [+] Twitter: https://twitter.com/johndoe")
    print("\n✅ Normalized output:")
    print(json.dumps(sherlock_normalized, indent=2))
    
    # 2. THEHARVESTER OUTPUT
    print("\n\n📧 THEHARVESTER (Email/Domain Enumeration)")
    print("-" * 80)
    
    harvester = TheHarvesterAdapter(dm)
    
    # Simulate TheHarvester's raw output
    raw_harvester_output = """
*******************************************************************
*  _   _                                            _             *
* | |_| |__   ___    H a r v e s t e r    __      __ | |__   ___  *
*******************************************************************

[*] Target: johndoe.com

[+] Emails found:
john@johndoe.com
contact@johndoe.com
admin@johndoe.com

[+] Hosts found:
192.168.1.1: mail.johndoe.com
"""
    
    harvester_normalized = harvester.parse_results(raw_harvester_output)
    
    print("Raw output (excerpt):")
    print("  john@johndoe.com")
    print("  contact@johndoe.com")
    print("\n✅ Normalized output:")
    print(json.dumps(harvester_normalized, indent=2)[:500] + "...")
    
    # 3. H8MAIL OUTPUT
    print("\n\n🔓 H8MAIL (Breach Checking)")
    print("-" * 80)
    
    h8mail = H8MailAdapter(dm)
    
    # Simulate h8mail's raw output
    raw_h8mail_output = """
[INFO] Checking john@johndoe.com
{"target": "john@johndoe.com", "breach": "Collection1", "email": "john@johndoe.com"}
{"target": "john@johndoe.com", "breach": "LinkedIn2021", "email": "john@johndoe.com"}
[INFO] Done
"""
    
    h8mail_normalized = h8mail.parse_results(raw_h8mail_output)
    
    print("Raw output (excerpt):")
    print('  {"target": "john@johndoe.com", "breach": "Collection1"}')
    print("\n✅ Normalized output:")
    print(json.dumps(h8mail_normalized, indent=2))

def demo_workflow_aggregation():
    """Show how WorkflowManager aggregates multiple tools."""
    
    print("\n\n" + "=" * 80)
    print("WORKFLOW-LEVEL AGGREGATION")
    print("=" * 80)
    
    # Simulate what WorkflowManager.execute_workflow() returns
    workflow_result = {
        "workflow": "username_check",
        "target": "johndoe",
        "steps": [
            {
                "tool": "sherlock",
                "results": [
                    {"service": "Instagram", "url": "https://www.instagram.com/johndoe"},
                    {"service": "Twitter", "url": "https://twitter.com/johndoe"},
                    {"service": "GitHub", "url": "https://github.com/johndoe"},
                    {"service": "Reddit", "url": "https://www.reddit.com/user/johndoe"}
                ],
                "raw_output": "[+] Instagram: https://..."
            }
        ]
    }
    
    print("\n📊 Workflow Output Structure:")
    print(json.dumps(workflow_result, indent=2))
    
    print("\n\n💡 Key Points:")
    print("  • 'workflow': Identifies which workflow was run")
    print("  • 'target': The original search target")
    print("  • 'steps': Array of results from each tool in sequence")
    print("  • Each step has: 'tool', 'results', 'raw_output'")

def demo_unified_output_format():
    """Show the proposed unified Hermes output format."""
    
    print("\n\n" + "=" * 80)
    print("UNIFIED HERMES OUTPUT FORMAT (Proposed)")
    print("=" * 80)
    
    # This is what the final unified output could look like
    hermes_output = {
        "scan_metadata": {
            "target": "johndoe",
            "scan_type": "username_enumeration",
            "timestamp": "2025-11-28T10:56:00Z",
            "duration_seconds": 45.3,
            "tools_used": ["sherlock"],
            "success": True
        },
        "findings": {
            "social_media": [
                {
                    "platform": "Instagram",
                    "url": "https://www.instagram.com/johndoe",
                    "username": "johndoe",
                    "verified": True,
                    "source": "sherlock"
                },
                {
                    "platform": "Twitter",
                    "url": "https://twitter.com/johndoe",
                    "username": "johndoe",
                    "verified": True,
                    "source": "sherlock"
                },
                {
                    "platform": "GitHub",
                    "url": "https://github.com/johndoe",
                    "username": "johndoe",
                    "verified": True,
                    "source": "sherlock"
                },
                {
                    "platform": "Reddit",
                    "url": "https://www.reddit.com/user/johndoe",
                    "username": "johndoe",
                    "verified": True,
                    "source": "sherlock"
                }
            ],
            "emails": [],
            "breaches": [],
            "domains": []
        },
        "raw_data": {
            "sherlock": {
                "exit_code": 0,
                "output": "[+] Instagram: https://...",
                "platforms_checked": 350,
                "platforms_found": 4
            }
        },
        "summary": {
            "total_findings": 4,
            "social_media_accounts": 4,
            "email_addresses": 0,
            "data_breaches": 0,
            "risk_score": "LOW"
        }
    }
    
    print("\n🎯 Unified Output for 'johndoe':")
    print(json.dumps(hermes_output, indent=2))
    
    print("\n\n📋 Output Structure:")
    print("  1. scan_metadata   → When, what, how long")
    print("  2. findings        → Categorized results (social_media, emails, breaches)")
    print("  3. raw_data        → Original tool outputs for reference")
    print("  4. summary         → Quick statistics and risk assessment")

def demo_domain_workflow():
    """Show domain intelligence workflow output."""
    
    print("\n\n" + "=" * 80)
    print("DOMAIN INTELLIGENCE WORKFLOW (domain_intel)")
    print("=" * 80)
    
    hermes_output = {
        "scan_metadata": {
            "target": "johndoe.com",
            "scan_type": "domain_intelligence",
            "timestamp": "2025-11-28T10:56:00Z",
            "duration_seconds": 120.5,
            "tools_used": ["theharvester", "h8mail"],
            "success": True
        },
        "findings": {
            "emails": [
                {
                    "address": "john@johndoe.com",
                    "source": "theharvester",
                    "breached": True,
                    "breaches": ["Collection1", "LinkedIn2021"]
                },
                {
                    "address": "contact@johndoe.com",
                    "source": "theharvester",
                    "breached": False,
                    "breaches": []
                },
                {
                    "address": "admin@johndoe.com",
                    "source": "theharvester",
                    "breached": True,
                    "breaches": ["Collection1"]
                }
            ],
            "domains": [
                "mail.johndoe.com",
                "www.johndoe.com"
            ],
            "breaches": [
                {
                    "name": "Collection1",
                    "affected_emails": ["john@johndoe.com", "admin@johndoe.com"],
                    "severity": "HIGH"
                },
                {
                    "name": "LinkedIn2021",
                    "affected_emails": ["john@johndoe.com"],
                    "severity": "MEDIUM"
                }
            ]
        },
        "summary": {
            "total_findings": 7,
            "emails_found": 3,
            "emails_breached": 2,
            "unique_breaches": 2,
            "risk_score": "HIGH"
        }
    }
    
    print("\n🎯 Unified Output for 'johndoe.com':")
    print(json.dumps(hermes_output, indent=2))

def main():
    """Run all normalization demos."""
    
    print("\n" + "=" * 80)
    print(" " * 20 + "HERMES OUTPUT NORMALIZATION DEMO")
    print(" " * 25 + "Target: johndoe")
    print("=" * 80)
    
    # Show individual tool outputs
    demo_individual_outputs()
    
    # Show workflow aggregation
    demo_workflow_aggregation()
    
    # Show unified format
    demo_unified_output_format()
    
    # Show domain workflow
    demo_domain_workflow()
    
    print("\n\n" + "=" * 80)
    print("📝 SUMMARY")
    print("=" * 80)
    print("""
CURRENT STATE (Phase 1 - IMPLEMENTED ✅):
  • Each adapter normalizes its own output
  • WorkflowManager aggregates results into 'steps' array
  • Structure: {workflow, target, steps: [{tool, results, raw_output}]}

NEXT LEVEL (Phase 2 - PROPOSED):
  • ResultNormalizer class to unify all outputs
  • Category-based organization (social_media, emails, breaches)
  • Cross-tool correlation (link breaches to emails)
  • Risk scoring and summary statistics
  • Clean JSON export for reporting

EXAMPLE FLOW:
  1. User: "python main.py --workflow username_check --target johndoe"
  2. WorkflowManager runs Sherlock
  3. SherlockAdapter normalizes: {tool: "sherlock", results: [...]}
  4. ResultNormalizer unifies: {scan_metadata, findings, summary}
  5. ReportGenerator exports: JSON, PDF, HTML
  6. User gets: Clean, professional report with all findings
""")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
