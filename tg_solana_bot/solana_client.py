import aiohttp
import asyncio
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SolanaClient:
    def __init__(self, rpc_url: str, alt_rpc_url: str = ""):
        self.rpc_url = rpc_url
        self.alt_rpc_url = alt_rpc_url
        self.session: Optional[aiohttp.ClientSession] = None
        self._retry_delays = [1, 2, 4, 8, 16]  # Exponential backoff

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

    async def _make_request(self, method: str, params: List[Any], max_retries: int = 3) -> Optional[Dict[str, Any]]:
        await self._ensure_session()
        
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params
        }

        for attempt in range(max_retries):
            try:
                async with self.session.post(self.rpc_url, json=payload, timeout=30) as response:
                    if response.status == 429:  # Rate limit
                        if attempt < len(self._retry_delays):
                            delay = self._retry_delays[attempt]
                            logger.warning(f"Rate limited, retrying in {delay}s...")
                            await asyncio.sleep(delay)
                            continue
                        else:
                            logger.error("Max retries reached for rate limit")
                            return None
                    
                    if response.status != 200:
                        logger.error(f"HTTP {response.status}: {await response.text()}")
                        return None
                    
                    data = await response.json()
                    if "error" in data:
                        logger.error(f"RPC error: {data['error']}")
                        return None
                    
                    return data.get("result")
                    
            except asyncio.TimeoutError:
                logger.warning(f"Request timeout, attempt {attempt + 1}/{max_retries}")
                if attempt == max_retries - 1:
                    logger.error("Max retries reached for timeout")
                    return None
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Request failed: {e}")
                return None
        
        return None

    async def get_signatures_for_address(self, address: str, before: Optional[str] = None, limit: int = 25) -> List[Dict[str, Any]]:
        params = [address, {"limit": limit}]
        if before:
            params[1]["before"] = before
        
        result = await self._make_request("getSignaturesForAddress", params)
        return result or []

    async def get_transaction(self, signature: str) -> Optional[Dict[str, Any]]:
        params = [signature, {"encoding": "json", "maxSupportedTransactionVersion": 0}]
        return await self._make_request("getTransaction", params)

    async def get_token_accounts_by_owner(self, owner: str) -> List[str]:
        params = [
            owner,
            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
            {"encoding": "jsonParsed"}
        ]
        
        result = await self._make_request("getTokenAccountsByOwner", params)
        if not result or "value" not in result:
            return []
        
        token_accounts = []
        for account in result["value"]:
            if "pubkey" in account:
                token_accounts.append(account["pubkey"])
        
        return token_accounts

    def get_first_signer_address(self, transaction: Dict[str, Any]) -> Optional[str]:
        try:
            if "transaction" in transaction and "message" in transaction["transaction"]:
                message = transaction["transaction"]["message"]
                if "accountKeys" in message and len(message["accountKeys"]) > 0:
                    return message["accountKeys"][0]
        except Exception as e:
            logger.error(f"Error extracting signer address: {e}")
        return None


