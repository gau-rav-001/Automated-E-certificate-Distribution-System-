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
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# MASTER CSS + 3D ANIMATIONS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Clash+Display:wght@400;500;600;700&family=Cabinet+Grotesk:wght@300;400;500;700;800;900&family=Instrument+Serif:ital@0;1&family=Space+Mono:wght@400;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@200;300;400;500;600;700;900&display=swap');

/* ══════════════════════════════════════════
   CSS VARIABLES
══════════════════════════════════════════ */
:root {
  --gold:    #f5c842;
  --gold2:   #ffab00;
  --amber:   #ff6b35;
  --cream:   #fdf6e3;
  --ink:     #0d0a05;
  --ink2:    #1a1408;
  --ink3:    #251e10;
  --ink4:    #332c1a;
  --muted:   rgba(245,200,66,0.45);
  --glass:   rgba(245,200,66,0.06);
  --border:  rgba(245,200,66,0.18);
  --shadow:  rgba(245,200,66,0.25);
}

/* ══════════════════════════════════════════
   KEYFRAMES
══════════════════════════════════════════ */
@keyframes float3d {
  0%   { transform: perspective(800px) rotateX(8deg) rotateY(-6deg) translateY(0px); }
  33%  { transform: perspective(800px) rotateX(2deg) rotateY(6deg)  translateY(-12px); }
  66%  { transform: perspective(800px) rotateX(-4deg) rotateY(0deg) translateY(-6px); }
  100% { transform: perspective(800px) rotateX(8deg) rotateY(-6deg) translateY(0px); }
}

@keyframes shimmer {
  0%   { background-position: -200% center; }
  100% { background-position: 200% center; }
}

@keyframes particleFloat {
  0%   { transform: translateY(0) translateX(0) scale(1); opacity: 0.7; }
  50%  { transform: translateY(-30px) translateX(15px) scale(1.2); opacity: 1; }
  100% { transform: translateY(-60px) translateX(-10px) scale(0.8); opacity: 0; }
}

@keyframes rotateGlow {
  0%   { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@keyframes fadeSlideUp {
  0%   { opacity: 0; transform: translateY(30px); }
  100% { opacity: 1; transform: translateY(0); }
}

@keyframes fadeSlideLeft {
  0%   { opacity: 0; transform: translateX(-40px); }
  100% { opacity: 1; transform: translateX(0); }
}

@keyframes pulseGold {
  0%, 100% { box-shadow: 0 0 20px rgba(245,200,66,0.3), 0 0 60px rgba(245,200,66,0.1); }
  50%       { box-shadow: 0 0 40px rgba(245,200,66,0.6), 0 0 100px rgba(245,200,66,0.2); }
}

@keyframes scanLine {
  0%   { top: -10%; }
  100% { top: 110%; }
}

@keyframes borderDraw {
  0%   { stroke-dashoffset: 1000; }
  100% { stroke-dashoffset: 0; }
}

@keyframes logoReveal {
  0%   { clip-path: inset(0 100% 0 0); opacity: 0; }
  100% { clip-path: inset(0 0% 0 0); opacity: 1; }
}

@keyframes starTwinkle {
  0%, 100% { opacity: 0.2; transform: scale(0.8); }
  50%       { opacity: 1; transform: scale(1.4); }
}

@keyframes ribbonSlide {
  0%   { transform: translateX(-100%) skewX(-15deg); opacity: 0; }
  100% { transform: translateX(0) skewX(-15deg); opacity: 1; }
}

@keyframes countUp {
  0%   { transform: translateY(20px); opacity: 0; }
  100% { transform: translateY(0); opacity: 1; }
}

@keyframes spinSlow {
  from { transform: rotate(0deg); }
  to   { transform: rotate(360deg); }
}

@keyframes morphBlob {
  0%,100% { border-radius: 60% 40% 30% 70% / 60% 30% 70% 40%; }
  50%      { border-radius: 30% 60% 70% 40% / 50% 60% 30% 60%; }
}

/* ══════════════════════════════════════════
   GLOBAL RESET
══════════════════════════════════════════ */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"] {
  font-family: 'Outfit', sans-serif;
  background-color: var(--ink);
  color: var(--cream);
  scroll-behavior: smooth;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
  padding: 0 2.5rem 4rem 2.5rem !important;
  max-width: 1280px !important;
}

/* ══════════════════════════════════════════
   ANIMATED BACKGROUND CANVAS
══════════════════════════════════════════ */
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(ellipse 70% 50% at 15% 15%, rgba(245,200,66,0.10) 0%, transparent 55%),
    radial-gradient(ellipse 50% 40% at 85% 85%, rgba(255,107,53,0.08) 0%, transparent 50%),
    radial-gradient(ellipse 80% 60% at 50% 50%, rgba(13,10,5,0.95) 0%, transparent 80%),
    var(--ink);
  min-height: 100vh;
  overflow-x: hidden;
}

/* Stars */
[data-testid="stAppViewContainer"]::before {
  content: '✦ ✧ ★ ✦ ✧ ★ ✦ ✧ ✦ ★ ✧ ✦ ★ ✧ ✦ ✧ ★ ✦ ✧ ★ ✦';
  position: fixed;
  top: 8%;
  left: 0;
  width: 100%;
  font-size: 0.6rem;
  letter-spacing: 3.5rem;
  color: rgba(245,200,66,0.12);
  pointer-events: none;
  animation: starTwinkle 4s ease-in-out infinite;
  z-index: 0;
}

[data-testid="stAppViewContainer"]::after {
  content: '★ ✦ ✧ ✦ ★ ✧ ✦ ✧ ★ ✦ ✧ ✦ ✧ ★ ✦ ✧ ✦ ★ ✧ ✦ ✧';
  position: fixed;
  bottom: 12%;
  left: 2%;
  width: 100%;
  font-size: 0.5rem;
  letter-spacing: 4rem;
  color: rgba(245,200,66,0.08);
  pointer-events: none;
  animation: starTwinkle 6s ease-in-out infinite reverse;
  z-index: 0;
}

/* ══════════════════════════════════════════
   SIDEBAR
══════════════════════════════════════════ */
[data-testid="stSidebar"] {
  background: linear-gradient(160deg, #120f08 0%, #0d0a05 60%, #1a1408 100%) !important;
  border-right: 1px solid var(--border) !important;
  box-shadow: 4px 0 30px rgba(245,200,66,0.06) !important;
}
[data-testid="stSidebar"] * { color: var(--cream) !important; }
[data-testid="stSidebar"] [data-testid="stTextInput"] input,
[data-testid="stSidebar"] [data-testid="stNumberInput"] input {
  background: rgba(245,200,66,0.05) !important;
  border: 1px solid rgba(245,200,66,0.2) !important;
  border-radius: 8px !important;
  color: var(--cream) !important;
}

/* ══════════════════════════════════════════
   HERO SECTION
══════════════════════════════════════════ */
.hero-wrapper {
  position: relative;
  padding: 3.5rem 0 2rem 0;
  display: flex;
  align-items: center;
  gap: 4rem;
  animation: fadeSlideUp 0.9s cubic-bezier(0.16,1,0.3,1) both;
}

/* 3D Certificate Card */
.cert-3d-wrap {
  flex-shrink: 0;
  perspective: 900px;
}
.cert-3d {
  width: 220px;
  height: 155px;
  background: linear-gradient(135deg, #1e1808 0%, #2a2010 40%, #1a1408 100%);
  border: 1px solid rgba(245,200,66,0.35);
  border-radius: 12px;
  animation: float3d 7s ease-in-out infinite;
  position: relative;
  overflow: hidden;
  box-shadow:
    0 30px 80px rgba(0,0,0,0.7),
    0 0 0 1px rgba(245,200,66,0.1),
    inset 0 1px 0 rgba(245,200,66,0.2);
}
.cert-3d::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(245,200,66,0.08) 0%, transparent 60%, rgba(255,107,53,0.05) 100%);
}
/* Scan line effect */
.cert-3d::after {
  content: '';
  position: absolute;
  left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(245,200,66,0.4), transparent);
  animation: scanLine 3s linear infinite;
  z-index: 2;
}
.cert-inner {
  position: absolute;
  inset: 14px;
  border: 1px solid rgba(245,200,66,0.2);
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.cert-trophy {
  font-size: 2rem;
  filter: drop-shadow(0 0 12px rgba(245,200,66,0.6));
  animation: starTwinkle 2s ease-in-out infinite;
}
.cert-lines {
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: 70%;
}
.cert-line {
  height: 4px;
  border-radius: 4px;
  background: linear-gradient(90deg, rgba(245,200,66,0.5), rgba(245,200,66,0.15));
}
.cert-line.short { width: 60%; margin: 0 auto; }
.cert-seal {
  position: absolute;
  bottom: 14px; right: 14px;
  width: 32px; height: 32px;
  border: 2px solid rgba(245,200,66,0.5);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.8rem;
  animation: spinSlow 10s linear infinite;
}

/* Logo & Tagline */
.hero-text { flex: 1; }

.logo-badge {
  display: inline-block;
  background: linear-gradient(135deg, rgba(245,200,66,0.12), rgba(255,107,53,0.08));
  border: 1px solid rgba(245,200,66,0.3);
  border-radius: 50px;
  padding: 0.3rem 1rem;
  font-family: 'Space Mono', monospace;
  font-size: 0.65rem;
  letter-spacing: 0.2em;
  color: var(--gold);
  text-transform: uppercase;
  margin-bottom: 1rem;
  animation: fadeSlideLeft 0.7s 0.2s both;
}

.hero-title-main {
  font-family: 'Bebas Neue', sans-serif;
  font-size: clamp(3.5rem, 6vw, 6rem);
  letter-spacing: 0.06em;
  line-height: 0.95;
  background: linear-gradient(135deg, #f5c842 0%, #ffab00 30%, #fff4cc 55%, #f5c842 70%, #ff6b35 100%);
  background-size: 200% auto;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation:
    fadeSlideLeft 0.8s 0.3s both,
    shimmer 4s linear 1s infinite;
}

.hero-subtitle {
  font-family: 'Instrument Serif', serif;
  font-style: italic;
  font-size: 1.15rem;
  color: rgba(253,246,227,0.55);
  margin-top: 0.6rem;
  margin-bottom: 1.5rem;
  animation: fadeSlideLeft 0.8s 0.5s both;
  letter-spacing: 0.02em;
}

.hero-stats {
  display: flex;
  gap: 1.2rem;
  flex-wrap: wrap;
  animation: fadeSlideLeft 0.8s 0.7s both;
}
.hero-stat {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: var(--glass);
  border: 1px solid var(--border);
  border-radius: 50px;
  padding: 0.4rem 1rem;
  font-size: 0.78rem;
  font-weight: 500;
  color: rgba(253,246,227,0.7);
  backdrop-filter: blur(8px);
  transition: all 0.3s ease;
}
.hero-stat:hover {
  background: rgba(245,200,66,0.12);
  border-color: rgba(245,200,66,0.4);
  color: var(--gold);
  transform: translateY(-2px);
}
.hero-stat span { color: var(--gold); font-weight: 700; }

/* Gold divider */
.gold-divider {
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold), rgba(255,107,53,0.5), transparent);
  margin: 2rem 0;
  animation: fadeSlideUp 1s 0.9s both;
  position: relative;
}
.gold-divider::after {
  content: '✦';
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  background: var(--ink);
  padding: 0 0.8rem;
  color: var(--gold);
  font-size: 0.7rem;
}

/* ══════════════════════════════════════════
   STEP CARDS  (3-D tilt on hover)
══════════════════════════════════════════ */
.step-card {
  position: relative;
  background: linear-gradient(145deg, rgba(245,200,66,0.04) 0%, rgba(13,10,5,0.9) 100%);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 2rem 2.2rem;
  margin-bottom: 1.4rem;
  overflow: hidden;
  transition: transform 0.4s cubic-bezier(0.16,1,0.3,1), box-shadow 0.4s ease, border-color 0.3s ease;
  animation: fadeSlideUp 0.8s both;
  transform-style: preserve-3d;
}
.step-card:hover {
  transform: perspective(1000px) rotateX(-1deg) rotateY(1deg) translateY(-4px);
  box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(245,200,66,0.08);
  border-color: rgba(245,200,66,0.35);
}

/* Animated top border */
.step-card::before {
  content: '';
  position: absolute;
  top: 0; left: -100%; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold), rgba(255,107,53,0.7), transparent);
  transition: left 0.5s ease;
}
.step-card:hover::before { left: 0; }

/* Corner ornament */
.step-card::after {
  content: '';
  position: absolute;
  top: 0; right: 0;
  width: 60px; height: 60px;
  background: radial-gradient(circle at top right, rgba(245,200,66,0.08), transparent 70%);
  border-radius: 0 20px 0 0;
}

/* Step number badge */
.step-num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px; height: 36px;
  background: linear-gradient(135deg, var(--gold), var(--gold2));
  border-radius: 50%;
  font-family: 'Space Mono', monospace;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 0.8rem;
  box-shadow: 0 4px 15px rgba(245,200,66,0.4);
  flex-shrink: 0;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-bottom: 1.3rem;
}

.step-title {
  font-family: 'Cabinet Grotesk', 'Outfit', sans-serif;
  font-size: 1.15rem;
  font-weight: 800;
  color: #fdf6e3;
  letter-spacing: -0.01em;
}
.step-desc {
  font-size: 0.78rem;
  color: rgba(253,246,227,0.38);
  font-weight: 300;
  margin-top: 0.1rem;
}

/* Stagger animation delays */
.step-card:nth-child(1) { animation-delay: 0.1s; }
.step-card:nth-child(2) { animation-delay: 0.2s; }
.step-card:nth-child(3) { animation-delay: 0.3s; }
.step-card:nth-child(4) { animation-delay: 0.4s; }
.step-card:nth-child(5) { animation-delay: 0.5s; }

/* ══════════════════════════════════════════
   INPUTS
══════════════════════════════════════════ */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
  background: rgba(245,200,66,0.04) !important;
  border: 1px solid rgba(245,200,66,0.2) !important;
  border-radius: 10px !important;
  color: var(--cream) !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 0.93rem !important;
  transition: all 0.25s ease !important;
  caret-color: var(--gold) !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus,
[data-testid="stNumberInput"] input:focus {
  border-color: rgba(245,200,66,0.55) !important;
  box-shadow: 0 0 0 3px rgba(245,200,66,0.1), 0 0 20px rgba(245,200,66,0.06) !important;
  background: rgba(245,200,66,0.06) !important;
}

/* ══════════════════════════════════════════
   LABELS
══════════════════════════════════════════ */
label, [data-testid="stWidgetLabel"] p {
  color: rgba(253,246,227,0.6) !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 0.8rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.05em !important;
  text-transform: uppercase !important;
}

/* ══════════════════════════════════════════
   SELECT BOX
══════════════════════════════════════════ */
[data-testid="stSelectbox"] > div > div {
  background: rgba(245,200,66,0.04) !important;
  border: 1px solid rgba(245,200,66,0.2) !important;
  border-radius: 10px !important;
  color: var(--cream) !important;
  transition: all 0.25s ease !important;
}
[data-testid="stSelectbox"] > div > div:hover {
  border-color: rgba(245,200,66,0.45) !important;
}

/* ══════════════════════════════════════════
   FILE UPLOADER
══════════════════════════════════════════ */
[data-testid="stFileUploader"] {
  background: rgba(245,200,66,0.02) !important;
  border: 1.5px dashed rgba(245,200,66,0.28) !important;
  border-radius: 14px !important;
  transition: all 0.3s ease !important;
}
[data-testid="stFileUploader"]:hover {
  border-color: rgba(245,200,66,0.6) !important;
  background: rgba(245,200,66,0.05) !important;
  box-shadow: 0 0 30px rgba(245,200,66,0.07) !important;
}

/* ══════════════════════════════════════════
   SEND BUTTON — CINEMATIC
══════════════════════════════════════════ */
.stButton > button {
  font-family: 'Bebas Neue', sans-serif !important;
  font-size: 1.2rem !important;
  letter-spacing: 0.15em !important;
  background: linear-gradient(135deg, #f5c842 0%, #ffab00 50%, #ff6b35 100%) !important;
  color: var(--ink) !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 0.9rem 3rem !important;
  width: 100% !important;
  position: relative !important;
  overflow: hidden !important;
  transition: all 0.3s cubic-bezier(0.16,1,0.3,1) !important;
  box-shadow: 0 4px 25px rgba(245,200,66,0.35), 0 0 0 1px rgba(245,200,66,0.2) !important;
}
.stButton > button::before {
  content: '' !important;
  position: absolute !important;
  top: 0 !important; left: -100% !important;
  width: 100% !important; height: 100% !important;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent) !important;
  transition: left 0.4s ease !important;
}
.stButton > button:hover {
  transform: translateY(-3px) scale(1.01) !important;
  box-shadow: 0 12px 40px rgba(245,200,66,0.5), 0 0 0 1px rgba(245,200,66,0.4) !important;
}
.stButton > button:hover::before { left: 100% !important; }
.stButton > button:active { transform: translateY(-1px) scale(0.99) !important; }
.stButton > button:disabled {
  background: rgba(245,200,66,0.12) !important;
  color: rgba(253,246,227,0.25) !important;
  box-shadow: none !important;
}

/* ══════════════════════════════════════════
   PROGRESS BAR
══════════════════════════════════════════ */
[data-testid="stProgress"] > div {
  background: rgba(245,200,66,0.08) !important;
  border-radius: 50px !important;
  height: 10px !important;
  overflow: hidden !important;
  border: 1px solid rgba(245,200,66,0.15) !important;
}
[data-testid="stProgress"] > div > div {
  background: linear-gradient(90deg, #f5c842, #ffab00, #ff6b35) !important;
  border-radius: 50px !important;
  background-size: 200% 100% !important;
  animation: shimmer 1.5s linear infinite !important;
  box-shadow: 0 0 15px rgba(245,200,66,0.4) !important;
}

/* ══════════════════════════════════════════
   ALERTS
══════════════════════════════════════════ */
[data-testid="stAlert"] {
  border-radius: 12px !important;
  border: none !important;
  font-family: 'Outfit', sans-serif !important;
}

/* ══════════════════════════════════════════
   DATAFRAME
══════════════════════════════════════════ */
[data-testid="stDataFrame"] {
  border-radius: 12px !important;
  overflow: hidden !important;
  border: 1px solid rgba(245,200,66,0.15) !important;
}

/* ══════════════════════════════════════════
   SIDEBAR SPECIFICS
══════════════════════════════════════════ */
.sidebar-logo-wrap {
  padding: 1.2rem 0 0.5rem 0;
  text-align: center;
  position: relative;
}
.sidebar-logo-icon {
  font-size: 2.5rem;
  display: block;
  animation: float3d 5s ease-in-out infinite;
  filter: drop-shadow(0 0 16px rgba(245,200,66,0.5));
  margin-bottom: 0.5rem;
}
.sidebar-logo-name {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 1.8rem;
  letter-spacing: 0.12em;
  background: linear-gradient(135deg, #f5c842, #ffab00, #ff6b35);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  display: block;
}
.sidebar-tagline {
  font-family: 'Instrument Serif', serif;
  font-style: italic;
  font-size: 0.72rem;
  color: rgba(253,246,227,0.35);
  letter-spacing: 0.05em;
  display: block;
  margin-top: 0.2rem;
}
.sidebar-sep {
  width: 100%;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(245,200,66,0.3), transparent);
  margin: 1.2rem 0;
}
.sidebar-section {
  font-family: 'Space Mono', monospace;
  font-size: 0.6rem;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: rgba(245,200,66,0.5);
  display: block;
  margin: 1rem 0 0.5rem 0;
}

/* ══════════════════════════════════════════
   STAT PILLS
══════════════════════════════════════════ */
.stat-row {
  display: flex;
  gap: 0.8rem;
  margin: 1rem 0 1.5rem;
  flex-wrap: wrap;
  animation: countUp 0.6s both;
}
.stat-pill {
  background: linear-gradient(135deg, rgba(245,200,66,0.08), rgba(255,107,53,0.05));
  border: 1px solid rgba(245,200,66,0.2);
  border-radius: 50px;
  padding: 0.45rem 1rem;
  font-family: 'Outfit', sans-serif;
  font-size: 0.8rem;
  font-weight: 500;
  color: rgba(253,246,227,0.65);
  display: flex;
  align-items: center;
  gap: 0.4rem;
  transition: all 0.25s ease;
}
.stat-pill:hover {
  background: rgba(245,200,66,0.12);
  color: var(--gold);
  border-color: rgba(245,200,66,0.4);
  transform: translateY(-2px);
}
.stat-pill b { color: var(--gold); font-weight: 700; }

/* ══════════════════════════════════════════
   POSITION HELPER LABELS
══════════════════════════════════════════ */
.field-group-label {
  font-family: 'Space Mono', monospace;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  padding: 0.3rem 0.8rem;
  border-radius: 6px;
  display: inline-block;
  margin-bottom: 0.7rem;
}
.fg-gold {
  background: rgba(245,200,66,0.12);
  border: 1px solid rgba(245,200,66,0.3);
  color: var(--gold);
}
.fg-amber {
  background: rgba(255,107,53,0.1);
  border: 1px solid rgba(255,107,53,0.3);
  color: #ff6b35;
}

/* ══════════════════════════════════════════
   HINT PILL
══════════════════════════════════════════ */
.hint-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  background: rgba(245,200,66,0.06);
  border: 1px dashed rgba(245,200,66,0.2);
  border-radius: 8px;
  padding: 0.5rem 1rem;
  font-size: 0.78rem;
  color: rgba(253,246,227,0.45);
  margin-top: 0.5rem;
}
.hint-pill code {
  background: rgba(245,200,66,0.15);
  color: var(--gold);
  padding: 0.1rem 0.45rem;
  border-radius: 4px;
  font-family: 'Space Mono', monospace;
  font-size: 0.75rem;
}

/* ══════════════════════════════════════════
   LOG BOX
══════════════════════════════════════════ */
.log-box {
  background: rgba(0,0,0,0.55);
  border: 1px solid rgba(245,200,66,0.14);
  border-radius: 12px;
  padding: 1rem 1.3rem;
  font-family: 'Space Mono', monospace;
  font-size: 0.75rem;
  line-height: 2;
  color: rgba(245,200,66,0.75);
  max-height: 260px;
  overflow-y: auto;
  white-space: pre-wrap;
  letter-spacing: 0.02em;
  box-shadow: inset 0 0 30px rgba(0,0,0,0.3);
}
.log-box::-webkit-scrollbar { width: 4px; }
.log-box::-webkit-scrollbar-track { background: transparent; }
.log-box::-webkit-scrollbar-thumb { background: rgba(245,200,66,0.3); border-radius: 4px; }

/* ══════════════════════════════════════════
   LIVE STATUS
══════════════════════════════════════════ */
.live-status {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  font-family: 'Outfit', sans-serif;
  font-size: 0.88rem;
  color: rgba(253,246,227,0.5);
  margin: 0.8rem 0;
}
.live-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--gold);
  animation: pulseGold 1.5s ease-in-out infinite;
  display: inline-block;
}

/* ══════════════════════════════════════════
   SUCCESS BANNER
══════════════════════════════════════════ */
.success-banner {
  position: relative;
  background: linear-gradient(135deg, rgba(245,200,66,0.08) 0%, rgba(255,107,53,0.05) 100%);
  border: 1px solid rgba(245,200,66,0.3);
  border-radius: 20px;
  padding: 2.5rem 2rem;
  text-align: center;
  overflow: hidden;
  animation: fadeSlideUp 0.8s cubic-bezier(0.16,1,0.3,1) both;
}
.success-banner::before {
  content: '';
  position: absolute;
  top: 0; left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--gold), var(--amber), transparent);
}
.success-trophy {
  font-size: 3.5rem;
  display: block;
  margin-bottom: 0.8rem;
  filter: drop-shadow(0 0 20px rgba(245,200,66,0.5));
  animation: float3d 4s ease-in-out infinite;
}
.success-title {
  font-family: 'Bebas Neue', sans-serif;
  font-size: 2.5rem;
  letter-spacing: 0.1em;
  background: linear-gradient(135deg, #f5c842, #ffab00, #ff6b35);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.4rem;
}
.success-sub {
  font-family: 'Instrument Serif', serif;
  font-style: italic;
  color: rgba(253,246,227,0.5);
  font-size: 1rem;
}

/* ══════════════════════════════════════════
   MISC
══════════════════════════════════════════ */
hr {
  border: none !important;
  height: 1px !important;
  background: linear-gradient(90deg, transparent, rgba(245,200,66,0.2), transparent) !important;
  margin: 2rem 0 !important;
}

/* Slider */
[data-testid="stSlider"] [role="slider"] {
  background: var(--gold) !important;
  border: 2px solid var(--ink) !important;
  box-shadow: 0 0 12px rgba(245,200,66,0.5) !important;
}
[data-baseweb="slider"] [data-testid="stThumbValue"] {
  background: var(--gold) !important;
  color: var(--ink) !important;
  font-family: 'Space Mono', monospace !important;
}

/* Checkbox */
[data-testid="stCheckbox"] span { color: rgba(253,246,227,0.6) !important; }

/* Caption */
.stCaption, [data-testid="stCaptionContainer"] {
  color: rgba(253,246,227,0.35) !important;
  font-family: 'Outfit', sans-serif !important;
}

/* Expander */
[data-testid="stExpander"] {
  border: 1px solid rgba(245,200,66,0.15) !important;
  border-radius: 12px !important;
  background: rgba(245,200,66,0.02) !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo-wrap">
        <span class="sidebar-logo-icon">🏆</span>
        <span class="sidebar-logo-name">AutoCertify</span>
        <span class="sidebar-tagline">Automate. Personalize. Deliver.</span>
        <div class="sidebar-sep"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="sidebar-section">⚙ Gmail Configuration</span>', unsafe_allow_html=True)
    sender_email = st.text_input("Sender Email", placeholder="you@gmail.com")
    app_password = st.text_input("App Password", type="password", placeholder="xxxx xxxx xxxx xxxx")

    if sender_email and app_password:
        st.success("✓ Credentials ready")

    st.markdown('<div class="sidebar-sep"></div>', unsafe_allow_html=True)
    st.markdown('<span class="sidebar-section">🔑 Get App Password</span>', unsafe_allow_html=True)
    st.markdown("""
    <div style='font-size:0.78rem;color:rgba(253,246,227,0.38);line-height:2.1;'>
    1 · myaccount.google.com<br>
    2 · Security → 2-Step Verification<br>
    3 · App Passwords → Mail → Generate<br>
    4 · Paste the 16-char code above
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-sep"></div>', unsafe_allow_html=True)
    st.markdown('<span class="sidebar-section">⏱ Send Settings</span>', unsafe_allow_html=True)
    delay = st.slider("Delay between emails (s)", 1, 10, 2)


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
    <div class="hero-subtitle">Generate, personalize & deliver certificates — instantly.</div>
    <div class="hero-stats">
      <div class="hero-stat">📋 <span>CSV</span> Driven</div>
      <div class="hero-stat">📄 <span>PDF</span> Overlay</div>
      <div class="hero-stat">📧 <span>Gmail</span> Powered</div>
      <div class="hero-stat">⚡ <span>Zero</span> Code</div>
    </div>
  </div>
</div>

<div class="gold-divider"></div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# STEP 1 — UPLOAD
# ─────────────────────────────────────────────
st.markdown("""
<div class="step-card">
  <div class="step-header">
    <div class="step-num">01</div>
    <div>
      <div class="step-title">Upload Your Files</div>
      <div class="step-desc">Drop your participant list and certificate template below</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with st.container():
    col1, col2 = st.columns(2)
    with col1:
        csv_file = st.file_uploader("📋  Participant List (CSV)", type=["csv"])
    with col2:
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
          <div class="step-desc">Tell AutoCertify which column is which</div>
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
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            name_col = st.selectbox("👤  Name Column", columns)
        with col_b:
            dept_col = st.selectbox("🏢  Department Column", columns)
        with col_c:
            email_col = st.selectbox("📧  Email Column", columns)

    except Exception as e:
        st.error(f"Could not read CSV: {e}")


# ─────────────────────────────────────────────
# STEP 3 — TEXT POSITIONING
# ─────────────────────────────────────────────
st.markdown("""
<div class="step-card">
  <div class="step-header">
    <div class="step-num">03</div>
    <div>
      <div class="step-title">Certificate Text Position</div>
      <div class="step-desc">X = from left edge &nbsp;·&nbsp; Y = from bottom edge &nbsp;·&nbsp; Defaults suit A4 landscape</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<span class="field-group-label fg-gold">✦ Name</span>', unsafe_allow_html=True)
    n1, n2, n3 = st.columns(3)
    with n1: name_x = st.number_input("X", value=250, step=5, key="nx")
    with n2: name_y = st.number_input("Y", value=223, step=5, key="ny")
    with n3: name_size = st.number_input("Size", value=14, step=1, key="ns", min_value=6, max_value=72)
    center_name = st.checkbox("⬛ Center-align Name", value=False)

with col2:
    st.markdown('<span class="field-group-label fg-amber">✦ Department</span>', unsafe_allow_html=True)
    d1, d2, d3 = st.columns(3)
    with d1: dept_x = st.number_input("X", value=185, step=5, key="dx")
    with d2: dept_y = st.number_input("Y", value=198, step=5, key="dy")
    with d3: dept_size = st.number_input("Size", value=14, step=1, key="ds", min_value=6, max_value=72)
    center_dept = st.checkbox("⬛ Center-align Department", value=False)


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
email_body = st.text_area("Message Body", height=190, value="""Dear {name},

Congratulations on your outstanding participation!

Please find your personalized certificate attached to this email.

With warm regards,
AutoCertify · Event Team""")

st.markdown("""
<div class="hint-pill">
  💡 Use <code>{name}</code> anywhere in the body — it'll be replaced with each participant's actual name.
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
      <div class="step-desc">AutoCertify will generate and email every certificate automatically</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

ready = bool(csv_file and template_pdf and sender_email and app_password and data is not None)

if not ready:
    missing = []
    if not csv_file: missing.append("CSV file")
    if not template_pdf: missing.append("Certificate PDF")
    if not sender_email: missing.append("Gmail (sidebar)")
    if not app_password: missing.append("App password (sidebar)")
    st.warning(f"⚠️  Still needed: **{', '.join(missing)}**")

if data is not None:
    t = len(data)
    est_min = (t * delay) // 60
    est_sec = (t * delay) % 60
    st.markdown(f"""
    <div class="stat-row">
      <div class="stat-pill">👥 &nbsp;<b>{t}</b>&nbsp; participants</div>
      <div class="stat-pill">⏱️ &nbsp;~<b>{est_min}m {est_sec}s</b>&nbsp; estimated</div>
      <div class="stat-pill">📨 &nbsp;<b>1</b>&nbsp; certificate each</div>
      <div class="stat-pill">✉️ &nbsp;<b>Gmail</b>&nbsp; SMTP</div>
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
    overlay_path = os.path.join(output_folder, "overlay.pdf")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
    <div style='font-family:"Bebas Neue",sans-serif;font-size:1.3rem;letter-spacing:0.15em;
                color:#f5c842;margin-bottom:0.8rem;'>
      ⚡ LIVE DISTRIBUTION FEED
    </div>
    """, unsafe_allow_html=True)

    with st.spinner("Connecting to Gmail SMTP..."):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(sender_email, app_password)
            st.success("✅ Secure Gmail connection established")
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

            # Validate email
            if "@" not in email or "." not in email.split("@")[-1]:
                logs.append(f"⚠  Skipped  ·  {name}  ·  invalid email: '{email}'")
                failed += 1
                continue

            # Overlay
            c = canvas.Canvas(overlay_path, pagesize=landscape(A4))
            pw = landscape(A4)[0]

            c.setFont("Helvetica-Bold", name_size)
            if center_name:
                tw = c.stringWidth(name, "Helvetica-Bold", name_size)
                c.drawString(pw / 2 - tw / 2, name_y, name)
            else:
                c.drawString(name_x, name_y, name)

            c.setFont("Helvetica", dept_size)
            if center_dept:
                tw = c.stringWidth(dept, "Helvetica", dept_size)
                c.drawString(pw / 2 - tw / 2, dept_y, dept)
            else:
                c.drawString(dept_x, dept_y, dept)

            c.save()

            # Merge
            tr = PdfReader(template_path)
            ov = PdfReader(overlay_path)
            wr = PdfWriter()
            pg = tr.pages[0]
            pg.merge_page(ov.pages[0])
            wr.add_page(pg)

            safe = "".join(ch for ch in name if ch.isalnum() or ch in (" ", "_")).rstrip()
            cert_path = os.path.join(output_folder, f"{safe}.pdf")
            with open(cert_path, "wb") as f:
                wr.write(f)

            # Email
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = email_subject
            msg.attach(MIMEText(email_body.replace("{name}", name), "plain"))

            with open(cert_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
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
            f'<div class="live-status">'
            f'<span class="live-dot"></span>'
            f'Processing <b style="color:#f5c842">{index+1} / {total}</b>'
            f'&nbsp;·&nbsp;<b style="color:#4ade80">✅ {count} sent</b>'
            f'&nbsp;·&nbsp;<b style="color:#f87171">❌ {failed} failed</b>'
            f'</div>',
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
      <div class="success-sub">{count} certificates delivered with pride &nbsp;·&nbsp; {failed} failed</div>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 Full Distribution Log"):
        st.markdown('<div class="log-box">' + '\n'.join(logs) + '</div>', unsafe_allow_html=True)
