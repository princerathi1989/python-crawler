import urllib.robotparser
from urllib.parse import urlparse
from typing import Dict, Optional


class RobotsChecker:
    """Handles robots.txt checking for URLs."""
    
    def __init__(self):
        self._robots_cache: Dict[str, urllib.robotparser.RobotFileParser] = {}
    
    def is_allowed(self, url: str, user_agent: str = "finance-crawler-mvp/0.1") -> bool:
        """Check if URL is allowed by robots.txt."""
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        
        # Get or create robot parser for this domain
        if base_url not in self._robots_cache:
            rp = urllib.robotparser.RobotFileParser()
            robots_url = f"{base_url}/robots.txt"
            rp.set_url(robots_url)
            try:
                rp.read()
            except Exception:
                # If robots.txt can't be read, assume allowed
                pass
            self._robots_cache[base_url] = rp
        
        robot_parser = self._robots_cache[base_url]
        
        try:
            return robot_parser.can_fetch(user_agent, url)
        except Exception:
            # If there's any error, assume allowed
            return True
