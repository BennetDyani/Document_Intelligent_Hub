from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd
import streamlit as st


APP_NAME = "Enterprise AI Hub"


def initialize_session_state() -> None:
    """Initialize demo in-memory state.

    In production, these values should be backed by Postgres/DynamoDB/S3/vector DB.
    """
    defaults: dict[str, Any] = {
        "uploaded_documents": [],
        "audit_logs": [],
        "workflow_runs": [],
        "users": [
            {"username": "admin", "role": "Admin", "status": "Active"},
            {"username": "compliance.user", "role": "Compliance Analyst", "status": "Active"},
            {"username": "viewer.user", "role": "Viewer", "status": "Active"},
        ],
        "flagged_risks": [],
        "authenticated": False,
        "current_user": None,
        "current_role": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def add_audit_log(event_type: str, description: str, actor: str = "demo-user") -> None:
    st.session_state.audit_logs.insert(
        0,
        {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "actor": actor,
            "event_type": event_type,
            "description": description,
        },
    )


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            """
            <div style="padding: 0.75rem 0 1.25rem 0;">
                <h1 style="font-size: 1.6rem; margin-bottom: 0;">Enterprise AI Hub</h1>
                <p style="color: #808495; margin-top: 0.25rem;">
                    Document intelligence, automation, and enterprise knowledge.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        selected_tab = st.radio(
            "Navigation",
            [
                "Document Intelligence",
                "Workflow Orchestrator",
                "Knowledge Management",
                "Admin / Settings",
            ],
        )

        st.divider()

        if st.session_state.authenticated:
            st.success(f"Signed in as {st.session_state.current_user}")
            st.caption(f"Role: {st.session_state.current_role}")

            if st.button("Sign Out", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.current_user = None
                st.session_state.current_role = None
                st.rerun()
        else:
            st.info("Demo session is not authenticated.")

        st.divider()
        st.caption("Prototype UI")
        st.caption("Vector DB, S3, ECS, Postgres/DynamoDB integrations can be wired behind these controls.")

    return selected_tab


def render_status_cards() -> None:
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Documents", len(st.session_state.uploaded_documents))

    with col2:
        st.metric("Workflow Runs", len(st.session_state.workflow_runs))

    with col3:
        st.metric("Flagged Risks", len(st.session_state.flagged_risks))

    with col4:
        st.metric("Audit Events", len(st.session_state.audit_logs))


def document_intelligence_page() -> None:
    st.header("Document Intelligence Hub")
    st.caption("Upload, analyze, summarize, and flag compliance/risk in enterprise documents.")

    render_status_cards()
    st.divider()

    upload_col, list_col = st.columns([1, 1])

    with upload_col:
        st.subheader("Upload Documents")
        uploaded_files = st.file_uploader(
            "Drag and drop PDFs, DOCX, or text files",
            type=["pdf", "doc", "docx", "txt"],
            accept_multiple_files=True,
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                existing_names = {doc["name"] for doc in st.session_state.uploaded_documents}

                if uploaded_file.name not in existing_names:
                    doc_metadata = {
                        "name": uploaded_file.name,
                        "size_kb": round(uploaded_file.size / 1024, 2),
                        "type": uploaded_file.type or "Unknown",
                        "uploaded_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    }
                    st.session_state.uploaded_documents.append(doc_metadata)
                    add_audit_log("DOCUMENT_UPLOAD", f"Uploaded document: {uploaded_file.name}")

            st.success(f"{len(uploaded_files)} file(s) processed for demo metadata.")

    with list_col:
        st.subheader("Document List Panel")

        if st.session_state.uploaded_documents:
            st.dataframe(
                pd.DataFrame(st.session_state.uploaded_documents),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No documents uploaded yet.")

    st.divider()

    st.subheader("Semantic Search")
    search_query = st.text_input(
        "Search across documents",
        placeholder="Search for indemnity clauses, AML thresholds, privacy obligations...",
    )

    if search_query:
        add_audit_log("DOCUMENT_SEARCH", f"Document semantic search: {search_query}")
        st.write("### Results Viewer")

        st.info(
            "Demo result: Found potentially relevant clauses in uploaded documents. "
            "Connect this section to your vector database for real semantic retrieval."
        )

        st.markdown(
            """
            **Highlighted Clause**

            > The organization shall report suspicious financial activity exceeding the defined AML threshold
            > within the required regulatory reporting window.

            **Summary**

            The clause appears related to AML monitoring, threshold reporting, and regulatory compliance.

            **Risk Flags**

            - Medium risk: AML threshold reference should be validated against current policy.
            - Medium risk: Reporting window should be checked against jurisdiction-specific rules.
            """
        )

    st.divider()

    st.subheader("Document Actions")
    action_col1, action_col2, action_col3 = st.columns(3)

    with action_col1:
        if st.button("Summarize Document", use_container_width=True):
            add_audit_log("DOCUMENT_SUMMARY", "Generated document summary")
            st.success("Summary generated.")
            st.write(
                "Demo summary: This document contains operational, compliance, and reporting obligations. "
                "Several clauses may require review by legal or compliance teams."
            )

    with action_col2:
        if st.button("Flag Compliance Risks", use_container_width=True):
            risk = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "document": st.session_state.uploaded_documents[0]["name"]
                if st.session_state.uploaded_documents
                else "No document selected",
                "risk_level": "Medium",
                "description": "Potential AML threshold/reporting obligation requires validation.",
            }
            st.session_state.flagged_risks.insert(0, risk)
            add_audit_log("RISK_FLAGGED", risk["description"])
            st.warning("Compliance risk flagged.")

    with action_col3:
        if st.button("Export Report", use_container_width=True):
            add_audit_log("REPORT_EXPORT", "Exported document intelligence report")
            st.download_button(
                "Download Demo Report",
                data="Enterprise AI Hub - Demo Document Intelligence Report\n\nNo backend export configured yet.",
                file_name="document_intelligence_report.txt",
                mime="text/plain",
                use_container_width=True,
            )


def workflow_orchestrator_page() -> None:
    st.header("Workflow Orchestrator")
    st.caption("Trigger and schedule natural-language enterprise automation workflows.")

    workflow_col, status_col = st.columns([1.2, 0.8])

    with workflow_col:
        st.subheader("Command Input")
        command = st.text_area(
            "Describe the task to automate",
            placeholder="Generate monthly compliance report",
            height=120,
        )

        workflow_type = st.selectbox(
            "Workflow Selector",
            ["Reports", "Notifications", "Data Sync"],
        )

        run_col, schedule_col = st.columns(2)

        with run_col:
            if st.button("Run Workflow", use_container_width=True):
                workflow_run = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "workflow": workflow_type,
                    "command": command or "No command provided",
                    "status": "Completed",
                }
                st.session_state.workflow_runs.insert(0, workflow_run)
                add_audit_log("WORKFLOW_RUN", f"Ran {workflow_type} workflow")
                st.success("Workflow executed.")

        with schedule_col:
            if st.button("Schedule Workflow", use_container_width=True):
                workflow_run = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "workflow": workflow_type,
                    "command": command or "No command provided",
                    "status": "Scheduled",
                }
                st.session_state.workflow_runs.insert(0, workflow_run)
                add_audit_log("WORKFLOW_SCHEDULED", f"Scheduled {workflow_type} workflow")
                st.success("Workflow scheduled.")

    with status_col:
        st.subheader("Integration Status")

        integrations = pd.DataFrame(
            [
                {"Application": "Google Sheets", "Status": "Connected", "Last Sync": "2 min ago"},
                {"Application": "Slack", "Status": "Connected", "Last Sync": "5 min ago"},
                {"Application": "Email", "Status": "Connected", "Last Sync": "1 min ago"},
                {"Application": "Database", "Status": "Connected", "Last Sync": "10 min ago"},
            ]
        )

        st.dataframe(integrations, use_container_width=True, hide_index=True)

    st.divider()

    st.subheader("Execution Log Panel")

    if st.session_state.workflow_runs:
        st.dataframe(
            pd.DataFrame(st.session_state.workflow_runs),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("No workflow executions yet.")


def knowledge_management_page() -> None:
    st.header("Knowledge Management System")
    st.caption("Secure Q&A over enterprise knowledge with citations, source links, and RBAC.")

    auth_col, qa_col = st.columns([0.8, 1.2])

    with auth_col:
        st.subheader("Demo Login / RBAC")

        if not st.session_state.authenticated:
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="demo-password")
            role = st.selectbox("Role", ["Admin", "Compliance Analyst", "Viewer"])

            if st.button("Login", use_container_width=True):
                if username and password:
                    st.session_state.authenticated = True
                    st.session_state.current_user = username
                    st.session_state.current_role = role
                    add_audit_log("LOGIN", f"{username} logged in as {role}", actor=username)
                    st.success("Login successful.")
                    st.rerun()
                else:
                    st.error("Enter a username and password.")
        else:
            st.success("Authenticated")
            st.write(f"**User:** {st.session_state.current_user}")
            st.write(f"**Role:** {st.session_state.current_role}")

        st.divider()

        st.subheader("Document Source Viewer")
        st.markdown(
            """
            **Source Document:** AML Policy Manual.pdf  
            **Section:** 4.2 Transaction Monitoring Thresholds  
            **Source Link:** `/knowledge-base/aml-policy#section-4.2`
            """
        )

    with qa_col:
        st.subheader("Search / Q&A")
        question = st.text_input(
            "Ask a question",
            placeholder="What is the AML policy threshold?",
        )

        if question:
            actor = st.session_state.current_user or "anonymous"
            add_audit_log("KNOWLEDGE_QUERY", f"Knowledge Q&A query: {question}", actor=actor)

            st.write("### Answer Panel")
            st.markdown(
                """
                **AI Response**

                Based on the enterprise AML policy, transactions above the configured monitoring threshold
                should be reviewed by compliance operations and escalated when suspicious indicators are present.

                **Citations**

                1. AML Policy Manual.pdf — Section 4.2 Transaction Monitoring Thresholds
                2. Compliance Escalation SOP.docx — Section 2.1 Review Procedure

                **Source Links**

                - `/knowledge-base/aml-policy#section-4.2`
                - `/knowledge-base/compliance-escalation-sop#section-2.1`
                """
            )

        st.divider()

        action_col1, action_col2 = st.columns(2)

        with action_col1:
            if st.button("Add New Document", use_container_width=True):
                if st.session_state.current_role in {"Admin", "Compliance Analyst"}:
                    add_audit_log("KB_DOCUMENT_ADD", "Started add-document flow")
                    st.success("Add-document flow started.")
                else:
                    st.error("Insufficient permissions.")

        with action_col2:
            if st.button("View Audit Logs", use_container_width=True):
                if st.session_state.current_role == "Admin":
                    st.dataframe(
                        pd.DataFrame(st.session_state.audit_logs),
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.error("Only Admin users can view audit logs.")


def admin_settings_page() -> None:
    st.header("Admin / Settings")
    st.caption("Manage users, logs, deployment status, embeddings, and service controls.")

    user_col, infra_col = st.columns([1, 1])

    with user_col:
        st.subheader("User Management")

        with st.form("add_user_form"):
            new_username = st.text_input("New username")
            new_role = st.selectbox("Assign role", ["Admin", "Compliance Analyst", "Viewer"])
            submitted = st.form_submit_button("Add User", use_container_width=True)

            if submitted:
                if new_username:
                    st.session_state.users.append(
                        {
                            "username": new_username,
                            "role": new_role,
                            "status": "Active",
                        }
                    )
                    add_audit_log("USER_ADDED", f"Added user {new_username} with role {new_role}")
                    st.success("User added.")
                else:
                    st.error("Username is required.")

        if st.session_state.users:
            st.dataframe(
                pd.DataFrame(st.session_state.users),
                use_container_width=True,
                hide_index=True,
            )

        remove_username = st.selectbox(
            "Remove user",
            [user["username"] for user in st.session_state.users],
        )

        if st.button("Remove Selected User", use_container_width=True):
            st.session_state.users = [
                user for user in st.session_state.users if user["username"] != remove_username
            ]
            add_audit_log("USER_REMOVED", f"Removed user {remove_username}")
            st.warning(f"Removed {remove_username}.")

    with infra_col:
        st.subheader("AWS Deployment Status")

        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Container Health", "Healthy")
        metric_col2.metric("Uptime", "99.98%")
        metric_col3.metric("Desired Tasks", "3")

        st.progress(72, text="CPU utilization: 72%")
        st.progress(48, text="Memory utilization: 48%")

        st.subheader("Docker Controls")

        docker_col1, docker_col2 = st.columns(2)

        with docker_col1:
            if st.button("Restart Services", use_container_width=True):
                add_audit_log("DOCKER_RESTART", "Restarted services from admin UI")
                st.success("Demo restart command triggered.")

        with docker_col2:
            if st.button("View Logs", use_container_width=True):
                add_audit_log("DOCKER_LOG_VIEW", "Viewed service logs")
                st.code(
                    """
2026-06-19 10:00:01 streamlit service started
2026-06-19 10:00:03 vector-db health check passed
2026-06-19 10:00:05 api service ready
                    """.strip(),
                    language="text",
                )

    st.divider()

    st.subheader("System Logs")

    logs_tab, workflows_tab, risks_tab = st.tabs(
        ["Query History / Audit Logs", "Workflow Runs", "Flagged Risks"]
    )

    with logs_tab:
        if st.session_state.audit_logs:
            st.dataframe(
                pd.DataFrame(st.session_state.audit_logs),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No audit logs yet.")

    with workflows_tab:
        if st.session_state.workflow_runs:
            st.dataframe(
                pd.DataFrame(st.session_state.workflow_runs),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No workflow runs yet.")

    with risks_tab:
        if st.session_state.flagged_risks:
            st.dataframe(
                pd.DataFrame(st.session_state.flagged_risks),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No risks flagged yet.")

    st.divider()

    st.subheader("System Actions")
    action_col1, action_col2 = st.columns(2)

    with action_col1:
        if st.button("Sync with S3", use_container_width=True):
            add_audit_log("S3_SYNC", "Started S3 synchronization")
            st.success("S3 sync started.")

    with action_col2:
        if st.button("Refresh Embeddings", use_container_width=True):
            add_audit_log("EMBEDDINGS_REFRESH", "Started embeddings refresh")
            st.success("Embeddings refresh started.")


def main() -> None:
    st.set_page_config(
        page_title=APP_NAME,
        page_icon="🏢",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    initialize_session_state()

    selected_tab = render_sidebar()

    if selected_tab == "Document Intelligence":
        document_intelligence_page()
    elif selected_tab == "Workflow Orchestrator":
        workflow_orchestrator_page()
    elif selected_tab == "Knowledge Management":
        knowledge_management_page()
    elif selected_tab == "Admin / Settings":
        admin_settings_page()


if __name__ == "__main__":
    main()