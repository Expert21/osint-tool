import re
import logging
import asyncio
from typing import List, Dict, Optional, Set
import dns.resolver
from validators import email as validate_email_format

logger = logging.getLogger("OSINT_Tool")

class EmailEnumerator:
    """
    Email enumeration module with async support for DNS checks.
    """
    
    def __init__(self):
        self.common_patterns = [
            "{first}.{last}@{domain}",
            "{first}{last}@{domain}",
            "{first}_{last}@{domain}",
            "{first}-{last}@{domain}",
            "{first}@{domain}",
            "{last}@{domain}",
            "{f}{last}@{domain}",
            "{first}{l}@{domain}",
            "{f}.{last}@{domain}",
            "{first}.{l}@{domain}",
            "{last}.{first}@{domain}",
            "{last}{first}@{domain}",
        ]
        
        self.common_domains = [
            "gmail.com",
            "outlook.com",
            "yahoo.com",
            "hotmail.com",
            "protonmail.com",
            "icloud.com"
        ]
    
    def generate_email_patterns(
        self, 
        first_name: str, 
        last_name: Optional[str] = None,
        domain: Optional[str] = None,
        custom_domains: Optional[List[str]] = None
    ) -> List[str]:
        """Generate potential email addresses"""
        emails = set()
        first = first_name.lower().strip()
        last = last_name.lower().strip() if last_name else ""
        f = first[0] if first else ""
        l = last[0] if last else ""
        
        domains_to_check = []
        if domain:
            domains_to_check.append(domain.lower().strip())
        if custom_domains:
            domains_to_check.extend([d.lower().strip() for d in custom_domains])
        if not domains_to_check:
            domains_to_check = self.common_domains
        
        for pattern in self.common_patterns:
            for dom in domains_to_check:
                try:
                    email = pattern.format(
                        first=first, last=last, f=f, l=l, domain=dom
                    )
                    if self.validate_email_format(email):
                        emails.add(email)
                except (KeyError, IndexError):
                    continue
        
        return sorted(list(emails))
    
    def validate_email_format(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False
        try:
            return validate_email_format(email) is True
        except:
            return False
    
    def verify_domain_mx_records_sync(self, domain: str) -> bool:
        """Synchronous DNS check (to be run in executor)"""
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            if mx_records:
                return True
            return False
        except Exception:
            return False

    async def verify_domain_mx_records(self, domain: str) -> bool:
        """Async wrapper for DNS check"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.verify_domain_mx_records_sync, domain)
    
    async def enumerate_emails(
        self,
        first_name: str,
        last_name: Optional[str] = None,
        domain: Optional[str] = None,
        custom_domains: Optional[List[str]] = None,
        verify_mx: bool = True
    ) -> Dict[str, any]:
        """
        Async main enumeration function.
        """
        logger.info(f"Starting email enumeration for: {first_name} {last_name or ''}")
        
        results = {
            "target_name": f"{first_name} {last_name or ''}".strip(),
            "emails_generated": [],
            "valid_format_count": 0,
            "domains_checked": [],
            "domains_with_mx": []
        }
        
        emails = self.generate_email_patterns(
            first_name=first_name,
            last_name=last_name,
            domain=domain,
            custom_domains=custom_domains
        )
        
        results["emails_generated"] = emails
        results["valid_format_count"] = len(emails)
        
        domains = set()
        for email in emails:
            domain_part = email.split('@')[1]
            domains.add(domain_part)
        
        results["domains_checked"] = sorted(list(domains))
        
        if verify_mx:
            logger.info(f"Verifying MX records for {len(domains)} domain(s)...")
            tasks = [self.verify_domain_mx_records(dom) for dom in domains]
            mx_results = await asyncio.gather(*tasks)
            
            for i, has_mx in enumerate(mx_results):
                if has_mx:
                    results["domains_with_mx"].append(list(domains)[i])
        
        logger.info(f"Email enumeration complete: {len(emails)} potential addresses generated")
        return results


async def run_email_enumeration_async(
    target_name: str,
    domain: Optional[str] = None,
    custom_domains: Optional[List[str]] = None,
    verify_mx: bool = True
) -> Dict[str, any]:
    """
    Async convenience function.
    """
    enumerator = EmailEnumerator()
    
    name_parts = target_name.strip().split()
    first_name = name_parts[0] if name_parts else ""
    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else None
    
    return await enumerator.enumerate_emails(
        first_name=first_name,
        last_name=last_name,
        domain=domain,
        custom_domains=custom_domains,
        verify_mx=verify_mx
    )
