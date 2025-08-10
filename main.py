import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from tg_solana_bot.config import load_settings
from tg_solana_bot.solana_client import SolanaClient
from tg_solana_bot.tx_parser import TransactionParser
from tg_solana_bot.notifier import TelegramNotifier
from tg_solana_bot.state import StateStore
from tg_solana_bot.price_client import PriceClient
from tg_solana_bot.manual_price_store import ManualPriceStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Simple health check for Fly.io
def health_check():
    """Simple health check endpoint for Fly.io"""
    return {"status": "healthy", "service": "tg-solana-bot"}

async def process_wallet_and_token_accounts(
    solana_client: SolanaClient,
    tx_parser: TransactionParser,
    notifier: TelegramNotifier,
    state_manager: StateStore,
    price_client: PriceClient,
    wallet_address: str,
    wallet_name: str
):
    """Process a wallet and all its associated token accounts"""
    try:
        # Get all token accounts for this wallet
        token_accounts = await solana_client.get_token_accounts_by_owner(wallet_address)
        all_addresses = [wallet_address] + [acc['pubkey'] for acc in token_accounts]
        
        logger.info(f"[poll] owner={wallet_address} addresses={len(all_addresses)} (wallet + token accounts)")
        
        for addr in all_addresses:
            last_sig = state_manager.load_last_signature(addr)
            
            # Get recent signatures
            signatures = await solana_client.get_signatures_for_address(addr, last_sig)
            
            if not signatures:
                logger.info(f"[poll] addr={addr} last_sig={last_sig[:50]}...")
                continue
            
            # Process each transaction
            for sig_info in signatures:
                signature = sig_info['signature']
                
                # Get transaction details
                tx_data = await solana_client.get_transaction(signature)
                if not tx_data:
                    continue
                
                # Parse transaction
                event = tx_parser.parse_transaction(tx_data, wallet_address, wallet_name)
                
                if event:
                    # Get signer address
                    signer = solana_client.get_first_signer_address(tx_data)
                    
                    # Get USD price
                    usd_value = None
                    if event.get('amount') and event.get('mint'):
                        usd_value = await price_client.get_usd_price(event['mint'], event['amount'])
                    
                    # Send notification
                    if event['type'] == 'fee':
                        message = f"BULLIEVE-SWAP FEES COLLECTED! 💰\n\nFEES COLLECTED: {event['amount']} {event['symbol']}"
                        if usd_value:
                            message += f" (~${usd_value:,.2f})"
                        message += f"\n\nBULLIEVER: {signer}\n\n🔥 Let's burnnnnn 🔥"
                        
                        await notifier.send_media(
                            message=message,
                            media_url="/media/alert.jpg"
                        )
                        
                    elif event['type'] == 'burn':
                        message = f"BULLIEVE BURN! 🔥\n\nAMOUNT BURNED: {event['amount']} {event['symbol']}"
                        if usd_value:
                            message += f" (~${usd_value:,.2f})"
                        message += f"\n\n🔥 Let's burnnnnn 🔥"
                        
                        await notifier.send_media(
                            message=message,
                            media_url="/media/alert.jpg"
                        )
                
                # Update last signature
                state_manager.save_last_signature(addr, signature)
                
    except Exception as e:
        logger.error(f"Error processing wallet {wallet_address}: {e}")

async def main():
    """Main function"""
    try:
        # Load configuration
        config = load_settings()
        
        # Initialize components
        solana_client = SolanaClient(config.solana_rpc_url, config.solana_alt_rpc_url)
        tx_parser = TransactionParser(
            config.primary_wallet_address,
            config.secondary_wallet_address,
            config.bullieve_mint_address,
            config.burn_incinerator_address
        )
        notifier = TelegramNotifier(config.telegram_bot_token, config.telegram_chat_id, config.telegram_chat_ids)
        state_manager = StateStore(config.state_file_path)
        price_client = PriceClient()
        
        # Load manual prices
        manual_price_store = ManualPriceStore(config.manual_price_file_path)
        manual_price_store.load_prices()
        
        logger.info("Bot started successfully!")
        
        while True:
            try:
                # Reload manual prices in each cycle
                manual_price_store.load_prices()
                
                # Process primary wallet
                await process_wallet_and_token_accounts(
                    solana_client, tx_parser, notifier, state_manager, price_client,
                    config.primary_wallet_address, 'primary'
                )
                
                # Process secondary wallet
                await process_wallet_and_token_accounts(
                    solana_client, tx_parser, notifier, state_manager, price_client,
                    config.secondary_wallet_address, 'secondary'
                )
                
                # Wait before next poll
                await asyncio.sleep(config.poll_interval_seconds)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(10)  # Wait a bit before retrying
                
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
