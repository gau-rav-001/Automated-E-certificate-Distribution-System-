"""
Shared code for every page of AutoCertify.

Import from here instead of copy-pasting — if you fix a bug or change a
style here, it fixes/changes on all three pages at once.
"""
import io
import streamlit as st
import fitz  # PyMuPDF - rasterizes the PDF for the live preview
from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter


# ── CERTIFICATE BUILDING (shared by preview + send) ──────────────────
def build_certificate_pdf(template_bytes, name, dept,
                           name_x, name_y, name_size, center_name,
                           dept_x, dept_y, dept_size, center_dept):
    """
    Overlay Name & Department onto the template PDF and return the
    merged single-page PDF as bytes. Used by both the live preview
    and the certificates actually emailed, so the preview always
    matches the real output.
    """
    template_reader = PdfReader(io.BytesIO(template_bytes))
    template_page = template_reader.pages[0]

    page_width = float(template_page.mediabox.width)
    page_height = float(template_page.mediabox.height)

    overlay_buffer = io.BytesIO()
    c = canvas.Canvas(overlay_buffer, pagesize=(page_width, page_height))

    c.setFont("Helvetica-Bold", name_size)
    tw = c.stringWidth(name, "Helvetica-Bold", name_size)
    c.drawString(page_width / 2 - tw / 2 if center_name else name_x, name_y, name)

    c.setFont("Helvetica", dept_size)
    tw = c.stringWidth(dept, "Helvetica", dept_size)
    c.drawString(page_width / 2 - tw / 2 if center_dept else dept_x, dept_y, dept)

    c.save()
    overlay_buffer.seek(0)

    overlay_reader = PdfReader(overlay_buffer)
    writer = PdfWriter()
    template_page.merge_page(overlay_reader.pages[0])
    writer.add_page(template_page)

    out_buffer = io.BytesIO()
    writer.write(out_buffer)
    return out_buffer.getvalue()


@st.cache_data(show_spinner=False)
def render_pdf_preview(pdf_bytes, dpi=140):
    """Rasterize page 1 of a PDF to PNG bytes for on-screen preview."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pix = doc[0].get_pixmap(dpi=dpi)
    return pix.tobytes("png")


# ── SESSION STATE ─────────────────────────────────────────────────────
# Everything a page collects gets written here so it survives navigating
# to the next page. Streamlit re-runs the whole script on every page
# switch, but st.session_state persists across that — plain local
# variables and file_uploader widgets do NOT.
DEFAULTS = {
    "sender_email": "",
    "app_password": "",
    "delay": 2,
    "csv_bytes": None,
    "csv_filename": None,
    "template_bytes": None,
    "template_filename": None,
    "name_col": None,
    "dept_col": None,
    "email_col": None,
    "name_x": 250, "name_y": 223, "name_size": 14, "center_name": False,
    "dept_x": 185, "dept_y": 198, "dept_size": 14, "center_dept": False,
    "email_subject": "Your Certificate 🎓",
    "email_body": (
        "Dear {name},\n\n"
        "Congratulations on your outstanding participation!\n\n"
        "Please find your personalized certificate attached.\n\n"
        "With warm regards,\nAutoCertify · Event Team"
    ),
}


def init_session_state():
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value


def step_status():
    """Returns which of the 3 steps are complete, for the stepper UI."""
    ss = st.session_state
    setup_done = bool(ss.sender_email and ss.app_password
                       and ss.csv_bytes and ss.template_bytes)
    design_done = setup_done and bool(ss.name_col and ss.dept_col and ss.email_col)
    return {"setup": setup_done, "design": design_done}


# ── STYLING ─────────────────────────────────────────────────────────
# Design system v2: glassmorphism + a slow-moving mesh-gradient
# background, layered over the same Inter/JetBrains Mono pairing and
# ink/blue-violet palette from v1 (so nothing here changes what any
# page *does* — every class name below is a drop-in replacement for
# the same class in v1, still used unchanged by every page).
BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --ink:      #05070D;
  --panel:    rgba(255,255,255,0.035);
  --panel-2:  rgba(255,255,255,0.05);
  --line:     rgba(255,255,255,0.09);
  --line-2:   rgba(255,255,255,0.18);

  --text:      #EDEFF5;
  --text-dim:  #8B93A8;
  --text-dim2: #5C6478;

  --accent:    #5B8DEF;
  --accent-2:  #8B7CF6;
  --cyan:      #22D3EE;
  --seal:      #CBA135;
  --seal-soft: rgba(203,161,53,0.16);
  --good:      #38C793;
  --warn:      #E8A651;

  --glass-blur: blur(20px);

  --fs-hero:  clamp(2.3rem, 5.6vw, 3.8rem);
  --fs-h2:    clamp(1rem, 2.2vw, 1.15rem);
  --fs-body:  clamp(0.84rem, 1.8vw, 0.95rem);
  --fs-label: clamp(0.66rem, 1.6vw, 0.76rem);
  --fs-mono:  clamp(0.62rem, 1.4vw, 0.7rem);
}

*, *::before, *::after { box-sizing:border-box; }
html, body, [class*="css"] {
  font-family:'Inter',sans-serif;
  background:var(--ink);
  color:var(--text);
}
#MainMenu, footer, header { visibility:hidden; }
.block-container {
  padding:clamp(0.8rem,3vw,2rem) clamp(0.8rem,3vw,2.5rem) 4rem !important;
  max-width:1160px !important;
  width:100% !important;
  position:relative; z-index:1;
}

/* ── Futuristic mesh background: fixed, behind everything, drifts slowly ── */
[data-testid="stAppViewContainer"] {
  background:var(--ink);
  min-height:100vh;
  overflow:hidden;
  position:relative;
}
[data-testid="stAppViewContainer"]::before,
[data-testid="stAppViewContainer"]::after {
  content:''; position:fixed; border-radius:50%; filter:blur(90px);
  pointer-events:none; z-index:0;
}
[data-testid="stAppViewContainer"]::before {
  width:46vw; height:46vw; top:-14vw; left:-10vw;
  background:radial-gradient(circle, rgba(91,141,239,0.28) 0%, transparent 70%);
  animation:orbDrift1 26s ease-in-out infinite;
}
[data-testid="stAppViewContainer"]::after {
  width:38vw; height:38vw; bottom:-12vw; right:-8vw;
  background:radial-gradient(circle, rgba(139,124,246,0.22) 0%, transparent 70%);
  animation:orbDrift2 32s ease-in-out infinite;
}
.orb-mid {
  position:fixed; top:30%; left:55%; width:30vw; height:30vw; border-radius:50%;
  background:radial-gradient(circle, rgba(34,211,238,0.14) 0%, transparent 70%);
  filter:blur(90px); pointer-events:none; z-index:0; animation:orbDrift3 38s ease-in-out infinite;
}
@keyframes orbDrift1 { 0%,100%{ transform:translate(0,0) scale(1); } 50%{ transform:translate(4vw,3vw) scale(1.08); } }
@keyframes orbDrift2 { 0%,100%{ transform:translate(0,0) scale(1); } 50%{ transform:translate(-3vw,-4vw) scale(1.1); } }
@keyframes orbDrift3 { 0%,100%{ transform:translate(0,0) scale(1); } 50%{ transform:translate(-5vw,3vw) scale(0.92); } }

[data-testid="stSidebar"] {
  background:linear-gradient(160deg,rgba(10,14,24,0.9),rgba(5,7,13,0.95)) !important;
  backdrop-filter:var(--glass-blur) !important;
  border-right:1px solid var(--line) !important;
}
[data-testid="stSidebar"] * { color:var(--text) !important; font-family:'Inter',sans-serif !important; }
[data-testid="stSidebarNav"] { display:none; }  /* replaced by our own stepper */

h1, h2, h3 { font-family:'Inter',sans-serif !important; font-weight:800 !important; letter-spacing:-0.01em; color:var(--text); }

@keyframes fadeSlideUp { from{ opacity:0; transform:translateY(16px);} to{ opacity:1; transform:translateY(0);} }
@keyframes glowPulse { 0%,100%{ box-shadow:0 0 0 rgba(91,141,239,0);} 50%{ box-shadow:0 0 22px rgba(91,141,239,0.35);} }

/* ── Brand mark (top-left, every page) ── */
.brand-row { display:flex; align-items:center; gap:0.6rem; margin-bottom:1.4rem; animation:fadeSlideUp 0.5s ease both; }
.brand-mark {
  width:30px; height:30px; border-radius:8px;
  background:linear-gradient(135deg,var(--accent),var(--accent-2));
  box-shadow:0 4px 16px rgba(91,141,239,0.4);
  display:flex; align-items:center; justify-content:center;
  font-weight:800; font-size:0.85rem; color:#fff; flex-shrink:0;
}
.brand-name { font-weight:700; font-size:1.02rem; letter-spacing:-0.01em; color:var(--text); }

/* ── Stepper (glass pill nav, active step glows, connector animates) ── */
.stepper { display:flex; align-items:center; gap:0; margin-bottom:1.8rem; flex-wrap:wrap; animation:fadeSlideUp 0.55s ease both; }
.step-chip {
  display:flex; align-items:center; gap:0.5rem;
  padding:0.5rem 0.9rem; border-radius:99px;
  font-family:'JetBrains Mono',monospace; font-size:0.78rem; font-weight:500;
  background:rgba(255,255,255,0.03); backdrop-filter:var(--glass-blur);
  border:1px solid var(--line); color:var(--text-dim2);
  transition:all 0.25s ease;
}
.step-chip.active {
  border-color:rgba(91,141,239,0.55); color:var(--text);
  background:linear-gradient(135deg, rgba(91,141,239,0.18), rgba(139,124,246,0.12));
  animation:glowPulse 2.6s ease-in-out infinite;
}
.step-chip.done { border-color:rgba(56,199,147,0.35); color:var(--good); background:rgba(56,199,147,0.06); }
.step-chip .n {
  width:18px; height:18px; border-radius:50%; display:flex; align-items:center; justify-content:center;
  font-size:0.68rem; border:1px solid currentColor; flex-shrink:0;
}
.step-connector {
  width:26px; height:2px; flex-shrink:0; border-radius:2px;
  background:linear-gradient(90deg, var(--line-2), var(--line-2));
  position:relative; overflow:hidden;
}
.step-connector.filled { background:linear-gradient(90deg, var(--accent), var(--accent-2)); }

/* ── Page header ── */
.page-eyebrow {
  font-family:'JetBrains Mono',monospace; font-size:var(--fs-mono);
  letter-spacing:0.14em; text-transform:uppercase; color:var(--cyan);
  margin-bottom:0.5rem; animation:fadeSlideUp 0.5s ease both;
}
.page-title {
  font-size:var(--fs-hero); font-weight:800; letter-spacing:-0.02em; line-height:1.05;
  background:linear-gradient(135deg, var(--text) 40%, var(--accent) 100%);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  animation:fadeSlideUp 0.6s 0.05s ease both;
}
.page-subtitle {
  font-size:clamp(0.88rem,1.8vw,1rem); color:var(--text-dim); margin:0.6rem 0 1.6rem; max-width:34rem; line-height:1.6;
  animation:fadeSlideUp 0.6s 0.12s ease both;
}

/* ── Cards: frosted glass, floats on hover, soft layered shadow ── */
.step-card, .gmail-card, .glass-panel {
  background:linear-gradient(160deg, rgba(255,255,255,0.045), rgba(255,255,255,0.015));
  backdrop-filter:var(--glass-blur); -webkit-backdrop-filter:var(--glass-blur);
  border:1px solid var(--line); border-radius:16px;
  padding:clamp(1.1rem,2.4vw,1.5rem) clamp(1.05rem,2.4vw,1.6rem);
  margin-bottom:clamp(0.7rem,1.6vw,1rem);
  box-shadow:0 8px 32px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.04);
  transition:border-color 0.25s ease, transform 0.25s cubic-bezier(0.16,1,0.3,1), box-shadow 0.25s ease;
  animation:fadeSlideUp 0.5s ease both;
}
.step-card:hover, .gmail-card:hover, .glass-panel:hover {
  border-color:rgba(91,141,239,0.4); transform:translateY(-3px);
  box-shadow:0 18px 44px rgba(0,0,0,0.34), 0 0 0 1px rgba(91,141,239,0.12), inset 0 1px 0 rgba(255,255,255,0.06);
}
.gmail-card { border-left:2px solid var(--accent); }
.step-header { display:flex; align-items:flex-start; gap:0.85rem; margin-bottom:0.2rem; }
.step-num {
  display:inline-flex; align-items:center; justify-content:center;
  min-width:32px; height:32px; padding:0 0.3rem;
  border:1px solid var(--line-2); border-radius:9px;
  font-family:'JetBrains Mono',monospace; font-weight:600; font-size:0.76rem; color:var(--accent);
  background:rgba(91,141,239,0.1); flex-shrink:0; margin-top:0.05rem;
}
.step-title { font-size:var(--fs-h2); font-weight:700; color:var(--text); letter-spacing:-0.005em; }
.step-desc { font-size:clamp(0.72rem,1.5vw,0.8rem); color:var(--text-dim2); margin-top:0.15rem; line-height:1.5; }
.gmail-hint { font-size:clamp(0.75rem,1.5vw,0.82rem); color:var(--text-dim); line-height:2; margin-top:0.7rem; }

/* ── Status / badges ── */
.status-badge {
  display:inline-flex; align-items:center; gap:0.5rem; border-radius:9px; padding:0.42rem 0.9rem;
  font-family:'JetBrains Mono',monospace; font-size:clamp(0.7rem,1.4vw,0.78rem); font-weight:500; margin-top:0.5rem;
}
.status-ready { background:rgba(56,199,147,0.08); border:1px solid rgba(56,199,147,0.28); color:var(--good); }
.status-warn  { background:rgba(232,166,81,0.08); border:1px solid rgba(232,166,81,0.28); color:var(--warn); }

/* ── Inputs: glass surfaces with a clear focus glow ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
  background:rgba(255,255,255,0.04) !important; backdrop-filter:var(--glass-blur) !important;
  border:1px solid var(--line) !important; border-radius:10px !important;
  color:var(--text) !important; font-family:'Inter',sans-serif !important; font-size:var(--fs-body) !important;
  min-height:42px !important; padding:0.55rem 0.8rem !important; caret-color:var(--accent) !important;
  transition:all 0.2s ease !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stNumberInput"] input:focus {
  border-color:var(--accent) !important; box-shadow:0 0 0 3px rgba(91,141,239,0.18), 0 0 18px rgba(91,141,239,0.15) !important;
  background:rgba(91,141,239,0.05) !important;
}
label,[data-testid="stWidgetLabel"] p {
  color:var(--text-dim) !important; font-family:'JetBrains Mono',monospace !important;
  font-size:var(--fs-label) !important; font-weight:500 !important; letter-spacing:0.04em !important;
  text-transform:uppercase !important;
}
[data-testid="stSelectbox"]>div>div {
  background:rgba(255,255,255,0.04) !important; backdrop-filter:var(--glass-blur) !important;
  border:1px solid var(--line) !important; border-radius:10px !important;
  color:var(--text) !important; min-height:42px !important;
}
[data-testid="stFileUploader"] {
  background:rgba(255,255,255,0.02) !important; backdrop-filter:var(--glass-blur) !important;
  border:1.5px dashed var(--line-2) !important; border-radius:14px !important; transition:all 0.25s ease !important;
}
[data-testid="stFileUploader"]:hover {
  border-color:var(--accent) !important; background:rgba(91,141,239,0.06) !important;
  box-shadow:0 0 24px rgba(91,141,239,0.12) !important;
}

/* ── Buttons: gradient glass with glow, press feedback ── */
.stButton>button {
  font-family:'Inter',sans-serif !important; font-size:clamp(0.9rem,2vw,1rem) !important;
  font-weight:600 !important; letter-spacing:0.01em !important;
  background:linear-gradient(135deg,var(--accent),var(--accent-2)) !important;
  color:#fff !important; border:1px solid rgba(255,255,255,0.18) !important; border-radius:11px !important;
  padding:clamp(0.65rem,1.6vw,0.8rem) 1.8rem !important; min-height:48px !important;
  transition:all 0.22s cubic-bezier(0.16,1,0.3,1) !important;
  box-shadow:0 10px 28px rgba(91,141,239,0.32), inset 0 1px 0 rgba(255,255,255,0.25) !important;
}
.stButton>button:hover {
  transform:translateY(-2px) scale(1.01) !important; filter:brightness(1.08) !important;
  box-shadow:0 16px 38px rgba(91,141,239,0.42), inset 0 1px 0 rgba(255,255,255,0.3) !important;
}
.stButton>button:active { transform:translateY(0) scale(0.98) !important; }
.stButton>button:disabled { background:rgba(255,255,255,0.04) !important; color:var(--text-dim2) !important; box-shadow:none !important; border-color:var(--line) !important; }

/* secondary buttons (nav "Back") — quiet glass, no glow */
.stButton.secondary>button, button[kind="secondary"] {
  background:rgba(255,255,255,0.03) !important; backdrop-filter:var(--glass-blur) !important;
  color:var(--text) !important; border:1px solid var(--line-2) !important; box-shadow:none !important;
}
.stButton.secondary>button:hover, button[kind="secondary"]:hover {
  border-color:var(--accent) !important; background:rgba(91,141,239,0.06) !important;
}

/* ── Progress ── */
[data-testid="stProgress"]>div { background:var(--panel-2) !important; border-radius:50px !important; height:9px !important; border:1px solid var(--line) !important; }
[data-testid="stProgress"]>div>div { background:linear-gradient(90deg,var(--accent),var(--accent-2)) !important; border-radius:50px !important; }

/* ── Pills ── */
.stat-row { display:flex; gap:clamp(0.4rem,1.1vw,0.7rem); margin:0.8rem 0 1.1rem; flex-wrap:wrap; }
.stat-pill {
  background:rgba(255,255,255,0.035); backdrop-filter:var(--glass-blur);
  border:1px solid var(--line); border-radius:10px;
  padding:clamp(0.32rem,0.9vw,0.42rem) clamp(0.65rem,1.4vw,0.9rem);
  font-size:clamp(0.72rem,1.6vw,0.8rem); font-weight:500; color:var(--text-dim); white-space:nowrap;
  display:flex; align-items:center; gap:0.32rem; transition:all 0.2s ease;
}
.stat-pill:hover { border-color:rgba(91,141,239,0.35); transform:translateY(-1px); }
.stat-pill b { color:var(--text); font-weight:700; }

.field-group-label {
  font-family:'JetBrains Mono',monospace; font-size:clamp(0.62rem,1.3vw,0.68rem); font-weight:600;
  letter-spacing:0.1em; text-transform:uppercase; padding:0.24rem 0.6rem; border-radius:6px;
  display:inline-block; margin-bottom:0.7rem;
}
.fg-gold  { background:rgba(91,141,239,0.1);  border:1px solid rgba(91,141,239,0.28); color:var(--accent); }
.fg-amber { background:var(--seal-soft);      border:1px solid rgba(203,161,53,0.32); color:var(--seal); }

.hint-pill {
  display:inline-flex; align-items:flex-start; gap:0.5rem; flex-wrap:wrap;
  background:rgba(255,255,255,0.015); border:1px dashed var(--line-2); border-radius:9px;
  padding:clamp(0.4rem,1vw,0.55rem) clamp(0.7rem,1.6vw,0.95rem);
  font-size:clamp(0.72rem,1.5vw,0.79rem); color:var(--text-dim); margin-top:0.6rem; line-height:1.6;
}
.hint-pill code { background:rgba(91,141,239,0.14); color:var(--accent); padding:0.06rem 0.4rem; border-radius:4px; font-family:'JetBrains Mono',monospace; font-size:0.85em; }

.eyebrow-label {
  display:flex; align-items:center; gap:0.5rem; font-family:'JetBrains Mono',monospace; font-size:0.72rem;
  font-weight:600; letter-spacing:0.12em; text-transform:uppercase; color:var(--text-dim); margin:1.2rem 0 0.7rem;
}
.eyebrow-label .dot { width:6px; height:6px; border-radius:50%; background:var(--accent); flex-shrink:0; }

.log-box {
  background:rgba(0,0,0,0.4); backdrop-filter:var(--glass-blur); border:1px solid var(--line); border-radius:11px; padding:0.85rem 1.05rem;
  font-family:'JetBrains Mono',monospace; font-size:clamp(0.68rem,1.5vw,0.75rem); line-height:1.9;
  color:var(--text-dim); max-height:240px; overflow-y:auto; white-space:pre-wrap;
}
.log-box::-webkit-scrollbar{width:3px}
.log-box::-webkit-scrollbar-thumb{background:var(--line-2);border-radius:4px}

.live-status { display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap; font-size:clamp(0.78rem,1.8vw,0.87rem); color:var(--text-dim); margin:0.7rem 0; }
.live-dot { width:7px; height:7px; border-radius:50%; background:var(--accent); flex-shrink:0; animation:dotPulse 1.3s ease-in-out infinite; }
@keyframes dotPulse { 0%,100%{ transform:scale(1); opacity:1; } 50%{ transform:scale(1.6); opacity:0.5; } }

.success-banner {
  background:linear-gradient(160deg, rgba(255,255,255,0.05), rgba(255,255,255,0.015));
  backdrop-filter:var(--glass-blur); border:1px solid rgba(56,199,147,0.3); border-radius:18px;
  padding:clamp(1.5rem,3.4vw,2.2rem) clamp(1.1rem,2.6vw,2rem); text-align:center;
  box-shadow:0 20px 50px rgba(0,0,0,0.3), 0 0 40px rgba(56,199,147,0.1);
  animation:fadeSlideUp 0.55s cubic-bezier(0.16,1,0.3,1) both;
}
.success-mark {
  width:52px; height:52px; margin:0 auto 0.9rem; border-radius:50%;
  background:rgba(56,199,147,0.12); border:1px solid rgba(56,199,147,0.45);
  display:flex; align-items:center; justify-content:center; font-size:1.4rem; color:var(--good);
  box-shadow:0 0 24px rgba(56,199,147,0.3);
  animation:glowPulse 2s ease-in-out infinite;
}
.success-title { font-size:clamp(1.3rem,3.2vw,1.6rem); font-weight:700; color:var(--text); margin-bottom:0.3rem; }
.success-sub { color:var(--text-dim); font-size:clamp(0.82rem,1.8vw,0.92rem); }

hr { border:none !important; height:1px !important; background:linear-gradient(90deg,transparent,var(--line-2),transparent) !important; margin:clamp(0.8rem,2vw,1.5rem) 0 !important; }
[data-testid="stCheckbox"] span { color:var(--text-dim) !important; font-family:'Inter',sans-serif !important; text-transform:none !important; }
.stCaption,[data-testid="stCaptionContainer"] { color:var(--text-dim2) !important; }
[data-testid="stAlert"] { border-radius:10px !important; }
[data-testid="stDataFrame"] { border-radius:10px !important; border:1px solid var(--line) !important; }
[data-testid="stExpander"] { border:1px solid var(--line) !important; border-radius:12px !important; background:var(--panel) !important; }
[data-testid="stSlider"] [role="slider"] { background:var(--accent) !important; box-shadow:0 0 8px rgba(91,141,239,0.4) !important; }
[data-testid="stSlider"] > div > div > div { background:var(--accent) !important; }

@media(max-width:480px) {
  .block-container { padding:0.6rem 0.7rem 3rem !important; }
  .step-card, .gmail-card { padding:1rem 0.9rem; border-radius:14px; }
  .log-box { max-height:160px; }
}
</style>
"""


def inject_base_css():
    st.markdown(BASE_CSS, unsafe_allow_html=True)


def brand_header():
    st.markdown("""
    <div class="brand-row">
      <div class="brand-mark">AC</div>
      <div class="brand-name">AutoCertify</div>
    </div>
    """, unsafe_allow_html=True)


def render_background_orbs():
    """A third ambient glow orb that ::before/::after alone can't place well."""
    st.markdown('<div class="orb-mid"></div>', unsafe_allow_html=True)


def render_stepper(current: str):
    """current is one of: 'setup', 'design', 'send'."""
    status = step_status()
    order = [("setup", "1", "Setup"), ("design", "2", "Design"), ("send", "3", "Send")]
    html = ['<div class="stepper">']
    for i, (key, num, label) in enumerate(order):
        cls = "step-chip"
        if key == current:
            cls += " active"
        elif status.get(key):
            cls += " done"
        mark = "✓" if status.get(key) and key != current else num
        html.append(f'<div class="{cls}"><span class="n">{mark}</span>{label}</div>')
        if i < len(order) - 1:
            connector_cls = "step-connector filled" if status.get(key) else "step-connector"
            html.append(f'<div class="{connector_cls}"></div>')
    html.append('</div>')
    st.markdown("".join(html), unsafe_allow_html=True)


def page_header(eyebrow: str, title: str, subtitle: str):
    st.markdown(f"""
    <div class="page-eyebrow">{eyebrow}</div>
    <div class="page-title">{title}</div>
    <div class="page-subtitle">{subtitle}</div>
    """, unsafe_allow_html=True)