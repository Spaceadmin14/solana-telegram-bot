# Déploiement sur Railway

## 🚀 Railway - Parfait pour les bots 24/24 !

Railway est idéal pour ton bot Telegram car :
- ✅ **500h/mois gratuites** (20 jours)
- ✅ **Toujours actif** pendant les heures gratuites
- ✅ **Restart automatique** si crash
- ✅ **Déploiement simple** via GitHub
- ✅ **Variables d'environnement** sécurisées

## 📋 Étapes de déploiement

### 1. Créer un compte Railway
1. Va sur [railway.app](https://railway.app)
2. Connecte-toi avec GitHub
3. Clique sur "New Project"

### 2. Connecter GitHub
1. Choisis "Deploy from GitHub repo"
2. Sélectionne ton repo ou crée-en un nouveau
3. Railway va automatiquement détecter le Dockerfile

### 3. Configurer les variables d'environnement
Dans Railway Dashboard → Variables, ajoute :

```env
TELEGRAM_BOT_TOKEN=8083638248:AAF5A1Re49xWBrJn5kNr2jhQtIRRdNRWQqM
TELEGRAM_CHAT_ID=-1002421701303
SOLANA_RPC_URL=https://rpc.helius.xyz/?api-key=2258d67f-c201-443b-abbe-571505a4d516
SOLANA_ALT_RPC_URL=https://api.mainnet-beta.solana.com
PRIMARY_WALLET_ADDRESS=6674vbB9LRJKymhEz9DxxJc5HyXbCsSVFh1jGuL7xM6B
SECONDARY_WALLET_ADDRESS=5aYBTU9x6F8qmytdmAiLcRQyPEVjBiGN2tHArFbop8V5
BULLIEVE_MINT_ADDRESS=HdzMjvQvFP9nxp1X2NbHFptZK1G6ASsyRcxNdn65ABxi
BURN_INCINERATOR_ADDRESS=11111111111111111111111111111112
POLL_INTERVAL_SECONDS=30
STATE_FILE_PATH=/app/data/state.json
MANUAL_PRICE_FILE_PATH=/app/data/manual_prices.json
NOTIFY_FEE_MEDIA_URL=/app/media/swap_alert.jpg
NOTIFY_BURN_MEDIA_URL=/app/media/swap_alert.jpg
```

### 4. Déployer
1. Railway va automatiquement construire l'image Docker
2. Le bot démarre automatiquement
3. Tu peux voir les logs en temps réel

## 🔧 Gestion du projet

### Voir les logs
- Dashboard Railway → Ton projet → Logs
- Ou dans l'onglet "Deployments"

### Redémarrer le bot
- Dashboard → "Redeploy" button

### Modifier le code
1. Modifie le code localement
2. Push sur GitHub
3. Railway redéploie automatiquement

### Variables d'environnement
- Dashboard → Variables
- Modifie et sauvegarde
- Redéploiement automatique

## 📊 Monitoring

### Statut du bot
- Dashboard → "Deployments" tab
- Voir l'état en temps réel

### Logs en temps réel
- Dashboard → "Logs" tab
- Voir les messages du bot

### Métriques
- Dashboard → "Metrics" tab
- CPU, mémoire, etc.

## 💰 Coûts

### Plan gratuit
- **500h/mois** (20 jours)
- **1GB RAM**
- **1 vCPU**
- **Parfait pour ton bot**

### Si tu dépasses
- **$5/mois** pour plus d'heures
- **$10/mois** pour toujours actif

## 🎯 Avantages Railway

✅ **Simple** : Connecte GitHub, c'est tout  
✅ **Fiable** : Restart automatique  
✅ **Monitoring** : Logs et métriques  
✅ **Scaling** : Facile d'upgrader  
✅ **Sécurisé** : Variables d'environnement  

## 🚨 En cas de problème

1. **Bot ne démarre pas** : Vérifie les logs
2. **Variables manquantes** : Vérifie Railway Variables
3. **Crash fréquent** : Augmente la mémoire
4. **Pas d'alertes** : Vérifie les logs Telegram

## 📱 Test du bot

Une fois déployé :
1. Fais un swap sur Jupiter
2. Vérifie les logs Railway
3. Tu devrais recevoir l'alerte Telegram

Le bot va maintenant tourner 24/24 et envoyer les alertes automatiquement ! 🎉
