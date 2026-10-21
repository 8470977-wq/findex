# findex — Лабораторна робота №8 Швидше, потім розумніше: профілювання, NumPy і семантичний пошук

> **Одне речення про проєкт**: Повнофункціональна високоефективна пошукова система на Python з інвертованим індексом, паралельним індексуванням, асинхронним краулером, FastAPI REST API та семантичним гібридним пошуком.

🌐 **Живий публічний сервіс (Render)**: https://findex-nnc5.onrender.com
![Version](https://img.shields.io/badge/version-v1.0.0-brightgreen)

---

## 1. Архітектурна схема системи (Data Flow)

```text
 [ Веб-сайти ]
       │
 (Async Crawler)
       ▼
 [ JSONL Корпус ] ──► (Tokenizer) ──► (Inverted Index)
                                              │
 [ Web UI / API ] ◄── (FastAPI) ◄── (BM25 + RRF Hybrid)
