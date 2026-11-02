# Architecture

## Components

### 1. Intake Layer
Accepts leads from CSV or REST API.

### 2. Normalization Layer
Cleans domains, email fields, company metadata, and structured fields.

### 3. Enrichment Layer
Implements a swappable service interface. The demo version uses only supplied lead attributes and local deterministic logic, avoiding fabricated web research.

### 4. ICP Scoring Engine
Produces:
- numeric score;
- qualification category;
- explanation string.

This makes the workflow auditable and easy to discuss in interviews.

### 5. Drafting Layer
Uses a deterministic Jinja-based template by default.
An optional OpenAI connector is included behind environment variables.

### 6. Human Review
No lead can enter the CRM-ready state without approval.

### 7. Handoff
Approved records can be exported to CSV or adapted to a CRM webhook.

### 8. Audit Trail
Every enrichment, scoring, drafting, approval, and rejection action is logged.

## Why This Design Matters

Many automation demos jump directly from "lead found" to "email sent."
This project deliberately separates:
- evidence collection;
- qualification;
- content drafting;
- human review;
- handoff.

That separation is safer and closer to how production RevOps and sales-operations systems should be designed.
