import aiohttp
import logging
import json
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class PriceClient:
    def __init__(self, manual_price_store):
        self.manual_price_store = manual_price_store
        self.session: Optional[aiohttp.ClientSession] = None
        self.jupiter_url = "https://price.jup.ag/v4/price"

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

    async def get_usd_price(self, mint: str) -> Optional[float]:
        """Get USD price for a token mint address or symbol."""
        try:
            # Try Jupiter first
            jupiter_price = await self._get_jupiter_price(mint)
            if jupiter_price is not None:
                logger.info(f"Got Jupiter price for {mint}: ${jupiter_price}")
                return jupiter_price

            # Try manual prices
            manual_price = self.manual_price_store.get_price(mint)
            if manual_price is not None:
                logger.info(f"Got manual price for {mint}: ${manual_price}")
                return manual_price

            # No price available
            logger.warning(f"No price available for {mint}")
            return None

        except Exception as e:
            logger.error(f"Error getting price for {mint}: {e}")
            return None

    async def _get_jupiter_price(self, mint: str) -> Optional[float]:
        """Get price from Jupiter API."""
        try:
            await self._ensure_session()
            
            params = {"ids": mint}
            async with self.session.get(self.jupiter_url, params=params, timeout=10) as response:
                if response.status != 200:
                    logger.warning(f"Jupiter API returned {response.status}")
                    return None
                
                data = await response.json()
                if "data" in data and mint in data["data"]:
                    return float(data["data"][mint]["price"])
                
                return None
                
        except asyncio.TimeoutError:
            logger.warning(f"Jupiter API timeout for {mint}")
            return None
        except Exception as e:
            logger.error(f"Error fetching Jupiter price for {mint}: {e}")
            return None


