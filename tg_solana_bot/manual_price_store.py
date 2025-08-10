import json
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class ManualPriceStore:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.prices: Dict[str, float] = {}
        self._ensure_directory()
        self.refresh()

    def _ensure_directory(self):
        """Ensure the directory for the price file exists."""
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def refresh(self):
        """Load prices from the JSON file."""
        try:
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
                    self.prices = data
                logger.info(f"Loaded {len(self.prices)} manual prices from {self.file_path}")
            else:
                logger.info(f"Manual price file not found: {self.file_path}")
                self.prices = {}
        except Exception as e:
            logger.error(f"Error loading manual prices: {e}")
            self.prices = {}

    def get_price(self, mint_or_symbol: str) -> Optional[float]:
        """Get price for a mint address or symbol."""
        # Direct match
        if mint_or_symbol in self.prices:
            return self.prices[mint_or_symbol]
        
        # Try uppercase symbol
        if mint_or_symbol.upper() in self.prices:
            return self.prices[mint_or_symbol.upper()]
        
        # Try lowercase symbol
        if mint_or_symbol.lower() in self.prices:
            return self.prices[mint_or_symbol.lower()]
        
        return None

    def set_price(self, mint_or_symbol: str, price: float) -> bool:
        """Set price for a mint address or symbol."""
        try:
            self.prices[mint_or_symbol] = price
            self._save_prices()
            logger.info(f"Set price for {mint_or_symbol}: ${price}")
            return True
        except Exception as e:
            logger.error(f"Error setting price for {mint_or_symbol}: {e}")
            return False

    def _save_prices(self):
        """Save prices to the JSON file."""
        try:
            with open(self.file_path, 'w') as f:
                json.dump(self.prices, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving manual prices: {e}")

    def get_all_prices(self) -> Dict[str, float]:
        """Get all manual prices."""
        return self.prices.copy()

    def clear_prices(self) -> bool:
        """Clear all manual prices."""
        try:
            self.prices = {}
            self._save_prices()
            logger.info("Cleared all manual prices")
            return True
        except Exception as e:
            logger.error(f"Error clearing manual prices: {e}")
            return False


