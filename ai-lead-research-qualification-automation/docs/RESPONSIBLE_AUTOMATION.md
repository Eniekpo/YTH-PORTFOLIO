# Responsible Automation Notes

This project is designed for portfolio demonstration and controlled business workflows.

## Guardrails

1. **Human approval required**
   Drafts are not automatically sent.

2. **Evidence-constrained personalization**
   The default drafting engine only uses supplied lead fields and stored evidence.

3. **No invented research claims**
   The system does not pretend that a company raised funding, hired staff, changed software, or experienced a problem unless that information is explicitly provided by an approved source.

4. **Suppression support**
   Suppressed leads receive a score of zero and cannot enter the outreach stage.

5. **Explainable qualification**
   Scores store their component reasons.

6. **Auditability**
   Key workflow actions are logged.

7. **Provider abstraction**
   External research, CRM, and messaging providers should be connected only under the business's data-processing, privacy, and compliance requirements.

## Production Considerations

Before real deployment:
- validate lawful basis and regional outreach rules;
- maintain opt-out/suppression lists;
- use approved enrichment providers;
- rate-limit provider APIs;
- secure secrets;
- add role-based access;
- add reviewer identity;
- add CRM idempotency;
- monitor model/prompt drift;
- record consent and source provenance where required.
