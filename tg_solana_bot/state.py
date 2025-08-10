import json
import logging
import os
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class StateStore:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self._ensure_directory()

    def _ensure_directory(self):
        """Ensure the directory for the state file exists."""
        directory = os.path.dirname(self.file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def load_last_signature(self, address: str) -> Optional[str]:
        """Load the last processed signature for a given address."""
        try:
            if not os.path.exists(self.file_path):
                return None
            
            with open(self.file_path, 'r') as f:
                data = json.load(f)
                return data.get(address)
        except Exception as e:
            logger.error(f"Error loading last signature for {address}: {e}")
            return None

    def save_last_signature(self, address: str, signature: str) -> bool:
        """Save the last processed signature for a given address."""
        try:
            # Load existing data
            data = {}
            if os.path.exists(self.file_path):
                with open(self.file_path, 'r') as f:
                    data = json.load(f)
            
            # Update with new signature
            data[address] = signature
            
            # Save back to file
            with open(self.file_path, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Saved last signature for {address}: {signature[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Error saving last signature for {address}: {e}")
            return False

    def get_all_signatures(self) -> Dict[str, str]:
        """Get all saved signatures."""
        try:
            if not os.path.exists(self.file_path):
                return {}
            
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading all signatures: {e}")
            return {}

    def clear_signatures(self) -> bool:
        """Clear all saved signatures."""
        try:
            if os.path.exists(self.file_path):
                os.remove(self.file_path)
            logger.info("Cleared all signatures")
            return True
        except Exception as e:
            logger.error(f"Error clearing signatures: {e}")
            return False


