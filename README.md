# 🤖 Telegram Solana Bot

Bot Telegram pour surveiller les wallets Solana et envoyer des alertes automatiques.

## 🎯 Fonctionnalités

- **Surveillance des frais** : Détecte les frais de swap sur le wallet principal
- **Détection des burns** : Surveille les burns de tokens Bullieve
- **Alertes Telegram** : Envoie des notifications personnalisées avec images
- **Prix en temps réel** : Affiche les valeurs en USD
- **24/7** : Fonctionne en continu sur Railway

## 🚀 Déploiement

### Railway (Recommandé)
1. Fork ce repo
2. Connecte Railway à ton repo GitHub
3. Configure les variables d'environnement
4. Déploie automatiquement

### Variables d'environnement requises

```env
TELEGRAM_BOT_TOKEN=ton_token_bot
TELEGRAM_CHAT_ID=ton_chat_id
SOLANA_RPC_URL=url_rpc_solana
PRIMARY_WALLET_ADDRESS=adresse_wallet_principal
SECONDARY_WALLET_ADDRESS=adresse_wallet_secondaire
BULLIEVE_MINT_ADDRESS=adresse_token_bullieve
```

## 📁 Structure

```
tg_solana_bot/
├── tg_solana_bot/
│   ├── config.py          # Configuration
│   ├── solana_client.py   # Client Solana RPC
│   ├── tx_parser.py       # Parseur de transactions
│   ├── notifier.py        # Notifications Telegram
│   ├── state.py           # Gestion d'état
│   ├── price_client.py    # Prix des tokens
│   └── manual_price_store.py # Prix manuels
├── main.py                # Point d'entrée
├── requirements.txt       # Dépendances Python
├── Dockerfile            # Configuration Docker
└── railway.toml          # Configuration Railway
```

## 🔧 Configuration

### Wallets surveillés
- **Wallet Principal** : Reçoit les frais de swap
- **Wallet Secondaire** : Effectue les burns

### Types d'alertes
1. **Frais collectés** : Inflows sur le wallet principal
2. **Burns détectés** : Burns de tokens Bullieve

## 📱 Messages d'alerte

### Frais collectés
```
BULLIEVE-SWAP FEES COLLECTED! 💰

FEES COLLECTED: 0.000492099 SOL (~$0.09)

BULLIEVER: E1d9ihjAquGCA9XXmoaep6cFfeQRtSxpHNQpaFZxswENK

🔥 Let's burnnnnn 🔥
```

### Burns détectés
```
BULLIEVE BURN! 🔥

AMOUNT BURNED: 1000 BULLIEVE (~$0.45)

🔥 Let's burnnnnn 🔥
```

## 🛠️ Développement local

```bash
# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec tes valeurs

# Lancer le bot
python main.py
```

## 📊 Monitoring

- **Logs** : Voir les logs Railway en temps réel
- **Métriques** : CPU, mémoire, etc.
- **Statut** : État du bot et des connexions

## 🔒 Sécurité

- Variables d'environnement sécurisées
- Pas de clés privées dans le code
- Validation des transactions

## 📄 Licence

MIT License - Libre d'utilisation

## 🤝 Support

Pour toute question ou problème :
1. Vérifie les logs Railway
2. Consulte la documentation
3. Ouvre une issue sur GitHub

---

**Bot développé pour la communauté Bullieve** 🚀
