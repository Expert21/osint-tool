"""
Final Integration Test - All Features
Tests all Priority 1, 2, and 3 features integrated into main.py
"""
import subprocess
import json
import os

def run_test(name, command, expected_success=True):
    """Run a test command and report results."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if expected_success:
        if result.returncode == 0:
            print("✅ PASSED")
            return True
        else:
            print(f"❌ FAILED (exit code: {result.returncode})")
            print(f"Error: {result.stderr}")
            return False
    else:
        print("✅ Command executed")
        return True

def main():
    print("="*60)
    print("OSINT Tool - Complete Integration Test Suite")
    print("="*60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Help menu
    tests_total += 1
    if run_test("Help Menu", "python main.py --help"):
        tests_passed += 1
    
    # Test 2: List profiles
    tests_total += 1
    if run_test("List Profiles", "python main.py --list-profiles"):
        tests_passed += 1
    
    # Test 3: Cache stats
    tests_total += 1
    if run_test("Cache Statistics", "python main.py --cache-stats"):
        tests_passed += 1
    
    # Test 4: Email enumeration
    tests_total += 1
    if run_test("Email Enumeration", 
                "python main.py --target testuser --type individual --email-enum --domain example.com --skip-search --skip-social --output test_email.json"):
        tests_passed += 1
        # Verify output
        if os.path.exists("test_email.json"):
            with open("test_email.json") as f:
                data = json.load(f)
                if data.get('emails', {}).get('valid_format_count', 0) > 0:
                    print(f"  ✓ Generated {data['emails']['valid_format_count']} emails")
    
    # Test 5: Domain enumeration
    tests_total += 1
    if run_test("Domain Enumeration",
                "python main.py --target example.com --type company --domain-enum --skip-search --skip-social --output test_domain.json"):
        tests_passed += 1
        # Verify output
        if os.path.exists("test_domain.json"):
            with open("test_domain.json") as f:
                data = json.load(f)
                dns_count = len(data.get('domain_data', {}).get('dns_records', {}))
                print(f"  ✓ Retrieved {dns_count} DNS record types")
    
    # Test 6: HTML Report
    tests_total += 1
    if run_test("HTML Report Generation",
                "python main.py --target testuser --type individual --skip-search --skip-social --output test.html"):
        tests_passed += 1
        if os.path.exists("test.html"):
            print("  ✓ HTML file created")
    
    # Test 7: Markdown Report
    tests_total += 1
    if run_test("Markdown Report Generation",
                "python main.py --target testuser --type individual --skip-search --skip-social --output test.md"):
        tests_passed += 1
        if os.path.exists("test.md"):
            print("  ✓ Markdown file created")
    
    # Test 8: PDF Report
    tests_total += 1
    if run_test("PDF Report Generation",
                "python main.py --target testuser --type individual --skip-search --skip-social --output test.pdf"):
        tests_passed += 1
        if os.path.exists("test.pdf"):
            print("  ✓ PDF file created")
    
    # Test 9: STIX Export
    tests_total += 1
    if run_test("STIX Export",
                "python main.py --target testuser --type individual --email-enum --domain example.com --skip-search --skip-social --output test.stix.json"):
        tests_passed += 1
        if os.path.exists("test.stix.json"):
            with open("test.stix.json") as f:
                data = json.load(f)
                if data.get('type') == 'bundle':
                    print(f"  ✓ STIX bundle with {len(data.get('objects', []))} objects")
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests Passed: {tests_passed}/{tests_total}")
    print(f"Success Rate: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed == tests_total:
        print("\n🎉 ALL TESTS PASSED! All features integrated successfully!")
        return 0
    else:
        print(f"\n⚠️ {tests_total - tests_passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit(main())
