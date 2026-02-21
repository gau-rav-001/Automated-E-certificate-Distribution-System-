# 🎓 Automated E-Certificate Distribution System

A Streamlit-based web application that automates the generation and distribution of personalized certificates via email. This system reads participant data from a CSV file, overlays names and departments onto a certificate template, and sends certificates automatically using Gmail SMTP.

---

## 🚀 Features

* 📋 Upload participant data using CSV
* 📄 Use a custom certificate template (PDF)
* ✍️ Automatically generate personalized certificates
* 📧 Send certificates via Gmail SMTP
* ⚙️ Adjustable text position and font size
* 📊 Progress tracking and send logs
* 🛡️ Error handling for invalid emails
* ⏱️ Configurable delay between emails

---

## 🛠️ Tech Stack

* Python
* Streamlit
* Pandas
* ReportLab
* PyPDF2
* SMTP (Gmail)
* Email MIME libraries

---

## 📂 Project Structure

```
Automated-E-certificate-Distribution-System-
│
├── app.py
├── requirements.txt
├── README.md
├── sample.csv
└── .gitignore
```

---

## ⚙️ Installation

### 1. Clone the repository

```
git clone https://github.com/gau-rav-001/Automated-E-certificate-Distribution-System-.git
cd Automated-E-certificate-Distribution-System-
```

### 2. Create virtual environment

```
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

## ▶️ Run the application

```
streamlit run app.py
```

---

## 📧 Gmail Setup

To send emails, you must use a Gmail App Password:

1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Generate App Password
4. Use that password in the app

---

## 📋 CSV Format Example

```
Name,Department,Email
John Doe,Computer Engineering,john@email.com
Jane Smith,IT,jane@email.com
```

---

## 🎯 Use Case

* College events
* Workshops
* Certifications
* Online courses
* Hackathons

---

## 👨‍💻 Author

**Gaurav Kumbhare**

GitHub: https://github.com/gau-rav-001

---

## ⭐ Contribution

Feel free to fork this project and improve it.

---

## 📜 License

This project is open source and available under the MIT License.

---
