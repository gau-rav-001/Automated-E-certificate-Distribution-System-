import io
import os
import time
import smtplib
import tempfile
import pandas as pd
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

from common import inject_base_css, brand_header, render_stepper, render_background_orbs, page_header, init_session_state, build_certificate_pdf

st.set_page_config(page_title="Send · AutoCertify", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")
init_session_state()
inject_base_css()
render_background_orbs()
brand_header()
render_stepper("send")

ss = st.session_state
if not (ss.csv_bytes and ss.template_bytes and ss.name_col and ss.dept_col and ss.email_col):
    st.markdown("""
    <div class="status-badge status-warn">Finish Design first — map your CSV columns before sending.</div>
    """, unsafe_allow_html=True)
    st.page_link("pages/2_Design.py", label="← Go to Design")
    st.stop()

try:
    data = pd.read_csv(io.BytesIO(ss.csv_bytes), encoding="cp1252")
    data.columns = data.columns.str.strip()
except Exception as e:
    st.error(f"Could not read CSV: {e}")
    st.stop()

page_header(
    "Step 3 of 3",
    "Send",
    "Write the message every participant will receive, then send — "
    "each one gets their own personalized certificate attached."
)

# ── COMPOSE ────────────────────────────────────
st.markdown("""
<div class="step-card">
  <div class="step-header">
    <div class="step-num">04</div>
    <div>
      <div class="step-title">Compose email</div>
      <div class="step-desc">Write the message every participant will receive</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

ss.email_subject = st.text_input("Subject line", value=ss.email_subject)
ss.email_body = st.text_area("Message body", height=175, value=ss.email_body)
st.markdown("""
<div class="hint-pill">
  Use <code>{name}</code> anywhere — it will be replaced with each participant's actual name.
</div>
""", unsafe_allow_html=True)

# ── SEND ───────────────────────────────────────
st.markdown("""
<div class="step-card">
  <div class="step-header">
    <div class="step-num">05</div>
    <div>
      <div class="step-title">Send certificates</div>
      <div class="step-desc">AutoCertify generates and emails every certificate automatically</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

total = len(data)
est_min = (total * ss.delay) // 60
est_sec = (total * ss.delay) % 60
st.markdown(f"""
<div class="stat-row">
  <div class="stat-pill">👥 <b>{total}</b> participants</div>
  <div class="stat-pill">⏱️ ~<b>{est_min}m {est_sec}s</b> estimated</div>
  <div class="stat-pill">📨 <b>1</b> certificate each</div>
  <div class="stat-pill">✉️ <b>Gmail</b> SMTP</div>
</div>
""", unsafe_allow_html=True)

send_clicked = st.button("Send all certificates", type="primary")

nav1, _ = st.columns([1, 2])
with nav1:
    st.page_link("pages/2_Design.py", label="← Back to Design")

if send_clicked:
    output_folder = tempfile.mkdtemp()

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="eyebrow-label"><span class="dot"></span>Delivery status</div>', unsafe_allow_html=True)

    with st.spinner("Connecting to Gmail SMTP..."):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(ss.sender_email, ss.app_password)
            st.success("Secure Gmail connection established")
        except Exception as e:
            st.error(f"Gmail login failed: {e}")
            st.stop()

    progress_bar = st.progress(0)
    status_text = st.empty()
    log_placeholder = st.empty()
    logs = []
    count = failed = 0

    for index, row in data.iterrows():
        try:
            name = str(row[ss.name_col]).strip()
            dept = str(row[ss.dept_col]).strip()
            email = str(row[ss.email_col]).strip()

            if "@" not in email or "." not in email.split("@")[-1]:
                logs.append(f"⚠  Skipped · {name} · invalid email: '{email}'")
                failed += 1
                continue

            pdf_bytes = build_certificate_pdf(
                ss.template_bytes, name, dept,
                ss.name_x, ss.name_y, ss.name_size, ss.center_name,
                ss.dept_x, ss.dept_y, ss.dept_size, ss.center_dept,
            )

            safe = "".join(ch for ch in name if ch.isalnum() or ch in (" ", "_")).rstrip()
            cert_path = os.path.join(output_folder, f"{safe}.pdf")
            with open(cert_path, "wb") as f:
                f.write(pdf_bytes)

            msg = MIMEMultipart()
            msg["From"], msg["To"], msg["Subject"] = ss.sender_email, email, ss.email_subject
            msg.attach(MIMEText(ss.email_body.replace("{name}", name), "plain"))
            with open(cert_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={safe}.pdf")
                msg.attach(part)

            server.sendmail(ss.sender_email, email, msg.as_string())
            count += 1
            logs.append(f"✅  {name}  →  {email}")

        except Exception as e:
            failed += 1
            logs.append(f"❌  Row {index}  →  {str(e)[:80]}")

        progress_bar.progress((index + 1) / total)
        status_text.markdown(
            f'<div class="live-status"><span class="live-dot"></span>'
            f'Processing <b style="color:var(--accent)">{index+1}/{total}</b>'
            f' &nbsp;·&nbsp; <b style="color:var(--good)">✓ {count}</b>'
            f' &nbsp;·&nbsp; <b style="color:var(--warn)">✕ {failed}</b></div>',
            unsafe_allow_html=True,
        )
        log_placeholder.markdown(
            '<div class="log-box">' + "\n".join(logs[-14:]) + "</div>",
            unsafe_allow_html=True,
        )
        time.sleep(ss.delay)

    server.quit()
    st.balloons()

    st.markdown(f"""
    <div class="success-banner">
      <div class="success-mark">✓</div>
      <div class="success-title">Certificates sent</div>
      <div class="success-sub">{count} delivered &nbsp;·&nbsp; {failed} failed</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("Full delivery log"):
        st.markdown('<div class="log-box">' + "\n".join(logs) + "</div>", unsafe_allow_html=True)