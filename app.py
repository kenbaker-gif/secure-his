import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8000"
st.set_page_config(page_title="Secure HIS Dashboard", page_icon="🏥", layout="wide")

# --- SESSION STATE INITIALIZATION ---
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2740/2740605.png", width=80)
    st.title("Secure Gate")
    
    if not st.session_state.token:
        st.markdown("### Staff Login")
        u_input = st.text_input("Username", placeholder="e.g. dr_smith")
        p_input = st.text_input("Password", type="password")
        
        if st.button("Authenticate"):
            try:
                response = requests.post(f"{API_URL}/auth/login", json={"username": u_input.strip(), "password": p_input}, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.token = data["access_token"]
                    st.session_state.username = u_input.strip()
                    st.session_state.role = "Admin" if "admin" in u_input.lower() else "Doctor"
                    st.rerun()
                else:
                    st.error("Invalid Credentials")
            except Exception as e:
                st.error(f"Backend Offline: {e}")

        # Quick connectivity check for debugging
        if st.button("Check Backend"):
            try:
                r = requests.get(f"{API_URL}/openapi.json", timeout=3)
                if r.status_code == 200:
                    st.success("Backend reachable: openapi.json OK")
                else:
                    st.error(f"Backend responded with status {r.status_code}")
            except Exception as e:
                st.error(f"Backend Offline: {e}")
    else:
        st.success(f"Verified: {st.session_state.username}")
        st.info(f"Role: {st.session_state.role}")
        if st.button("🚪 Terminate Session"):
            st.session_state.token = None
            st.session_state.role = None
            st.rerun()

# --- MAIN DASHBOARD ---
if not st.session_state.token:
    st.markdown('<div class="header-box"><h1>🏥 Hospital Information System</h1><p>Secure Portal for Medical Professionals</p></div>', unsafe_allow_html=True)
    st.warning("🔒 Access Restricted. Please log in from the sidebar to view clinical data.")
    st.image("https://img.freepik.com/free-vector/data-security-concept-illustration_114360-1563.jpg", width=500)
else:
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    # --- DOCTOR DASHBOARD ---
    if st.session_state.role == "Doctor":
        st.markdown(f'<div class="header-box"><h1>🩺 Clinical Decision Support</h1><p>User: {st.session_state.username} | Status: Authorized</p></div>', unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Connection", "Stable", "Supabase")
        m2.metric("Pillar", "Confidentiality", "JWT")
        m3.metric("Pillar", "Availability", "Break-Glass")

        tab1, tab2 = st.tabs(["Patient Lookup", "Emergency Override"])
        
        with tab1:
            col1, col2 = st.columns([1, 2])
            with col1:
                p_id = st.number_input("Patient ID", min_value=1, step=1)
                if st.button("🔍 Search Record"):
                    try:
                        res = requests.get(f"{API_URL}/patients/{p_id}", headers=headers, timeout=5)
                        if res.status_code == 200:
                            st.session_state.p_data = res.json()
                        elif res.status_code == 403:
                            st.error("Access Denied.")
                        else:
                            st.error(f"Request failed: {res.status_code} - {res.text}")
                    except Exception as e:
                        st.error(f"Backend Offline: {e}")
            with col2:
                if "p_data" in st.session_state:
                    st.success(f"Displaying Record for ID: {st.session_state.p_data['id']}")
                    st.markdown(f"**Full Name:** {st.session_state.p_data['full_name']}")
                    st.info(f"**Clinical History:** {st.session_state.p_data['medical_history']}")

        with tab2:
            st.error("🔥 EMERGENCY BREAK-GLASS")
            em_id = st.number_input("Emergency ID", min_value=1, key="em")
            reason = st.text_area("Justification (Required for Audit Trail)")
            if st.button("Activate Emergency Access"):
                if reason:
                    try:
                        res = requests.post(f"{API_URL}/patients/{em_id}/break-glass", params={"reason": reason}, headers=headers, timeout=5)
                        if res.status_code == 200:
                            st.warning("Override Successful. Record Logged.")
                            st.json(res.json())
                        else:
                            st.error(f"Request failed: {res.status_code} - {res.text}")
                    except Exception as e:
                        st.error(f"Backend Offline: {e}")

    # --- ADMIN DASHBOARD ---
    elif st.session_state.role == "Admin":
        st.markdown(f'<div class="header-box"><h1>⚙️ System Administration</h1><p>User: {st.session_state.username} | Role: Integrity Officer</p></div>', unsafe_allow_html=True)
        
        a1, a2, a3 = st.columns(3)
        a1.metric("System Health", "Optimal")
        a2.metric("Encryption", "Bcrypt/AES")
        a3.metric("Database", "PostgreSQL")

        tab1, tab2, tab3 = st.tabs(["🛡️ Audit Logs", "👥 User Management", "🖥️ Network Health"])

        # --- AUDIT LOGS ---
        with tab1:
            st.subheader("Integrity Verification")
            if st.button("🔄 Pull Security Logs"):
                try:
                    res = requests.get(f"{API_URL}/admin/audit-logs", headers=headers, timeout=5)
                    if res.status_code == 200:
                        st.table(pd.DataFrame(res.json()))
                    else:
                        st.error(f"Request failed: {res.status_code} - {res.text}")
                except Exception as e:
                    st.error(f"Backend Offline: {e}")

        # --- USER MANAGEMENT ---
        with tab2:
            st.subheader("Account Provisioning")

            # Fetch roles dynamically
            try:
                role_res = requests.get(f"{API_URL}/admin/roles", headers=headers, timeout=5)
                if role_res.status_code == 200:
                    roles_list = [r["role_name"] for r in role_res.json()]
                elif role_res.status_code == 403:
                    st.warning("Not authorized to fetch roles; using default list.")
                    roles_list = ["Doctor", "Nurse", "Admin"]
                else:
                    st.error(f"Failed to fetch roles: {role_res.status_code}")
                    roles_list = ["Doctor", "Nurse", "Admin"]
            except Exception as e:
                st.error(f"Backend Offline while fetching roles: {e}")
                roles_list = ["Doctor", "Nurse", "Admin"]

            c1, c2 = st.columns(2)
            with c1:
                new_u = st.text_input("New Username")
                new_p = st.text_input("Initial Password", type="password")
            with c2:
                new_r = st.selectbox("Assign Role", roles_list)

            if st.button("Create Staff Account"):
                if not new_u or not new_p or not new_r:
                    st.error("Please fill in all fields before creating the account.")
                else:
                    payload = {"username": new_u.strip(), "password": new_p, "role_name": new_r}
                    try:
                        res = requests.post(f"{API_URL}/admin/register-user", json=payload, headers=headers, timeout=5)
                        if res.status_code == 200:
                            st.success(f"Account '{new_u}' successfully provisioned with role '{new_r}'.")
                            new_u, new_p = "", ""
                        else:
                            st.error(f"Failed to create account: {res.json().get('detail', res.text)}")
                    except Exception as e:
                        st.error(f"Backend Offline: {e}")

        # --- NETWORK HEALTH ---
        with tab3:
            st.subheader("Network & System Health")
            st.info("Monitoring tools coming soon...")
