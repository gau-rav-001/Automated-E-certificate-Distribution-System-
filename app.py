import io
import pandas as pd
import streamlit as st
from common import (
    inject_base_css, brand_header, render_background_orbs, render_icon_ring,
    step_status, init_session_state,
)

st.set_page_config(page_title="AutoCertify", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")
init_session_state()
inject_base_css()
render_background_orbs()
brand_header()

status = step_status()
ss = st.session_state

# ── HERO ────────────────────────────────────────
render_icon_ring()

st.markdown("""
<div style="text-align:center; margin-top:-2.6rem; padding:0 0 clamp(1rem,2vw,1.6rem);">
  <div class="page-eyebrow" style="justify-content:center; display:flex;">Certificate Automation Platform</div>
  <div style="
    font-size:clamp(2.4rem,6.4vw,4.2rem); font-weight:700; letter-spacing:-0.035em; line-height:1.02;
    color:var(--text); font-family:'Google Sans Flex',sans-serif;
    animation:fadeSlideUp 0.6s 0.05s ease both;">
    Experience liftoff for<br>your certificates
  </div>
  <div style="
    margin-top:0.8rem; font-family:'JetBrains Mono',monospace; font-size:clamp(0.78rem,1.8vw,0.92rem);
    letter-spacing:0.08em; color:var(--text-dim); text-transform:uppercase;
    animation:fadeSlideUp 0.6s 0.12s ease both;">
    Create &nbsp;·&nbsp; Generate &nbsp;·&nbsp; Distribute
  </div>
</div>
""", unsafe_allow_html=True)

hc1, hc2, hc3 = st.columns([1, 1, 1])
with hc2:
    if status["design"]:
        st.page_link("pages/3_Send.py", label="Continue to Send")
    elif status["setup"]:
        st.page_link("pages/2_Design.py", label="Continue to Design")
    else:
        st.page_link("pages/1_Setup.py", label="Get started")

st.markdown('<div style="height:1.6rem;"></div>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ── WORKFLOW: 01 SETUP · 02 DESIGN · 03 SEND ────
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown(f"""
    <div class="step-card stagger-1">
      <div class="step-header">
        <div class="step-num">01</div>
        <div>
          <div class="step-title">Setup</div>
          <div class="step-desc">Connect Gmail, upload your participant list and certificate template.</div>
        </div>
      </div>
      {'<div class="status-badge status-ready">Ready</div>' if status['setup'] else '<div class="status-badge status-warn">Not started</div>'}
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Setup.py", label="Go to Setup →")

with c2:
    st.markdown(f"""
    <div class="step-card stagger-2">
      <div class="step-header">
        <div class="step-num">02</div>
        <div>
          <div class="step-title">Design</div>
          <div class="step-desc">Map your CSV columns and position the name and department with a live preview.</div>
        </div>
      </div>
      {'<div class="status-badge status-ready">Ready</div>' if status['design'] else '<div class="status-badge status-warn">Needs Setup first</div>'}
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_Design.py", label="Go to Design →")

with c3:
    st.markdown("""
    <div class="step-card stagger-3">
      <div class="step-header">
        <div class="step-num">03</div>
        <div>
          <div class="step-title">Send</div>
          <div class="step-desc">Write the email message and send every certificate — with a live delivery log.</div>
        </div>
      </div>
      <div class="status-badge status-warn">Needs Design first</div>
    </div>
    """, unsafe_allow_html=True)
    st.page_link("pages/3_Send.py", label="Go to Send →")

# ── PLATFORM STATISTICS (from your actual uploaded data — nothing invented) ──
st.markdown('<div class="eyebrow-label"><span class="dot"></span>Platform status</div>', unsafe_allow_html=True)

participant_count = "—"
if ss.csv_bytes:
    try:
        df = pd.read_csv(io.BytesIO(ss.csv_bytes), encoding="cp1252")
        participant_count = str(len(df))
    except Exception:
        participant_count = "—"

files_ready = sum(bool(x) for x in [ss.csv_bytes, ss.template_bytes])
gmail_ready = "Connected" if (ss.sender_email and ss.app_password) else "Not connected"

st.markdown(f"""
<div class="stat-row">
  <div class="stat-pill">👥 <b>{participant_count}</b> participants loaded</div>
  <div class="stat-pill">📁 <b>{files_ready}/2</b> files uploaded</div>
  <div class="stat-pill">✉️ Gmail: <b>{gmail_ready}</b></div>
  <div class="stat-pill">⏱️ <b>{ss.delay}s</b> delay between sends</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<div class="hint-pill">
  Your Gmail credentials and uploaded files stay in this browser session only —
  nothing is written to a database or sent anywhere except Gmail's own SMTP server.
</div>
""", unsafe_allow_html=True)