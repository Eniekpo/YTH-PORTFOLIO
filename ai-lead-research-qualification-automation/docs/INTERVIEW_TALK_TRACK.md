# Interview Talk Track

## 30-second version

I built LeadPilot AI to show how I approach workflow automation as a business system rather than a collection of disconnected prompts. Raw prospect records are normalized, enriched, scored against an explainable ICP, and only qualified leads move into AI-assisted drafting. Every draft requires human approval before CRM handoff, and the workflow maintains an audit trail.

## Problem
Manual B2B prospecting creates repetitive research, inconsistent qualification, and generic outreach.

## Technical approach
- FastAPI for operational endpoints
- SQLAlchemy + SQLite for persistence
- Streamlit for operations and approval review
- deterministic enrichment and scoring
- optional LLM drafting
- n8n workflow for orchestration
- Docker for reproducibility
- Pytest for automated validation

## Most important design choice
I separated enrichment, scoring, drafting, review, and handoff. That makes the workflow auditable and prevents an AI-generated draft from automatically becoming an external action.

## What I would add in production
- approved data-enrichment APIs
- HubSpot/Salesforce connector
- OAuth and RBAC
- background queues
- Postgres
- provider rate limiting
- centralized observability
- secrets manager
- reviewer identity and approval history
- compliance-specific suppression logic
