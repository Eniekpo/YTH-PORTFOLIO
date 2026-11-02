# Portfolio positioning

## Suggested project title
**InsightForge: Market Research & Survey Analytics SaaS Platform**

## One-line value proposition
A full-stack research workspace that turns raw survey files into quality checks, descriptive statistics, cross-tabulation, association tests, automated research narratives and downloadable reports.

## Skills demonstrated
- React + Vite frontend architecture
- FastAPI REST API design
- SQLite / SQLAlchemy relational data modelling
- Token-based authentication and password hashing
- File upload and persistence
- Survey statistics with pandas + SciPy
- Cross-tabulation and chi-square tests
- Data-quality profiling
- Automated narrative insight generation
- Excel and PDF report export
- Docker and CI testing

## Interview talking points
1. The statistical narrative is deterministic by default so the demo runs locally and does not invent findings.
2. Chi-square is included because market research frequently compares categorical respondent groups and outcomes.
3. Uploaded response files are separated from project metadata to keep the relational model lightweight while preserving reproducibility.
4. A production version can move uploads to object storage, SQLite to PostgreSQL, and large analyses to background jobs.
5. Strong next enhancements include survey weighting, multiple-response questions, significance banners, saved analysis views, team roles and audit logs.
