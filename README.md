---
title: NBFC Onboarding
emoji: 🏦
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# NBFC Onboarding — Multi-Agent Loan Pipeline

A LangGraph-based multi-agent system for NBFC loan onboarding: document/KYC
verification, credit risk assessment (CIBIL + DTI + RAG policy grounding),
and automated customer communication.

## Deployment

Deployed via Docker. Currently hosted on [Render](https://render.com) (Web
Service, Docker runtime). The `sdk`/`app_port` frontmatter above is for
Hugging Face Spaces compatibility if redeployed there later.

## Required Secrets (set as environment variables on the hosting platform)

- `SUPABASE_URL`
- `SUPABASE_SERVICE_KEY`
- `GROQ_API`
- `SENDGRID_API_KEY1`
- `SENDGRID_FROM_EMAIL`
