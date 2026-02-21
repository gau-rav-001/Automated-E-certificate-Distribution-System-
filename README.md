<<<<<<< HEAD
# 🎓 Certificate Distribution System

A user-friendly Streamlit app to generate and email personalized certificates.

---

## ⚙️ Setup (One Time)

**1. Install dependencies:**
```bash
pip install -r requirements.txt
```

**2. Run the app:**
```bash
streamlit run app.py
```

Your browser will open automatically at `http://localhost:8501`

---

## 🚀 How to Use

1. **Enter your Gmail** and App Password in the sidebar
2. **Upload your CSV** (must have name, department, email columns)
3. **Upload your certificate PDF template**
4. **Map your CSV columns** to Name / Department / Email
5. **Adjust text positions** (X, Y coordinates) to match your template
6. **Write your email subject and body** (use `{name}` for personalization)
7. **Click Send All** and watch the live progress!

---

## 📋 CSV Format Example

| candidates_name | organisation_name | candidates_email |
|---|---|---|
| John Doe | Computer Engineering | john@example.com |
| Jane Smith | Mechanical Engineering | jane@example.com |

Any column names work — you'll map them in the app.

---

## 🔑 Gmail App Password

1. Go to [myaccount.google.com](https://myaccount.google.com)
2. Security → 2-Step Verification → App Passwords
3. Generate a password for "Mail"
4. Paste it in the sidebar (spaces are OK)

---

## 📍 Finding Text Positions

The default X/Y values are set for a standard A4 landscape certificate.  
If your text appears in the wrong place, adjust X and Y values:
- **X** = distance from left edge (pixels)
- **Y** = distance from bottom edge (pixels)
- Use the **Center-align** checkboxes for centered text regardless of name length
=======
# Automated-E-certificate-Distribution-System-
Certificate Distribution System is a Streamlit-based application that automates certificate generation and emailing. It reads participant data from CSV, overlays names and departments onto a PDF template, and sends personalized certificates via Gmail SMTP. It includes progress tracking, logging, and customizable layout settings.
>>>>>>> f061381a4b9ca0f8cbd939f70f563c7abb77ad97
