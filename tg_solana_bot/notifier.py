import aiohttp
import logging
import os
from typing import Optional, List

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str, chat_ids: Optional[List[str]] = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.chat_ids = chat_ids or [chat_id] if chat_id else []
        self.session: Optional[aiohttp.ClientSession] = None
        self.base_url = f"https://api.telegram.org/bot{bot_token}"

    async def __aenter__(self):
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _ensure_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None

    async def send_message(self, text: str) -> bool:
        """Send a text message to all configured chat IDs."""
        await self._ensure_session()
        
        success = True
        for chat_id in self.chat_ids:
            try:
                payload = {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML"
                }
                
                async with self.session.post(f"{self.base_url}/sendMessage", json=payload, timeout=30) as response:
                    if response.status != 200:
                        logger.error(f"Failed to send message to {chat_id}: {response.status}")
                        success = False
                    else:
                        logger.info(f"Message sent successfully to {chat_id}")
                        
            except Exception as e:
                logger.error(f"Error sending message to {chat_id}: {e}")
                success = False
                
        return success

    async def send_media(self, media_url: str, caption: str = "", media_type: str = "photo") -> bool:
        """Send media (photo, video, etc.) with caption to all configured chat IDs."""
        await self._ensure_session()
        
        success = True
        for chat_id in self.chat_ids:
            try:
                # Check if it's a local file
                if os.path.exists(media_url):
                    # Local file - use sendDocument or sendPhoto
                    with open(media_url, 'rb') as file:
                        files = {'document': file} if media_type == "document" else {'photo': file}
                        data = {
                            "chat_id": chat_id,
                            "caption": caption,
                            "parse_mode": "HTML"
                        }
                        
                        async with self.session.post(f"{self.base_url}/sendDocument" if media_type == "document" else f"{self.base_url}/sendPhoto", 
                                                   data=data, files=files, timeout=30) as response:
                            if response.status != 200:
                                logger.error(f"Failed to send local media to {chat_id}: {response.status}")
                                success = False
                            else:
                                logger.info(f"Local media sent successfully to {chat_id}")
                else:
                    # Remote URL
                    payload = {
                        "chat_id": chat_id,
                        "caption": caption,
                        "parse_mode": "HTML"
                    }
                    
                    if media_type == "photo":
                        payload["photo"] = media_url
                        endpoint = "/sendPhoto"
                    elif media_type == "video":
                        payload["video"] = media_url
                        endpoint = "/sendVideo"
                    elif media_type == "animation":
                        payload["animation"] = media_url
                        endpoint = "/sendAnimation"
                    else:
                        payload["document"] = media_url
                        endpoint = "/sendDocument"
                    
                    async with self.session.post(f"{self.base_url}{endpoint}", json=payload, timeout=30) as response:
                        if response.status != 200:
                            logger.error(f"Failed to send remote media to {chat_id}: {response.status}")
                            success = False
                        else:
                            logger.info(f"Remote media sent successfully to {chat_id}")
                            
            except Exception as e:
                logger.error(f"Error sending media to {chat_id}: {e}")
                success = False
                
        return success


