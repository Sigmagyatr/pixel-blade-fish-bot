"""
Panic Webhook System
Sends Discord notifications when fishing UI not detected
"""

import time
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Try to import requests, but handle case where it's not available
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests module not available - Discord notifications disabled")

class PanicWebhookSystem:
    def __init__(self):
        self.webhook_url = ""
        self.enabled = False
        self.last_panic_time = 0
        self.panic_cooldown = 300  # 5 minutes between panic messages
        self.consecutive_failures = 0
        self.max_failures = 5  # Send panic after 5 consecutive failures
    
    def configure(self, webhook_url: str, enabled: bool):
        """Configure panic webhook settings"""
        self.webhook_url = webhook_url
        self.enabled = enabled and REQUESTS_AVAILABLE
        self.consecutive_failures = 0
        self.last_panic_time = 0
        
        if not REQUESTS_AVAILABLE and enabled:
            logger.warning("Cannot enable panic webhook - requests module not available")
    
    def check_fishing_status(self, fishing_detected: bool):
        """Check fishing status and send panic if needed"""
        if not self.enabled or not self.webhook_url:
            return
        
        current_time = time.time()
        
        if fishing_detected:
            # Reset failures on successful detection
            if self.consecutive_failures > 0:
                logger.info(f"Fishing UI detected after {self.consecutive_failures} failures")
            self.consecutive_failures = 0
        else:
            # Increment failures
            self.consecutive_failures += 1
            
            # Check if we should send panic
            if (self.consecutive_failures >= self.max_failures and 
                current_time - self.last_panic_time > self.panic_cooldown):
                self.send_panic_message()
                self.last_panic_time = current_time
    
    def send_panic_message(self):
        """Send panic webhook message"""
        if not REQUESTS_AVAILABLE:
            logger.warning("Cannot send panic webhook - requests module not available")
            return
            
        try:
            embed = {
                "title": "🚨 FISHING BOT PANIC ALERT",
                "description": f"Bot cannot detect fishing UI for {self.consecutive_failures} consecutive attempts!",
                "color": 0xFF0000,
                "fields": [
                    {
                        "name": "Status",
                        "value": "⚠️ FISHING UI NOT DETECTED",
                        "inline": True
                    },
                    {
                        "name": "Consecutive Failures",
                        "value": str(self.consecutive_failures),
                        "inline": True
                    },
                    {
                        "name": "Action Required",
                        "value": "Check if Pixel Blade is running and visible",
                        "inline": False
                    }
                ],
                "footer": {
                    "text": "Pixel Blade Fishing Bot - Panic System"
                }
            }
            
            response = requests.post(self.webhook_url, json={"embeds": [embed]}, timeout=10)
            
            if response.status_code == 204:
                logger.info(f"Panic webhook sent successfully after {self.consecutive_failures} failures")
            else:
                logger.error(f"Panic webhook failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to send panic webhook: {e}")
    
    def reset(self):
        """Reset panic system"""
        self.consecutive_failures = 0
        self.last_panic_time = 0
        logger.info("Panic webhook system reset")
    
    def get_status(self) -> Dict:
        """Get current panic system status"""
        return {
            'enabled': self.enabled,
            'webhook_configured': bool(self.webhook_url),
            'requests_available': REQUESTS_AVAILABLE,
            'consecutive_failures': self.consecutive_failures,
            'last_panic_time': self.last_panic_time,
            'cooldown_remaining': max(0, self.panic_cooldown - (time.time() - self.last_panic_time))
        }
