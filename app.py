import streamlit as st
import pandas as pd
import smtplib
import os
import time
import tempfile

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from PyPDF2 import PdfReader, PdfWriter
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

# ─────────────────────────────────────────────
# PAGE CONFIG & CUSTOM CSS
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="CertMailer Pro",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0a0a0f;
    color: #e8e6f0;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem 3rem; max-width: 1200px; }

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(ellipse 80% 60% at 20% 10%, rgba(139,92,246,0.12) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 80% 80%, rgba(6,182,212,0.10) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 60% 30%, rgba(236,72,153,0.07) 0%, transparent 50%),
        #0a0a0f;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #12101e 0%, #0e0c1a 100%);
    border-right: 1px solid rgba(139,92,246,0.2);
}
[data-testid="stSidebar"] * { color: #e8e6f0 !important; }

.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    line-height: 1.1;
    background: linear-gradient(135deg, #c084fc 0%, #67e8f9 50%, #f0abfc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
    letter-spacing: -1px;
}

.hero-sub {
    font-size: 1.05rem;
    font-weight: 300;
    color: rgba(232,230,240,0.5);
    margin-bottom: 2.5rem;
}

.step-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(139,92,246,0.18);
    border-radius: 20px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.step-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(139,92,246,0.5), transparent);
}

.step-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #a78bfa;
    margin-bottom: 0.3rem;
}
.step-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: #f3f0ff;
    margin-bottom: 1.2rem;
}

.stat-row {
    display: flex;
    gap: 1rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.stat-pill {
    background: rgba(139,92,246,0.1);
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 50px;
    padding: 0.45rem 1.1rem;
    font-size: 0.83rem;
    font-weight: 500;
    color: #c4b5fd;
}

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(139,92,246,0.25) !important;
    border-radius: 10px !important;
    color: #e8e6f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: rgba(139,92,246,0.6) !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,0.12) !important;
}

label, [data-testid="stWidgetLabel"] {
    color: rgba(232,230,240,0.65) !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
}

[data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(139,92,246,0.25) !important;
    border-radius: 10px !important;
    color: #e8e6f0 !important;
}

[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.02) !important;
    border: 1.5px dashed rgba(139,92,246,0.35) !important;
    border-radius: 14px !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: rgba(139,92,246,0.65) !important;
    background: rgba(139,92,246,0.05) !important;
}

.stButton > button {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.05em !important;
    background: linear-gradient(135deg, #7c3aed, #6d28d9) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.75rem 2.5rem !important;
    box-shadow: 0 4px 20px rgba(124,58,237,0.35) !important;
    width: 100% !important;
    transition: all 0.2s ease !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #8b5cf6, #7c3aed) !important;
    box-shadow: 0 8px 30px rgba(124,58,237,0.55) !important;
    transform: translateY(-2px) !important;
}

[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #7c3aed, #06b6d4) !important;
    border-radius: 10px !important;
}
[data-testid="stProgress"] > div {
    background: rgba(255,255,255,0.06) !important;
    border-radius: 10px !important;
    height: 8px !important;
}

hr { border-color: rgba(139,92,246,0.15) !important; margin: 2rem 0 !important; }

.sidebar-logo {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem;
    font-weight: 800;
    background: linear-gradient(135deg, #c084fc, #67e8f9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 1.5rem;
    display: block;
}

.sidebar-section {
    font-family: 'Syne', sans-serif;
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: rgba(196,181,253,0.55);
    margin: 1.5rem 0 0.6rem 0;
    display: block;
}

.log-box {
    background: rgba(0,0,0,0.45);
    border: 1px solid rgba(139,92,246,0.18);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    font-family: 'Courier New', monospace;
    font-size: 0.78rem;
    line-height: 1.8;
    color: #c4b5fd;
    max-height: 280px;
    overflow-y: auto;
    white-space: pre-wrap;
}

.success-banner {
    background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(6,182,212,0.08));
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin-top: 1.5rem;
}
.success-banner h2 {
    font-family: 'Syne', sans-serif;
    font-size: 1.7rem;
    font-weight: 800;
    color: #34d399;
    margin: 0 0 0.4rem 0;
}
.success-banner p {
    color: rgba(232,230,240,0.55);
    font-size: 0.95rem;
    margin: 0;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<span class="sidebar-logo">🎓 CertMailer</span>', unsafe_allow_html=True)
    st.markdown('<span class="sidebar-section">Gmail Configuration</span>', unsafe_allow_html=True)

    sender_email = st.text_input("Sender Email", placeholder="you@gmail.com")
    app_password = st.text_input("App Password", type="password", placeholder="xxxx xxxx xxxx xxxx")

    if sender_email and app_password:
        st.success("✓ Credentials saved")

    st.markdown('<span class="sidebar-section">Get App Password</span>', unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.8rem;color:rgba(232,230,240,0.45);line-height:2;'>
    1. myaccount.google.com<br>
    2. Security → 2-Step Verification<br>
    3. App Passwords → Mail → Generate<br>
    4. Paste the 16-char code above
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<span class="sidebar-section">Send Settings</span>', unsafe_allow_html=True)
    delay = st.slider("Delay between emails (s)", 1, 10, 2)


# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown('<div class="hero-title">Certificate Distribution</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Generate personalized certificates & deliver them instantly — no code required.</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STEP 1 — UPLOAD
# ─────────────────────────────────────────────
st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.markdown('<div class="step-label">Step 01</div><div class="step-title">Upload Your Files</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    csv_file = st.file_uploader("📋  Participant List (CSV)", type=["csv"])
with col2:
    template_pdf = st.file_uploader("📄  Certificate Template (PDF)", type=["pdf"])

st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STEP 2 — MAP COLUMNS
# ─────────────────────────────────────────────
data = None
name_col = dept_col = email_col = None

if csv_file:
    st.markdown('<div class="step-card">', unsafe_allow_html=True)
    st.markdown('<div class="step-label">Step 02</div><div class="step-title">Map Your Columns</div>', unsafe_allow_html=True)

    try:
        data = pd.read_csv(csv_file, encoding="cp1252")
        data.columns = data.columns.str.strip()

        st.caption(f"Preview — {len(data)} participants detected")
        st.dataframe(data.head(4), use_container_width=True, hide_index=True)

        columns = data.columns.tolist()
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            name_col = st.selectbox("👤  Name Column", columns)
        with col_b:
            dept_col = st.selectbox("🏢  Department Column", columns)
        with col_c:
            email_col = st.selectbox("📧  Email Column", columns)

    except Exception as e:
        st.error(f"Could not read CSV: {e}")

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STEP 3 — TEXT POSITION
# ─────────────────────────────────────────────
st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.markdown('<div class="step-label">Step 03</div><div class="step-title">Certificate Text Position</div>', unsafe_allow_html=True)
st.caption("X = distance from left  |  Y = distance from bottom  |  Defaults suit most A4 landscape templates.")

col1, col2 = st.columns(2)
with col1:
    st.markdown('<p style="font-size:0.88rem;font-weight:600;color:#c4b5fd;margin:0 0 0.5rem 0;">✦ Name</p>', unsafe_allow_html=True)
    n1, n2, n3 = st.columns(3)
    with n1: name_x = st.number_input("X", value=250, step=5, key="nx")
    with n2: name_y = st.number_input("Y", value=223, step=5, key="ny")
    with n3: name_size = st.number_input("Size", value=14, step=1, key="ns", min_value=6, max_value=60)
    center_name = st.checkbox("Center-align Name", value=False)

with col2:
    st.markdown('<p style="font-size:0.88rem;font-weight:600;color:#67e8f9;margin:0 0 0.5rem 0;">✦ Department</p>', unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)
    with d1: dept_x = st.number_input("X", value=185, step=5, key="dx")
    with d2: dept_y = st.number_input("Y", value=198, step=5, key="dy")
    with d3: dept_size = st.number_input("Size", value=14, step=1, key="ds", min_value=6, max_value=60)
    center_dept = st.checkbox("Center-align Department", value=False)

st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STEP 4 — EMAIL CONTENT
# ─────────────────────────────────────────────
st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.markdown('<div class="step-label">Step 04</div><div class="step-title">Email Content</div>', unsafe_allow_html=True)

email_subject = st.text_input("Subject Line", value="Your Certificate 🎓")
email_body = st.text_area("Message Body", height=180, value="""Dear {name},

Congratulations on your participation!

Please find your personalized certificate attached.

Best regards,
Event Team""")
st.caption("💡 Use {name} anywhere in the body — it'll be replaced with each participant's name.")

st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STEP 5 — SEND
# ─────────────────────────────────────────────
st.markdown('<div class="step-card">', unsafe_allow_html=True)
st.markdown('<div class="step-label">Step 05</div><div class="step-title">Send Certificates</div>', unsafe_allow_html=True)

ready = bool(csv_file and template_pdf and sender_email and app_password and data is not None)

if not ready:
    missing = []
    if not csv_file: missing.append("CSV file")
    if not template_pdf: missing.append("certificate template")
    if not sender_email: missing.append("Gmail address (sidebar)")
    if not app_password: missing.append("app password (sidebar)")
    st.warning(f"⚠️  Still needed: **{', '.join(missing)}**")

if data is not None:
    t = len(data)
    est_min = (t * delay) // 60
    est_sec = (t * delay) % 60
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-pill">👥 &nbsp;{t} participants</div>
        <div class="stat-pill">⏱️ &nbsp;~{est_min}m {est_sec}s estimated</div>
        <div class="stat-pill">📨 &nbsp;1 certificate each</div>
    </div>
    """, unsafe_allow_html=True)

send_clicked = st.button("🚀  Send All Certificates", disabled=not ready, type="primary")
st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SEND LOGIC
# ─────────────────────────────────────────────
if send_clicked:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(template_pdf.read())
        template_path = tmp.name

    output_folder = tempfile.mkdtemp()
    overlay_path = os.path.join(output_folder, "overlay.pdf")

    st.markdown("---")
    st.markdown('<p style="font-family:Syne,sans-serif;font-weight:700;color:#c4b5fd;margin-bottom:0.8rem;">⚡ Live Progress</p>', unsafe_allow_html=True)

    with st.spinner("Connecting to Gmail..."):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, app_password)
            st.success("✅ Connected to Gmail successfully")
        except Exception as e:
            st.error(f"❌ Gmail login failed: {e}")
            st.stop()

    total = len(data)
    progress_bar = st.progress(0)
    status_text = st.empty()
    log_placeholder = st.empty()

    logs = []
    count = 0
    failed = 0

    for index, row in data.iterrows():
        try:
            name = str(row[name_col]).strip()
            dept = str(row[dept_col]).strip()
            email = str(row[email_col]).strip()

            if "@" not in email or "." not in email.split("@")[-1]:
                logs.append(f"⚠️  Skipped  →  {name}  (invalid email: '{email}')")
                failed += 1
                continue

            # Generate overlay
            c = canvas.Canvas(overlay_path, pagesize=landscape(A4))
            page_width = landscape(A4)[0]

            c.setFont("Helvetica-Bold", name_size)
            if center_name:
                tw = c.stringWidth(name, "Helvetica-Bold", name_size)
                c.drawString(page_width / 2 - tw / 2, name_y, name)
            else:
                c.drawString(name_x, name_y, name)

            c.setFont("Helvetica", dept_size)
            if center_dept:
                tw = c.stringWidth(dept, "Helvetica", dept_size)
                c.drawString(page_width / 2 - tw / 2, dept_y, dept)
            else:
                c.drawString(dept_x, dept_y, dept)

            c.save()

            # Merge PDF
            template_reader = PdfReader(template_path)
            overlay_reader = PdfReader(overlay_path)
            writer = PdfWriter()
            page = template_reader.pages[0]
            page.merge_page(overlay_reader.pages[0])
            writer.add_page(page)

            safe_name = "".join(ch for ch in name if ch.isalnum() or ch in (" ", "_")).rstrip()
            cert_path = os.path.join(output_folder, f"{safe_name}.pdf")
            with open(cert_path, "wb") as f:
                writer.write(f)

            # Send email
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = email_subject
            msg.attach(MIMEText(email_body.replace("{name}", name), "plain"))

            with open(cert_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={safe_name}.pdf")
                msg.attach(part)

            server.sendmail(sender_email, email, msg.as_string())
            count += 1
            logs.append(f"✅  {name}  →  {email}")

        except Exception as e:
            failed += 1
            logs.append(f"❌  Row {index}  →  {e}")

        progress_bar.progress((index + 1) / total)
        status_text.markdown(
            f'<p style="font-size:0.87rem;color:rgba(232,230,240,0.5);">'
            f'Processing <b style="color:#c4b5fd">{index+1} / {total}</b> &nbsp;·&nbsp; '
            f'<b style="color:#34d399">✅ {count} sent</b> &nbsp;·&nbsp; '
            f'<b style="color:#f87171">❌ {failed} failed</b></p>',
            unsafe_allow_html=True
        )
        log_placeholder.markdown(
            '<div class="log-box">' + '\n'.join(logs[-12:]) + '</div>',
            unsafe_allow_html=True
        )
        time.sleep(delay)

    server.quit()
    st.balloons()

    st.markdown(f"""
    <div class="success-banner">
        <h2>🎉 All Done!</h2>
        <p>{count} certificates delivered &nbsp;·&nbsp; {failed} failed</p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 Full Send Log"):
        st.markdown('<div class="log-box">' + '\n'.join(logs) + '</div>', unsafe_allow_html=True)
