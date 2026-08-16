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
# Design system v3: modeled on antigravity.google — near-black canvas,
# Google Sans Flex (Google's real, now open-source brand typeface) for
# every headline and body line, Material Symbols for icon glyphs, and
# a deliberately monochrome palette (white/gray hairlines and glows)
# instead of color to carry hierarchy. Semantic colors (good/warn) are
# kept because they carry functional meaning (status), not decoration.
# Every class name below is a drop-in replacement for the same class
# in v2, so no page's Python logic needed to change for this.
BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Google+Sans+Flex:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,300..500,0..1,0&display=swap');

:root {
  --ink:      #000000;
  --panel:    rgba(255,255,255,0.035);
  --panel-2:  rgba(255,255,255,0.05);
  --line:     rgba(255,255,255,0.12);
  --line-2:   rgba(255,255,255,0.24);

  --text:      #F5F5F7;
  --text-dim:  #9A9AA3;
  --text-dim2: #5C5C63;

  --accent:    #FFFFFF;
  --accent-2:  #E4E4E8;
  --good:      #4ADE80;
  --warn:      #FBBF6E;

  --glass-blur: blur(20px);

  --fs-hero:  clamp(2.3rem, 5.6vw, 3.8rem);
  --fs-h2:    clamp(1rem, 2.2vw, 1.15rem);
  --fs-body:  clamp(0.84rem, 1.8vw, 0.95rem);
  --fs-label: clamp(0.66rem, 1.6vw, 0.76rem);
  --fs-mono:  clamp(0.62rem, 1.4vw, 0.7rem);
}

*, *::before, *::after { box-sizing:border-box; }
html, body, [class*="css"] {
  font-family:'Google Sans Flex','Inter',sans-serif;
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
.material-symbols-outlined {
  font-variation-settings:'FILL' 0,'wght' 300,'GRAD' 0,'opsz' 24;
  vertical-align:middle; line-height:1;
}

/* ── Antigravity-style backdrop: pure black, one faint drifting glow, no color ── */
[data-testid="stAppViewContainer"] {
  background:var(--ink);
  min-height:100vh;
  overflow:hidden;
  position:relative;
}
[data-testid="stAppViewContainer"]::before {
  content:''; position:fixed; border-radius:50%; filter:blur(120px);
  pointer-events:none; z-index:0;
  width:52vw; height:52vw; top:-20vw; left:50%; transform:translateX(-50%);
  background:radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
  animation:orbDrift1 30s ease-in-out infinite;
}
.orb-mid {
  position:fixed; bottom:-18vw; right:-10vw; width:36vw; height:36vw; border-radius:50%;
  background:radial-gradient(circle, rgba(255,255,255,0.03) 0%, transparent 70%);
  filter:blur(110px); pointer-events:none; z-index:0; animation:orbDrift2 38s ease-in-out infinite;
}
@keyframes orbDrift1 { 0%,100%{ transform:translateX(-50%) translateY(0) scale(1); } 50%{ transform:translateX(-46%) translateY(3vw) scale(1.06); } }
@keyframes orbDrift2 { 0%,100%{ transform:translate(0,0) scale(1); } 50%{ transform:translate(-3vw,-2vw) scale(1.1); } }

[data-testid="stSidebar"] {
  background:rgba(0,0,0,0.95) !important;
  backdrop-filter:var(--glass-blur) !important;
  border-right:1px solid var(--line) !important;
}
[data-testid="stSidebar"] * { color:var(--text) !important; font-family:'Google Sans Flex',sans-serif !important; }
[data-testid="stSidebarNav"] { display:none; }  /* replaced by our own stepper */

h1, h2, h3 { font-family:'Google Sans Flex',sans-serif !important; font-weight:700 !important; letter-spacing:-0.01em; color:var(--text); }

@keyframes fadeSlideUp { from{ opacity:0; transform:translateY(16px);} to{ opacity:1; transform:translateY(0);} }
@keyframes glowPulse { 0%,100%{ box-shadow:0 0 0 rgba(255,255,255,0);} 50%{ box-shadow:0 0 22px rgba(255,255,255,0.18);} }
@keyframes ringSpin { from{ transform:rotate(0deg);} to{ transform:rotate(360deg);} }
@keyframes ringSpinReverse { from{ transform:rotate(360deg);} to{ transform:rotate(0deg);} }
@keyframes fadeSlideLeft { from{ opacity:0; transform:translateX(-14px);} to{ opacity:1; transform:translateX(0);} }
@keyframes pulseOnce { 0%{ transform:scale(1);} 35%{ transform:scale(1.05);} 100%{ transform:scale(1);} }
@keyframes successPop { 0%{ opacity:0; transform:scale(0.94);} 100%{ opacity:1; transform:scale(1);} }
@keyframes shimmerSweep { 0%{ background-position:-160% 0;} 100%{ background-position:160% 0;} }
@keyframes dropGlow { 0%,100%{ box-shadow:0 0 0 rgba(255,255,255,0);} 50%{ box-shadow:0 0 20px rgba(255,255,255,0.1);} }
@keyframes previewFlash { 0%{ opacity:0.35; filter:brightness(1.4);} 100%{ opacity:1; filter:brightness(1);} }
@keyframes staggerIn { from{ opacity:0; transform:translateY(14px);} to{ opacity:1; transform:translateY(0);} }

/* ── Per-page animation utilities ── */
/* Setup: a one-shot pulse for "just connected" states, not a loop */
.pulse-once { animation:pulseOnce 0.5s cubic-bezier(0.34,1.56,0.64,1) both; }
[data-testid="stFileUploader"]:hover { animation:dropGlow 1.6s ease-in-out infinite; }

/* Design: the live preview "flashes" to signal a fresh render, then settles */
.preview-flash { animation:previewFlash 0.35s ease-out both; }
.preview-flash [data-testid="stImage"] img { border-radius:10px; }

/* Send: log lines stream in from the left, progress bar shimmers while active */
.log-line { animation:fadeSlideLeft 0.22s ease both; }
[data-testid="stProgress"]>div>div {
  background-image:linear-gradient(90deg, var(--text) 0%, var(--text) 40%, #cfcfd6 50%, var(--text) 60%, var(--text) 100%) !important;
  background-size:250% 100% !important;
  animation:shimmerSweep 1.8s linear infinite !important;
}

/* Home: staggered entrance for the workflow cards */
.stagger-1 { animation-delay:0.05s !important; }
.stagger-2 { animation-delay:0.15s !important; }
.stagger-3 { animation-delay:0.25s !important; }

/* Brand mark (top-left, every page) */
.brand-row { display:flex; align-items:center; gap:0.6rem; margin-bottom:1.4rem; animation:fadeSlideUp 0.5s ease both; }
.brand-mark {
  width:30px; height:30px; border-radius:8px;
  background:var(--text); color:#000;
  display:flex; align-items:center; justify-content:center;
  font-weight:800; font-size:0.85rem; flex-shrink:0;
}
.brand-name { font-weight:600; font-size:1.02rem; letter-spacing:-0.01em; color:var(--text); }

/* ── Stepper: white filled = active, hairline outline = pending, check = done ── */
.stepper { display:flex; align-items:center; gap:0; margin-bottom:1.8rem; flex-wrap:wrap; animation:fadeSlideUp 0.55s ease both; }
.step-chip {
  display:flex; align-items:center; gap:0.5rem;
  padding:0.5rem 0.9rem; border-radius:99px;
  font-family:'JetBrains Mono',monospace; font-size:0.78rem; font-weight:500;
  background:transparent; border:1px solid var(--line); color:var(--text-dim2);
  transition:all 0.25s ease;
}
.step-chip.active { border-color:var(--text); color:#000; background:var(--text); font-weight:600; }
.step-chip.done { border-color:var(--line-2); color:var(--text); }
.step-chip .n {
  width:18px; height:18px; border-radius:50%; display:flex; align-items:center; justify-content:center;
  font-size:0.68rem; border:1px solid currentColor; flex-shrink:0;
}
.step-connector { width:26px; height:1px; flex-shrink:0; background:var(--line); }
.step-connector.filled { background:var(--text); }

/* ── Page header ── */
.page-eyebrow {
  font-family:'JetBrains Mono',monospace; font-size:var(--fs-mono);
  letter-spacing:0.14em; text-transform:uppercase; color:var(--text-dim);
  margin-bottom:0.5rem; animation:fadeSlideUp 0.5s ease both;
}
.page-title {
  font-size:var(--fs-hero); font-weight:700; letter-spacing:-0.025em; line-height:1.03;
  color:var(--text); font-family:'Google Sans Flex',sans-serif;
  animation:fadeSlideUp 0.6s 0.05s ease both;
}
.page-subtitle {
  font-size:clamp(0.88rem,1.8vw,1rem); color:var(--text-dim); margin:0.6rem 0 1.6rem; max-width:34rem; line-height:1.6;
  animation:fadeSlideUp 0.6s 0.12s ease both;
}

/* ── Cards: hairline borders on near-black, brighten + lift on hover ── */
.step-card, .gmail-card, .glass-panel {
  background:rgba(255,255,255,0.025);
  backdrop-filter:var(--glass-blur); -webkit-backdrop-filter:var(--glass-blur);
  border:1px solid var(--line); border-radius:16px;
  padding:clamp(1.1rem,2.4vw,1.5rem) clamp(1.05rem,2.4vw,1.6rem);
  margin-bottom:clamp(0.7rem,1.6vw,1rem);
  box-shadow:0 8px 32px rgba(0,0,0,0.5);
  transition:border-color 0.25s ease, transform 0.25s cubic-bezier(0.16,1,0.3,1), box-shadow 0.25s ease;
  animation:fadeSlideUp 0.5s ease both;
}
.step-card:hover, .gmail-card:hover, .glass-panel:hover {
  border-color:var(--line-2); transform:translateY(-3px);
  box-shadow:0 18px 44px rgba(0,0,0,0.6), 0 0 0 1px rgba(255,255,255,0.06);
}
.gmail-card { border-left:2px solid var(--text); }
.step-header { display:flex; align-items:flex-start; gap:0.85rem; margin-bottom:0.2rem; }
.step-num {
  display:inline-flex; align-items:center; justify-content:center;
  min-width:32px; height:32px; padding:0 0.3rem;
  border:1px solid var(--line-2); border-radius:9px;
  font-family:'JetBrains Mono',monospace; font-weight:600; font-size:0.76rem; color:var(--text);
  background:rgba(255,255,255,0.05); flex-shrink:0; margin-top:0.05rem;
}
.step-title { font-size:var(--fs-h2); font-weight:600; color:var(--text); letter-spacing:-0.005em; }
.step-desc { font-size:clamp(0.72rem,1.5vw,0.8rem); color:var(--text-dim2); margin-top:0.15rem; line-height:1.5; }
.gmail-hint { font-size:clamp(0.75rem,1.5vw,0.82rem); color:var(--text-dim); line-height:2; margin-top:0.7rem; }

/* ── Status / badges (semantic color kept for clarity) ── */
.status-badge {
  display:inline-flex; align-items:center; gap:0.5rem; border-radius:9px; padding:0.42rem 0.9rem;
  font-family:'JetBrains Mono',monospace; font-size:clamp(0.7rem,1.4vw,0.78rem); font-weight:500; margin-top:0.5rem;
}
.status-ready { background:rgba(74,222,128,0.08); border:1px solid rgba(74,222,128,0.3); color:var(--good); }
.status-warn  { background:rgba(251,191,110,0.08); border:1px solid rgba(251,191,110,0.3); color:var(--warn); }

/* ── Inputs: black glass, hairline border, brightens on focus ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
  background:rgba(255,255,255,0.03) !important; backdrop-filter:var(--glass-blur) !important;
  border:1px solid var(--line) !important; border-radius:10px !important;
  color:var(--text) !important; font-family:'Google Sans Flex',sans-serif !important; font-size:var(--fs-body) !important;
  min-height:42px !important; padding:0.55rem 0.8rem !important; caret-color:var(--text) !important;
  transition:all 0.2s ease !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stNumberInput"] input:focus {
  border-color:var(--text) !important; box-shadow:0 0 0 3px rgba(255,255,255,0.08) !important;
  background:rgba(255,255,255,0.05) !important;
}
label,[data-testid="stWidgetLabel"] p {
  color:var(--text-dim) !important; font-family:'JetBrains Mono',monospace !important;
  font-size:var(--fs-label) !important; font-weight:500 !important; letter-spacing:0.04em !important;
  text-transform:uppercase !important;
}
[data-testid="stSelectbox"]>div>div {
  background:rgba(255,255,255,0.03) !important; backdrop-filter:var(--glass-blur) !important;
  border:1px solid var(--line) !important; border-radius:10px !important;
  color:var(--text) !important; min-height:42px !important;
}
[data-testid="stFileUploader"] {
  background:rgba(255,255,255,0.015) !important; backdrop-filter:var(--glass-blur) !important;
  border:1.5px dashed var(--line-2) !important; border-radius:14px !important; transition:all 0.25s ease !important;
}
[data-testid="stFileUploader"]:hover {
  border-color:var(--text-dim) !important; background:rgba(255,255,255,0.035) !important;
}

/* ── Buttons: inverted white pill (Antigravity's "Download" CTA), outline secondary ── */
.stButton>button {
  font-family:'Google Sans Flex',sans-serif !important; font-size:clamp(0.9rem,2vw,1rem) !important;
  font-weight:600 !important; letter-spacing:0.01em !important;
  background:var(--text) !important;
  color:#000 !important; border:1px solid var(--text) !important; border-radius:99px !important;
  padding:clamp(0.65rem,1.6vw,0.8rem) 1.8rem !important; min-height:48px !important;
  transition:all 0.22s cubic-bezier(0.16,1,0.3,1) !important;
  box-shadow:0 10px 28px rgba(0,0,0,0.4) !important;
}
.stButton>button:hover {
  transform:translateY(-2px) scale(1.01) !important; filter:brightness(0.94) !important;
  box-shadow:0 16px 38px rgba(0,0,0,0.5), 0 0 24px rgba(255,255,255,0.15) !important;
}
.stButton>button:active { transform:translateY(0) scale(0.98) !important; }
.stButton>button:disabled { background:rgba(255,255,255,0.06) !important; color:var(--text-dim2) !important; box-shadow:none !important; border-color:var(--line) !important; }

/* secondary buttons (nav "Back") — outline only */
.stButton.secondary>button, button[kind="secondary"] {
  background:transparent !important; backdrop-filter:var(--glass-blur) !important;
  color:var(--text) !important; border:1px solid var(--line-2) !important; box-shadow:none !important;
}
.stButton.secondary>button:hover, button[kind="secondary"]:hover {
  border-color:var(--text) !important; background:rgba(255,255,255,0.05) !important;
}

/* ── Progress ── */
[data-testid="stProgress"]>div { background:var(--panel-2) !important; border-radius:50px !important; height:9px !important; border:1px solid var(--line) !important; }

/* ── Pills ── */
.stat-row { display:flex; gap:clamp(0.4rem,1.1vw,0.7rem); margin:0.8rem 0 1.1rem; flex-wrap:wrap; }
.stat-pill {
  background:rgba(255,255,255,0.03); backdrop-filter:var(--glass-blur);
  border:1px solid var(--line); border-radius:99px;
  padding:clamp(0.32rem,0.9vw,0.42rem) clamp(0.65rem,1.4vw,0.9rem);
  font-size:clamp(0.72rem,1.6vw,0.8rem); font-weight:500; color:var(--text-dim); white-space:nowrap;
  display:flex; align-items:center; gap:0.32rem; transition:all 0.2s ease;
}
.stat-pill:hover { border-color:var(--line-2); transform:translateY(-1px); }
.stat-pill b { color:var(--text); font-weight:700; }

.field-group-label {
  font-family:'JetBrains Mono',monospace; font-size:clamp(0.62rem,1.3vw,0.68rem); font-weight:600;
  letter-spacing:0.1em; text-transform:uppercase; padding:0.24rem 0.6rem; border-radius:6px;
  display:inline-block; margin-bottom:0.7rem;
}
.fg-gold  { background:rgba(255,255,255,0.08); border:1px solid var(--line-2); color:var(--text); }
.fg-amber { background:transparent; border:1px dashed var(--line-2); color:var(--text-dim); }

.hint-pill {
  display:inline-flex; align-items:flex-start; gap:0.5rem; flex-wrap:wrap;
  background:rgba(255,255,255,0.015); border:1px dashed var(--line-2); border-radius:9px;
  padding:clamp(0.4rem,1vw,0.55rem) clamp(0.7rem,1.6vw,0.95rem);
  font-size:clamp(0.72rem,1.5vw,0.79rem); color:var(--text-dim); margin-top:0.6rem; line-height:1.6;
}
.hint-pill code { background:rgba(255,255,255,0.1); color:var(--text); padding:0.06rem 0.4rem; border-radius:4px; font-family:'JetBrains Mono',monospace; font-size:0.85em; }

.eyebrow-label {
  display:flex; align-items:center; gap:0.5rem; font-family:'JetBrains Mono',monospace; font-size:0.72rem;
  font-weight:600; letter-spacing:0.12em; text-transform:uppercase; color:var(--text-dim); margin:1.2rem 0 0.7rem;
}
.eyebrow-label .dot { width:6px; height:6px; border-radius:50%; background:var(--text); flex-shrink:0; }

.log-box {
  background:rgba(255,255,255,0.02); backdrop-filter:var(--glass-blur); border:1px solid var(--line); border-radius:11px; padding:0.85rem 1.05rem;
  font-family:'JetBrains Mono',monospace; font-size:clamp(0.68rem,1.5vw,0.75rem); line-height:1.9;
  color:var(--text-dim); max-height:240px; overflow-y:auto; white-space:pre-wrap;
}
.log-box::-webkit-scrollbar{width:3px}
.log-box::-webkit-scrollbar-thumb{background:var(--line-2);border-radius:4px}

.live-status { display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap; font-size:clamp(0.78rem,1.8vw,0.87rem); color:var(--text-dim); margin:0.7rem 0; }
.live-dot { width:7px; height:7px; border-radius:50%; background:var(--text); flex-shrink:0; animation:dotPulse 1.3s ease-in-out infinite; }
@keyframes dotPulse { 0%,100%{ transform:scale(1); opacity:1; } 50%{ transform:scale(1.6); opacity:0.5; } }

.success-banner {
  background:rgba(255,255,255,0.025);
  backdrop-filter:var(--glass-blur); border:1px solid rgba(74,222,128,0.3); border-radius:18px;
  padding:clamp(1.5rem,3.4vw,2.2rem) clamp(1.1rem,2.6vw,2rem); text-align:center;
  box-shadow:0 20px 50px rgba(0,0,0,0.5), 0 0 40px rgba(74,222,128,0.08);
  animation:successPop 0.4s cubic-bezier(0.34,1.56,0.64,1) both;
}
.success-mark {
  width:52px; height:52px; margin:0 auto 0.9rem; border-radius:50%;
  background:rgba(74,222,128,0.1); border:1px solid rgba(74,222,128,0.45);
  display:flex; align-items:center; justify-content:center; font-size:1.4rem; color:var(--good);
  box-shadow:0 0 24px rgba(74,222,128,0.25);
  animation:glowPulse 1.3s ease-in-out 3 both;
}
.success-title { font-size:clamp(1.3rem,3.2vw,1.6rem); font-weight:700; color:var(--text); margin-bottom:0.3rem; }
.success-sub { color:var(--text-dim); font-size:clamp(0.82rem,1.8vw,0.92rem); }

hr { border:none !important; height:1px !important; background:linear-gradient(90deg,transparent,var(--line-2),transparent) !important; margin:clamp(0.8rem,2vw,1.5rem) 0 !important; }
[data-testid="stCheckbox"] span { color:var(--text-dim) !important; font-family:'Google Sans Flex',sans-serif !important; text-transform:none !important; }
.stCaption,[data-testid="stCaptionContainer"] { color:var(--text-dim2) !important; }
[data-testid="stAlert"] { border-radius:10px !important; }
[data-testid="stDataFrame"] { border-radius:10px !important; border:1px solid var(--line) !important; }
[data-testid="stExpander"] { border:1px solid var(--line) !important; border-radius:12px !important; background:var(--panel) !important; }
[data-testid="stSlider"] [role="slider"] { background:var(--text) !important; box-shadow:0 0 8px rgba(255,255,255,0.3) !important; }
[data-testid="stSlider"] > div > div > div { background:var(--text) !important; }

/* ── Icon ring (Antigravity's floating-glyph hero motif) ── */
.icon-ring-wrap { position:relative; width:100%; max-width:520px; height:220px; margin:0 auto; pointer-events:none; }
.icon-ring { position:absolute; inset:0; }
.icon-ring .ic {
  position:absolute; top:50%; left:50%; width:34px; height:34px; margin:-17px 0 0 -17px;
  display:flex; align-items:center; justify-content:center; border-radius:9px;
  background:rgba(255,255,255,0.04); border:1px solid var(--line);
  color:var(--text-dim); font-size:17px;
}
.icon-ring .orbit { position:absolute; inset:0; animation:ringSpin 42s linear infinite; }

@media(max-width:480px) {
  .block-container { padding:0.6rem 0.7rem 3rem !important; }
  .step-card, .gmail-card { padding:1rem 0.9rem; border-radius:14px; }
  .log-box { max-height:160px; }
  .icon-ring-wrap { height:150px; }
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
    """A second ambient glow orb that ::before alone can't place well."""
    st.markdown('<div class="orb-mid"></div>', unsafe_allow_html=True)


ICON_RING_GLYPHS = [
    "mail", "description", "verified", "badge", "send",
    "table_chart", "tune", "image", "check_circle", "upload_file",
]


def render_icon_ring():
    """
    A ring of Material Symbols orbiting the hero title — this is the
    same visual device antigravity.google uses (a circle of outlined
    glyphs slowly rotating behind the headline), adapted to icons
    relevant to certificates instead of coding.
    """
    import math
    n = len(ICON_RING_GLYPHS)
    radius = 150
    items = []
    for i, glyph in enumerate(ICON_RING_GLYPHS):
        angle = (2 * math.pi / n) * i
        x = radius * math.cos(angle)
        y = radius * math.sin(angle) * 0.55  # flatten into an ellipse
        items.append(
            f'<div class="ic" style="transform:translate({x:.0f}px,{y:.0f}px);">'
            f'<span class="material-symbols-outlined">{glyph}</span></div>'
        )
    st.markdown(f"""
    <div class="icon-ring-wrap">
      <div class="icon-ring">
        <div class="orbit">{''.join(items)}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


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