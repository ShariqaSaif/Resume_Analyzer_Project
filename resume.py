import os
import re
from collections import Counter
import docx2txt
import PyPDF2
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pymysql
import hashlib

UPLOAD_FOLDER = "Uploads/"

# MySQL connection setup
def create_connection():
    return pymysql.connect(
        host='localhost',
        port=3306,
        user="Shariqa",
        password="Sharu@123",
        database="RESUME"
    )

# Initialize database and create table if not exists
def initialize_database():
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("CREATE DATABASE IF NOT EXISTS RESUME")
        cursor.execute("USE RESUME")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            )
        """)
        conn.commit()
    except pymysql.MySQLError as err:
        st.error(f"Error initializing database: {err}")
    finally:
        cursor.close()
        conn.close()

# User management functions
def add_user(username, password):
    hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed))
        conn.commit()
        st.success("User registered successfully!")
    except pymysql.MySQLError as err:
        st.error(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()

def login_user(username, password):
    hashed = hashlib.sha256(password.encode('utf-8')).hexdigest()
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    if result and result[0] == hashed:
        return True
    return False

# Functions to extract text from different file types
from PyPDF2 import PdfReader

def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(docx_file):
    return docx2txt.process(docx_file)

def extract_text_from_txt(txt_file):
    return txt_file.read().decode('utf-8')


def extract_text(file_path):
    if file_path.endswith('.pdf'):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith('.docx'):
        return extract_text_from_docx(file_path)
    elif file_path.endswith('.txt'):
        return extract_text_from_txt(file_path)
    else:
        return ""

# Function to extract key terms from text (job description or resumes)
def extract_key_terms(text):
    stop_words = set(["the", "is", "in", "and", "to", "with", "a", "for", "of", "on", "or", "as", "by"])
    text = text.lower()
    words = re.findall(r'\b\w+\b', text)
    terms = [word for word in words if word not in stop_words]
    return Counter(terms)

# Generate suggestions for resumes based on job description
def generate_suggestions(job_description, resumes):
    job_terms = extract_key_terms(job_description)
    suggestions = []
    for resume in resumes:
        resume_terms = extract_key_terms(resume)
        missing_terms = job_terms - resume_terms
        if missing_terms:
            missing_keywords = ', '.join(missing_terms.keys())
            suggestions.append(f"Consider adding these keywords to your resume: {missing_keywords}")
        else:
            suggestions.append("Your resume is a good match for the job description.")
    return suggestions

# Match resumes and generate suggestions
def match_resumes(job_description, resume_files):
    resumes = []
    for resume_file in resume_files:
        # Directly read file from the uploaded file object without saving to disk
        if resume_file.type == 'application/pdf':
            # For PDFs
            text = extract_text_from_pdf(resume_file)
        elif resume_file.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            # For DOCX
            text = extract_text_from_docx(resume_file)
        elif resume_file.type == 'text/plain':
            # For TXT
            text = extract_text_from_txt(resume_file)
        else:
            st.error(f"Unsupported file type: {resume_file.type}")
            continue

        resumes.append(text)

    # Vectorize and compute similarity
    vectorizer = TfidfVectorizer().fit_transform([job_description] + resumes)
    vectors = vectorizer.toarray()

    job_vector = vectors[0]
    resume_vectors = vectors[1:]
    similarities = cosine_similarity([job_vector], resume_vectors)[0]

    # Sort and select top matches
    top_indices = similarities.argsort()[-5:][::-1]
    top_resumes = [resume_files[i].name for i in top_indices]
    similarity_scores = [round(similarities[i], 2) for i in top_indices]
    prediction_scores = [round(((score + 1) / 2) * 100, 2) for score in similarity_scores]

    # Generate suggestions for the top resumes
    top_resumes_texts = [resumes[i] for i in top_indices]
    suggestions = generate_suggestions(job_description, top_resumes_texts)

    return top_resumes, similarity_scores, prediction_scores, suggestions


# Create upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Initialize the database and table
initialize_database()

# Streamlit interface
st.title("Resume Analyzer")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def logout():
    st.session_state.logged_in = False
    st.success("Logged out successfully!")

if not st.session_state.logged_in:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
   
    if st.button("Login"):
        if login_user(username, password):
            st.session_state.logged_in = True
            st.success("Logged in successfully!")
        else:
            st.error("Invalid username or password.")
   
    st.subheader("Register")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type='password')
   
    if st.button("Register"):
        if new_username and new_password:
            add_user(new_username, new_password)
        else:
            st.error("Please fill in all fields.")
else:
    st.success("Welcome to the Resume Analyzer!")
   
    if st.button("Logout"):
        logout()

    # Add custom CSS for responsive design
    st.markdown("""
        <style>
            .container {
                max-width: 800px;
                margin: auto;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            }
            .result {
                background-color: #dff0d8;
                padding: 10px;
                border-radius: 8px;
                margin-top: 20px;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.subheader("Enter Job Description")
        job_description = st.text_area("Job Description")

        st.subheader("Upload Resumes")
        resume_files = st.file_uploader("Upload Resumes", type=['pdf', 'docx', 'txt'], accept_multiple_files=True)

        if st.button("Match Resumes"):
            if not resume_files or not job_description:
                st.warning("Please upload resumes and enter a job description.")
            else:
                top_resumes, similarity_scores, prediction_scores, suggestions = match_resumes(job_description, resume_files)

                # Display results
                st.success("Top Matching Resumes:")
                for resume, score, pred_score, suggestion in zip(top_resumes, similarity_scores, prediction_scores, suggestions):
                    st.write(f"**{resume}**:  <span style='font-size:24px; font-weight:bold;'>Prediction Score: {pred_score}%</span>", unsafe_allow_html=True)
                    
                    st.write(f"<p style='font-size:20px; font-weight:bold;'>Suggestions:</p> {suggestion}", unsafe_allow_html=True)

                    st.write("---")
