import streamlit as st
from groq import Groq
import PyPDF2
import os
import time
import uuid
import logging
from dotenv import load_dotenv
import boto3
from botocore.exceptions import ClientError

# Page Configurations
st.set_page_config(page_title="Resume Analyzer", page_icon="📝", layout="wide")

# Custom CSS for UI improvements
st.markdown("""
    <style>
        body {
            background-color: #f5f7fa;
            font-family: 'Arial', sans-serif;
        }
        .stApp {
            max-width: 1300px;
            margin: 0 auto;
        }
        .header {
            font-size: 32px;
            color: #333;
            font-weight: bold;
            text-align: center;
        }
        .card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
            transition: transform 0.3s ease;
        }
        .card:hover {
            transform: translateY(-10px);
        }
        .btn {
            background-color: #007bff;
            color: white;
            padding: 15px;
            border-radius: 10px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        .btn:hover {
            background-color: #0056b3;
        }
        .analysis-box {
            background-color: #e7f3f0;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.1);
            font-size: 14px;
        }
        .match-score {
            font-size: 32px;
            font-weight: bold;
            color: #28a745;
        }
        .download-btn {
            background-color: #28a745;
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
        }
        .download-btn:hover {
            background-color: #218838;
        }
    </style>
    """, unsafe_allow_html=True)

# Function to Extract Text from PDF
def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

# Function to Analyze Resume (Using Groq API)
def analyze_resume(client, resume_text, job_description):
    """Analyze resume against job description using Groq API."""
    prompt = f"""
    Analyze the following resume against the job description:
    Resume: {resume_text}
    Job Description: {job_description}
    Provide a match score, strengths, and suggestions.
    """
    
    try:
        response = client.chat.completions.create(
            model="qwen-qwq-32b",
            messages=[{"role": "system", "content": "You are an expert resume analyzer."},
                      {"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error during analysis: {str(e)}")
        return None

# Main Function to Create UI
def main():
    st.title("📝 Resume Analyzer")
    st.write("Upload your resume and paste the job description for instant feedback!")
    
    # Input Fields
    name = st.text_input("Your Name")
    email = st.text_input("Your Email")
    preferred_job_role = st.text_input("Preferred Job Role")
    
    # File Upload and Job Description Inputs
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=['pdf'])
    job_description = st.text_area("Job Description", height=200)

    # Proceed Only If Both Inputs Are Provided
    if uploaded_file and job_description:
        resume_text = extract_text_from_pdf(uploaded_file)
        
        # Display extracted resume text
        if resume_text:
            st.markdown('<div class="card"><h3>Extracted Resume Text</h3></div>', unsafe_allow_html=True)
            st.text_area("Resume Text", resume_text, height=300)

            # Trigger Analysis on Button Click
            if st.button("Analyze Resume", key="analyze_button"):
                with st.spinner("Analyzing your resume..."):
                    analysis = analyze_resume(client, resume_text, job_description)
                    
                    if analysis:
                        st.markdown("""
                        <div class="card">
                            <h3 class="header">Match Score</h3>
                            <div class="match-score">85%</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div class="card">
                            <h3 class="header">Analysis</h3>
                            <div class="analysis-box">{analysis}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Add download button
                        analysis_bytes = analysis.encode()
                        st.download_button(label="Download Analysis", data=analysis_bytes, file_name="resume_analysis.txt", mime="text/plain")

# Run the Application
if __name__ == "__main__":
    main()
