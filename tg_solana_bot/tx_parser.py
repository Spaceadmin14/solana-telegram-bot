import logging
from typing import Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

class TransactionParser:
    def __init__(self, primary_wallet: str, secondary_wallet: str, bullieve_mint: str, incinerator: str):
        self.primary_wallet = primary_wallet
        self.secondary_wallet = secondary_wallet
        self.bullieve_mint = bullieve_mint
        self.incinerator = incinerator

    def parse_transaction_raw(self, tx: Dict[str, Any], primary_wallet: str, secondary_wallet: str, bullieve_mint: str, incinerator: str) -> Tuple[str, Dict[str, Any]]:
        """Parse a raw transaction and classify the event type."""
        try:
            # Update instance variables with passed parameters
            self.primary_wallet = primary_wallet
            self.secondary_wallet = secondary_wallet
            self.bullieve_mint = bullieve_mint
            self.incinerator = incinerator
            
            return self.classify_event(tx)
        except Exception as e:
            logger.error(f"Error parsing transaction: {e}")
            return "unknown", {}

    def classify_event(self, tx: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
        """Classify the type of event in the transaction."""
        try:
            # Check for burn events first (explicit burn instructions)
            burn_details = self._check_burn_event(tx)
            if burn_details:
                return "burn", burn_details

            # Check for transfers
            transfer_details = self._check_transfers(tx)
            if transfer_details:
                return transfer_details["type"], transfer_details

            return "unknown", {}
        except Exception as e:
            logger.error(f"Error classifying event: {e}")
            return "unknown", {}

    def _check_burn_event(self, tx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for explicit burn instructions or significant balance reductions."""
        try:
            if "meta" not in tx or "postTokenBalances" not in tx["meta"] or "preTokenBalances" not in tx["meta"]:
                return None

            pre_balances = {b["mint"]: float(b["uiTokenAmount"]["uiAmount"] or 0) for b in tx["meta"]["preTokenBalances"]}
            post_balances = {b["mint"]: float(b["uiTokenAmount"]["uiAmount"] or 0) for b in tx["meta"]["postTokenBalances"]}

            # Check for Bullieve token burn (significant reduction)
            if self.bullieve_mint in pre_balances and self.bullieve_mint in post_balances:
                pre_amount = pre_balances[self.bullieve_mint]
                post_amount = post_balances[self.bullieve_mint]
                burned_amount = pre_amount - post_amount
                
                # Consider it a burn if significant amount was reduced
                if burned_amount > 0.001:  # Minimum threshold
                    return {
                        "amount": str(burned_amount),
                        "mint": self.bullieve_mint,
                        "type": "burn"
                    }

            # Check for explicit burn instructions in transaction
            if "transaction" in tx and "message" in tx["transaction"]:
                message = tx["transaction"]["message"]
                if "instructions" in message:
                    for instruction in message["instructions"]:
                        if "programId" in instruction and instruction["programId"] == "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA":
                            # This is a token program instruction, could be a burn
                            # We'll rely on balance changes for now as they're more reliable
                            pass

            return None
        except Exception as e:
            logger.error(f"Error checking burn event: {e}")
            return None

    def _check_transfers(self, tx: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check for various types of transfers."""
        try:
            if "meta" not in tx or "postTokenBalances" not in tx["meta"] or "preTokenBalances" not in tx["meta"]:
                return None

            pre_balances = {}
            post_balances = {}

            # Build pre-balances map
            for balance in tx["meta"]["preTokenBalances"]:
                if "mint" in balance and "uiTokenAmount" in balance:
                    mint = balance["mint"]
                    amount = float(balance["uiTokenAmount"]["uiAmount"] or 0)
                    pre_balances[mint] = amount

            # Build post-balances map
            for balance in tx["meta"]["postTokenBalances"]:
                if "mint" in balance and "uiTokenAmount" in balance:
                    mint = balance["mint"]
                    amount = float(balance["uiTokenAmount"]["uiAmount"] or 0)
                    post_balances[mint] = amount

            # Check for fee income to primary wallet
            primary_fee = self._check_primary_wallet_fee(pre_balances, post_balances)
            if primary_fee:
                return primary_fee

            # Check for transfer to secondary wallet
            secondary_transfer = self._check_secondary_wallet_transfer(pre_balances, post_balances)
            if secondary_transfer:
                return secondary_transfer

            return None
        except Exception as e:
            logger.error(f"Error checking transfers: {e}")
            return None

    def _check_primary_wallet_fee(self, pre_balances: Dict[str, float], post_balances: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Check if primary wallet received fees (any token inflow)."""
        try:
            for mint in post_balances:
                pre_amount = pre_balances.get(mint, 0)
                post_amount = post_balances[mint]
                
                # Check for positive balance change (inflow)
                if post_amount > pre_amount:
                    increase = post_amount - pre_amount
                    if increase > 0.000001:  # Minimum threshold
                        return {
                            "type": "fee_income",
                            "mint": mint,
                            "amount": str(increase),
                            "wallet": self.primary_wallet
                        }
            return None
        except Exception as e:
            logger.error(f"Error checking primary wallet fee: {e}")
            return None

    def _check_secondary_wallet_transfer(self, pre_balances: Dict[str, float], post_balances: Dict[str, float]) -> Optional[Dict[str, Any]]:
        """Check if secondary wallet received transfers."""
        try:
            for mint in post_balances:
                pre_amount = pre_balances.get(mint, 0)
                post_amount = post_balances[mint]
                
                # Check for positive balance change (inflow)
                if post_amount > pre_amount:
                    increase = post_amount - pre_amount
                    if increase > 0.000001:  # Minimum threshold
                        return {
                            "type": "transfer_to_secondary",
                            "mint": mint,
                            "amount": str(increase),
                            "wallet": self.secondary_wallet
                        }
            return None
        except Exception as e:
            logger.error(f"Error checking secondary wallet transfer: {e}")
            return None


