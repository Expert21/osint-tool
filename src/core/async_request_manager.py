import asyncio
import aiohttp
import logging
import random
import os
from typing import Optional, Dict, Any, List, Union

logger = logging.getLogger("OSINT_Tool")

class AsyncRequestManager:
    """
    Singleton class to manage async HTTP requests with rate limiting, retries, and proxy rotation.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AsyncRequestManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self, proxy_file: Optional[str] = None, auto_fetch_proxies: bool = False):
        if self.initialized:
            return
            
        self.session: Optional[aiohttp.ClientSession] = None
        self.sem = asyncio.Semaphore(10) 
        self.initialized = True
        
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
        ]
        
        # Proxy Management
        self.proxies: List[str] = []
        self.proxy_file = proxy_file
        self.auto_fetch = auto_fetch_proxies
        
        if self.proxy_file:
            self.load_proxies()
            
        if not self.proxies and self.auto_fetch:
            # We can't await here in __init__, so we'll do it lazily or require explicit call
            pass

    def load_proxies(self):
        """Load proxies from file"""
        if not self.proxy_file or not os.path.exists(self.proxy_file):
            return
            
        try:
            with open(self.proxy_file, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
            logger.info(f"Loaded {len(self.proxies)} proxies from {self.proxy_file}")
        except Exception as e:
            logger.error(f"Failed to load proxies: {e}")

    async def fetch_free_proxies(self):
        """Fetch free proxies from public sources"""
        logger.info("Auto-fetching free proxies...")
        url = "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
        
        try:
            # Use a temporary session to avoid circular dependency or issues
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        text = await response.text()
                        new_proxies = [line.strip() for line in text.splitlines() if line.strip()]
                        self.proxies.extend(new_proxies)
                        # Remove duplicates
                        self.proxies = list(set(self.proxies))
                        logger.info(f"Fetched {len(new_proxies)} proxies. Total: {len(self.proxies)}")
                        
                        # Save to file if configured
                        if self.proxy_file:
                            try:
                                with open(self.proxy_file, 'w') as f:
                                    f.write('\n'.join(self.proxies))
                            except Exception as e:
                                logger.warning(f"Could not save fetched proxies to file: {e}")
                    else:
                        logger.error(f"Failed to fetch proxies: HTTP {response.status}")
        except Exception as e:
            logger.error(f"Error fetching proxies: {e}")

    def get_proxy(self) -> Optional[str]:
        """Get a random proxy from the list"""
        if not self.proxies:
            return None
        return f"http://{random.choice(self.proxies)}"

    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create the ClientSession."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session

    async def close(self):
        """Close the ClientSession."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def fetch(
        self, 
        url: str, 
        method: str = "GET", 
        headers: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Any = None,
        json_data: Any = None,
        retries: int = 3,
        delay: float = 1.0
    ) -> Dict[str, Any]:
        """
        Perform an HTTP request with retries, rate limiting, and proxy rotation.
        """
        if headers is None:
            headers = {}
            
        if "User-Agent" not in headers:
            headers["User-Agent"] = random.choice(self.user_agents)

        session = await self.get_session()
        
        # Auto-fetch proxies if needed and enabled (lazy load)
        if not self.proxies and self.auto_fetch:
            await self.fetch_free_proxies()
            self.auto_fetch = False # Only try once to avoid loops
        
        async with self.sem:
            for attempt in range(retries):
                proxy = self.get_proxy()
                
                try:
                    await asyncio.sleep(random.uniform(0.1, 0.5))
                    
                    async with session.request(
                        method, 
                        url, 
                        headers=headers, 
                        params=params, 
                        data=data, 
                        json=json_data,
                        proxy=proxy
                    ) as response:
                        
                        if response.status == 429:
                            retry_after = int(response.headers.get("Retry-After", 5))
                            logger.warning(f"Rate limited by {url}. Waiting {retry_after}s...")
                            await asyncio.sleep(retry_after)
                            continue
                        
                        # 403 Forbidden might indicate a bad proxy or bot detection
                        if response.status == 403 and proxy:
                            logger.debug(f"Proxy {proxy} blocked by {url}")
                            # Optional: Remove bad proxy from list
                            # if proxy.replace("http://", "") in self.proxies:
                            #     self.proxies.remove(proxy.replace("http://", ""))
                            continue 
                            
                        try:
                            text = await response.text()
                        except UnicodeDecodeError:
                            text = await response.read()
                            
                        return {
                            "status": response.status,
                            "text": text,
                            "headers": dict(response.headers),
                            "url": str(response.url),
                            "ok": response.status < 400
                        }
                        
                except (aiohttp.ClientError, asyncio.TimeoutError, OSError) as e:
                    # Proxy errors often manifest as ClientProxyConnectionError, ServerDisconnectedError, etc.
                    logger.debug(f"Request failed ({attempt+1}/{retries}) with proxy {proxy}: {e}")
                    
                    if attempt == retries - 1:
                        logger.error(f"Max retries reached for {url}")
                        return {"status": 0, "text": "", "error": str(e), "ok": False}
                    
                    await asyncio.sleep(delay * (2 ** attempt))
                    
        return {"status": 0, "text": "", "error": "Unknown error", "ok": False}
