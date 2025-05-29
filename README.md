# 🧠 AI Resume Analyzer

The **AI Resume Analyzer** is an intelligent web application that automates resume screening using NLP techniques. It compares uploaded resumes against a job description, detects fake information, and provides tailored suggestions to improve resume quality — saving 80% of manual screening time and increasing precision in hiring decisions.

---

## 🚀 Features

- 🔍 **Resume Matching** using TF-IDF and Cosine Similarity
- 📄 **Multi-format Support**: `.pdf`, `.docx`, `.txt`
- ⚠️ **Fake Info Detection**: Checks for fake universities/companies
- 💡 **Improvement Suggestions** based on job role
- 🔐 **Login/Signup System** with secure password hashing
- 🖥️ **Streamlit UI** for easy interaction

---

## 🧰 Tech Stack

- **Frontend**: Streamlit  
- **Backend**: Python  
- **NLP/ML**: scikit-learn, PyPDF2, docx2txt  
- **Database**: MySQL (via pymysql)  
- **Others**: hashlib, os, re

---
## 🛠️ MySQL Configuration
1. **Create Database and Table**
Log into your MySQL client and run:

CREATE DATABASE RESUME;
USE RESUME;
CREATE TABLE users (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(100)
);



**2. Update Credentials** 
in resume.py
Replace the placeholders with your actual MySQL credentials:


def create_connection():
    return pymysql.connect(
        host='localhost',
        user='your_username',
        password='your_password',
        db='RESUME'
    )

---
## ▶️ Run the Application
In the terminal, run:
**streamlit run resume.py**
This will launch the app in your default web browser.

---

## 💡 How It Works
* User logs in or creates an account.

* Enters the job title and description.

* Uploads one or more resumes.

**The app:**

* Extracts and cleans resume content

* Converts resumes and job description into TF-IDF vectors

* Uses cosine similarity to find the best match

* Detects fake universities and companies

* Shows match scores and suggestions

---

## 📊 Sample Output

* File: resume1.pdf
* Match Score: 85.73%
* Fake Info: No fake university/company detected
* Suggestions: Add role-specific keywords like 'Python', 'Data Analysis'

---
🙋‍♀️ Author
Shaik Shariqa Saif
🎓 Final Year Engineering Student
🔍 Data Science Enthusiast
