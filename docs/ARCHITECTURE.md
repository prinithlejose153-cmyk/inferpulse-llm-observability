# Architecture Notes

## 1. System Goal

InferPulse is designed as a lightweight inference logging and ingestion system for an LLM application. The goal is to demonstrate how an AI product can capture useful metadata around LLM calls and make it observable through dashboards.

---

## 2. High-Level Flow

```txt
User
 |
 v
React Chat UI
 |
 v
Flask Chat API
 |
 v
InferenceLogger SDK Wrapper
 |
 v
Foundation Model Provider / Mock Fallback
 |
 v
Ingestion API
 |
 v
SQLite Database
 |
 v
Dashboard API
 |
 v
React Dashboard