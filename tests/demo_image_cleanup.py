#!/usr/bin/env python3
"""
Docker Image Cleanup Demo
Demonstrates the new OPSEC feature: automatic image deletion after use
"""

import logging
import sys
from src.orchestration.docker_manager import DockerManager, TRUSTED_IMAGES

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demo_image_cleanup():
    """Demonstrate the image cleanup functionality."""
    
    print("=" * 70)
    print("DOCKER IMAGE CLEANUP DEMO (OPSEC MODE)")
    print("=" * 70)
    print("\nThis demonstrates leaving NO TRACES after tool execution:\n")
    
    dm = DockerManager()
    
    if not dm.is_available:
        print("❌ Docker daemon not running. Please start Docker Desktop.")
        return False
    
    # Add alpine for demo
    TRUSTED_IMAGES["alpine"] = "alpine:latest"
    
    print("📊 SCENARIO 1: Normal execution (image remains)")
    print("-" * 70)
    
    try:
        # Normal execution - image stays
        print("\n1️⃣  Running container WITHOUT cleanup_image...")
        output = dm.run_container(
            image_name="alpine",
            command=["echo", "Normal mode - image will remain"],
            cleanup_image=False  # Default behavior
        )
        print(f"   Output: {output.strip()}")
        
        # Check if image exists
        try:
            image = dm.client.images.get("alpine:latest")
            print(f"   ✅ Image still exists: {image.tags[0]} ({image.short_id})")
        except:
            print("   ⚠️  Image not found (unexpected)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("📊 SCENARIO 2: OPSEC mode (image auto-deleted)")
    print("-" * 70)
    
    try:
        print("\n2️⃣  Running container WITH cleanup_image=True (OPSEC)...")
        output = dm.run_container(
            image_name="alpine",
            command=["echo", "OPSEC mode - image will be removed"],
            cleanup_image=True  # 🔥 OPSEC MODE
        )
        print(f"   Output: {output.strip()}")
        
        # Check if image was removed
        try:
            image = dm.client.images.get("alpine:latest")
            print(f"   ⚠️  Image still exists (unexpected): {image.tags[0]}")
        except:
            print("   ✅ Image successfully removed - NO TRACES!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 70)
    print("📊 SCENARIO 3: Manual image cleanup")
    print("-" * 70)
    
    try:
        # Pull image again for demo
        print("\n3️⃣  Pulling image to demonstrate manual cleanup...")
        dm.pull_image("alpine")
        
        print("   Manually removing image...")
        dm.remove_image("alpine", force=True)
        
        # Verify
        try:
            dm.client.images.get("alpine:latest")
            print("   ⚠️  Image still exists")
        except:
            print("   ✅ Image manually removed successfully")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("📊 SCENARIO 4: Bulk cleanup of all tool images")
    print("-" * 70)
    
    try:
        print("\n4️⃣  Cleaning up ALL OSINT tool images...")
        print("   Tools:")
        for tool in TRUSTED_IMAGES.keys():
            if tool != "alpine":  # Skip our test image
                print(f"      - {tool}")
        
        # This will remove all tool images if they exist
        results = dm.cleanup_all_tool_images(force=True)
        
        print("\n   Results:")
        for image_name, removed in results.items():
            if image_name != "alpine":
                status = "✅ Removed" if removed else "⏭️  Not present"
                print(f"      {status}: {image_name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ DEMO COMPLETE")
    print("=" * 70)
    print("\n📝 SUMMARY:")
    print("   • cleanup_image=False → Normal mode (images cached)")
    print("   • cleanup_image=True  → OPSEC mode (auto-delete after use)")
    print("   • remove_image()      → Manual image removal")
    print("   • cleanup_all_tool_images() → Bulk cleanup")
    print("\n💡 USE CASES:")
    print("   • OPSEC: Leave no traces of tools used")
    print("   • Privacy: Remove sensitive tool images")
    print("   • Disk space: Clean up large images (Sherlock ~1GB)")
    print("   • Testing: Ensure fresh pulls every time")
    print("=" * 70 + "\n")
    
    return True

def show_current_images():
    """Show what OSINT tool images are currently on the system."""
    print("\n" + "=" * 70)
    print("CURRENT OSINT TOOL IMAGES ON SYSTEM")
    print("=" * 70)
    
    try:
        dm = DockerManager()
        if not dm.is_available:
            print("Docker not available")
            return
        
        for tool_name, image_tag in TRUSTED_IMAGES.items():
            if tool_name == "alpine":
                continue
            try:
                image = dm.client.images.get(image_tag)
                size_mb = image.attrs['Size'] / (1024 * 1024)
                print(f"✅ {tool_name:20s} {size_mb:8.1f} MB   {image.short_id}")
            except:
                print(f"⏭️  {tool_name:20s} (not present)")
        
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("\n🔍 Checking current state...")
    show_current_images()
    
    print("\nPress Enter to run demo (or Ctrl+C to cancel)...")
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)
    
    success = demo_image_cleanup()
    
    print("\n🔍 Final state:")
    show_current_images()
    
    sys.exit(0 if success else 1)
