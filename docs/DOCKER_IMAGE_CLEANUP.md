# Docker Image Cleanup Feature (OPSEC Mode)

## Overview

The Docker orchestration framework now supports **automatic image cleanup** after container execution. This is especially useful for:

- **🔒 OPSEC/Privacy**: Leave no traces of tools used on the system
- **💾 Disk Space**: Remove large images (e.g., Sherlock ~1GB)
- **🧪 Testing**: Ensure fresh image pulls every time
- **🔐 Security**: Remove sensitive tools after one-time use

## Usage

### Option 1: Per-Container Cleanup

Use the `cleanup_image` parameter when running containers:

```python
from src.orchestration.docker_manager import DockerManager

dm = DockerManager()

# Normal mode - image stays cached
output = dm.run_container(
    image_name="sherlock/sherlock",
    command=["username"],
    cleanup_image=False  # Default
)

# OPSEC mode - image auto-deleted after use
output = dm.run_container(
    image_name="sherlock/sherlock",
    command=["username"],
    cleanup_image=True  # 🔥 Image will be removed!
)
```

### Option 2: Workflow-Level Cleanup

Set cleanup mode for entire workflows:

```python
from src.orchestration.workflow_manager import WorkflowManager

# Normal mode
wm = WorkflowManager(cleanup_images=False)
results = wm.execute_workflow("username_check", "johndoe")

# OPSEC mode - all images removed after workflow
wm = WorkflowManager(cleanup_images=True)
results = wm.execute_workflow("username_check", "johndoe")
# Sherlock image automatically removed after execution
```

### Option 3: Manual Image Removal

Remove specific images manually:

```python
from src.orchestration.docker_manager import DockerManager

dm = DockerManager()

# Remove one image
dm.remove_image("sherlock/sherlock", force=True)

# Remove all OSINT tool images
results = dm.cleanup_all_tool_images(force=True)
# Returns: {"sherlock/sherlock": True, "secsi/theharvester": True, ...}
```

## API Reference

### DockerManager Methods

#### `run_container(..., cleanup_image=False)`

Run a container with optional image cleanup.

**Parameters:**
- `image_name` (str): Tool image name (must be in whitelist)
- `command` (str | list): Command to execute
- `environment` (dict, optional): Environment variables
- `timeout` (int): Timeout in seconds (default: 300)
- `cleanup_image` (bool): **Remove image after execution** (default: False)

**Returns:** Container output (str)

**Example:**
```python
dm = DockerManager()
output = dm.run_container(
    "sherlock/sherlock",
    ["johndoe"],
    cleanup_image=True  # OPSEC mode
)
```

---

#### `remove_image(image_name, force=False)`

Manually remove a Docker image.

**Parameters:**
- `image_name` (str): Image to remove (must be in whitelist)
- `force` (bool): Force removal even if containers exist (default: False)

**Returns:** bool (True if removed, False if not found)

**Example:**
```python
dm = DockerManager()
dm.remove_image("sherlock/sherlock", force=True)
```

---

#### `cleanup_all_tool_images(force=False)`

Remove all OSINT tool images.

**Parameters:**
- `force` (bool): Force removal (default: False)

**Returns:** dict mapping image names to removal status

**Example:**
```python
dm = DockerManager()
results = dm.cleanup_all_tool_images(force=True)
# {'sherlock/sherlock': True, 'secsi/theharvester': True, 'khast3x/h8mail': False}
```

---

### WorkflowManager

#### `WorkflowManager(cleanup_images=False)`

**Parameters:**
- `cleanup_images` (bool): Enable OPSEC mode for all workflows (default: False)

**Example:**
```python
# OPSEC mode - all images deleted after workflow
wm = WorkflowManager(cleanup_images=True)
wm.execute_workflow("domain_intel", "example.com")
# theHarvester and h8mail images auto-removed
```

## Execution Flow (OPSEC Mode)

```
User Request
    ↓
Pull Image (if needed)
    ↓
Start Container
    ↓
Execute Command
    ↓
Capture Output
    ↓
Remove Container ← Always happens
    ↓
Remove Image     ← Only if cleanup_image=True
    ↓
Return Results
```

## Use Cases

### 🔒 **OPSEC/Privacy**
```python
# No traces left on filesystem
wm = WorkflowManager(cleanup_images=True)
wm.execute_workflow("username_check", "target_user")
# System verification: docker images | grep sherlock
# → (no results)
```

### 💾 **Disk Space Management**
```python
# Remove 2GB+ of tool images
dm = DockerManager()
dm.cleanup_all_tool_images(force=True)
```

### 🧪 **Testing/Development**
```python
# Always use latest version
dm = DockerManager()
for test in tests:
    dm.run_container(
        "sherlock/sherlock",
        [test.username],
        cleanup_image=True  # Fresh pull next time
    )
```

### 🔐 **One-Time Operations**
```python
# Use tool once, then remove
dm = DockerManager()
output = dm.run_container(
    "khast3x/h8mail",
    ["-t", "sensitive@email.com"],
    cleanup_image=True  # Remove immediately after
)
```

## Image Sizes (Reference)

Typical OSINT tool image sizes:

| Tool | Size | Download Time (10 Mbps) |
|------|------|-------------------------|
| sherlock/sherlock | ~1.0 GB | ~13 minutes |
| secsi/theharvester | ~800 MB | ~10 minutes |
| khast3x/h8mail | ~500 MB | ~6 minutes |
| **Total** | **~2.3 GB** | **~30 minutes** |

**OPSEC benefit:** Free up 2.3GB and leave no traces  
**Performance cost:** Re-download if needed again

## Security Considerations

### ✅ **Safe to Use**
- Only whitelisted images can be removed
- Cannot accidentally remove system images
- Force flag prevents accidental data loss
- Cleanup happens in finally block (always executes)

### ⚠️ **Performance Trade-off**
- **Normal mode**: Fast reuse, but images stay on disk
- **OPSEC mode**: Slower (re-download), but zero traces

### 🔐 **OPSEC Recommendation**
For maximum privacy:
```python
wm = WorkflowManager(cleanup_images=True)
results = wm.execute_workflow("username_check", "target")

# Also clear any cached data
import shutil
shutil.rmtree(".osint_cache", ignore_errors=True)
```

## Examples

### Example 1: Normal Development Workflow
```python
# Keep images for fast iteration
dm = DockerManager()

# First run: downloads image
output1 = dm.run_container("sherlock/sherlock", ["user1"])

# Second run: uses cached image (fast!)
output2 = dm.run_container("sherlock/sherlock", ["user2"])

# Later: manually cleanup
dm.remove_image("sherlock/sherlock", force=True)
```

### Example 2: High-Security OPSEC Mode
```python
# Every execution is isolated
dm = DockerManager()

for target in sensitive_targets:
    output = dm.run_container(
        "sherlock/sherlock",
        [target],
        cleanup_image=True  # Zero persistence
    )
    process_results(output)
    
# No tool images remain on system
```

### Example 3: Bulk Cleanup Script
```python
#!/usr/bin/env python3
"""Remove all OSINT tool images."""
from src.orchestration.docker_manager import DockerManager

dm = DockerManager()
results = dm.cleanup_all_tool_images(force=True)

for image, removed in results.items():
    status = "✅ Removed" if removed else "❌ Failed"
    print(f"{status}: {image}")
```

## Troubleshooting

### "Failed to remove image: conflict"
**Cause:** Container using the image still exists  
**Solution:** Use `force=True`:
```python
dm.remove_image("sherlock/sherlock", force=True)
```

### Image removal seems slow
**Explanation:** Docker removes layers, which can take 5-10 seconds  
**This is normal** and indicates the image is being fully deleted

### Image keeps reappearing
**Check:** Are you running multiple workflows simultaneously?  
**Solution:** Wait for all workflows to complete before cleanup:
```python
wm = WorkflowManager(cleanup_images=False)
# ... run all workflows ...
dm.cleanup_all_tool_images(force=True)
```

## CLI Integration (Future)

When integrated into main.py, usage will be:

```bash
# Normal mode
python main.py --workflow username_check --target johndoe

# OPSEC mode
python main.py --workflow username_check --target johndoe --opsec

# Manual cleanup
python main.py --cleanup-images
```

## Demo Script

Run the included demo to see it in action:

```bash
python demo_image_cleanup.py
```

This will:
1. Show normal execution (image remains)
2. Show OPSEC mode (image deleted)
3. Demonstrate manual cleanup
4. Show bulk cleanup of all tools

---

**Last Updated:** 2025-11-28  
**Feature Added In:** Phase 1 Foundation  
**Status:** ✅ Fully Functional
