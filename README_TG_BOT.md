## Telegram Bot de surveillance Solana (frais + burn)

Fonctions:
- Surveillance du wallet principal pour les frais (petit % reçu lors des swaps)
- Ignorer les transferts vers le wallet secondaire
- Détecter les burns (envoi vers l'incinerator) et notifier

### 1) Créer le bot Telegram
1. Ouvrir Telegram, parler à `@BotFather`
2. `/newbot` → nom + username → récupérer le `token`
3. Ajouter le bot dans votre groupe/canal si nécessaire et récupérer `chat_id` (ex: via @RawDataBot ou en DM au bot et appel à l'API `getUpdates`)

### 2) Variables d'environnement
Créer un fichier `.env` (ou exporter dans votre hébergeur):

```
TELEGRAM_BOT_TOKEN=123456:ABC...
TELEGRAM_CHAT_ID=123456789
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
PRIMARY_WALLET_ADDRESS=6674vbB9LRJKymhEz9DxxJc5HyXbCsSVFh1jGuL7xM6B
SECONDARY_WALLET_ADDRESS=5aYBTU9x6F8qmytdmAiLcRQyPEVjBiGN2tHArFbop8V5
BULLIEVE_MINT_ADDRESS=<MINT_TOKEN_BULLIEVE>
BURN_INCINERATOR_ADDRESS=1nc1nerator11111111111111111111111111111111
POLL_INTERVAL_SECONDS=15
STATE_FILE_PATH=/data/state.json
NOTIFY_FEE_MEDIA_URL=https://...
NOTIFY_BURN_MEDIA_URL=https://...
```

Astuce: Le répertoire `/data` peut être monté en volume Docker pour persister l'état.

### 3) Installer et lancer en local (optionnel)

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m tg_solana_bot.main
```

### 4) Docker

```
docker build -t tg-solana-bot .
docker run --restart unless-stopped -d \
  --name tg-solana-bot \
  -e TELEGRAM_BOT_TOKEN=... \
  -e TELEGRAM_CHAT_ID=... \
  -e SOLANA_RPC_URL=https://api.mainnet-beta.solana.com \
  -e PRIMARY_WALLET_ADDRESS=6674vbB9LRJKymhEz9DxxJc5HyXbCsSVFh1jGuL7xM6B \
  -e SECONDARY_WALLET_ADDRESS=5aYBTU9x6F8qmytdmAiLcRQyPEVjBiGN2tHArFbop8V5 \
  -e BULLIEVE_MINT_ADDRESS=<MINT_TOKEN_BULLIEVE> \
  -e BURN_INCINERATOR_ADDRESS=1nc1nerator11111111111111111111111111111111 \
  -e POLL_INTERVAL_SECONDS=15 \
  -e STATE_FILE_PATH=/data/state.json \
  -e NOTIFY_FEE_MEDIA_URL=https://... \
  -e NOTIFY_BURN_MEDIA_URL=https://... \
  -v $(pwd)/data:/data \
  tg-solana-bot
```

### 5) Comment ça marche (technique rapide)
- Le bot interroge `getSignaturesForAddress` et `getTransaction` (RPC Solana, `jsonParsed`)
- Un parseur agrège les deltas de `preTokenBalances`/`postTokenBalances` par owner+mint
- Heuristiques:
  - `burn`: delta > 0 chez l'`incinerator` pour le mint Bullieve
  - `transfer_to_secondary`: inflow sur le wallet secondaire avec outflow sur le principal
  - `fee_income`: inflow sur le principal (petit montant typiquement)
- Seules les catégories `fee_income` et `burn` déclenchent des notifications (média + caption)

Notes:
- Si c'est le premier lancement, on initialise sans notifier l'historique (anti-spam)
- Vous pouvez remplacer l'heuristique par des filtres spécifiques à Jupiter si nécessaire (logs/program IDs)


