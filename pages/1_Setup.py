import streamlit as st
from common import inject_base_css, brand_header, render_stepper, render_background_orbs, page_header, init_session_state

st.set_page_config(page_title="Setup · AutoCertify", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")
init_session_state()
inject_base_css()
render_background_orbs()
brand_header()
render_stepper("setup")

page_header(
    "Step 1 of 3",
    "Setup",
    "Connect the Gmail account certificates will be sent from, then upload "
    "your participant list and certificate template."
)

# ── GMAIL CONFIG ──────────────────────────────
st.markdown("""
<div class="gmail-card">
  <div class="step-header">
    <div class="step-num">✉</div>
    <div>
      <div class="step-title">Gmail configuration</div>
      <div class="step-desc">Your credentials are used only for this session and are never stored</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

gc1, gc2 = st.columns(2)
with gc1:
    st.session_state.sender_email = st.text_input(
        "Gmail address", value=st.session_state.sender_email, placeholder="you@gmail.com"
    )
with gc2:
    st.session_state.app_password = st.text_input(
        "App password", value=st.session_state.app_password, type="password",
        placeholder="xxxx xxxx xxxx xxxx"
    )

if st.session_state.sender_email and st.session_state.app_password:
    st.markdown(f"""
    <div class="status-badge status-ready pulse-once">
      <span style="width:6px;height:6px;border-radius:50%;background:var(--good);display:inline-block;flex-shrink:0;"></span>
      Ready · {st.session_state.sender_email}
    </div>
    """, unsafe_allow_html=True)

with st.expander("How to create a Gmail App Password"):
    st.markdown("""
    <div class="gmail-hint">
    1 · Go to <b style="color:var(--accent)">myaccount.google.com</b><br>
    2 · Security → 2-Step Verification → turn on<br>
    3 · Search "App Passwords" in the search bar<br>
    4 · Select app: <b style="color:var(--accent)">Mail</b> → Generate<br>
    5 · Copy the 16-character code and paste it above
    </div>
    """, unsafe_allow_html=True)

delay_col, _ = st.columns([1, 2])
with delay_col:
    st.session_state.delay = st.slider("Delay between emails (s)", 1, 10, st.session_state.delay)

st.markdown("<hr>", unsafe_allow_html=True)

# ── UPLOADS ────────────────────────────────────
st.markdown("""
<div class="step-card">
  <div class="step-header">
    <div class="step-num">01</div>
    <div>
      <div class="step-title">Upload your files</div>
      <div class="step-desc">Participant list in CSV · Certificate template in PDF</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

u1, u2 = st.columns(2)
with u1:
    csv_file = st.file_uploader("Participant list (CSV)", type=["csv"], key="csv_uploader")
    if csv_file is not None:
        st.session_state.csv_bytes = csv_file.getvalue()
        st.session_state.csv_filename = csv_file.name
    if st.session_state.csv_bytes:
        st.caption(f"Using: {st.session_state.csv_filename}")

with u2:
    template_file = st.file_uploader("Certificate template (PDF)", type=["pdf"], key="pdf_uploader")
    if template_file is not None:
        st.session_state.template_bytes = template_file.getvalue()
        st.session_state.template_filename = template_file.name
    if st.session_state.template_bytes:
        st.caption(f"Using: {st.session_state.template_filename}")

st.markdown("<hr>", unsafe_allow_html=True)

ready = bool(
    st.session_state.sender_email and st.session_state.app_password
    and st.session_state.csv_bytes and st.session_state.template_bytes
)

if not ready:
    missing = []
    if not st.session_state.sender_email: missing.append("Gmail address")
    if not st.session_state.app_password: missing.append("App password")
    if not st.session_state.csv_bytes:    missing.append("CSV file")
    if not st.session_state.template_bytes: missing.append("Certificate PDF")
    st.markdown(f'<div class="status-badge status-warn">Still needed: {" · ".join(missing)}</div>', unsafe_allow_html=True)
    st.write("")

nav1, nav2 = st.columns([1, 1])
with nav1:
    st.page_link("app.py", label="← Back to overview")
with nav2:
    if ready:
        st.page_link("pages/2_Design.py", label="Continue to Design →")
    else:
        st.button("Continue to Design →", disabled=True)