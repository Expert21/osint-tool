import requests
import logging

logger = logging.getLogger("OSINT_Tool")

def run_social_media_checks(target, target_type, config):
    """
    Checks for the existence of the target on various social media platforms.
    If target_type is 'individual', it assumes 'target' is a username.
    If target_type is 'company', it tries to find company pages.
    """
    results = []
    
    # Define platforms to check
    # Format: "Platform Name": "URL Pattern"
    platforms = {
        "Twitter": "https://twitter.com/{}",
        "Instagram": "https://www.instagram.com/{}",
        "Facebook": "https://www.facebook.com/{}",
        "LinkedIn": "https://www.linkedin.com/in/{}", # For individuals
        "LinkedIn Company": "https://www.linkedin.com/company/{}", # For companies
        "GitHub": "https://github.com/{}",
        "Pinterest": "https://www.pinterest.com/{}",
        "TikTok": "https://www.tiktok.com/@{}"
    }
    
    # Filter platforms based on target type
    if target_type == "company":
        # Remove individual-specific platforms or adjust URLs
        if "LinkedIn" in platforms:
            del platforms["LinkedIn"]
    else:
         if "LinkedIn Company" in platforms:
            del platforms["LinkedIn Company"]

    logger.info(f"Checking social media profiles for: {target}")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    for platform, url_pattern in platforms.items():
        url = url_pattern.format(target)
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                logger.info(f"Found potential profile on {platform}: {url}")
                results.append({
                    "platform": platform,
                    "url": url,
                    "status": "Found"
                })
            elif response.status_code == 404:
                logger.debug(f"No profile found on {platform}")
            else:
                logger.warning(f"Unknown status {response.status_code} for {platform}: {url}")
        except Exception as e:
            logger.error(f"Error checking {platform}: {e}")
            
    return results
