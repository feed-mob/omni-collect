# OmniCollect

Multi-platform topic intelligence API for AI agents. Install a Skill guide, auto-collect data from Xiaohongshu, GitHub, Twitter and more, then generate structured intel reports locally.

## How It Works

```
┌──────────────┐     install skill      ┌──────────────────┐
│  AI Agent    │◄───────────────────────│  Skill (API Guide)│
│  Claude Code │                        └──────────────────┘
│  Codex       │── HTTP + secret key ──►┌──────────────────┐
│  Continue    │◄── structured JSONL ───│  OmniCollect API │
│  OpenClaw    │                        │  (Django + DRF)  │
│  ...         │                        └───────┬──────────┘
└──────┬───────┘                                │
       │ local AI analysis                      │ Agent-Reach
       ▼                                        ▼
┌──────────────┐                     ┌─────────────────────┐
│  Intel Report│                     │ Xiaohongshu│GitHub  │
│  JSONL + MD  │── sync report ─────►│ Twitter    │ ...    │
└──────────────┘                     └─────────────────────┘
```

- **Platform (cloud)**: Data collection API, auth, report sync
- **Skill (local)**: A Markdown guide that teaches any AI agent how to call our APIs
- **AI analysis (local)**: Runs on the user's own model — we don't do inference

## Supported Platforms

| Platform | Method | Status |
|----------|--------|--------|
| Xiaohongshu | mcporter + Cookie | Planned |
| GitHub | gh CLI | Planned |
| Twitter/X | bird + Cookie | Planned |
| More (HN, Reddit, ...) | TBD | Future |

## Tech Stack

- **Python + Django + DRF** — full-stack, one project
- **SQLite** — lightweight, zero-ops
- **Agent-Reach** — native Python integration for multi-platform data fetching

## Auth

No human registration needed. The AI agent handles everything:

1. AI generates a key pair locally
2. AI calls `POST /api/v1/auth/register` with the public key
3. Server stores the key (max 3 registrations per IP)
4. Key is persisted in the skill directory — done

## Project Structure

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the full architecture document, module breakdown, and development schedule.

## License

TBD
