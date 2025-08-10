import asyncio
import os
import sys
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging

sys.path.append(str(Path(__file__).parent))

from tg_solana_bot.config import load_settings
from tg_solana_bot.solana_client import SolanaClient
from tg_solana_bot.tx_parser import TransactionParser
from tg_solana_bot.notifier import TelegramNotifier
from tg_solana_bot.state import StateStore
from dotenv import load_dotenv
from tg_solana_bot.price_client import PriceClient
from tg_solana_bot.manual_price_store import ManualPriceStore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

price_client: PriceClient

def _fmt_amount(val: float, max_decimals: int = 9) -> str:
    s = f"{val:.{max_decimals}f}".rstrip("0").rstrip(".")
    if s.startswith("."):
        s = "0" + s
    if s == "-0":
        s = "0"
    return s

async def process_wallet_and_token_accounts(
    client: SolanaClient,
    notifier: TelegramNotifier,
    state: StateStore,
    wallet: str,
    settings,
) -> None:
    try:
        token_accounts = await client.get_token_accounts_by_owner(wallet)
    except Exception as exc:
        logger.error(f"[error] get_token_accounts_by_owner failed for {wallet}: {exc}")
        token_accounts = []

    addresses: List[str] = [wallet] + token_accounts
    logger.info(f"[poll] owner={wallet} addresses={len(addresses)} (wallet + token accounts)")

    processed_sigs: set[str] = set()

    for addr in addresses:
        try:
            last_sig = state.load_last_signature(addr)
            logger.info(f"[poll] addr={addr} last_sig={last_sig[:50]}..." if last_sig else f"[poll] addr={addr} last_sig=None")
            signatures = await client.get_signatures_for_address(addr, before=None, limit=25)
        except Exception as exc:
            logger.error(f"[error] get_signatures_for_address failed addr={addr}: {exc}")
            continue

        if not signatures:
            continue

        if last_sig is None:
            top_sig = signatures[0].get("signature")
            logger.info(f"[init] addr={addr} initialize last_sig to {top_sig} (skip history)")
            state.save_last_signature(addr, top_sig)
            continue

        new_sigs: List[str] = []
        for entry in signatures:
            sig = entry.get("signature")
            if sig == last_sig:
                break
            new_sigs.append(sig)

        if not new_sigs:
            continue

        logger.info(f"[poll] addr={addr} new_sigs={len(new_sigs)}")

        tx_parser = TransactionParser(
            settings.primary_wallet_address,
            settings.secondary_wallet_address,
            settings.bullieve_mint_address,
            settings.burn_incinerator_address,
        )

        for sig in reversed(new_sigs):
            if sig in processed_sigs:
                continue
            processed_sigs.add(sig)
            try:
                tx = await client.get_transaction(sig)
            except Exception as exc:
                logger.error(f"[error] get_transaction failed signature={sig}: {exc}")
                continue
            if not tx:
                continue

            event_type, details = tx_parser.parse_transaction_raw(
                tx,
                primary_wallet=settings.primary_wallet_address,
                secondary_wallet=settings.secondary_wallet_address,
                bullieve_mint=settings.bullieve_mint_address,
                incinerator=settings.burn_incinerator_address,
            )
            logger.info(f"[event] owner={wallet} via={addr} sig={sig} type={event_type} details={details}")

            if event_type == "fee_income":
                mint = details.get("mint", "")
                amount = float(details.get("amount", 0))
                signer = client.get_first_signer_address(tx) or "unknown"
                if mint == "So11111111111111111111111111111111111111112" or mint.upper() == "SOL":
                    symbol = "SOL"
                elif mint == "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v":
                    symbol = "USDC"
                elif mint == "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB":
                    symbol = "USDT"
                else:
                    symbol = mint

                usd = None
                if amount and mint:
                    usd_price = await price_client.get_usd_price(mint)
                    if usd_price:
                        usd = amount * usd_price
                amt_txt = _fmt_amount(amount, 9)
                
                caption = (
                    "BULLIEVE-SWAP FEES COLLECTED! 💰\n\n"
                    f"FEES COLLECTED: {amt_txt} {symbol}"
                )
                if usd is not None:
                    caption += f" (~${usd:,.2f})"
                caption += (
                    f"\n\nBULLIEVER: {signer}\n\n"
                    "🔥 Let's burnnnnn 🔥"
                )

                try:
                    await notifier.send_media(settings.notify_fee_media_url, caption=caption, media_type="photo")
                except Exception as exc:
                    logger.error(f"[error] telegram send fee_income failed: {exc}")
            elif event_type == "burn":
                amount = float(details.get("amount", 0))
                symbol = "BULLIEVE"
                usd = None
                try:
                    usd_price = await price_client.get_usd_price(symbol) or await price_client.get_usd_price(
                        settings.bullieve_mint_address
                    )
                    if usd_price:
                        usd = amount * usd_price
                except Exception as exc:
                    logger.warning(f"Could not get USD price for burn: {exc}")
                    usd = None
                amt_txt = _fmt_amount(amount, 9)
                
                caption = (
                    "BULLIEVE BURN! 🔥\n\n"
                    f"AMOUNT BURNED: {amt_txt} {symbol}"
                )
                if usd is not None:
                    caption += f" (~${usd:,.2f})"
                caption += "\n\n🔥 Let's burnnnnn 🔥"

                try:
                    await notifier.send_media(settings.notify_burn_media_url, caption=caption, media_type="photo")
                except Exception as exc:
                    logger.error(f"[error] telegram send burn failed: {exc}")
            elif event_type == "transfer_to_secondary":
                pass

            state.save_last_signature(addr, new_sigs[0])


async def main() -> None:
    if os.path.exists(".env"):
        load_dotenv(".env")
    settings = load_settings()
    logger.info(
        f"[start] polling every {settings.poll_interval_seconds}s on primary={settings.primary_wallet_address} secondary={settings.secondary_wallet_address}"
    )
    client = SolanaClient(settings.solana_rpc_url, settings.solana_alt_rpc_url)
    global price_client
    manual_store = ManualPriceStore(settings.manual_price_file_path)
    price_client = PriceClient(manual_store)
    notifier = TelegramNotifier(settings.telegram_bot_token, settings.telegram_chat_id, settings.telegram_chat_ids)
    state = StateStore(settings.state_file_path)
    try:
        while True:
            try:
                manual_store.refresh()
            except Exception as exc:
                logger.error(f"Failed to refresh manual prices: {exc}")
                pass
            await process_wallet_and_token_accounts(client, notifier, state, settings.primary_wallet_address, settings)
            await process_wallet_and_token_accounts(client, notifier, state, settings.secondary_wallet_address, settings)
            await asyncio.sleep(settings.poll_interval_seconds)
    finally:
        await notifier.close()
        await client.close()
        await price_client.close()


if __name__ == "__main__":
    asyncio.run(main())


