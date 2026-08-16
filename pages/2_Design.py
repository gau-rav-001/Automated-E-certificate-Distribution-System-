import io
import pandas as pd
import streamlit as st
from common import (
    inject_base_css, brand_header, render_stepper, page_header, init_session_state,
    build_certificate_pdf, render_pdf_preview,
)

st.set_page_config(page_title="Design · AutoCertify", page_icon="🎓", layout="wide", initial_sidebar_state="collapsed")
init_session_state()
inject_base_css()
brand_header()
render_stepper("design")

# Design-page-only motion: no ambient/orbiting background here (this page is
# about *seeing changes happen*, so it stays calm and doesn't compete with
# the live preview), a stronger focus ring on position inputs (precision
# matters most here), and a "just updated" flash on the live preview image.
st.markdown("""
<style>
[data-testid="stAppViewContainer"]::before { animation:none !important; opacity:0.35 !important; }
[data-testid="stNumberInput"] input:focus {
  box-shadow:0 0 0 4px rgba(255,255,255,0.14) !important;
}
[data-testid="stImage"] img { animation:previewFlash 0.35s ease-out; border-radius:10px; }
</style>
""", unsafe_allow_html=True)

if not (st.session_state.csv_bytes and st.session_state.template_bytes):
    st.markdown("""
    <div class="status-badge status-warn">Finish Setup first — upload a CSV and a certificate template.</div>
    """, unsafe_allow_html=True)
    st.page_link("pages/1_Setup.py", label="← Go to Setup")
    st.stop()

page_header(
    "Step 2 of 3",
    "Design studio",
    "Map your CSV columns to the right fields, then position the name and "
    "department on the certificate — the canvas on the right updates live."
)

controls_col, canvas_col = st.columns([1, 1.05], gap="large")

# ══ LEFT: DESIGN CONTROLS ══════════════════════
with controls_col:
    st.markdown("""
    <div class="step-card">
      <div class="step-header">
        <div class="step-num">02</div>
        <div>
          <div class="step-title">Map CSV columns</div>
          <div class="step-desc">Select which column holds each piece of data</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        data = pd.read_csv(io.BytesIO(st.session_state.csv_bytes), encoding="cp1252")
        data.columns = data.columns.str.strip()
        st.caption(f"{len(data)} participants detected")
        st.dataframe(data.head(4), use_container_width=True, hide_index=True)
        columns = data.columns.tolist()

        st.session_state.name_col = st.selectbox(
            "Name column", columns,
            index=columns.index(st.session_state.name_col) if st.session_state.name_col in columns else 0
        )
        st.session_state.dept_col = st.selectbox(
            "Department column", columns,
            index=columns.index(st.session_state.dept_col) if st.session_state.dept_col in columns else 0
        )
        st.session_state.email_col = st.selectbox(
            "Email column", columns,
            index=columns.index(st.session_state.email_col) if st.session_state.email_col in columns else 0
        )
    except Exception as e:
        data = None
        st.error(f"Could not read CSV: {e}")

    st.markdown("""
    <div class="step-card">
      <div class="step-header">
        <div class="step-num">03</div>
        <div>
          <div class="step-title">Text position</div>
          <div class="step-desc">X = from left edge · Y = from bottom · Defaults suit A4 landscape</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="field-group-label fg-gold">Name</span>', unsafe_allow_html=True)
    na, nb, nc = st.columns(3)
    with na: st.session_state.name_x = st.number_input("X", value=st.session_state.name_x, step=5, key="nx")
    with nb: st.session_state.name_y = st.number_input("Y", value=st.session_state.name_y, step=5, key="ny")
    with nc: st.session_state.name_size = st.number_input("Size", value=st.session_state.name_size, step=1, key="ns", min_value=6, max_value=72)
    st.session_state.center_name = st.checkbox("Center-align name", value=st.session_state.center_name)

    st.markdown('<span class="field-group-label fg-amber">Department</span>', unsafe_allow_html=True)
    da, db, dc = st.columns(3)
    with da: st.session_state.dept_x = st.number_input("X", value=st.session_state.dept_x, step=5, key="dx")
    with db: st.session_state.dept_y = st.number_input("Y", value=st.session_state.dept_y, step=5, key="dy")
    with dc: st.session_state.dept_size = st.number_input("Size", value=st.session_state.dept_size, step=1, key="ds", min_value=6, max_value=72)
    st.session_state.center_dept = st.checkbox("Center-align department", value=st.session_state.center_dept)

# ══ RIGHT: LIVE CANVAS ═════════════════════════
with canvas_col:
    st.markdown("""
    <div class="glass-panel" style="text-align:center;">
      <div class="eyebrow-label" style="justify-content:center;"><span class="dot"></span>Certificate preview</div>
    </div>
    """, unsafe_allow_html=True)

    preview_name = "John Doe"
    preview_dept = "Sample Department"
    if data is not None and len(data) > 0 and st.session_state.name_col and st.session_state.dept_col:
        try:
            preview_name = str(data.iloc[0][st.session_state.name_col]).strip()
            preview_dept = str(data.iloc[0][st.session_state.dept_col]).strip()
        except Exception:
            pass

    try:
        preview_pdf_bytes = build_certificate_pdf(
            st.session_state.template_bytes, preview_name, preview_dept,
            st.session_state.name_x, st.session_state.name_y, st.session_state.name_size, st.session_state.center_name,
            st.session_state.dept_x, st.session_state.dept_y, st.session_state.dept_size, st.session_state.center_dept,
        )
        preview_png = render_pdf_preview(preview_pdf_bytes)
        st.image(preview_png, use_container_width=True)
        st.markdown(f"""
        <div class="hint-pill">
          Previewing with <code>{preview_name}</code> / <code>{preview_dept}</code> —
          updates as you adjust the settings on the left.
        </div>
        """, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Couldn't render preview: {e}")

st.markdown("<hr>", unsafe_allow_html=True)

ready = bool(st.session_state.name_col and st.session_state.dept_col and st.session_state.email_col)
nav1, nav2 = st.columns([1, 1])
with nav1:
    st.page_link("pages/1_Setup.py", label="← Back to Setup")
with nav2:
    if ready:
        st.page_link("pages/3_Send.py", label="Continue to Send →")
    else:
        st.button("Continue to Send →", disabled=True)