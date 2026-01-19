# SkyComfort Airlines Support Chatbot

A specialized customer support chatbot for **SkyComfort Airlines** built with FastAPI, PostgreSQL, and OpenAI's GPT models. This project demonstrates a production-ready **Retrieval-Augmented Generation (RAG)** system with strict domain boundaries and professional airline branding.

---

## ✨ Features

- **Instant Access** - No authentication required, start chatting immediately
- **Domain-Specific RAG** - Answers only airline-related questions using vector search
- **Strict Guardrails** - Politely declines off-topic queries
- **Professional UI** - Airline-themed chat interface with sky blue branding
- **Vector Search** - pgvector for semantic similarity search
- **Chat Memory** - Contextual conversations with query reformulation
- **Modern Stack** - FastAPI, PostgreSQL, SQLAlchemy 2.x, OpenAI GPT-4o-mini

---

## 🎯 What It Does

SkyComfort Airlines Support is a **customer service chatbot** that helps passengers with:
- ✈️ Baggage allowances and policies
- 🎫 Check-in procedures (online and airport)
- ♿ Special assistance services
- 🔄 Flight changes and cancellations
- 💺 Seat selection and ticket types
- 🐕 Traveling with pets, children, or medical equipment

The chatbot uses **RAG (Retrieval-Augmented Generation)** to provide accurate, context-based answers from a curated knowledge base, ensuring it stays on-topic and provides reliable information.

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- OpenAI API key

### 1. Clone the Repository
```bash
git clone https://github.com/SimenRoisi/RAG.git
cd RAG
```

### 2. Set Up Environment Variables
Create a `.env` file in the project root:
```env
DB_USER=app
DB_PASS=devpass
DB_HOST=db
DB_PORT=5432
DB_NAME=appdb
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 3. Start the Application
```bash
docker-compose up --build
```

This starts:
- **API** at http://localhost:8000
- **Chat UI** at http://localhost:8000
- **API Docs** at http://localhost:8000/docs
- **Adminer** (DB UI) at http://localhost:8080

### 4. Run Database Migrations
```bash
docker-compose exec api alembic upgrade head
```

### 5. Ingest Airline Data
```bash
docker-compose exec api python scripts/ingest_airline_data_manual.py
```

This populates the vector database with SkyComfort Airlines support documents.

### 6. Start Chatting!
Open http://localhost:8000 in your browser - the chat interface loads instantly, no login required!

**Try asking:**
- "What is the carry-on baggage weight limit?"
- "How do I check in online?"
- "Can I travel with a wheelchair?"
- "What are the flight change fees?"

---

## 🏗️ Architecture

```
┌─────────────┐
│   User UI   │ (Frontend: HTML/JS/Tailwind)
└──────┬──────┘
       │ Anonymous Access
       ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend                 │
│  ┌──────────────────────────────────┐   │
│  │  /assist Endpoint                │   │
│  │  1. Contextualize query          │   │
│  │  2. Generate embedding           │   │
│  │  3. Vector search (top 3 chunks) │   │
│  │  4. Inject context into prompt   │   │
│  │  5. LLM generation with guardrails│  │
│  └──────────────────────────────────┘   │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│   PostgreSQL + pgvector                 │
│   - Documents & chunks                  │
│   - Vector embeddings (1536-dim)        │
│   - Chat conversation history           │
└─────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
RAG/
├── app/
│   ├── main.py           # FastAPI application
│   ├── config.py         # Settings & system prompt
│   ├── models.py         # SQLAlchemy models
│   ├── llm.py            # OpenAI integration
│   └── routers/
│       ├── assist.py     # RAG chat endpoint
│       ├── documents.py  # Document management
│       └── users.py      # User management
├── frontend/
│   └── index.html        # Chat UI
├── scripts/
│   └── ingest_airline_data_manual.py  # Data ingestion
├── alembic/              # Database migrations
├── tests/                # Test suite
├── docker-compose.yml    # Docker orchestration
└── requirements.txt      # Python dependencies
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.13 |
| **Framework** | FastAPI |
| **Database** | PostgreSQL 16 |
| **Vector Search** | pgvector |
| **ORM** | SQLAlchemy 2.x |
| **Migrations** | Alembic |
| **LLM** | OpenAI GPT-4o-mini |
| **Embeddings** | text-embedding-3-small |
| **Frontend** | HTML/JS/Tailwind CSS |
| **Containerization** | Docker & Docker Compose |

---

## 🧪 Testing

Run the test suite:
```bash
docker-compose exec api pytest
```

Test the RAG functionality:
```bash
docker-compose exec api python tests/verify_rag.py
```

---

## 🎨 Customization

### Change the System Prompt
Edit `app/config.py` to modify the chatbot's persona and guardrails.

### Add More Knowledge
Edit `scripts/ingest_airline_data_manual.py` to add more support documents, then re-run the ingestion script.

### Modify UI Branding
Edit `frontend/index.html` to change colors, messaging, or layout.

---

## 📊 Knowledge Base

The chatbot currently has knowledge about:
1. **Baggage Allowance** - Carry-on and checked baggage policies
2. **Check-in Information** - Online and airport procedures
3. **Special Assistance** - Wheelchair services, medical equipment, service animals
4. **Flight Changes & Cancellations** - Policies, fees, and refunds

All content is based on real airline policies (Norwegian Air) but anonymized to "SkyComfort Airlines."

---

## 🔒 Security Notes

- **Anonymous Access**: No user authentication required - suitable for public support tools
- **Environment Variables**: Never commit `.env` to version control
- **Rate Limiting**: **Strongly recommended** for production to prevent abuse (e.g., 10 requests/minute per IP)
- **CORS**: Configure appropriately for production deployment
- **OpenAI Costs**: Monitor API usage as all users share the same OpenAI account


---

## 📝 License

This project is for educational and demonstration purposes.

---

## 🙏 Acknowledgments

- Airline policies based on Norwegian Air's public support documentation
- Built as a learning project to demonstrate RAG implementation
- Inspired by modern customer support chatbot architectures

---

## 🚧 Future Enhancements

- [ ] Multi-language support
- [ ] Flight status lookup integration
- [ ] Booking reference validation
- [ ] Analytics dashboard
- [ ] Caching for common queries
- [ ] Production deployment guide

---

**Ready to fly with SkyComfort Airlines? Start the app and ask away!** ✈️
