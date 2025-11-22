import asyncio
import logging
import random
from typing import Dict, List, Optional
from src.core.async_request_manager import AsyncRequestManager

logger = logging.getLogger("OSINT_Tool")

class AsyncSocialMediaChecker:
    """Async social media checker"""
    
    def __init__(self):
        self.request_manager = AsyncRequestManager()
    
    async def _check_profile_exists(self, url: str, platform: str) -> Optional[Dict[str, str]]:
        """
        Check if a profile exists asynchronously.
        """
        try:
            response = await self.request_manager.fetch(url, retries=2)
            
            if response["status"] == 200:
                if self._verify_profile_content(response["text"], platform):
                    logger.info(f"✓ Found verified profile on {platform}: {url}")
                    return {
                        "platform": platform,
                        "url": url,
                        "status": "Verified",
                        "status_code": 200
                    }
                else:
                    logger.warning(f"⚠ Profile found but verification failed on {platform}: {url}")
                    return {
                        "platform": platform,
                        "url": url,
                        "status": "Found (Unverified)",
                        "status_code": 200
                    }
            elif response["status"] == 404:
                logger.debug(f"✗ No profile found on {platform}")
                return None
            elif response["status"] == 403:
                logger.warning(f"⚠ Access forbidden on {platform} (possible blocking)")
                return None
            elif response["status"] == 429:
                logger.error(f"⚠ Rate limited on {platform}")
                return None
            else:
                return None
                
        except Exception as e:
            logger.error(f"✗ Error checking {platform}: {e}")
            return None
    
    def _verify_profile_content(self, content: str, platform: str) -> bool:
        """Verify content markers"""
        content = content.lower()
        
        verification_markers = {
            "twitter": ["profile", "tweets", "following", "followers"],
            "instagram": ["followers", "following", "posts", "instagram"],
            "facebook": ["facebook", "profile", "friends", "posts"],
            "linkedin": ["linkedin", "experience", "connections", "profile"],
            "github": ["repositories", "contributions", "github", "profile"],
            "pinterest": ["pinterest", "pins", "boards", "followers"],
            "tiktok": ["tiktok", "followers", "following", "likes"]
        }
        
        platform_key = platform.lower().replace(" company", "").replace("linkedin company", "linkedin")
        markers = verification_markers.get(platform_key, [])
        
        matches = sum(1 for marker in markers if marker in content)
        
        not_found_markers = ["page not found", "doesn't exist", "isn't available", "suspended"]
        has_not_found = any(marker in content for marker in not_found_markers)
        
        return matches >= 2 and not has_not_found


async def run_social_media_checks_async(target: str, target_type: str, config: Dict) -> List[Dict[str, str]]:
    """
    Async entry point for social media checks.
    """
    checker = AsyncSocialMediaChecker()
    results = []
    
    platforms_config = {
        "Twitter": ["https://twitter.com/{}", "https://x.com/{}"],
        "Instagram": ["https://www.instagram.com/{}"],
        "Facebook": ["https://www.facebook.com/{}"],
        "LinkedIn": ["https://www.linkedin.com/in/{}"],
        "LinkedIn Company": ["https://www.linkedin.com/company/{}"],
        "GitHub": ["https://github.com/{}"],
        "Pinterest": ["https://www.pinterest.com/{}"],
        "TikTok": ["https://www.tiktok.com/@{}"]
    }
    
    if target_type == "company":
        platforms_config.pop("LinkedIn", None)
    else:
        platforms_config.pop("LinkedIn Company", None)
    
    logger.info(f"Checking {len(platforms_config)} platforms for: {target}")
    
    tasks = []
    for platform, url_patterns in platforms_config.items():
        for url_pattern in url_patterns:
            url = url_pattern.format(target)
            tasks.append(checker._check_profile_exists(url, platform))
    
    # Run all checks concurrently
    check_results = await asyncio.gather(*tasks)
    
    # Filter out None results
    results = [r for r in check_results if r is not None]
    
    logger.info(f"Completed social media checks: {len(results)} profiles found")
    return results