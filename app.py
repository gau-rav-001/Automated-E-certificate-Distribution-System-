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

st.set_page_config(
    page_title="AutoCertify",
    page_icon="🎖️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

/* ═══════════════════════════════════════════════
   VARIABLES
═══════════════════════════════════════════════ */
:root {
  --navy:     #050d1a;
  --navy2:    #071224;
  --navy3:    #0a1a35;
  --cyan:     #00d4ff;
  --cyan2:    #00b8e6;
  --cyan-dim: rgba(0,212,255,0.15);
  --coral:    #ff4f6d;
  --coral2:   #ff2d50;
  --violet:   #7b5ea7;
  --violet2:  #9d7fd4;
  --snow:     #f0f8ff;
  --snow-dim: rgba(240,248,255,0.55);
  --glass:    rgba(255,255,255,0.04);
  --glass2:   rgba(255,255,255,0.08);
  --border:   rgba(0,212,255,0.2);
  --border2:  rgba(0,212,255,0.4);

  --fs-display: clamp(3rem, 9vw, 7.5rem);
  --fs-h2:      clamp(1rem, 2.5vw, 1.18rem);
  --fs-body:    clamp(0.83rem, 1.8vw, 0.95rem);
  --fs-label:   clamp(0.68rem, 1.5vw, 0.78rem);
  --fs-mono:    clamp(0.62rem, 1.3vw, 0.72rem);
}

/* ═══════════════════════════════════════════════
   KEYFRAMES
═══════════════════════════════════════════════ */
@keyframes meshMove {
  0%   { transform: translate(0%,    0%)    rotate(0deg);   }
  25%  { transform: translate(3%,   -4%)    rotate(90deg);  }
  50%  { transform: translate(-2%,   3%)    rotate(180deg); }
  75%  { transform: translate(-4%,  -2%)    rotate(270deg); }
  100% { transform: translate(0%,    0%)    rotate(360deg); }
}
@keyframes orb1 {
  0%,100% { transform: translate(0,0) scale(1); opacity:.6; }
  50%     { transform: translate(60px,-40px) scale(1.15); opacity:.9; }
}
@keyframes orb2 {
  0%,100% { transform: translate(0,0) scale(1); opacity:.5; }
  50%     { transform: translate(-50px,30px) scale(0.85); opacity:.8; }
}
@keyframes orb3 {
  0%,100% { transform: translate(0,0) scale(1); opacity:.4; }
  50%     { transform: translate(30px,50px) scale(1.2); opacity:.7; }
}
@keyframes shimmerH {
  0%   { background-position: -300% center; }
  100% { background-position:  300% center; }
}
@keyframes typewriter {
  from { width: 0; }
  to   { width: 100%; }
}
@keyframes blink {
  0%,100% { border-color: var(--cyan); }
  50%      { border-color: transparent; }
}
@keyframes fadeUp {
  from { opacity:0; transform:translateY(32px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes fadeLeft {
  from { opacity:0; transform:translateX(-24px); }
  to   { opacity:1; transform:translateX(0); }
}
@keyframes glowPulse {
  0%,100% { box-shadow: 0 0 20px rgba(0,212,255,0.25), 0 0 60px rgba(0,212,255,0.08); }
  50%     { box-shadow: 0 0 40px rgba(0,212,255,0.5),  0 0 100px rgba(0,212,255,0.15); }
}
@keyframes glowPulseC {
  0%,100% { box-shadow: 0 0 20px rgba(255,79,109,0.25); }
  50%     { box-shadow: 0 0 40px rgba(255,79,109,0.55); }
}
@keyframes scanLine {
  0%   { top: -4px; }
  100% { top: calc(100% + 4px); }
}
@keyframes rotateBorder {
  from { --angle: 0deg; }
  to   { --angle: 360deg; }
}
@keyframes float {
  0%,100% { transform: translateY(0px) rotate(0deg); }
  33%     { transform: translateY(-14px) rotate(2deg); }
  66%     { transform: translateY(-7px) rotate(-1deg); }
}
@keyframes badgePop {
  0%   { transform: scale(0.7); opacity:0; }
  70%  { transform: scale(1.05); }
  100% { transform: scale(1); opacity:1; }
}
@keyframes progressShimmer {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}
@keyframes dotPulse {
  0%,100% { transform:scale(1);   opacity:1; }
  50%     { transform:scale(1.6); opacity:0.6; }
}
@keyframes successReveal {
  0%   { clip-path: inset(0 100% 0 0); }
  100% { clip-path: inset(0 0% 0 0); }
}
@keyframes particleDrift {
  0%   { transform:translateY(0)   translateX(0)   opacity:0;   }
  10%  { opacity:1; }
  90%  { opacity:1; }
  100% { transform:translateY(-120px) translateX(20px) opacity:0; }
}
@keyframes countIn {
  from { opacity:0; transform:translateY(10px); }
  to   { opacity:1; transform:translateY(0); }
}
@keyframes spinY {
  from { transform: rotateY(0deg); }
  to   { transform: rotateY(360deg); }
}

/* ═══════════════════════════════════════════════
   GLOBAL
═══════════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] {
  font-family: 'Plus Jakarta Sans', sans-serif;
  background: var(--navy);
  color: var(--snow);
}
#MainMenu, footer, header { visibility: hidden; }
.block-container {
  padding: clamp(0.5rem,2vw,1.5rem) clamp(0.6rem,3vw,2.5rem) 5rem !important;
  max-width: 1320px !important;
  width: 100% !important;
  position: relative;
  z-index: 1;
}

/* ═══════════════════════════════════════════════
   ANIMATED MESH BACKGROUND
═══════════════════════════════════════════════ */
[data-testid="stAppViewContainer"] {
  background: var(--navy);
  min-height: 100vh;
  overflow-x: hidden;
  position: relative;
}

/* Orb 1 — cyan */
[data-testid="stAppViewContainer"]::before {
  content: '';
  position: fixed;
  width: clamp(400px,60vw,800px);
  height: clamp(400px,60vw,800px);
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0,212,255,0.18) 0%, transparent 70%);
  top: -20%; left: -15%;
  animation: orb1 12s ease-in-out infinite;
  pointer-events: none;
  z-index: 0;
}
/* Orb 2 — coral */
[data-testid="stAppViewContainer"]::after {
  content: '';
  position: fixed;
  width: clamp(300px,50vw,700px);
  height: clamp(300px,50vw,700px);
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,79,109,0.14) 0%, transparent 70%);
  bottom: -15%; right: -10%;
  animation: orb2 15s ease-in-out infinite;
  pointer-events: none;
  z-index: 0;
}

/* Orb 3 — violet (injected via HTML) */
.bg-orb3 {
  position: fixed;
  width: clamp(250px,40vw,500px);
  height: clamp(250px,40vw,500px);
  border-radius: 50%;
  background: radial-gradient(circle, rgba(123,94,167,0.16) 0%, transparent 70%);
  top: 40%; right: 20%;
  animation: orb3 18s ease-in-out infinite;
  pointer-events: none;
  z-index: 0;
}

/* Grid overlay */
.grid-overlay {
  position: fixed;
  inset: 0;
  background-image:
    linear-gradient(rgba(0,212,255,0.035) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,212,255,0.035) 1px, transparent 1px);
  background-size: clamp(30px,5vw,60px) clamp(30px,5vw,60px);
  pointer-events: none;
  z-index: 0;
}

/* ═══════════════════════════════════════════════
   SIDEBAR (hidden but styled)
═══════════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: var(--navy2) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: var(--snow) !important; }

/* ═══════════════════════════════════════════════
   HERO
═══════════════════════════════════════════════ */
.hero-section {
  position: relative;
  padding: clamp(2.5rem,6vw,5rem) 0 clamp(1.5rem,4vw,3rem);
  text-align: center;
  animation: fadeUp 1s cubic-bezier(0.16,1,0.3,1) both;
  z-index: 1;
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  background: rgba(0,212,255,0.08);
  border: 1px solid rgba(0,212,255,0.3);
  border-radius: 50px;
  padding: 0.35rem 1.1rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: var(--fs-mono);
  letter-spacing: 0.18em;
  color: var(--cyan);
  text-transform: uppercase;
  margin-bottom: 1.5rem;
  animation: badgePop 0.7s 0.2s both;
}
.hero-eyebrow::before {
  content: '';
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--cyan);
  animation: dotPulse 1.5s ease-in-out infinite;
}

.hero-title {
  font-family: 'Playfair Display', serif;
  font-weight: 900;
  font-size: var(--fs-display);
  line-height: 0.92;
  letter-spacing: -0.02em;
  margin-bottom: 0.5rem;
  animation: fadeLeft 0.9s 0.3s both;
  position: relative;
  display: inline-block;
}
.hero-title .word-auto {
  display: inline-block;
  background: linear-gradient(135deg, var(--snow) 0%, rgba(240,248,255,0.8) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-title .word-certify {
  display: inline-block;
  background: linear-gradient(135deg, var(--cyan) 0%, var(--violet2) 50%, var(--coral) 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: shimmerH 4s linear 1s infinite;
  font-style: italic;
}

.hero-sub {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: clamp(0.95rem,2.5vw,1.2rem);
  font-weight: 300;
  color: var(--snow-dim);
  max-width: 520px;
  margin: 1rem auto 2rem;
  line-height: 1.65;
  animation: fadeUp 0.9s 0.5s both;
}

.hero-chips {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: clamp(0.4rem,1.5vw,0.8rem);
  flex-wrap: wrap;
  animation: fadeUp 0.9s 0.7s both;
}
.chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: var(--glass);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 50px;
  padding: 0.38rem clamp(0.7rem,2vw,1.1rem);
  font-size: clamp(0.72rem,1.8vw,0.82rem);
  font-weight: 500;
  color: var(--snow-dim);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  cursor: default;
}
.chip:hover {
  background: rgba(0,212,255,0.1);
  border-color: var(--border2);
  color: var(--cyan);
  transform: translateY(-2px);
}
.chip-icon { font-size: 0.85em; }

/* Decorative line */
.hero-line {
  width: 100%; height: 1px;
  background: linear-gradient(90deg, transparent, var(--cyan), var(--violet2), var(--coral), transparent);
  margin: clamp(1.5rem,4vw,3rem) 0;
  position: relative;
  opacity: 0.6;
}

/* ═══════════════════════════════════════════════
   SECTION LABEL
═══════════════════════════════════════════════ */
.section-label {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  margin-bottom: clamp(0.8rem,2vw,1.2rem);
}
.section-num {
  width: clamp(32px,4vw,40px);
  height: clamp(32px,4vw,40px);
  border-radius: 10px;
  background: linear-gradient(135deg, var(--cyan), var(--violet2));
  display: flex; align-items: center; justify-content: center;
  font-family: 'JetBrains Mono', monospace;
  font-size: clamp(0.65rem,1.4vw,0.78rem);
  font-weight: 700;
  color: var(--navy);
  box-shadow: 0 4px 20px rgba(0,212,255,0.4);
  flex-shrink: 0;
}
.section-title {
  font-family: 'Plus Jakarta Sans', sans-serif;
  font-size: var(--fs-h2);
  font-weight: 800;
  color: var(--snow);
  letter-spacing: -0.02em;
}
.section-desc {
  font-size: clamp(0.7rem,1.5vw,0.78rem);
  color: rgba(240,248,255,0.38);
  font-weight: 400;
  margin-top: 0.1rem;
}

/* ═══════════════════════════════════════════════
   GLASS CARDS
═══════════════════════════════════════════════ */
.glass-card {
  position: relative;
  background: linear-gradient(145deg, rgba(255,255,255,0.055) 0%, rgba(255,255,255,0.02) 100%);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: clamp(16px,2.5vw,24px);
  padding: clamp(1.3rem,3.5vw,2.2rem) clamp(1.1rem,3vw,2.2rem);
  margin-bottom: clamp(0.8rem,2vw,1.4rem);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  overflow: hidden;
  transition: transform 0.4s cubic-bezier(0.16,1,0.3,1), box-shadow 0.4s ease, border-color 0.3s ease;
  animation: fadeUp 0.8s both;
  z-index: 1;
}
.glass-card::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(0,212,255,0.6), rgba(123,94,167,0.4), transparent);
}
/* Corner glow */
.glass-card::after {
  content: '';
  position: absolute;
  top: -60px; right: -60px;
  width: 160px; height: 160px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(0,212,255,0.08), transparent 70%);
  pointer-events: none;
}
@media (hover: hover) {
  .glass-card:hover {
    transform: perspective(1200px) rotateX(-0.8deg) rotateY(0.8deg) translateY(-5px);
    box-shadow: 0 24px 60px rgba(0,0,0,0.4), 0 0 0 1px rgba(0,212,255,0.2), 0 0 50px rgba(0,212,255,0.06);
    border-color: rgba(0,212,255,0.25);
  }
}

/* Gmail card — special coral accent */
.glass-card.gmail-card::before {
  background: linear-gradient(90deg, transparent, rgba(0,212,255,0.5), rgba(255,79,109,0.5), transparent);
}
.glass-card.gmail-card::after {
  background: radial-gradient(circle, rgba(255,79,109,0.08), transparent 70%);
}

/* Animation delays */
.glass-card:nth-child(1) { animation-delay: 0.05s; }
.glass-card:nth-child(2) { animation-delay: 0.12s; }
.glass-card:nth-child(3) { animation-delay: 0.19s; }
.glass-card:nth-child(4) { animation-delay: 0.26s; }
.glass-card:nth-child(5) { animation-delay: 0.33s; }
.glass-card:nth-child(6) { animation-delay: 0.40s; }

/* ═══════════════════════════════════════════════
   INPUTS  — NEON GLOW ON FOCUS
═══════════════════════════════════════════════ */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 12px !important;
  color: var(--snow) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: var(--fs-body) !important;
  min-height: 46px !important;
  padding: 0.65rem 1rem !important;
  transition: all 0.3s ease !important;
  caret-color: var(--cyan) !important;
  backdrop-filter: blur(8px) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stNumberInput"] input:focus {
  border-color: rgba(0,212,255,0.6) !important;
  box-shadow: 0 0 0 3px rgba(0,212,255,0.12), 0 0 30px rgba(0,212,255,0.08) !important;
  background: rgba(0,212,255,0.05) !important;
}

/* ── Labels ── */
label, [data-testid="stWidgetLabel"] p {
  color: rgba(240,248,255,0.55) !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: var(--fs-label) !important;
  font-weight: 500 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] > div > div {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: 12px !important;
  color: var(--snow) !important;
  min-height: 46px !important;
  backdrop-filter: blur(8px) !important;
  transition: all 0.3s ease !important;
}
[data-testid="stSelectbox"] > div > div:hover {
  border-color: rgba(0,212,255,0.4) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
  background: rgba(255,255,255,0.03) !important;
  border: 1.5px dashed rgba(0,212,255,0.25) !important;
  border-radius: 16px !important;
  transition: all 0.3s ease !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: rgba(0,212,255,0.55) !important;
  background: rgba(0,212,255,0.04) !important;
  box-shadow: 0 0 30px rgba(0,212,255,0.06) !important;
}

/* ═══════════════════════════════════════════════
   LAUNCH BUTTON
═══════════════════════════════════════════════ */
.stButton > button {
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: clamp(0.9rem,2.5vw,1.05rem) !important;
  font-weight: 700 !important;
  letter-spacing: 0.04em !important;
  background: linear-gradient(135deg, var(--cyan) 0%, var(--violet2) 50%, var(--coral) 100%) !important;
  background-size: 200% 100% !important;
  color: var(--navy) !important;
  border: none !important;
  border-radius: 14px !important;
  padding: clamp(0.75rem,2vw,1rem) 2.5rem !important;
  width: 100% !important;
  min-height: 54px !important;
  transition: all 0.4s cubic-bezier(0.16,1,0.3,1) !important;
  box-shadow: 0 4px 30px rgba(0,212,255,0.3), 0 0 0 1px rgba(0,212,255,0.15) !important;
  position: relative !important;
  overflow: hidden !important;
}
@media (hover: hover) {
  .stButton > button:hover {
    background-position: right center !important;
    transform: translateY(-3px) scale(1.015) !important;
    box-shadow: 0 14px 45px rgba(0,212,255,0.45), 0 0 0 1px rgba(0,212,255,0.3) !important;
    color: white !important;
  }
}
.stButton > button:active {
  transform: scale(0.98) !important;
}
.stButton > button:disabled {
  background: rgba(255,255,255,0.06) !important;
  color: rgba(240,248,255,0.2) !important;
  box-shadow: none !important;
}

/* ═══════════════════════════════════════════════
   PROGRESS BAR
═══════════════════════════════════════════════ */
[data-testid="stProgress"] > div {
  background: rgba(255,255,255,0.06) !important;
  border-radius: 50px !important;
  height: 10px !important;
  border: 1px solid rgba(0,212,255,0.12) !important;
  overflow: hidden !important;
}
[data-testid="stProgress"] > div > div {
  background: linear-gradient(90deg, var(--cyan), var(--violet2), var(--coral)) !important;
  background-size: 200% 100% !important;
  border-radius: 50px !important;
  animation: progressShimmer 2s linear infinite !important;
  box-shadow: 0 0 16px rgba(0,212,255,0.5) !important;
}

/* ═══════════════════════════════════════════════
   SLIDER
═══════════════════════════════════════════════ */
[data-testid="stSlider"] [role="slider"] {
  background: var(--cyan) !important;
  box-shadow: 0 0 14px rgba(0,212,255,0.6) !important;
  border: 2px solid var(--navy) !important;
}

/* ═══════════════════════════════════════════════
   STAT PILLS
═══════════════════════════════════════════════ */
.stat-row {
  display: flex; gap: clamp(0.4rem,1.2vw,0.7rem);
  flex-wrap: wrap;
  margin: 0.8rem 0 1.2rem;
}
.stat-pill {
  display: inline-flex; align-items: center; gap: 0.35rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 50px;
  padding: clamp(0.3rem,1vw,0.4rem) clamp(0.65rem,1.5vw,0.95rem);
  font-size: clamp(0.7rem,1.7vw,0.8rem);
  font-weight: 500;
  color: var(--snow-dim);
  white-space: nowrap;
  transition: all 0.25s ease;
  backdrop-filter: blur(6px);
}
.stat-pill:hover {
  background: rgba(0,212,255,0.1);
  border-color: rgba(0,212,255,0.3);
  color: var(--cyan);
  transform: translateY(-2px);
}
.stat-pill b { color: var(--cyan); }

/* ═══════════════════════════════════════════════
   FIELD GROUP
═══════════════════════════════════════════════ */
.fgl {
  font-family: 'JetBrains Mono', monospace;
  font-size: clamp(0.58rem,1.3vw,0.67rem);
  font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
  padding: 0.22rem 0.65rem; border-radius: 6px;
  display: inline-block; margin-bottom: 0.6rem;
}
.fgl-cyan   { background:rgba(0,212,255,0.1);   border:1px solid rgba(0,212,255,0.3);   color:var(--cyan); }
.fgl-coral  { background:rgba(255,79,109,0.1);   border:1px solid rgba(255,79,109,0.3);  color:var(--coral); }
.fgl-violet { background:rgba(123,94,167,0.15);  border:1px solid rgba(157,127,212,0.3); color:var(--violet2); }

/* ═══════════════════════════════════════════════
   HINT
═══════════════════════════════════════════════ */
.hint {
  display: inline-flex; align-items: center; gap: 0.45rem; flex-wrap: wrap;
  background: rgba(0,212,255,0.05);
  border: 1px dashed rgba(0,212,255,0.2);
  border-radius: 10px;
  padding: clamp(0.4rem,1vw,0.5rem) clamp(0.65rem,1.5vw,1rem);
  font-size: clamp(0.7rem,1.7vw,0.77rem);
  color: rgba(240,248,255,0.42); margin-top: 0.5rem;
}
.hint code {
  background: rgba(0,212,255,0.15); color: var(--cyan);
  padding: 0.1rem 0.4rem; border-radius: 5px;
  font-family: 'JetBrains Mono', monospace; font-size: 0.82em;
}

/* ═══════════════════════════════════════════════
   INFO TOOLTIP
═══════════════════════════════════════════════ */
.info-steps {
  font-size: clamp(0.72rem,1.6vw,0.8rem);
  color: rgba(240,248,255,0.4);
  line-height: 2.1;
}
.info-steps span { color: var(--cyan); font-weight: 600; }

/* ═══════════════════════════════════════════════
   LOG
═══════════════════════════════════════════════ */
.log-box {
  background: rgba(5,13,26,0.8);
  border: 1px solid rgba(0,212,255,0.12);
  border-radius: 14px;
  padding: 1rem 1.2rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: clamp(0.66rem,1.5vw,0.74rem);
  line-height: 2;
  color: rgba(0,212,255,0.75);
  max-height: 240px;
  overflow-y: auto;
  white-space: pre-wrap;
  backdrop-filter: blur(12px);
}
.log-box::-webkit-scrollbar { width: 3px; }
.log-box::-webkit-scrollbar-thumb { background: rgba(0,212,255,0.3); border-radius: 4px; }

/* ═══════════════════════════════════════════════
   LIVE STATUS
═══════════════════════════════════════════════ */
.live-status {
  display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;
  font-size: clamp(0.76rem,1.9vw,0.88rem);
  color: var(--snow-dim); margin: 0.7rem 0;
}
.live-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--cyan); flex-shrink: 0;
  animation: dotPulse 1.4s ease-in-out infinite;
}

/* ═══════════════════════════════════════════════
   SUCCESS
═══════════════════════════════════════════════ */
.success-banner {
  position: relative;
  background: linear-gradient(145deg, rgba(0,212,255,0.08), rgba(123,94,167,0.06), rgba(255,79,109,0.05));
  border: 1px solid rgba(0,212,255,0.25);
  border-radius: clamp(16px,2.5vw,24px);
  padding: clamp(1.8rem,5vw,3rem) clamp(1.2rem,3vw,2.5rem);
  text-align: center; overflow: hidden;
  animation: fadeUp 0.9s cubic-bezier(0.16,1,0.3,1) both;
  backdrop-filter: blur(20px);
}
.success-banner::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, transparent, var(--cyan), var(--violet2), var(--coral), transparent);
}
.success-icon {
  font-size: clamp(2.5rem,7vw,4rem);
  display: block; margin-bottom: 0.8rem;
  animation: float 3.5s ease-in-out infinite;
  filter: drop-shadow(0 0 24px rgba(0,212,255,0.4));
}
.success-title {
  font-family: 'Playfair Display', serif;
  font-weight: 900;
  font-size: clamp(2rem,5.5vw,3.2rem);
  background: linear-gradient(135deg, var(--cyan), var(--violet2), var(--coral));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
  margin-bottom: 0.5rem;
}
.success-sub {
  font-size: clamp(0.85rem,2.2vw,1rem);
  color: var(--snow-dim);
  font-weight: 300;
}

/* ═══════════════════════════════════════════════
   STATUS BADGE
═══════════════════════════════════════════════ */
.status-badge {
  display: inline-flex; align-items: center; gap: 0.5rem;
  border-radius: 50px;
  padding: 0.4rem 1rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: clamp(0.7rem,1.5vw,0.78rem);
  font-weight: 500;
  margin-top: 0.5rem;
}
.status-badge.ready {
  background: rgba(0,212,255,0.1);
  border: 1px solid rgba(0,212,255,0.3);
  color: var(--cyan);
  animation: glowPulse 2.5s ease-in-out infinite;
}
.status-badge.warn {
  background: rgba(255,79,109,0.08);
  border: 1px solid rgba(255,79,109,0.25);
  color: var(--coral);
}

/* ═══════════════════════════════════════════════
   MISC
═══════════════════════════════════════════════ */
hr {
  border: none !important; height: 1px !important;
  background: linear-gradient(90deg, transparent, rgba(0,212,255,0.2), rgba(123,94,167,0.2), transparent) !important;
  margin: clamp(1rem,3vw,2rem) 0 !important;
}
[data-testid="stCheckbox"] span { color: var(--snow-dim) !important; }
.stCaption, [data-testid="stCaptionContainer"] {
  color: rgba(240,248,255,0.35) !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
}
[data-testid="stAlert"] { border-radius: 14px !important; backdrop-filter: blur(10px) !important; }
[data-testid="stDataFrame"] { border-radius: 14px !important; border: 1px solid rgba(0,212,255,0.12) !important; }
[data-testid="stExpander"] {
  border: 1px solid rgba(255,255,255,0.09) !important;
  border-radius: 14px !important;
  background: rgba(255,255,255,0.02) !important;
  backdrop-filter: blur(8px) !important;
}

/* ═══════════════════════════════════════════════
   RESPONSIVE
═══════════════════════════════════════════════ */
@media (max-width: 480px) {
  .block-container { padding: 0.5rem 0.65rem 3.5rem !important; }
  .hero-section { padding: 1.5rem 0 1rem; }
  .glass-card { padding: 1.1rem 0.9rem; border-radius: 16px; }
  .log-box { max-height: 160px; }
  .hero-chips { justify-content: center; }
  [data-testid="stAppViewContainer"]::before,
  [data-testid="stAppViewContainer"]::after { display: none; }
}
@media (max-width: 360px) {
  .hero-title { font-size: 2.6rem; }
  .chip { font-size: 0.68rem; padding: 0.28rem 0.6rem; }
}
</style>
""", unsafe_allow_html=True)

# ── Background decoration ──
st.markdown("""
<div class="bg-orb3"></div>
<div class="grid-overlay"></div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════
# HERO
# ═══════════════════════════════════════
st.markdown("""
<div class="hero-section">
  <div class="hero-eyebrow">Certificate Automation Platform</div>
  <div class="hero-title">
    <span class="word-auto">Auto</span><span class="word-certify">Certify</span>
  </div>
  <div class="hero-sub">
    Generate personalized certificates &amp; deliver them via email — beautifully automated, effortlessly simple.
  </div>
  <div class="hero-chips">
    <div class="chip"><span class="chip-icon">📋</span> CSV Driven</div>
    <div class="chip"><span class="chip-icon">📄</span> PDF Overlay</div>
    <div class="chip"><span class="chip-icon">📧</span> Gmail SMTP</div>
    <div class="chip"><span class="chip-icon">⚡</span> Zero Code</div>
    <div class="chip"><span class="chip-icon">🔒</span> Secure</div>
  </div>
</div>
<div class="hero-line"></div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════
# GMAIL CONFIG CARD
# ═══════════════════════════════════════
st.markdown("""
<div class="glass-card gmail-card">
  <div class="section-label">
    <div class="section-num">✉</div>
    <div>
      <div class="section-title">Gmail Configuration</div>
      <div class="section-desc">Credentials are only used for this session — never stored</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

gc1, gc2 = st.columns(2)
with gc1:
    sender_email = st.text_input("📧  Gmail Address", placeholder="you@gmail.com")
with gc2:
    app_password = st.text_input("🔑  App Password", type="password", placeholder="xxxx xxxx xxxx xxxx")

if sender_email and app_password:
    st.markdown(f"""
    <div class="status-badge ready">
      <span style="width:7px;height:7px;border-radius:50%;background:var(--cyan);
                   animation:dotPulse 1.5s infinite;display:inline-block;"></span>
      Ready · {sender_email}
    </div>
    """, unsafe_allow_html=True)

with st.expander("❓  How to create a Gmail App Password"):
    st.markdown("""
    <div class="info-steps">
    <span>1 ·</span> Go to <b style="color:var(--cyan)">myaccount.google.com</b><br>
    <span>2 ·</span> Security → 2-Step Verification → turn ON<br>
    <span>3 ·</span> Search <b style="color:var(--cyan)">"App Passwords"</b> in the search bar<br>
    <span>4 ·</span> Select app: <b style="color:var(--cyan)">Mail</b> → Generate<br>
    <span>5 ·</span> Copy the 16-character code and paste above
    </div>
    """, unsafe_allow_html=True)

delay_c, _ = st.columns([1, 2])
with delay_c:
    delay = st.slider("⏱️  Delay between emails (sec)", 1, 10, 2)

st.markdown("<hr>", unsafe_allow_html=True)

# ═══════════════════════════════════════
# STEP 1 — UPLOAD
# ═══════════════════════════════════════
st.markdown("""
<div class="glass-card">
  <div class="section-label">
    <div class="section-num">01</div>
    <div>
      <div class="section-title">Upload Files</div>
      <div class="section-desc">Participant list in CSV · Certificate template in PDF</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

u1, u2 = st.columns(2)
with u1:
    csv_file = st.file_uploader("📋  Participant List (CSV)", type=["csv"])
with u2:
    template_pdf = st.file_uploader("📄  Certificate Template (PDF)", type=["pdf"])

# ═══════════════════════════════════════
# STEP 2 — MAP COLUMNS
# ═══════════════════════════════════════
data = None
name_col = dept_col = email_col = None

if csv_file:
    st.markdown("""
    <div class="glass-card">
      <div class="section-label">
        <div class="section-num">02</div>
        <div>
          <div class="section-title">Map CSV Columns</div>
          <div class="section-desc">Tell AutoCertify which column holds which data</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    try:
        data = pd.read_csv(csv_file, encoding="cp1252")
        data.columns = data.columns.str.strip()
        st.caption(f"✦ Preview — {len(data)} participants detected")
        st.dataframe(data.head(4), use_container_width=True, hide_index=True)

        columns = data.columns.tolist()
        m1, m2, m3 = st.columns(3)
        with m1: name_col  = st.selectbox("👤  Name Column",       columns)
        with m2: dept_col  = st.selectbox("🏢  Department Column", columns)
        with m3: email_col = st.selectbox("📧  Email Column",      columns)
    except Exception as e:
        st.error(f"Could not read CSV: {e}")

# ═══════════════════════════════════════
# STEP 3 — TEXT POSITION
# ═══════════════════════════════════════
st.markdown("""
<div class="glass-card">
  <div class="section-label">
    <div class="section-num">03</div>
    <div>
      <div class="section-title">Text Position on Certificate</div>
      <div class="section-desc">X = from left edge &nbsp;·&nbsp; Y = from bottom &nbsp;·&nbsp; Defaults suit A4 landscape</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

p1, p2 = st.columns(2)
with p1:
    st.markdown('<span class="fgl fgl-cyan">✦ Name</span>', unsafe_allow_html=True)
    na, nb, nc = st.columns(3)
    with na: name_x    = st.number_input("X",    value=250, step=5, key="nx")
    with nb: name_y    = st.number_input("Y",    value=223, step=5, key="ny")
    with nc: name_size = st.number_input("Size", value=14,  step=1, key="ns", min_value=6, max_value=72)
    center_name = st.checkbox("⬛ Center-align Name", value=False)

with p2:
    st.markdown('<span class="fgl fgl-coral">✦ Department</span>', unsafe_allow_html=True)
    da, db, dc = st.columns(3)
    with da: dept_x    = st.number_input("X",    value=185, step=5, key="dx")
    with db: dept_y    = st.number_input("Y",    value=198, step=5, key="dy")
    with dc: dept_size = st.number_input("Size", value=14,  step=1, key="ds", min_value=6, max_value=72)
    center_dept = st.checkbox("⬛ Center-align Dept", value=False)

# ═══════════════════════════════════════
# STEP 4 — EMAIL CONTENT
# ═══════════════════════════════════════
st.markdown("""
<div class="glass-card">
  <div class="section-label">
    <div class="section-num">04</div>
    <div>
      <div class="section-title">Compose Email</div>
      <div class="section-desc">Write the message every participant will receive with their certificate</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

email_subject = st.text_input("Subject Line", value="Your Certificate 🎖️")
email_body = st.text_area("Message Body", height=178, value="""Dear {name},

Congratulations on your outstanding participation!

Please find your personalized certificate attached to this email.

With warm regards,
AutoCertify · Event Team""")
st.markdown("""
<div class="hint">
  💡 Use <code>{name}</code> anywhere — it will be replaced with each participant's name automatically.
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════
# STEP 5 — LAUNCH
# ═══════════════════════════════════════
st.markdown("""
<div class="glass-card">
  <div class="section-label">
    <div class="section-num">05</div>
    <div>
      <div class="section-title">Launch Distribution</div>
      <div class="section-desc">AutoCertify generates and emails every certificate automatically</div>
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
    st.markdown(f"""
    <div class="status-badge warn">⚠ Still needed: {' · '.join(missing)}</div>
    """, unsafe_allow_html=True)
    st.write("")

if data is not None:
    t = len(data)
    est_min = (t * delay) // 60
    est_sec = (t * delay) % 60
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-pill">👥 <b>{t}</b> participants</div>
      <div class="stat-pill">⏱️ ~<b>{est_min}m {est_sec}s</b></div>
      <div class="stat-pill">📨 <b>1</b> cert each</div>
      <div class="stat-pill">✉️ <b>Gmail</b> SMTP</div>
    </div>
    """, unsafe_allow_html=True)

send_clicked = st.button("🚀  Launch — Send All Certificates", disabled=not ready, type="primary")

# ═══════════════════════════════════════
# SEND LOGIC
# ═══════════════════════════════════════
if send_clicked:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(template_pdf.read())
        template_path = tmp.name

    output_folder = tempfile.mkdtemp()
    overlay_path  = os.path.join(output_folder, "overlay.pdf")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:clamp(0.95rem,2.5vw,1.15rem);
                font-weight:800;letter-spacing:0.04em;color:var(--cyan);margin-bottom:0.9rem;">
      ⚡ Live Distribution Feed
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
            c.drawString(pw / 2 - tw / 2 if center_name else name_x, name_y, name)

            c.setFont("Helvetica", dept_size)
            tw = c.stringWidth(dept, "Helvetica", dept_size)
            c.drawString(pw / 2 - tw / 2 if center_dept else dept_x, dept_y, dept)
            c.save()

            tr = PdfReader(template_path); ov = PdfReader(overlay_path)
            wr = PdfWriter(); pg = tr.pages[0]
            pg.merge_page(ov.pages[0]); wr.add_page(pg)

            safe = "".join(ch for ch in name if ch.isalnum() or ch in (" ", "_")).rstrip()
            cert_path = os.path.join(output_folder, f"{safe}.pdf")
            with open(cert_path, "wb") as f:
                wr.write(f)

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
            f'Processing <b style="color:var(--cyan)">{index+1}/{total}</b>'
            f' &nbsp;·&nbsp; <b style="color:#4ade80">✅ {count} sent</b>'
            f' &nbsp;·&nbsp; <b style="color:var(--coral)">❌ {failed} failed</b></div>',
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
      <span class="success-icon">🎖️</span>
      <div class="success-title">Mission Accomplished</div>
      <div class="success-sub">
        <b style="color:var(--cyan)">{count}</b> certificates delivered with pride
        &nbsp;·&nbsp;
        <b style="color:var(--coral)">{failed}</b> failed
      </div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 Full Distribution Log"):
        st.markdown('<div class="log-box">' + '\n'.join(logs) + '</div>', unsafe_allow_html=True)
