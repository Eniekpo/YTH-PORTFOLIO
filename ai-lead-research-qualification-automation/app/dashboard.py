import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json
import pandas as pd
import streamlit as st
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models import Lead, AuditLog
from app.services.pipeline import run_pipeline, log_action

Base.metadata.create_all(bind=engine)

st.set_page_config(
    page_title="LeadPilot AI",
    page_icon="⚙️",
    layout="wide"
)

st.title("LeadPilot AI")
st.caption("AI-Powered Lead Research, Qualification & Outreach Automation System")

db: Session = SessionLocal()

try:
    leads = db.query(Lead).order_by(Lead.score.desc(), Lead.id.asc()).all()

    if not leads:
        st.warning("No leads found. Run `python -m app.seed` first.")
        st.stop()

    total = len(leads)
    qualified = sum(1 for x in leads if x.qualification == "Qualified")
    pending = sum(1 for x in leads if x.approval_status == "Pending Review")
    approved = sum(1 for x in leads if x.approval_status == "Approved for Handoff")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Leads", total)
    c2.metric("Qualified", qualified)
    c3.metric("Pending Review", pending)
    c4.metric("Approved", approved)

    st.divider()

    if st.button("Run Full Automation Pipeline", type="primary"):
        with st.spinner("Processing leads..."):
            result = run_pipeline(db)
        st.success(f"Processed {len(result)} leads.")
        st.rerun()

    df = pd.DataFrame([{
        "ID": x.id,
        "Company": x.company_name,
        "Industry": x.industry,
        "Country": x.country,
        "Employees": x.employee_count,
        "Score": x.score,
        "Qualification": x.qualification,
        "Approval": x.approval_status,
        "Suppressed": x.suppressed,
    } for x in leads])

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Lead Pipeline", "Approval Queue", "Approved Handoff", "Audit Log"]
    )

    with tab1:
        st.subheader("Lead Qualification Pipeline")
        st.dataframe(df, use_container_width=True, hide_index=True)

        selected_id = st.selectbox(
            "Inspect lead",
            options=[x.id for x in leads],
            format_func=lambda i: next(x.company_name for x in leads if x.id == i)
        )
        lead = db.get(Lead, selected_id)
        left, right = st.columns(2)

        with left:
            st.markdown("#### Qualification")
            st.write(f"**Score:** {lead.score:.0f}/100")
            st.write(f"**Status:** {lead.qualification}")
            st.write("**Score explanation:**")
            st.code(lead.score_explanation or "Not scored yet.")
        with right:
            st.markdown("#### Research Evidence")
            st.write(lead.research_note or "No research note yet.")
            st.write("**Evidence:**")
            for item in [x for x in (lead.evidence or "").split("||") if x]:
                st.write(f"- {item}")

    with tab2:
        queue = [x for x in leads if x.approval_status == "Pending Review"]
        if not queue:
            st.info("No drafts are waiting for review.")
        for lead in queue:
            with st.expander(f"{lead.company_name} · Score {lead.score:.0f}", expanded=False):
                st.write(f"**Subject:** {lead.draft_subject}")
                st.text_area(
                    "Draft",
                    value=lead.draft_body or "",
                    height=230,
                    key=f"draft_{lead.id}",
                    disabled=True
                )
                st.caption("Human approval is mandatory before CRM handoff.")
                a, b = st.columns(2)
                if a.button("Approve for Handoff", key=f"approve_{lead.id}"):
                    lead.approval_status = "Approved for Handoff"
                    db.commit()
                    log_action(db, lead.id, "APPROVED", "Approved in Streamlit dashboard")
                    st.rerun()
                if b.button("Reject", key=f"reject_{lead.id}"):
                    lead.approval_status = "Rejected"
                    db.commit()
                    log_action(db, lead.id, "REJECTED", "Rejected in Streamlit dashboard")
                    st.rerun()

    with tab3:
        approved_rows = [x for x in leads if x.approval_status == "Approved for Handoff"]
        handoff = pd.DataFrame([{
            "Company": x.company_name,
            "Contact": x.contact_name,
            "Email": x.email,
            "Score": x.score,
            "Subject": x.draft_subject,
            "Status": x.approval_status,
        } for x in approved_rows])
        st.dataframe(handoff, use_container_width=True, hide_index=True)
        if not handoff.empty:
            st.download_button(
                "Download CRM-ready CSV",
                handoff.to_csv(index=False).encode("utf-8"),
                "crm_ready_leads.csv",
                "text/csv"
            )

    with tab4:
        logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(300).all()
        audit_df = pd.DataFrame([{
            "Timestamp": x.created_at,
            "Lead ID": x.lead_id,
            "Action": x.action,
            "Details": x.details,
        } for x in logs])
        st.dataframe(audit_df, use_container_width=True, hide_index=True)

finally:
    db.close()
