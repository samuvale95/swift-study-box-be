# OAuth2 Setup Guide

Questo documento spiega come configurare l'autenticazione OAuth2 con Google e Apple per Swift Study Box.

## 🔧 Configurazione

### 1. Variabili d'Ambiente

Aggiungi le seguenti variabili al tuo file `.env`:

```bash
# Google OAuth2
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Apple OAuth2
APPLE_CLIENT_ID=your-apple-client-id
APPLE_CLIENT_SECRET=your-apple-client-secret
APPLE_TEAM_ID=your-apple-team-id
APPLE_KEY_ID=your-apple-key-id
APPLE_PRIVATE_KEY=your-apple-private-key

# OAuth2 URLs
FRONTEND_URL=http://localhost:3000
OAUTH_REDIRECT_URI=http://localhost:8000/api/v1/auth/oauth/callback
```

### 2. Google OAuth2 Setup

1. Vai su [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuovo progetto o seleziona uno esistente
3. Abilita l'API "Google+ API"
4. Vai a "Credenziali" → "Crea credenziali" → "ID client OAuth 2.0"
5. Configura:
   - **Tipo di applicazione**: Applicazione web
   - **Origini JavaScript autorizzate**: `http://localhost:3000`
   - **URI di reindirizzamento autorizzati**: `http://localhost:8000/api/v1/auth/oauth/callback`
6. Copia `Client ID` e `Client Secret` nel file `.env`

### 3. Apple OAuth2 Setup

1. Vai su [Apple Developer Console](https://developer.apple.com/)
2. Crea un nuovo "App ID" con "Sign In with Apple" abilitato
3. Crea un "Service ID" per la tua app
4. Crea una "Key" per "Sign In with Apple"
5. Scarica il file `.p8` della chiave privata
6. Configura:
   - **App ID**: Il tuo App ID
   - **Service ID**: Il tuo Service ID (Client ID)
   - **Team ID**: Il tuo Team ID
   - **Key ID**: L'ID della chiave
   - **Private Key**: Il contenuto del file `.p8`

## 🚀 Endpoint Disponibili

### 1. Lista Provider OAuth2
```http
GET /api/v1/auth/oauth/providers
```

**Risposta:**
```json
{
  "providers": [
    {
      "name": "google",
      "display_name": "Google",
      "login_url": "/api/v1/auth/oauth/login/google",
      "icon": "https://developers.google.com/identity/images/g-logo.png"
    },
    {
      "name": "apple",
      "display_name": "Apple",
      "login_url": "/api/v1/auth/oauth/login/apple",
      "icon": "https://developer.apple.com/assets/elements/icons/sign-in-with-apple/sign-in-with-apple-@2x.png"
    }
  ]
}
```

### 2. Inizia Login OAuth2
```http
GET /api/v1/auth/oauth/login/{provider}
```

**Parametri:**
- `provider`: `google` o `apple`
- `state` (opzionale): Parametro per protezione CSRF

**Risposta:** Redirect all'URL di autorizzazione del provider

### 3. Callback OAuth2
```http
GET /api/v1/auth/oauth/callback
POST /api/v1/auth/oauth/callback
```

**Parametri:**
- `provider`: `google` o `apple`
- `code`: Codice di autorizzazione dal provider
- `state` (opzionale): Parametro per protezione CSRF
- `error` (opzionale): Errore dal provider

**Risposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user-id",
    "email": "user@example.com",
    "name": "User Name",
    "avatar": "https://example.com/avatar.jpg",
    "is_active": true,
    "is_verified": true,
    "oauth_provider": "google",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  }
}
```

## 🔄 Flusso di Autenticazione

### 1. Frontend
```javascript
// 1. Ottieni la lista dei provider
const response = await fetch('/api/v1/auth/oauth/providers');
const { providers } = await response.json();

// 2. Reindirizza l'utente al provider
window.location.href = '/api/v1/auth/oauth/login/google';

// 3. Il callback gestirà il redirect e restituirà i token
```

### 2. Backend
```python
# Il servizio OAuth gestisce automaticamente:
# - Scambio del codice per il token di accesso
# - Recupero delle informazioni utente
# - Creazione o aggiornamento dell'utente nel database
# - Generazione dei token JWT per l'applicazione
```

## 🛡️ Sicurezza

- **State Parameter**: Usa sempre il parametro `state` per protezione CSRF
- **HTTPS**: In produzione, usa sempre HTTPS per tutti gli endpoint
- **Validazione**: I token vengono validati prima di creare sessioni utente
- **Scoping**: Google richiede `openid email profile`, Apple richiede `name email`

## 🐛 Troubleshooting

### Errori Comuni

1. **"Invalid client"**: Verifica che Client ID e Secret siano corretti
2. **"Redirect URI mismatch"**: Verifica che l'URI di redirect sia configurato correttamente
3. **"Invalid grant"**: Il codice di autorizzazione potrebbe essere scaduto o già utilizzato
4. **"Apple private key error"**: Verifica che la chiave privata sia nel formato corretto

### Debug

Abilita i log di debug per vedere i dettagli delle richieste OAuth:

```python
import logging
logging.getLogger("httpx").setLevel(logging.DEBUG)
```

## 📚 Risorse

- [Google OAuth2 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Apple Sign In Documentation](https://developer.apple.com/sign-in-with-apple/)
- [FastAPI OAuth2 Documentation](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
