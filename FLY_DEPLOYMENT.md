# Déploiement sur Fly.io

## Prérequis

1. **Compte Fly.io** : Crée un compte sur [fly.io](https://fly.io)
2. **CLI Fly.io** : Installe le CLI Fly.io

### Installation du CLI Fly.io

```bash
# macOS avec Homebrew
brew install flyctl

# Ou téléchargement direct
curl -L https://fly.io/install.sh | sh
```

## Étapes de déploiement

### 1. Connexion à Fly.io

```bash
fly auth login
```

### 2. Créer l'application

```bash
cd /Users/philippe/solana_tg_bot
fly apps create tg-solana-bot
```

### 3. Configurer les variables d'environnement

```bash
# Copier les variables depuis ton fichier .env local
fly secrets set TELEGRAM_BOT_TOKEN="8083638248:AAF5A1Re49xWBrJn5kNr2jhQtIRRdNRWQqM"
fly secrets set TELEGRAM_CHAT_ID="-1002421701303"
fly secrets set SOLANA_RPC_URL="https://rpc.helius.xyz/?api-key=2258d67f-c201-443b-abbe-571505a4d516"
fly secrets set SOLANA_ALT_RPC_URL="https://api.mainnet-beta.solana.com"
fly secrets set PRIMARY_WALLET="6674vbB9LRJKymhEz9DxxJc5HyXbCsSVFh1jGuL7xM6B"
fly secrets set SECONDARY_WALLET="5aYBTU9x6F8qmytdmAiLcRQyPEVjBiGN2tHArFbop8V5"
fly secrets set BULLIEVE_MINT_ADDRESS="HdzMjvQvFP9nxp1X2NbHFptZK1G6ASsyRcxNdn65ABxi"
fly secrets set INCINERATOR_ADDRESS="11111111111111111111111111111112"
fly secrets set POLLING_INTERVAL="30"
fly secrets set STATE_FILE_PATH="/app/data/state.json"
fly secrets set MANUAL_PRICE_FILE_PATH="/app/data/manual_prices.json"
```

### 4. Déployer l'application

```bash
fly deploy
```

### 5. Vérifier le déploiement

```bash
# Voir les logs
fly logs

# Voir le statut
fly status

# Ouvrir l'application (pour les health checks)
fly open
```

## Gestion de l'application

### Voir les logs en temps réel
```bash
fly logs --follow
```

### Redémarrer l'application
```bash
fly apps restart tg-solana-bot
```

### Mettre à jour les variables d'environnement
```bash
fly secrets set NOUVELLE_VARIABLE="nouvelle_valeur"
```

### Supprimer l'application
```bash
fly apps destroy tg-solana-bot
```

## Avantages de Fly.io

✅ **Gratuit** : 3 machines partagées gratuites  
✅ **Auto-scaling** : S'arrête automatiquement quand inactif  
✅ **Global** : Déploiement proche de toi (CDG = Paris)  
✅ **Simple** : Déploiement en une commande  
✅ **Persistant** : Les données persistent entre les redémarrages  

## Limitations

⚠️ **Crédits limités** : 2340 heures/mois gratuites  
⚠️ **Machine partagée** : Performance limitée  
⚠️ **Pas de volumes** : Utilise le système de fichiers éphémère  

## Monitoring

Le bot enverra automatiquement les alertes Telegram. Tu peux vérifier qu'il fonctionne en :

1. Faisant un swap sur Jupiter
2. Vérifiant les logs : `fly logs --follow`
3. Vérifiant que tu reçois l'alerte sur Telegram

## Mise à jour du bot

Pour mettre à jour le bot :

1. Modifie le code localement
2. Pousse les changements : `fly deploy`
3. Le bot redémarre automatiquement

## Support

Si tu as des problèmes :
- `fly logs` pour voir les erreurs
- `fly status` pour voir l'état
- `fly apps restart tg-solana-bot` pour redémarrer
