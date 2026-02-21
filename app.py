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
    page_title="AutoCertify",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@200;300;400;500;600;700;900&family=Instrument+Serif:ital@0;1&family=Space+Mono:wght@400;700&display=swap');

:root {
  --gold:   #f5c842;
  --gold2:  #ffab00;
  --amber:  #ff6b35;
  --cream:  #fdf6e3;
  --ink:    #0d0a05;
  --glass:  rgba(245,200,66,0.06);
  --border: rgba(245,200,66,0.18);
  --fs-hero:  clamp(2.6rem, 8vw, 6rem);
  --fs-h2:    clamp(1rem, 3vw, 1.2rem);
  --fs-body:  clamp(0.82rem, 2vw, 0.95rem);
  --fs-label: clamp(0.68rem, 1.8vw, 0.8rem);
  --fs-mono:  clamp(0.62rem, 1.5vw, 0.72rem);
}

/* ── Keyframes ── */
@keyframes float3d {
  0%   { transform: perspective(800px) rotateX(8deg) rotateY(-6deg) translateY(0px); }
  33%  { transform: perspective(800px) rotateX(2deg) rotateY(6deg)  translateY(-10px); }
  66%  { transform: perspective(800px) rotateX(-4deg) rotateY(0deg) translateY(-5px); }
  100% { transform: perspective(800px) rotateX(8deg) rotateY(-6deg) translateY(0px); }
}
@keyframes shimmer {
  0%   { background-position: -200% center; }
  100% { background-position:  200% center; }
}
@keyframes scanLine {
  0%   { top: -10%; }
  100% { top: 110%; }
}
@keyframes fadeSlideUp {
  from { opacity:0; transform:translateY(28px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes fadeSlideLeft {
  from { opacity:0; transform:translateX(-30px); }
  to   { opacity:1; transform:translateX(0); }
}
@keyframes starTwinkle {
  0%,100% { opacity:0.12; transform:scale(0.85); }
  50%     { opacity:0.8;  transform:scale(1.3); }
}
@keyframes pulseGold {
  0%,100% { box-shadow:0 0 6px rgba(245,200,66,0.4); }
  50%     { box-shadow:0 0 18px rgba(245,200,66,0.9); }
}
@keyframes spinSlow {
  from { transform:rotate(0deg); }
  to   { transform:rotate(360deg); }
}

/* ── Global ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
  font-family: 'Outfit', sans-serif;
  background: var(--ink);
  color: var(--cream);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
  padding: clamp(0.8rem,3vw,2rem) clamp(0.8rem,3vw,2.5rem) 4rem !important;
  max-width: 1280px !important;
  width: 100% !important;
}

/* ── Background ── */
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(ellipse 70% 50% at 15% 15%, rgba(245,200,66,0.10) 0%, transparent 55%),
    radial-gradient(ellipse 50% 40% at 85% 85%, rgba(255,107,53,0.08) 0%, transparent 50%),
    var(--ink);
  min-height: 100vh;
  overflow-x: hidden;
}
[data-testid="stAppViewContainer"]::before {
  content: '✦ ✧ ★ ✦ ✧ ★ ✦ ✧ ✦ ★';
  position: fixed; top: 5%; left: 0; width: 100%;
  font-size: clamp(0.35rem,0.8vw,0.55rem);
  letter-spacing: clamp(1.5rem,4vw,3.5rem);
  color: rgba(245,200,66,0.09);
  pointer-events: none;
  animation: starTwinkle 4s ease-in-out infinite;
  z-index: 0; overflow: hidden;
}

/* ── Sidebar (still exists for small helper) ── */
[data-testid="stSidebar"] {
  background: linear-gradient(160deg,#120f08,#0d0a05) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--cream) !important; }

/* ══════════════════════════════
   HERO
══════════════════════════════ */
.hero-wrapper {
  display: flex;
  align-items: center;
  gap: clamp(1.5rem,4vw,4rem);
  padding: clamp(2rem,5vw,3.5rem) 0 clamp(1rem,2vw,1.5rem);
  animation: fadeSlideUp 0.9s cubic-bezier(0.16,1,0.3,1) both;
  flex-wrap: wrap;
}
.cert-3d-wrap { flex-shrink:0; perspective:900px; margin:0 auto; }
.cert-3d {
  width: clamp(130px,20vw,210px);
  height: clamp(92px,14vw,148px);
  background: linear-gradient(135deg,#1e1808,#2a2010,#1a1408);
  border: 1px solid rgba(245,200,66,0.35);
  border-radius: 12px;
  animation: float3d 7s ease-in-out infinite;
  position: relative; overflow: hidden;
  box-shadow: 0 30px 80px rgba(0,0,0,0.7), inset 0 1px 0 rgba(245,200,66,0.18);
}
.cert-3d::before {
  content:''; position:absolute; inset:0;
  background: linear-gradient(135deg,rgba(245,200,66,0.07),transparent 60%);
}
.cert-3d::after {
  content:''; position:absolute; left:0; right:0; height:2px;
  background: linear-gradient(90deg,transparent,rgba(245,200,66,0.4),transparent);
  animation: scanLine 3s linear infinite;
}
.cert-inner {
  position:absolute; inset:12px;
  border:1px solid rgba(245,200,66,0.18); border-radius:6px;
  display:flex; flex-direction:column; align-items:center; justify-content:center; gap:5px;
}
.cert-trophy {
  font-size:clamp(1.3rem,3.5vw,1.9rem);
  filter:drop-shadow(0 0 10px rgba(245,200,66,0.5));
  animation:starTwinkle 2s ease-in-out infinite;
}
.cert-lines { display:flex; flex-direction:column; gap:4px; width:70%; }
.cert-line  { height:3px; border-radius:4px; background:linear-gradient(90deg,rgba(245,200,66,0.5),rgba(245,200,66,0.1)); }
.cert-line.short { width:60%; margin:0 auto; }
.cert-seal {
  position:absolute; bottom:9px; right:9px;
  width:24px; height:24px;
  border:1.5px solid rgba(245,200,66,0.45); border-radius:50%;
  display:flex; align-items:center; justify-content:center;
  font-size:0.6rem;
  animation:spinSlow 10s linear infinite;
}
.hero-text { flex:1; min-width:220px; }
.logo-badge {
  display:inline-block;
  background:linear-gradient(135deg,rgba(245,200,66,0.12),rgba(255,107,53,0.08));
  border:1px solid rgba(245,200,66,0.28); border-radius:50px;
  padding:0.25rem clamp(0.6rem,2vw,1rem);
  font-family:'Space Mono',monospace;
  font-size:var(--fs-mono); letter-spacing:0.15em; color:var(--gold);
  text-transform:uppercase; margin-bottom:0.7rem;
  animation:fadeSlideLeft 0.7s 0.2s both;
}
.hero-title-main {
  font-family:'Bebas Neue',sans-serif;
  font-size:var(--fs-hero);
  letter-spacing:0.06em; line-height:0.95;
  background:linear-gradient(135deg,#f5c842 0%,#ffab00 30%,#fff4cc 55%,#f5c842 70%,#ff6b35 100%);
  background-size:200% auto;
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  animation:fadeSlideLeft 0.8s 0.3s both, shimmer 4s linear 1s infinite;
}
.hero-subtitle {
  font-family:'Instrument Serif',serif; font-style:italic;
  font-size:clamp(0.85rem,2.2vw,1.1rem);
  color:rgba(253,246,227,0.5);
  margin:0.5rem 0 1.1rem;
  animation:fadeSlideLeft 0.8s 0.5s both;
}
.hero-stats {
  display:flex; gap:clamp(0.4rem,1.5vw,0.9rem);
  flex-wrap:wrap;
  animation:fadeSlideLeft 0.8s 0.7s both;
}
.hero-stat {
  display:flex; align-items:center; gap:0.35rem;
  background:var(--glass); border:1px solid var(--border); border-radius:50px;
  padding:clamp(0.25rem,1vw,0.38rem) clamp(0.55rem,1.5vw,0.9rem);
  font-size:clamp(0.7rem,1.8vw,0.8rem); font-weight:500;
  color:rgba(253,246,227,0.62); white-space:nowrap;
  transition:all 0.3s ease;
}
.hero-stat:hover { background:rgba(245,200,66,0.12); color:var(--gold); transform:translateY(-2px); }
.hero-stat b { color:var(--gold); font-weight:700; }

.gold-divider {
  width:100%; height:1px;
  background:linear-gradient(90deg,transparent,var(--gold),rgba(255,107,53,0.5),transparent);
  margin:clamp(1rem,3vw,1.8rem) 0; position:relative;
}
.gold-divider::after {
  content:'✦'; position:absolute; top:50%; left:50%;
  transform:translate(-50%,-50%);
  background:var(--ink); padding:0 0.7rem; color:var(--gold); font-size:0.62rem;
}

/* ══════════════════════════════
   STEP CARDS
══════════════════════════════ */
.step-card {
  position:relative;
  background:linear-gradient(145deg,rgba(245,200,66,0.04),rgba(13,10,5,0.9));
  border:1px solid var(--border);
  border-radius:clamp(12px,2vw,20px);
  padding:clamp(1.1rem,3vw,1.9rem) clamp(1rem,3vw,2.1rem);
  margin-bottom:clamp(0.7rem,2vw,1.3rem);
  overflow:hidden;
  transition:transform 0.4s cubic-bezier(0.16,1,0.3,1),box-shadow 0.4s ease,border-color 0.3s ease;
  animation:fadeSlideUp 0.8s both;
}
.step-card::before {
  content:''; position:absolute; top:0; left:0; right:0; height:1px;
  background:linear-gradient(90deg,transparent,var(--gold),rgba(255,107,53,0.7),transparent);
}
@media (hover:hover) {
  .step-card:hover {
    transform:perspective(1000px) rotateX(-1deg) rotateY(1deg) translateY(-3px);
    box-shadow:0 20px 60px rgba(0,0,0,0.5),0 0 40px rgba(245,200,66,0.07);
    border-color:rgba(245,200,66,0.35);
  }
}
.step-card:nth-child(1){animation-delay:0.05s}
.step-card:nth-child(2){animation-delay:0.12s}
.step-card:nth-child(3){animation-delay:0.19s}
.step-card:nth-child(4){animation-delay:0.26s}
.step-card:nth-child(5){animation-delay:0.33s}
.step-card:nth-child(6){animation-delay:0.40s}

.step-num {
  display:inline-flex; align-items:center; justify-content:center;
  width:clamp(26px,4vw,35px); height:clamp(26px,4vw,35px);
  background:linear-gradient(135deg,var(--gold),var(--gold2));
  border-radius:50%;
  font-family:'Space Mono',monospace;
  font-size:clamp(0.62rem,1.5vw,0.78rem); font-weight:700; color:var(--ink);
  box-shadow:0 4px 14px rgba(245,200,66,0.35); flex-shrink:0;
}
.step-header {
  display:flex; align-items:center;
  gap:clamp(0.5rem,1.5vw,0.8rem);
  margin-bottom:clamp(0.8rem,2vw,1.2rem);
}
.step-title {
  font-family:'Outfit',sans-serif; font-size:var(--fs-h2);
  font-weight:800; color:#fdf6e3; letter-spacing:-0.01em;
}
.step-desc {
  font-size:clamp(0.68rem,1.6vw,0.76rem);
  color:rgba(253,246,227,0.36); font-weight:300; margin-top:0.1rem;
}

/* ══════════════════════════════
   GMAIL CONFIG CARD  (always visible)
══════════════════════════════ */
.gmail-card {
  background:linear-gradient(135deg,rgba(245,200,66,0.07),rgba(255,107,53,0.04));
  border:1px solid rgba(245,200,66,0.28);
  border-radius:clamp(12px,2vw,18px);
  padding:clamp(1.1rem,3vw,1.8rem) clamp(1rem,3vw,2rem);
  margin-bottom:clamp(0.7rem,2vw,1.3rem);
  position:relative; overflow:hidden;
  animation:fadeSlideUp 0.8s 0.05s both;
}
.gmail-card::before {
  content:''; position:absolute; top:0; left:0; right:0; height:2px;
  background:linear-gradient(90deg,transparent,var(--gold),var(--amber),transparent);
}
.gmail-badge {
  display:inline-flex; align-items:center; gap:0.4rem;
  background:rgba(245,200,66,0.1); border:1px solid rgba(245,200,66,0.25);
  border-radius:50px; padding:0.25rem 0.8rem;
  font-family:'Space Mono',monospace; font-size:var(--fs-mono);
  letter-spacing:0.12em; color:var(--gold); text-transform:uppercase;
  margin-bottom:0.9rem; display:inline-block;
}
.gmail-hint {
  font-size:clamp(0.7rem,1.6vw,0.77rem);
  color:rgba(253,246,227,0.36); line-height:1.9;
  margin-top:0.6rem;
}
.gmail-hint a { color:var(--gold); text-decoration:none; }

/* status dot */
.status-dot {
  display:inline-block; width:8px; height:8px; border-radius:50%;
  background:var(--gold); margin-right:0.4rem;
  animation:pulseGold 1.5s ease-in-out infinite;
}

/* ══════════════════════════════
   INPUTS
══════════════════════════════ */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
  background:rgba(245,200,66,0.04) !important;
  border:1px solid rgba(245,200,66,0.2) !important;
  border-radius:10px !important;
  color:var(--cream) !important;
  font-family:'Outfit',sans-serif !important;
  font-size:var(--fs-body) !important;
  min-height:44px !important;
  padding:0.6rem 0.85rem !important;
  transition:all 0.25s ease !important;
  caret-color:var(--gold) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color:rgba(245,200,66,0.55) !important;
  box-shadow:0 0 0 3px rgba(245,200,66,0.1) !important;
  background:rgba(245,200,66,0.06) !important;
}
label,[data-testid="stWidgetLabel"] p {
  color:rgba(253,246,227,0.6) !important;
  font-family:'Outfit',sans-serif !important;
  font-size:var(--fs-label) !important;
  font-weight:500 !important; letter-spacing:0.05em !important;
  text-transform:uppercase !important;
}
[data-testid="stSelectbox"]>div>div {
  background:rgba(245,200,66,0.04) !important;
  border:1px solid rgba(245,200,66,0.2) !important;
  border-radius:10px !important; color:var(--cream) !important;
  min-height:44px !important;
}
[data-testid="stFileUploader"] {
  background:rgba(245,200,66,0.02) !important;
  border:1.5px dashed rgba(245,200,66,0.28) !important;
  border-radius:14px !important; transition:all 0.3s ease !important;
}
[data-testid="stFileUploader"]:hover {
  border-color:rgba(245,200,66,0.6) !important;
  background:rgba(245,200,66,0.04) !important;
}

/* ══════════════════════════════
   SEND BUTTON
══════════════════════════════ */
.stButton>button {
  font-family:'Bebas Neue',sans-serif !important;
  font-size:clamp(1rem,3vw,1.25rem) !important;
  letter-spacing:0.15em !important;
  background:linear-gradient(135deg,#f5c842 0%,#ffab00 50%,#ff6b35 100%) !important;
  color:var(--ink) !important; border:none !important;
  border-radius:12px !important;
  padding:clamp(0.7rem,2vw,0.9rem) 2rem !important;
  width:100% !important; min-height:52px !important;
  transition:all 0.3s cubic-bezier(0.16,1,0.3,1) !important;
  box-shadow:0 4px 25px rgba(245,200,66,0.35) !important;
}
@media (hover:hover) {
  .stButton>button:hover {
    transform:translateY(-3px) scale(1.01) !important;
    box-shadow:0 12px 40px rgba(245,200,66,0.5) !important;
  }
}
.stButton>button:active { transform:scale(0.98) !important; }
.stButton>button:disabled {
  background:rgba(245,200,66,0.1) !important;
  color:rgba(253,246,227,0.2) !important; box-shadow:none !important;
}

/* ══════════════════════════════
   PROGRESS
══════════════════════════════ */
[data-testid="stProgress"]>div {
  background:rgba(245,200,66,0.08) !important; border-radius:50px !important;
  height:10px !important; border:1px solid rgba(245,200,66,0.14) !important;
}
[data-testid="stProgress"]>div>div {
  background:linear-gradient(90deg,#f5c842,#ffab00,#ff6b35) !important;
  border-radius:50px !important; background-size:200% 100% !important;
  animation:shimmer 1.5s linear infinite !important;
  box-shadow:0 0 14px rgba(245,200,66,0.4) !important;
}

/* ══════════════════════════════
   STAT PILLS
══════════════════════════════ */
.stat-row { display:flex; gap:clamp(0.4rem,1.2vw,0.8rem); margin:0.8rem 0 1.1rem; flex-wrap:wrap; }
.stat-pill {
  background:linear-gradient(135deg,rgba(245,200,66,0.08),rgba(255,107,53,0.05));
  border:1px solid rgba(245,200,66,0.2); border-radius:50px;
  padding:clamp(0.3rem,1vw,0.42rem) clamp(0.6rem,1.5vw,0.95rem);
  font-size:clamp(0.7rem,1.8vw,0.8rem); font-weight:500;
  color:rgba(253,246,227,0.62); white-space:nowrap;
  display:flex; align-items:center; gap:0.3rem;
  transition:all 0.25s ease;
}
.stat-pill:hover { background:rgba(245,200,66,0.12); color:var(--gold); }
.stat-pill b { color:var(--gold); font-weight:700; }

/* field group */
.field-group-label {
  font-family:'Space Mono',monospace;
  font-size:clamp(0.58rem,1.4vw,0.67rem); font-weight:700;
  letter-spacing:0.12em; text-transform:uppercase;
  padding:0.22rem 0.65rem; border-radius:6px;
  display:inline-block; margin-bottom:0.6rem;
}
.fg-gold  { background:rgba(245,200,66,0.12); border:1px solid rgba(245,200,66,0.3); color:var(--gold); }
.fg-amber { background:rgba(255,107,53,0.1);  border:1px solid rgba(255,107,53,0.3); color:#ff6b35; }

/* hint */
.hint-pill {
  display:inline-flex; align-items:center; gap:0.4rem; flex-wrap:wrap;
  background:rgba(245,200,66,0.05); border:1px dashed rgba(245,200,66,0.2);
  border-radius:8px; padding:clamp(0.38rem,1vw,0.48rem) clamp(0.6rem,1.5vw,0.95rem);
  font-size:clamp(0.7rem,1.8vw,0.77rem); color:rgba(253,246,227,0.4); margin-top:0.5rem;
}
.hint-pill code {
  background:rgba(245,200,66,0.15); color:var(--gold);
  padding:0.08rem 0.38rem; border-radius:4px;
  font-family:'Space Mono',monospace; font-size:0.78em;
}

/* log */
.log-box {
  background:rgba(0,0,0,0.5); border:1px solid rgba(245,200,66,0.14);
  border-radius:12px; padding:0.85rem 1.1rem;
  font-family:'Space Mono',monospace;
  font-size:clamp(0.66rem,1.6vw,0.74rem); line-height:1.9;
  color:rgba(245,200,66,0.7); max-height:240px; overflow-y:auto;
  white-space:pre-wrap;
}
.log-box::-webkit-scrollbar{width:3px}
.log-box::-webkit-scrollbar-thumb{background:rgba(245,200,66,0.3);border-radius:4px}

/* live status */
.live-status {
  display:flex; align-items:center; gap:0.5rem; flex-wrap:wrap;
  font-size:clamp(0.76rem,2vw,0.87rem); color:rgba(253,246,227,0.5); margin:0.7rem 0;
}
.live-dot {
  width:7px; height:7px; border-radius:50%; background:var(--gold); flex-shrink:0;
  animation:pulseGold 1.5s ease-in-out infinite;
}

/* success */
.success-banner {
  position:relative;
  background:linear-gradient(135deg,rgba(245,200,66,0.08),rgba(255,107,53,0.05));
  border:1px solid rgba(245,200,66,0.3);
  border-radius:clamp(14px,2vw,20px);
  padding:clamp(1.4rem,4vw,2.5rem) clamp(1rem,3vw,2rem);
  text-align:center; overflow:hidden;
  animation:fadeSlideUp 0.8s cubic-bezier(0.16,1,0.3,1) both;
}
.success-banner::before {
  content:''; position:absolute; top:0; left:0; right:0; height:2px;
  background:linear-gradient(90deg,transparent,var(--gold),var(--amber),transparent);
}
.success-trophy {
  font-size:clamp(2rem,6vw,3.5rem); display:block; margin-bottom:0.6rem;
  filter:drop-shadow(0 0 18px rgba(245,200,66,0.5));
  animation:float3d 4s ease-in-out infinite;
}
.success-title {
  font-family:'Bebas Neue',sans-serif;
  font-size:clamp(1.8rem,5vw,2.5rem); letter-spacing:0.1em;
  background:linear-gradient(135deg,#f5c842,#ffab00,#ff6b35);
  -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
  margin-bottom:0.4rem;
}
.success-sub {
  font-family:'Instrument Serif',serif; font-style:italic;
  color:rgba(253,246,227,0.5); font-size:clamp(0.82rem,2.2vw,1rem);
}

/* misc */
hr {
  border:none !important; height:1px !important;
  background:linear-gradient(90deg,transparent,rgba(245,200,66,0.2),transparent) !important;
  margin:clamp(0.8rem,2.5vw,1.8rem) 0 !important;
}
[data-testid="stCheckbox"] span { color:rgba(253,246,227,0.6) !important; }
.stCaption,[data-testid="stCaptionContainer"] { color:rgba(253,246,227,0.35) !important; font-family:'Outfit',sans-serif !important; }
[data-testid="stAlert"] { border-radius:12px !important; }
[data-testid="stDataFrame"] { border-radius:12px !important; border:1px solid rgba(245,200,66,0.14) !important; }
[data-testid="stExpander"] { border:1px solid rgba(245,200,66,0.14) !important; border-radius:12px !important; background:rgba(245,200,66,0.02) !important; }
[data-testid="stSlider"] [role="slider"] { background:var(--gold) !important; box-shadow:0 0 10px rgba(245,200,66,0.45) !important; }

/* ══════════════════════════════
   MOBILE  ≤ 480px
══════════════════════════════ */
@media (max-width:480px) {
  .block-container { padding:0.6rem 0.7rem 3rem !important; }
  .hero-wrapper { flex-direction:column; align-items:center; text-align:center; gap:1.1rem; padding:1.3rem 0 0.8rem; }
  .hero-text { min-width:unset; width:100%; }
  .hero-stats { justify-content:center; }
  .step-card { padding:1rem 0.85rem; border-radius:14px; }
  .log-box { max-height:160px; }
  [data-testid="stAppViewContainer"]::before { display:none; }
  .success-banner { padding:1.3rem 0.9rem; }
  /* Gmail fields always 1-col on mobile */
  .gmail-cols [data-testid="column"] {
    width:100% !important; flex:1 1 100% !important;
  }
  /* send-settings row → stack */
  .send-settings-row [data-testid="column"] {
    width:100% !important; flex:1 1 100% !important;
  }
}
@media (max-width:360px) {
  .cert-3d { width:120px; height:84px; }
  .hero-title-main { font-size:2.2rem; }
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-wrapper">
  <div class="cert-3d-wrap">
    <div class="cert-3d">
      <div class="cert-inner">
        <div class="cert-trophy">🏆</div>
        <div class="cert-lines">
          <div class="cert-line"></div>
          <div class="cert-line short"></div>
          <div class="cert-line"></div>
        </div>
      </div>
      <div class="cert-seal">✦</div>
    </div>
  </div>
  <div class="hero-text">
    <div class="logo-badge">✦ Certificate Automation Platform</div>
    <div class="hero-title-main">AutoCertify</div>
    <div class="hero-subtitle">Generate, personalize &amp; deliver certificates — instantly.</div>
    <div class="hero-stats">
      <div class="hero-stat">📋 <b>CSV</b> Driven</div>
      <div class="hero-stat">📄 <b>PDF</b> Overlay</div>
      <div class="hero-stat">📧 <b>Gmail</b> SMTP</div>
      <div class="hero-stat">⚡ <b>Zero</b> Code</div>
    </div>
  </div>
</div>
<div class="gold-divider"></div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STEP 0 — GMAIL CONFIG  (always on main page)
# ─────────────────────────────────────────────
st.markdown("""
<div class="gmail-card">
  <div class="step-header">
    <div class="step-num">✉</div>
    <div>
      <div class="step-title">Gmail Configuration</div>
      <div class="step-desc">Your credentials are never stored — used only for this session</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

gc1, gc2 = st.columns(2)
with gc1:
    sender_email = st.text_input("📧  Sender Gmail Address", placeholder="you@gmail.com")
with gc2:
    app_password = st.text_input("🔑  App Password", type="password", placeholder="xxxx xxxx xxxx xxxx")

with st.expander("❓  How to get an App Password"):
    st.markdown("""
    <div class="gmail-hint">
    1 · Go to <b style='color:#f5c842'>myaccount.google.com</b><br>
    2 · Security → 2-Step Verification (must be ON)<br>
    3 · Scroll down → <b style='color:#f5c842'>App Passwords</b><br>
    4 · Select app: <b>Mail</b> → Generate<br>
    5 · Copy the 16-character code and paste it above
    </div>
    """, unsafe_allow_html=True)

delay_col, _ = st.columns([1, 2])
with delay_col:
    delay = st.slider("⏱️  Delay between emails (seconds)", 1, 10, 2)

if sender_email and app_password:
    st.success(f"✓ Ready to send from **{sender_email}**")

st.markdown("<hr>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STEP 1 — UPLOAD
# ─────────────────────────────────────────────
st.markdown("""
<div class="step-card">
  <div class="step-header">
    <div class="step-num">01</div>
    <div>
      <div class="step-title">Upload Your Files</div>
      <div class="step-desc">Your participant list (CSV) and blank certificate template (PDF)</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

u1, u2 = st.columns(2)
with u1:
    csv_file = st.file_uploader("📋  Participant List (CSV)", type=["csv"])
with u2:
    template_pdf = st.file_uploader("📄  Certificate Template (PDF)", type=["pdf"])


# ─────────────────────────────────────────────
# STEP 2 — MAP COLUMNS
# ─────────────────────────────────────────────
data = None
name_col = dept_col = email_col = None

if csv_file:
    st.markdown("""
    <div class="step-card">
      <div class="step-header">
        <div class="step-num">02</div>
        <div>
          <div class="step-title">Map Your Columns</div>
          <div class="step-desc">Select which CSV column holds each piece of data</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        data = pd.read_csv(csv_file, encoding="cp1252")
        data.columns = data.columns.str.strip()
        st.caption(f"Preview — {len(data)} participants detected")
        st.dataframe(data.head(4), use_container_width=True, hide_index=True)

        columns = data.columns.tolist()
        m1, m2, m3 = st.columns(3)
        with m1: name_col  = st.selectbox("👤  Name Column",       columns)
        with m2: dept_col  = st.selectbox("🏢  Department Column", columns)
        with m3: email_col = st.selectbox("📧  Email Column",      columns)

    except Exception as e:
        st.error(f"Could not read CSV: {e}")


# ─────────────────────────────────────────────
# STEP 3 — TEXT POSITION
# ─────────────────────────────────────────────
st.markdown("""
<div class="step-card">
  <div class="step-header">
    <div class="step-num">03</div>
    <div>
      <div class="step-title">Certificate Text Position</div>
      <div class="step-desc">X = distance from left &nbsp;·&nbsp; Y = distance from bottom &nbsp;·&nbsp; Defaults suit A4 landscape</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

p1, p2 = st.columns(2)
with p1:
    st.markdown('<span class="field-group-label fg-gold">✦ Name</span>', unsafe_allow_html=True)
    na, nb, nc = st.columns(3)
    with na: name_x    = st.number_input("X",    value=250, step=5, key="nx")
    with nb: name_y    = st.number_input("Y",    value=223, step=5, key="ny")
    with nc: name_size = st.number_input("Size", value=14,  step=1, key="ns", min_value=6, max_value=72)
    center_name = st.checkbox("Center-align Name", value=False)

with p2:
    st.markdown('<span class="field-group-label fg-amber">✦ Department</span>', unsafe_allow_html=True)
    da, db, dc = st.columns(3)
    with da: dept_x    = st.number_input("X",    value=185, step=5, key="dx")
    with db: dept_y    = st.number_input("Y",    value=198, step=5, key="dy")
    with dc: dept_size = st.number_input("Size", value=14,  step=1, key="ds", min_value=6, max_value=72)
    center_dept = st.checkbox("Center-align Department", value=False)


# ─────────────────────────────────────────────
# STEP 4 — EMAIL CONTENT
# ─────────────────────────────────────────────
st.markdown("""
<div class="step-card">
  <div class="step-header">
    <div class="step-num">04</div>
    <div>
      <div class="step-title">Compose Your Email</div>
      <div class="step-desc">Write the message every participant will receive</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

email_subject = st.text_input("Subject Line", value="Your Certificate 🏆")
email_body    = st.text_area("Message Body", height=175, value="""Dear {name},

Congratulations on your outstanding participation!

Please find your personalized certificate attached.

With warm regards,
AutoCertify · Event Team""")

st.markdown("""
<div class="hint-pill">
  💡 Use <code>{name}</code> anywhere in the body — it will be replaced with each participant's actual name.
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STEP 5 — SEND
# ─────────────────────────────────────────────
st.markdown("""
<div class="step-card">
  <div class="step-header">
    <div class="step-num">05</div>
    <div>
      <div class="step-title">Launch Distribution</div>
      <div class="step-desc">AutoCertify generates and emails every certificate automatically</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

ready = bool(csv_file and template_pdf and sender_email and app_password and data is not None)

if not ready:
    missing = []
    if not sender_email:  missing.append("Gmail address")
    if not app_password:  missing.append("App password")
    if not csv_file:      missing.append("CSV file")
    if not template_pdf:  missing.append("Certificate PDF")
    st.warning(f"⚠️  Still needed: **{', '.join(missing)}**")

if data is not None:
    t = len(data)
    est_min = (t * delay) // 60
    est_sec = (t * delay) % 60
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-pill">👥 <b>{t}</b> participants</div>
      <div class="stat-pill">⏱️ ~<b>{est_min}m {est_sec}s</b> estimated</div>
      <div class="stat-pill">📨 <b>1</b> cert each</div>
      <div class="stat-pill">✉️ <b>Gmail</b> SMTP</div>
    </div>
    """, unsafe_allow_html=True)

send_clicked = st.button("🚀  LAUNCH — Send All Certificates", disabled=not ready, type="primary")


# ─────────────────────────────────────────────
# SEND LOGIC
# ─────────────────────────────────────────────
if send_clicked:

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(template_pdf.read())
        template_path = tmp.name

    output_folder = tempfile.mkdtemp()
    overlay_path  = os.path.join(output_folder, "overlay.pdf")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family:"Bebas Neue",sans-serif;
                font-size:clamp(1rem,3vw,1.3rem);letter-spacing:0.15em;
                color:#f5c842;margin-bottom:0.8rem;'>
      ⚡ LIVE DISTRIBUTION FEED
    </div>""", unsafe_allow_html=True)

    with st.spinner("Connecting to Gmail SMTP..."):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, app_password)
            st.success("✅ Secure Gmail connection established")
        except Exception as e:
            st.error(f"❌ Gmail login failed: {e}")
            st.stop()

    total           = len(data)
    progress_bar    = st.progress(0)
    status_text     = st.empty()
    log_placeholder = st.empty()
    logs = []; count = failed = 0

    for index, row in data.iterrows():
        try:
            name  = str(row[name_col]).strip()
            dept  = str(row[dept_col]).strip()
            email = str(row[email_col]).strip()

            if "@" not in email or "." not in email.split("@")[-1]:
                logs.append(f"⚠  Skipped · {name} · invalid email: '{email}'")
                failed += 1
                continue

            c  = canvas.Canvas(overlay_path, pagesize=landscape(A4))
            pw = landscape(A4)[0]

            c.setFont("Helvetica-Bold", name_size)
            tw = c.stringWidth(name, "Helvetica-Bold", name_size)
            c.drawString(pw/2 - tw/2 if center_name else name_x, name_y, name)

            c.setFont("Helvetica", dept_size)
            tw = c.stringWidth(dept, "Helvetica", dept_size)
            c.drawString(pw/2 - tw/2 if center_dept else dept_x, dept_y, dept)
            c.save()

            tr = PdfReader(template_path); ov = PdfReader(overlay_path)
            wr = PdfWriter(); pg = tr.pages[0]
            pg.merge_page(ov.pages[0]); wr.add_page(pg)

            safe = "".join(ch for ch in name if ch.isalnum() or ch in (" ","_")).rstrip()
            cert_path = os.path.join(output_folder, f"{safe}.pdf")
            with open(cert_path, "wb") as f: wr.write(f)

            msg = MIMEMultipart()
            msg['From'], msg['To'], msg['Subject'] = sender_email, email, email_subject
            msg.attach(MIMEText(email_body.replace("{name}", name), "plain"))

            with open(cert_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read()); encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={safe}.pdf")
                msg.attach(part)

            server.sendmail(sender_email, email, msg.as_string())
            count += 1
            logs.append(f"✅  {name}  →  {email}")

        except Exception as e:
            failed += 1
            logs.append(f"❌  Row {index}  →  {str(e)[:80]}")

        progress_bar.progress((index + 1) / total)
        status_text.markdown(
            f'<div class="live-status"><span class="live-dot"></span>'
            f'Processing <b style="color:#f5c842">{index+1}/{total}</b>'
            f' &nbsp;·&nbsp; <b style="color:#4ade80">✅ {count}</b>'
            f' &nbsp;·&nbsp; <b style="color:#f87171">❌ {failed}</b></div>',
            unsafe_allow_html=True
        )
        log_placeholder.markdown(
            '<div class="log-box">' + '\n'.join(logs[-14:]) + '</div>',
            unsafe_allow_html=True
        )
        time.sleep(delay)

    server.quit()
    st.balloons()

    st.markdown(f"""
    <div class="success-banner">
      <span class="success-trophy">🏆</span>
      <div class="success-title">Mission Complete</div>
      <div class="success-sub">{count} certificates delivered &nbsp;·&nbsp; {failed} failed</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 Full Distribution Log"):
        st.markdown('<div class="log-box">' + '\n'.join(logs) + '</div>', unsafe_allow_html=True)
