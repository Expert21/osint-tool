import logging
from googlesearch import search

logger = logging.getLogger("OSINT_Tool")

def run_search_engines(target, config):
    """
    Runs search engine queries for the target.
    """
    results = []
    logger.info(f"Searching Google for: {target}")
    
    # Basic Search
    try:
        for url in search(target, num_results=10, advanced=True):
            results.append({
                "source": "Google",
                "title": url.title,
                "url": url.url,
                "description": url.description
            })
    except Exception as e:
        logger.error(f"Google search failed: {e}")

    # Dorking (Basic)
    dorks = [
        f'site:linkedin.com "{target}"',
        f'site:twitter.com "{target}"',
        f'site:facebook.com "{target}"',
        f'filetype:pdf "{target}"'
    ]
    
    for dork in dorks:
        logger.info(f"Running dork: {dork}")
        try:
            for url in search(dork, num_results=5, advanced=True):
                 results.append({
                    "source": "Google Dork",
                    "query": dork,
                    "title": url.title,
                    "url": url.url,
                    "description": url.description
                })
        except Exception as e:
            logger.error(f"Dork search failed for '{dork}': {e}")
            
    return results
