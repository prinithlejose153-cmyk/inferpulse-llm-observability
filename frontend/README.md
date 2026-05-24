# InferPulse — Lightweight LLM Inference Logging & Observability

InferPulse is a full-stack LLM observability project that demonstrates how an AI application can capture, ingest, store, and visualize inference metadata from foundation model calls.

It includes a chatbot UI, lightweight SDK/wrapper around LLM calls, ingestion API, database storage, PII redaction, and dashboard metrics for latency, token usage, success rate, and errors.

---

## Features

- Multi-turn chatbot UI
- Short conversational context
- Lightweight SDK/wrapper for LLM calls
- Near real-time inference log ingestion
- Ingestion API with payload validation
- Chat messages + inference logs stored in database
- Latency, token, success, error dashboard
- Recent inference logs table
- Conversation list and resume conversation
- Cancel/delete conversation
- PII redaction for email/phone-like data
- Gemini provider integration with mock fallback
- Docker Compose setup included

---

## Tech Stack

### Backend
- Python
- Flask
- Flask SQLAlchemy
- SQLite
- Gemini API
- REST APIs

### Frontend
- React
- Vite
- Axios
- Recharts
- CSS

### DevOps
- Docker
- Docker Compose

---

## Architecture Overview

```txt
React Frontend
   |
   | POST /api/chat
   v
Flask Chat API
   |
   | calls LLM through SDK wrapper
   v
InferenceLogger SDK
   |
   | captures metadata
   | sends log near real-time
   v
Ingestion API
   |
   | validates payload
   | redacts PII
   | stores processed log
   v
SQLite Database
   |
   v
Dashboard APIs -> React Dashboard