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
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Certificate Mailer",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Certificate Distribution System")
st.markdown("Upload your files, configure settings, and send certificates in one click.")

# ─────────────────────────────────────────────
# SIDEBAR — Gmail Config
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("📧 Gmail Configuration")
    sender_email = st.text_input("Sender Gmail", placeholder="you@gmail.com")
    app_password = st.text_input("App Password", type="password", placeholder="xxxx xxxx xxxx xxxx")

    st.markdown("---")
    st.markdown("**How to get App Password:**")
    st.markdown("1. Go to [myaccount.google.com](https://myaccount.google.com)")
    st.markdown("2. Security → 2-Step Verification → App Passwords")
    st.markdown("3. Generate for 'Mail'")

# ─────────────────────────────────────────────
# STEP 1 — Upload Files
# ─────────────────────────────────────────────
st.markdown("## Step 1: Upload Files")

col1, col2 = st.columns(2)

with col1:
    csv_file = st.file_uploader("📋 Participant CSV", type=["csv"])
    if csv_file:
        st.success("CSV uploaded!")

with col2:
    template_pdf = st.file_uploader("📄 Certificate Template (PDF)", type=["pdf"])
    if template_pdf:
        st.success("Template uploaded!")

# ─────────────────────────────────────────────
# STEP 2 — Map CSV Columns
# ─────────────────────────────────────────────
if csv_file:
    st.markdown("## Step 2: Map Your CSV Columns")

    try:
        data = pd.read_csv(csv_file, encoding="cp1252")
        data.columns = data.columns.str.strip()
        st.dataframe(data.head(3), use_container_width=True)

        columns = data.columns.tolist()

        col_a, col_b, col_c = st.columns(3)
        with col_a:
            name_col = st.selectbox("👤 Name Column", columns)
        with col_b:
            dept_col = st.selectbox("🏢 Department / Organisation Column", columns)
        with col_c:
            email_col = st.selectbox("📧 Email Column", columns)

    except Exception as e:
        st.error(f"Could not read CSV: {e}")
        data = None
else:
    data = None

# ─────────────────────────────────────────────
# STEP 3 — Certificate Text Position
# ─────────────────────────────────────────────
st.markdown("## Step 3: Certificate Text Position")
st.info("Adjust where the Name and Department appear on the certificate. Default values work for most A4 landscape templates.")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Name Position**")
    name_x = st.number_input("Name X", value=250, step=5)
    name_y = st.number_input("Name Y", value=223, step=5)
    name_size = st.slider("Name Font Size", 8, 36, 14)

with col2:
    st.markdown("**Department Position**")
    dept_x = st.number_input("Dept X", value=185, step=5)
    dept_y = st.number_input("Dept Y", value=198, step=5)
    dept_size = st.slider("Dept Font Size", 8, 36, 14)

center_name = st.checkbox("⬛ Center-align Name horizontally", value=False)
center_dept = st.checkbox("⬛ Center-align Department horizontally", value=False)

# ─────────────────────────────────────────────
# STEP 4 — Email Content
# ─────────────────────────────────────────────
st.markdown("## Step 4: Email Content")

email_subject = st.text_input(
    "📌 Email Subject",
    value="Your Certificate 🎓"
)

email_body = st.text_area(
    "✉️ Email Body",
    height=200,
    value="""Dear {name},

Congratulations!

Please find your certificate attached.

Regards,
Event Team"""
)
st.caption("Use `{name}` in the body and it will be replaced with each participant's name.")

# ─────────────────────────────────────────────
# STEP 5 — Send
# ─────────────────────────────────────────────
st.markdown("## Step 5: Send Certificates")

delay = st.slider("⏱️ Delay between emails (seconds)", 1, 10, 2)

ready = (
    csv_file is not None and
    template_pdf is not None and
    sender_email and
    app_password and
    data is not None
)

if not ready:
    st.warning("Complete all steps above before sending.")

if st.button("🚀 Send All Certificates", disabled=not ready, type="primary"):

    # Save template to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_template:
        tmp_template.write(template_pdf.read())
        template_path = tmp_template.name

    output_folder = tempfile.mkdtemp()
    overlay_path = os.path.join(output_folder, "overlay.pdf")

    # Connect to Gmail
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, app_password)
        st.success("✅ Connected to Gmail")
    except Exception as e:
        st.error(f"❌ Gmail login failed: {e}")
        st.stop()

    total = len(data)
    progress = st.progress(0)
    status_box = st.empty()
    log_area = st.empty()
    logs = []

    count = 0
    failed = 0

    for index, row in data.iterrows():
        try:
            name = str(row[name_col]).strip()
            dept = str(row[dept_col]).strip()
            email = str(row[email_col]).strip()

            # Generate certificate
            c = canvas.Canvas(overlay_path, pagesize=landscape(A4))
            page_width = landscape(A4)[0]

            # Draw Name
            c.setFont("Helvetica-Bold", name_size)
            if center_name:
                text_w = c.stringWidth(name, "Helvetica-Bold", name_size)
                c.drawString(page_width / 2 - text_w / 2, name_y, name)
            else:
                c.drawString(name_x, name_y, name)

            # Draw Dept
            c.setFont("Helvetica", dept_size)
            if center_dept:
                text_w = c.stringWidth(dept, "Helvetica", dept_size)
                c.drawString(page_width / 2 - text_w / 2, dept_y, dept)
            else:
                c.drawString(dept_x, dept_y, dept)

            c.save()

            # Merge with template
            template_reader = PdfReader(template_path)
            overlay_reader = PdfReader(overlay_path)

            writer = PdfWriter()
            page = template_reader.pages[0]
            page.merge_page(overlay_reader.pages[0])
            writer.add_page(page)

            safe_name = "".join(c2 for c2 in name if c2.isalnum() or c2 in (" ", "_")).rstrip()
            cert_path = os.path.join(output_folder, f"{safe_name}.pdf")

            with open(cert_path, "wb") as f:
                writer.write(f)

            # Send email
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = email_subject

            personalized_body = email_body.replace("{name}", name)
            msg.attach(MIMEText(personalized_body, "plain"))

            with open(cert_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={safe_name}.pdf")
                msg.attach(part)

            server.sendmail(sender_email, email, msg.as_string())

            count += 1
            logs.append(f"✅ Sent → {name} ({email})")

        except Exception as e:
            failed += 1
            logs.append(f"❌ Failed → Row {index}: {e}")

        progress.progress((index + 1) / total)
        status_box.markdown(f"**Progress:** {index + 1} / {total} | ✅ Sent: {count} | ❌ Failed: {failed}")
        log_area.text("\n".join(logs[-10:]))  # Show last 10 logs

        time.sleep(delay)

    server.quit()

    st.balloons()
    st.success(f"🎉 Done! {count} certificates sent, {failed} failed.")

    # Show full log
    with st.expander("📋 Full Send Log"):
        st.text("\n".join(logs))
