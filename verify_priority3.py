"""
Comprehensive test suite for Priority 3 features:
- Domain/Subdomain Enumeration
- Interactive Mode
"""
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_domain_enum_imports():
    """Test that domain enumeration module imports correctly."""
    print("\n=== Testing Domain Enumeration Module ===")
    try:
        from src.modules.domain_enum import DomainEnumerator, run_domain_enumeration
        print("✓ Domain enumeration imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_domain_enum_functionality():
    """Test domain enumeration functionality."""
    print("\n=== Testing Domain Enumeration Functionality ===")
    try:
        from src.modules.domain_enum import run_domain_enumeration
        
        print("Running DNS and CT log checks for example.com...")
        results = run_domain_enumeration("example.com", bruteforce=False)
        
        print(f"  - Domain: {results['domain']}")
        print(f"  - DNS Records Types Found: {len(results['dns_records'])}")
        print(f"  - Subdomain Count: {results['subdomain_count']}")
        
        if results['dns_records']:
            print(f"  - Sample DNS Record Types: {list(results['dns_records'].keys())[:3]}")
        
        print("✓ Domain enumeration functional test passed")
        return True
    except Exception as e:
        print(f"✗ Functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_interactive_imports():
    """Test that interactive mode imports correctly."""
    print("\n=== Testing Interactive Mode Module ===")
    try:
        from src.core.interactive import InteractiveWizard, run_interactive_mode
        print("✓ Interactive mode imports successful")
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_interactive_instantiation():
    """Test that InteractiveWizard can be instantiated."""
    print("\n=== Testing Interactive Mode Instantiation ===")
    try:
        from src.core.interactive import InteractiveWizard
        wizard = InteractiveWizard()
        
        # Test methods exist
        assert hasattr(wizard, 'run')
        assert hasattr(wizard, 'get_input')
        assert hasattr(wizard, 'select_option')
        assert hasattr(wizard, 'print_header')
        
        print("✓ InteractiveWizard class instantiated and verified")
        return True
    except Exception as e:
        print(f"✗ Instantiation test failed: {e}")
        return False

def test_all_priority2_modules():
    """Verify Priority 2 modules are still accessible."""
    print("\n=== Verifying Priority 2 Modules ===")
    modules_ok = True
    
    try:
        from src.modules.username_generator import generate_username_variations
        print("✓ Username generator OK")
    except Exception as e:
        print(f"✗ Username generator failed: {e}")
        modules_ok = False
    
    try:
        from src.core.cache_manager import get_cache_manager
        print("✓ Cache manager OK")
    except Exception as e:
        print(f"✗ Cache manager failed: {e}")
        modules_ok = False
    
    try:
        from src.reporting.markdown_report import generate_markdown_report
        from src.reporting.html_report import generate_html_report
        from src.reporting.pdf_report import generate_pdf_report
        from src.reporting.stix_export import generate_stix_report
        print("✓ All report generators OK")
    except Exception as e:
        print(f"✗ Report generators failed: {e}")
        modules_ok = False
    
    return modules_ok

def main():
    """Run all tests."""
    print("=" * 60)
    print("Priority 3 Feature Verification Suite")
    print("=" * 60)
    
    results = []
    
    # Priority 3 Tests
    results.append(("Domain Enum Imports", test_domain_enum_imports()))
    results.append(("Domain Enum Functionality", test_domain_enum_functionality()))
    results.append(("Interactive Mode Imports", test_interactive_imports()))
    results.append(("Interactive Mode Instantiation", test_interactive_instantiation()))
    
    # Verify Priority 2 still works
    results.append(("Priority 2 Modules", test_all_priority2_modules()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test_name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All Priority 3 features verified and working!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
