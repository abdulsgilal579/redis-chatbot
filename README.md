# 🤖 Redis Chatbot

A conversational AI chatbot built with **FastAPI**, **Redis**, and **Groq (LLaMA 3)**. Redis stores conversation history per session, so the AI remembers what you said — even across server restarts and multiple workers.

---

## 🧠 How It Works

```
User Request
     │
     ▼
 FastAPI (any worker)
     │
     ├──► Redis (read session history)
     │         │
     │         └──► Returns past messages
     │
     ├──► Groq API (send full history + new message)
     │         │
     │         └──► Returns AI reply
     │
     └──► Redis (save updated history with 30-min TTL)
```

Every message appends to a conversation stored in Redis under a unique `session_id`. Sessions automatically expire after **30 minutes** of inactivity.

---

## 🗂️ Project Structure

```
redis-chatbot/
├── main.py           # FastAPI app + chat endpoints
├── redis_client.py   # Redis connection + session helpers
├── groq_client.py    # Groq API wrapper
├── .env              # API keys (never commit this)
└── requirements.txt
```

---

## ⚙️ Setup

### Prerequisites

- Python 3.9+
- Docker (for Redis)
- A [Groq API key](https://console.groq.com)

### 1. Clone and create a virtual environment

```bash
git clone <your-repo-url>
cd redis-chatbot
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn groq redis python-dotenv
```

### 3. Set up environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
REDIS_URL=redis://localhost:6379
```

### 4. Start Redis via Docker

```bash
docker run -d -p 6379:6379 redis
```

### 5. Run the server

```bash
# Single worker
uvicorn main:app --reload

# Multiple workers (production-like)
uvicorn main:app --workers 4
```

Visit `http://localhost:8000/docs` for the interactive Swagger UI.

---

## 🚀 API Endpoints

### `POST /chat`

Send a message. Omit `session_id` on your first message — the server will generate one and return it.

**Request:**
```json
{
  "session_id": "optional-existing-session-id",
  "message": "Hey, is Redis good to use?"
}
```

**Response:**
```json
{
  "session_id": "9cb80ea0-7032-4dd3-b465-749b73e634f1",
  "reply": "Redis is great for caching, session storage, and real-time use cases...",
  "history_length": 2
}
```

---

### `GET /history/{session_id}`

Inspect the full conversation history stored in Redis.

**Response:**
```json
{
  "session_id": "9cb80ea0-...",
  "history": [
    { "role": "user", "content": "Hey, is Redis good to use?" },
    { "role": "assistant", "content": "Redis is great for..." }
  ]
}
```

---

### `DELETE /session/{session_id}`

Manually clear a session from Redis.

**Response:**
```json
{ "message": "Session 9cb80ea0-... cleared." }
```

---

## 🔍 Verifying Redis Works

### 1. History survives a server restart
Restart uvicorn, then call `GET /history/{session_id}` — your conversation is still there.

### 2. Check session TTL (auto-expiry)
```bash
docker exec -it <container_id> redis-cli
TTL session:<your-session-id>
```
You'll see a countdown (max 1800 seconds). It resets every time you send a message.

### 3. Multi-worker session sharing
Run with `--workers 4` and add this to your `/chat` endpoint:
```python
import os
print(f"[PID {os.getpid()}] Session: {session_id} | History length: {len(history)}")
```
You'll see different PIDs handling requests, but history keeps growing — all workers read from the same Redis.

---

## 📦 Tech Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI |
| AI model | LLaMA 3 8B via Groq |
| Session store | Redis (in-memory) |
| Redis client | redis-py (async) |
| Server | Uvicorn |

---

## 💡 Key Redis Concepts Used

| Concept | What it does in this project |
|---|---|
| `SET` / `GET` | Store and retrieve session history as JSON |
| `SETEX` | Set history with a 30-minute auto-expiry |
| `DELETE` | Manually clear a session |
| TTL | Time-to-live countdown on each session key |

---

## 🛑 Limitations

- Redis stores data in RAM — if the Docker container is removed (not just stopped), data is lost
- For production, enable Redis persistence (`AOF` or `RDB` snapshots)
- History grows unbounded per session — consider trimming to last N messages for very long conversations

---

## 📄 License

MIT
