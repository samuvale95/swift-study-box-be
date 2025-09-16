# Swift Study Box Backend

Backend API per Swift Study Box - una piattaforma di studio intelligente che combina quiz, esami, mappe concettuali e analisi di documenti.

## 🚀 Caratteristiche

- **Autenticazione JWT** con supporto OAuth2 (Google, Microsoft)
- **Gestione utenti e materie** con statistiche avanzate
- **Upload e processing file** (PDF, immagini, video, testo)
- **Sistema quiz ed esami** con generazione AI
- **Mappe concettuali interattive** generate automaticamente
- **Sincronizzazione cloud** (Google Drive, Dropbox, OneDrive)
- **Sistema di progressi** e achievement
- **API RESTful** complete con documentazione automatica

## 🛠️ Stack Tecnologico

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL + Redis
- **Storage**: AWS S3 / Google Cloud Storage
- **AI/ML**: OpenAI API per generazione contenuti
- **Background Tasks**: Celery + Redis
- **Containerizzazione**: Docker + Docker Compose

## 📋 Prerequisiti

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker e Docker Compose (opzionale)

## 🚀 Installazione

### 1. Clona il repository

```bash
git clone <repository-url>
cd swift-study-box-be
```

### 2. Crea ambiente virtuale

```bash
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```

### 3. Installa dipendenze

```bash
pip install -r requirements.txt
```

### 4. Configura variabili d'ambiente

```bash
cp env.example .env
# Modifica .env con le tue configurazioni
```

### 5. Avvia database e Redis

```bash
# Con Docker Compose
docker-compose up -d db redis

# Oppure installa manualmente PostgreSQL e Redis
```

### 6. Esegui migrazioni

```bash
# Le tabelle vengono create automaticamente al primo avvio
```

### 7. Avvia l'applicazione

```bash
# Sviluppo
uvicorn app.main:app --reload

# Produzione
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 🐳 Docker

### Avvio completo con Docker Compose

```bash
docker-compose up -d
```

Questo avvierà:
- PostgreSQL database
- Redis cache
- FastAPI application
- Celery worker
- Celery beat scheduler

### Solo l'applicazione

```bash
docker build -t swift-study-box-be .
docker run -p 8000:8000 swift-study-box-be
```

## 📚 API Documentation

Una volta avviata l'applicazione, la documentazione API è disponibile su:

- **Swagger UI**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc

## 🔧 Configurazione

### Variabili d'ambiente principali

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/swift_study_box
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (opzionale)
OPENAI_API_KEY=your-openai-api-key

# AWS S3 (opzionale)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET_NAME=your-bucket-name
```

### Configurazione OAuth2

Per abilitare l'autenticazione OAuth2, configura:

```env
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
MICROSOFT_CLIENT_ID=your-microsoft-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-client-secret
```

## 🧪 Testing

```bash
# Esegui tutti i test
pytest

# Esegui test con coverage
pytest --cov=app

# Esegui test specifici
pytest tests/test_auth.py
```

## 📊 Endpoints Principali

### Autenticazione
- `POST /api/v1/auth/register` - Registrazione utente
- `POST /api/v1/auth/login` - Login utente
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Informazioni utente corrente

### Gestione Materie
- `GET /api/v1/subjects` - Lista materie
- `POST /api/v1/subjects` - Crea materia
- `GET /api/v1/subjects/{id}/stats` - Statistiche materia

### Upload File
- `POST /api/v1/uploads` - Upload file
- `GET /api/v1/uploads` - Lista upload
- `POST /api/v1/uploads/{id}/process` - Processa file

### Quiz ed Esami
- `GET /api/v1/quizzes` - Lista quiz
- `POST /api/v1/quizzes/generate` - Genera quiz con AI
- `POST /api/v1/exams/generate` - Genera esame con AI

### Mappe Concettuali
- `GET /api/v1/concept-maps` - Lista mappe
- `POST /api/v1/concept-maps/generate` - Genera mappa con AI

### Sessioni di Studio
- `GET /api/v1/sessions` - Lista sessioni
- `POST /api/v1/sessions/start` - Inizia sessione

### Progressi
- `GET /api/v1/progress` - Progresso generale
- `GET /api/v1/progress/{subject_id}` - Progresso per materia

## 🔄 Background Tasks

L'applicazione utilizza Celery per task asincroni:

- **File Processing**: Estrazione testo da PDF, OCR, speech-to-text
- **AI Generation**: Generazione quiz, esami, mappe concettuali
- **Notifications**: Email, achievement, reminder

### Avvio Celery

```bash
# Worker
celery -A app.core.celery worker --loglevel=info

# Beat (scheduler)
celery -A app.core.celery beat --loglevel=info
```

## 🏗️ Architettura

```
app/
├── api/                    # API endpoints
│   └── v1/
│       └── endpoints/
├── core/                   # Configurazione core
│   ├── config.py          # Settings
│   ├── database.py        # Database config
│   ├── security.py        # JWT, OAuth2
│   └── middleware.py      # Custom middleware
├── models/                 # Database models
├── schemas/                # Pydantic schemas
├── services/               # Business logic
├── tasks/                  # Celery tasks
└── main.py                # FastAPI app
```

## 🚀 Deployment

### Produzione con Docker

```bash
# Build per produzione
docker build -t swift-study-box-be:prod .

# Run con variabili d'ambiente
docker run -d \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e SECRET_KEY=... \
  swift-study-box-be:prod
```

### Variabili d'ambiente produzione

Assicurati di configurare:
- `SECRET_KEY` sicura
- `DATABASE_URL` di produzione
- `REDIS_URL` di produzione
- Chiavi API per servizi esterni
- `DEBUG=False`

## 🤝 Contribuire

1. Fork del repository
2. Crea un branch per la feature (`git checkout -b feature/amazing-feature`)
3. Commit delle modifiche (`git commit -m 'Add amazing feature'`)
4. Push del branch (`git push origin feature/amazing-feature`)
5. Apri una Pull Request

## 📝 Licenza

Questo progetto è sotto licenza MIT. Vedi il file `LICENSE` per dettagli.

## 🆘 Supporto

Per supporto e domande:
- Apri una issue su GitHub
- Contatta il team di sviluppo

## 🔄 Changelog

### v1.0.0
- Rilascio iniziale
- API complete per tutte le funzionalità
- Supporto AI per generazione contenuti
- Sistema di autenticazione completo
- Integrazione cloud storage
