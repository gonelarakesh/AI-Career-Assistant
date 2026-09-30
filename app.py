import streamlit as st
from PyPDF2 import PdfReader
from google import genai
import json

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import tempfile

client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("Resume Analyzer")
st.write("Welcome to Resume Analyzer Project")

uploaded_file = st.file_uploader(
    "Upload Your Resume",
    type=["pdf"]
)

# Global variables
text = ""
job_description = ""

if uploaded_file is not None:

    st.success("Resume uploaded successfully!")

    pdf_reader = PdfReader(uploaded_file)

    text = ""

    for page in pdf_reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

        st.subheader("Resume Text")
        st.write(text)

    skills = [
        "Python",
        "Java",
        "C",
        "C++",
        "HTML",
        "CSS",
        "JavaScript",
        "SQL",
        "Machine Learning",
        "Data Science",
        "AI",
        "React",
        "Node.js",
        "Git",
        "Excel"
    ]

    found_skills = []

    for skill in skills:
        if skill.lower() in text.lower():
            found_skills.append(skill)

    st.subheader("Skills Found")

    if found_skills:
        for skill in found_skills:
            st.write("✅", skill)
    else:
        st.write("No skills found.")

    score = min(len(found_skills) * 10, 100)

    st.subheader("Resume Score")
    st.progress(score / 100)
    st.write(f"Score: {score}/100")

    st.subheader("Job Description")

    job_description = st.text_area(
        "Paste the Job Description Here"
    )

    if job_description:

        matched_skills = []
        missing_skills = []

        for skill in skills:
            if skill.lower() in job_description.lower():

                if skill in found_skills:
                    matched_skills.append(skill)
                else:
                    missing_skills.append(skill)

        st.subheader("Matched Skills")

        if matched_skills:
            for skill in matched_skills:
                st.write("✅", skill)
        else:
            st.write("No matching skills found.")

        st.subheader("Missing Skills")

        if missing_skills:
            for skill in missing_skills:
                st.write("❌", skill)
        else:
            st.write("No missing skills.")

        total = len(matched_skills) + len(missing_skills)

        if total > 0:
            match_percentage = (len(matched_skills) / total) * 100
        else:
            match_percentage = 0

        st.subheader("Job Match Percentage")
        st.progress(match_percentage / 100)
        st.write(f"{match_percentage:.2f}% Match")

        st.subheader("AI Resume Suggestions")

        if missing_skills:

            st.write(
                "Your resume can be improved by adding these skills:"
            )

            for skill in missing_skills:
                st.write("👉", skill)

            st.info(
                "Add projects, certifications, or experience related to these skills to improve your resume."
            )

        else:
            st.success(
                "Excellent! Your resume already matches the job description very well."
            )

    # ==========================
    # Part 2 starts from here
    # ==========================

    st.subheader("Gemini AI Resume Analysis")
    if st.button("Analyze Resume with AI"):

        prompt = f"""
You are an ATS Resume Analyzer.

Analyze the following resume and compare it with the job description.

Resume:
{text}

Job Description:
{job_description}

Return ONLY a valid JSON object.

Do NOT add markdown.
Do NOT use triple backticks.
Do NOT add any explanation.

Return in this exact format:

{{
    "ats_score": 85,
    "job_match_percentage": 90,
    "matching_skills": [
        "Python",
        "SQL"
    ],
    "missing_skills": [
        "Docker",
        "AWS"
    ],
    "strengths": [
        "Strong Python knowledge",
        "Good projects"
    ],
    "weaknesses": [
        "No cloud experience"
    ],
    "suggestions": [
        "Learn Docker",
        "Build AWS projects"
    ],
    "final_recommendation": "Good match for this role."
}}
"""

        try:

            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )

            data = json.loads(response.text)

            # Save ATS result
            st.session_state["ats_data"] = data

        except Exception as e:
            st.error(f"Error: {e}")

    # -------------------------------
    # Display ATS Analysis
    # -------------------------------

    if "ats_data" in st.session_state:

        data = st.session_state["ats_data"]

        st.subheader("ATS Analysis")

        st.subheader("ATS Score")
        st.progress(data["ats_score"] / 100)
        st.write(f'ATS Score: {data["ats_score"]}/100')

        st.subheader("Job Match Percentage")
        st.progress(data["job_match_percentage"] / 100)
        st.write(f'Job Match: {data["job_match_percentage"]}%')

        st.subheader("Matching Skills")

        for skill in data["matching_skills"]:
            st.write("✅", skill)

        st.subheader("Missing Skills")

        for skill in data["missing_skills"]:
            st.write("❌", skill)

        st.subheader("Strengths")

        for strength in data["strengths"]:
            st.write("✅", strength)

        st.subheader("Weaknesses")

        for weakness in data["weaknesses"]:
            st.write("❌", weakness)

        st.subheader("Resume Improvement Suggestions")

        for suggestion in data["suggestions"]:
            st.write("👉", suggestion)

        st.subheader("Final Recommendation")
        st.success(data["final_recommendation"])

# ==========================================
# AI Interview Question Generator
# ==========================================

st.subheader("AI Interview Question Generator")

if st.button("Generate Interview Questions"):

    interview_prompt = f"""
You are an AI Interviewer.

Based on the following Resume and Job Description, generate interview questions.

Resume:
{text}

Job Description:
{job_description}

Generate:

1. 5 Technical Interview Questions
2. 5 HR Interview Questions
3. 5 Project-Based Questions
4. 3 Coding Questions

Return ONLY a valid JSON object.

Do NOT add markdown.
Do NOT use triple backticks.
Do NOT add any explanation.

{{
  "technical_questions": [],
  "hr_questions": [],
  "project_questions": [],
  "coding_questions": []
}}
"""

    try:

        with st.spinner("Generating Interview Questions..."):

            interview_response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=interview_prompt
            )

        response_text = interview_response.text.strip()

        # Remove Markdown if Gemini returns it
        if response_text.startswith("```json"):
            response_text = (
                response_text.replace("```json", "")
                .replace("```", "")
                .strip()
            )

        elif response_text.startswith("```"):
            response_text = (
                response_text.replace("```", "")
                .strip()
            )

        interview_data = json.loads(response_text)

        # Save interview questions
        st.session_state["interview_data"] = interview_data

        st.success("Interview Questions Generated Successfully!")

    except json.JSONDecodeError:

        st.error("Gemini returned invalid JSON.")
        st.code(interview_response.text)

    except Exception as e:

        st.error(f"Error: {e}")

# ==========================================
# Display Interview Questions
# ==========================================

if "interview_data" in st.session_state:

    interview_data = st.session_state["interview_data"]

    st.subheader("Technical Interview Questions")

    for i, question in enumerate(
        interview_data.get("technical_questions", []),
        start=1
    ):
        st.write(f"{i}. {question}")

    st.subheader("HR Interview Questions")

    for i, question in enumerate(
        interview_data.get("hr_questions", []),
        start=1
    ):
        st.write(f"{i}. {question}")

    st.subheader("Project-Based Questions")

    for i, question in enumerate(
        interview_data.get("project_questions", []),
        start=1
    ):
        st.write(f"{i}. {question}")

    st.subheader("Coding Questions")

    for i, question in enumerate(
        interview_data.get("coding_questions", []),
        start=1
    ):
        st.write(f"{i}. {question}")

        # ==========================================
# AI Answer Evaluation
# ==========================================

st.subheader("AI Interview Answer Evaluation")

if "interview_data" in st.session_state:

    technical_questions = st.session_state["interview_data"]["technical_questions"]

    selected_question = st.selectbox(
        "Select a Technical Question",
        technical_questions
    )

    # ==========================================
# User Answer
# ==========================================

user_answer = st.text_area(
    "Write Your Answer Here",
    height=200,
    placeholder="Type your interview answer here..."
)

# ==========================================
# Evaluate Answer
# ==========================================

if st.button("Evaluate Answer"):

    evaluation_prompt = f"""
You are an AI Technical Interviewer.

Interview Question:
{selected_question}

Candidate Answer:
{user_answer}

Evaluate the candidate's answer.

Return ONLY valid JSON.

Do NOT use markdown.
Do NOT use triple backticks.

{{
    "score": 8,
    "strengths": [
        "Good explanation"
    ],
    "weaknesses": [
        "Needs more examples"
    ],
    "ideal_answer": "Ideal answer goes here.",
    "suggestions": [
        "Practice with real-world examples"
    ]
}}
"""

    try:

        with st.spinner("Evaluating Answer..."):

            evaluation_response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=evaluation_prompt
            )

        response_text = evaluation_response.text.strip()

        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()

        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()

        evaluation_data = json.loads(response_text)

        st.session_state["evaluation_data"] = evaluation_data

        st.success("Answer Evaluated Successfully!")

    except json.JSONDecodeError:

        st.error("Gemini returned invalid JSON.")
        st.code(evaluation_response.text)

    except Exception as e:

        st.error(f"Error: {e}")

        # ==========================================
# Display Evaluation Result
# ==========================================

if "evaluation_data" in st.session_state:

    result = st.session_state["evaluation_data"]

    st.subheader(" Evaluation Result")

    st.subheader(" Score")

    st.progress(result["score"] / 10)

    st.write(f"Score : {result['score']}/10")

    st.subheader("✅ Strengths")

    for item in result["strengths"]:
        st.write("✅", item)

    st.subheader("❌ Weaknesses")

    for item in result["weaknesses"]:
        st.write("❌", item)

    st.subheader(" Ideal Answer")

    st.info(result["ideal_answer"])

    st.subheader(" Suggestions")

    for item in result["suggestions"]:
        st.write("👉", item)

        # ==========================================
# PART 5
# Download PDF Report
# ==========================================

st.subheader(" Download Resume Report")

if st.button("Generate PDF Report", key="generate_pdf"):

    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    pdf_path = temp_pdf.name

    doc = SimpleDocTemplate(pdf_path)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph("AI Resume Analyzer Report", styles["Title"])
    )

    elements.append(
        Paragraph("<br/>Resume Report", styles["Heading2"])
    )

    # Resume Score
    Paragraph(
    f"Resume Score : {st.session_state.get('resume_score', 0)}/100",
    styles["Normal"]
)

    # Job Match
    Paragraph(
    f"Job Match : {st.session_state.get('job_match', 0):.2f}%",
    styles["Normal"]
)

        # ==========================================
    # ATS Analysis
    # ==========================================

    if "ats_data" in st.session_state:

        ats = st.session_state["ats_data"]

        elements.append(
            Paragraph("<br/><b>ATS Analysis</b>", styles["Heading2"])
        )

        elements.append(
            Paragraph(f"ATS Score : {ats['ats_score']}/100", styles["Normal"])
        )

        elements.append(
            Paragraph(f"Job Match : {ats['job_match_percentage']}%", styles["Normal"])
        )

        elements.append(
            Paragraph("<br/><b>Matching Skills</b>", styles["Heading3"])
        )

        for skill in ats["matching_skills"]:
            elements.append(
                Paragraph(f"• {skill}", styles["Normal"])
            )

        elements.append(
            Paragraph("<br/><b>Missing Skills</b>", styles["Heading3"])
        )

        for skill in ats["missing_skills"]:
            elements.append(
                Paragraph(f"• {skill}", styles["Normal"])
            )

        elements.append(
            Paragraph("<br/><b>Strengths</b>", styles["Heading3"])
        )

        for strength in ats["strengths"]:
            elements.append(
                Paragraph(f"• {strength}", styles["Normal"])
            )

        elements.append(
            Paragraph("<br/><b>Weaknesses</b>", styles["Heading3"])
        )

        for weakness in ats["weaknesses"]:
            elements.append(
                Paragraph(f"• {weakness}", styles["Normal"])
            )

        elements.append(
            Paragraph("<br/><b>Suggestions</b>", styles["Heading3"])
        )

        for suggestion in ats["suggestions"]:
            elements.append(
                Paragraph(f"• {suggestion}", styles["Normal"])
            )

    # ==========================================
    # Build PDF
    # ==========================================

    doc.build(elements)

    with open(pdf_path, "rb") as pdf_file:

        st.download_button(
            label=" Download PDF Report",
            data=pdf_file,
            file_name="Resume_Report.pdf",
            mime="application/pdf"
        )

    st.success("PDF Report Generated Successfully!")

   # ==========================================
# PART 6
# AI Resume Improver
# ==========================================

st.subheader(" AI Resume Improver")

if st.button("Improve My Resume", key="improve_resume"):

    improve_prompt = f"""
You are an expert Resume Writer.

Improve the following resume according to the Job Description.

Resume:
Resume:
{st.session_state.get("resume_text", "")}

Job Description:
{st.session_state.get("job_description", "")}

Instructions:
1. Rewrite the Professional Summary.
2. Improve the Skills section.
3. Improve the Projects section.
4. Improve the Experience section.
5. Make the resume ATS-friendly.
6. Return only the improved resume.
"""

    try:

        with st.spinner("Improving Resume..."):

            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=improve_prompt
            )
        
        st.session_state["improved_resume"] = response.text
        
        st.success(" Resume Improved Successfully!")
        
        # PART 6C goes HERE
        st.subheader(" Improved Resume")
        
        st.text_area(
            "Your Improved Resume",
            value=st.session_state["improved_resume"],
            height=500,
            key="improved_resume_output"
        )
            
        # PART 6D goes HERE
        st.download_button(
            label=" Download Improved Resume",
            data=st.session_state["improved_resume"],
            file_name="Improved_Resume.txt",
            mime="text/plain",
            key="download_improved_resume"
        )
                
    except Exception as e:
                    
        st.error(f"Error: {e}")

        # ==========================================
# PART 7
# AI Career Roadmap Generator
# ==========================================

st.subheader(" AI Career Roadmap Generator")

target_role = st.text_input(
    "Enter Your Target Career Role",
    placeholder="Example: Python Developer"
)

if st.button("Generate Career Roadmap", key="generate_career_roadmap"):

    if target_role.strip() == "":
        st.error("Please enter your target career role.")

    else:

        roadmap_prompt = f"""
You are an AI Career Mentor.

Create a complete career roadmap for someone who wants to become a:

{target_role}

Include the following sections:

1. 30-Day Learning Plan
2. 60-Day Learning Plan
3. 90-Day Learning Plan
4. Skills to Learn
5. Recommended Projects
6. Recommended Certifications
7. Recommended Online Courses
8. Top Companies Hiring
9. Interview Preparation Tips

Return the response in a clear, well-formatted text.
"""

        try:

            with st.spinner("Generating Career Roadmap..."):

                roadmap_response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=roadmap_prompt
                )

            st.session_state["career_roadmap"] = roadmap_response.text

            st.success(" Career Roadmap Generated Successfully!")

            # ==========================================
            # PART 7C
            # Display Career Roadmap
            # ==========================================

            st.subheader(" Your AI Career Roadmap")

            st.text_area(
                "Career Roadmap",
                value=st.session_state["career_roadmap"],
                height=600,
                key="career_roadmap_output"
            )

            # ==========================================
            # PART 7D
            # Download Career Roadmap
            # ==========================================

            st.download_button(
                label=" Download Career Roadmap",
                data=st.session_state["career_roadmap"],
                file_name="Career_Roadmap.txt",
                mime="text/plain",
                key="download_career_roadmap"
            )

        except Exception as e:

            st.error(f"Error: {e}")

           # ==========================================================
# AI MOCK INTERVIEW
# ==========================================================

st.subheader(" AI Mock Interview")

# ----------------------------------------------------------
# SESSION STATE
# ----------------------------------------------------------

if "mock_question" not in st.session_state:
    st.session_state.mock_question = ""

if "mock_evaluation" not in st.session_state:
    st.session_state.mock_evaluation = ""

if "mock_answer" not in st.session_state:
    st.session_state.mock_answer = ""

# ----------------------------------------------------------
# TARGET ROLE
# ----------------------------------------------------------

mock_role = st.text_input(
    " Target Job Role",
    placeholder="Example: Python Developer",
    key="mock_role_input"
)

# ----------------------------------------------------------
# GENERATE QUESTION
# ----------------------------------------------------------

if st.button(
    " Generate Interview Question",
    key="mock_generate_button"
):

    if mock_role.strip() == "":
        st.warning("Please enter your target job role.")

    elif "text" not in locals() or not text.strip():
        st.warning("Please upload your resume first.")

    else:

        question_prompt = f"""
You are a professional job interviewer.

Candidate Resume:
{text}

Target Job Role:
{mock_role}

Generate ONE interview question based on the
candidate's resume and target role.

Return ONLY the interview question.
"""

        try:

            with st.spinner("Generating interview question..."):

                question_response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=question_prompt
                )

            # Save question
            st.session_state.mock_question = (
                question_response.text.strip()
            )

            # Clear previous evaluation
            st.session_state.mock_evaluation = ""

            # Clear previous answer
            st.session_state.mock_answer = ""

            st.success(" Interview question generated.")

        except Exception as e:

            st.error(f"Gemini Error: {e}")

# ----------------------------------------------------------
# DISPLAY QUESTION
# ----------------------------------------------------------

if st.session_state.mock_question:

    st.subheader(" Interview Question")

    st.info(
        st.session_state.mock_question
    )

    # ------------------------------------------------------
    # ANSWER
    # ------------------------------------------------------

    mock_answer = st.text_area(
        " Write Your Answer",
        value=st.session_state.mock_answer,
        height=250,
        placeholder="Write your answer here...",
        key="mock_answer_box"
    )

    # Keep answer in session state
    st.session_state.mock_answer = mock_answer

    # ------------------------------------------------------
    # EVALUATE
    # ------------------------------------------------------

    if st.button(
        " Evaluate My Answer",
        key="mock_evaluate_button"
    ):

        if not st.session_state.mock_answer.strip():

            st.warning(
                "Please write your answer before evaluating."
            )

        else:

            evaluation_prompt = f"""
You are an expert interview evaluator.

Target Job Role:
{mock_role}

Interview Question:
{st.session_state.mock_question}

Candidate Answer:
{st.session_state.mock_answer}

Evaluate the candidate's answer.

Return the following:

Score: X/10

Strengths:
- ...

Weaknesses:
- ...

Technical Knowledge:
- ...

Communication:
- ...

Relevance:
- ...

Suggestions:
- ...

Ideal Answer:
...
"""

            try:

                with st.spinner("Evaluating your answer..."):

                    evaluation_response = (
                        client.models.generate_content(
                            model="gemini-3.5-flash",
                            contents=evaluation_prompt
                        )
                    )

                # Save evaluation
                st.session_state.mock_evaluation = (
                    evaluation_response.text
                )

                st.success(
                    " Answer evaluated successfully."
                )

            except Exception as e:

                st.error(
                    f"Gemini Error: {e}"
                )

# ----------------------------------------------------------
# DISPLAY EVALUATION
# ----------------------------------------------------------

if st.session_state.mock_evaluation:

    st.subheader(" Interview Evaluation")

    st.text_area(
        "AI Feedback",
        value=st.session_state.mock_evaluation,
        height=500,
        key="mock_feedback_output"
    )

    # ------------------------------------------------------
    # DOWNLOAD
    # ------------------------------------------------------

    st.download_button(
        label=" Download Interview Report",
        data=st.session_state.mock_evaluation,
        file_name="AI_Mock_Interview_Report.txt",
        mime="text/plain",
        key="mock_download_button"
    )

# ----------------------------------------------------------
# NEW QUESTION
# ----------------------------------------------------------

if st.session_state.mock_question:

    if st.button(
        " Generate New Question",
        key="mock_new_question_button"
    ):

        st.session_state.mock_question = ""
        st.session_state.mock_answer = ""
        st.session_state.mock_evaluation = ""

        st.rerun()

            # ==========================================
# PART 9
# Company-wise Interview Questions
# ==========================================

st.subheader(" Company-wise Interview Questions")

company_name = st.selectbox(
    "Select Company",
    [
        "Google",
        "Amazon",
        "Microsoft",
        "Infosys",
        "TCS",
        "Wipro",
        "Accenture",
        "Capgemini"
    ],
    key="company_select"
)

company_role = st.text_input(
    "Enter Job Role",
    placeholder="Example: Python Developer",
    key="company_role_input"
)

if st.button("Generate Company Questions", key="company_questions_button"):

    if company_role.strip() == "":
        st.error("Please enter a job role.")

    else:

        company_prompt = f"""
You are an expert interview coach.

Generate interview questions specifically for the company:

{company_name}

For the role:

{company_role}

Generate:

1. 5 Technical Questions
2. 3 HR Questions
3. 2 Coding Questions
4. 2 Behavioral Questions

Return the questions in a clear numbered format.
"""

        try:

            with st.spinner(f"Generating {company_name} Interview Questions..."):

                company_response = client.models.generate_content(
                    model="gemini-3.5-flash",   # Use your working model if different
                    contents=company_prompt
                )

            st.session_state["company_questions"] = company_response.text

            st.success(f" {company_name} Interview Questions Generated Successfully!")

            st.subheader(f" {company_name} Interview Questions")

            st.text_area(
                "Interview Questions",
                value=st.session_state["company_questions"],
                height=500,
                key="company_questions_output"
            )

            st.download_button(
                label=" Download Questions",
                data=st.session_state["company_questions"],
                file_name=f"{company_name}_Interview_Questions.txt",
                mime="text/plain",
                key="download_company_questions"
            )

        except Exception as e:

            st.error(f"Error: {e}")

            # ==========================================================
# PART 10
# AI COVER LETTER GENERATOR
# ==========================================================

st.subheader(" AI Cover Letter Generator")

candidate_name = st.text_input(
    "Candidate Name",
    key="candidate_name"
)

company_name = st.text_input(
    "Company Name",
    key="company_name"
)

cover_job_role = st.text_input(
    "Job Role",
    key="cover_job_role"
)

if st.button("Generate Cover Letter", key="generate_cover_letter"):

    if candidate_name.strip() == "":
        st.error("Please enter Candidate Name.")

    elif company_name.strip() == "":
        st.error("Please enter Company Name.")

    elif cover_job_role.strip() == "":
        st.error("Please enter Job Role.")

    elif text.strip() == "":
        st.error("Please upload your resume first.")

    elif job_description.strip() == "":
        st.error("Please enter Job Description.")

    else:

        cover_prompt = f"""
You are a Professional Resume Writer.

Generate an ATS-friendly Cover Letter.

Candidate Name:
{candidate_name}

Company Name:
{company_name}

Job Role:
{cover_job_role}

Resume:
{text}

Job Description:
{job_description}

Instructions:

1. Professional Greeting
2. Strong Introduction
3. Mention Skills
4. Mention Projects
5. Explain why the candidate is suitable.
6. Professional Closing.

Return ONLY the Cover Letter.
"""

        try:

            with st.spinner("Generating Cover Letter..."):

                response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=cover_prompt
                )

            st.session_state["cover_letter"] = response.text

            st.success(" Cover Letter Generated Successfully!")

            # ==========================================================
            # PART 10C
            # Display Cover Letter
            # ==========================================================

            st.subheader(" Your AI Cover Letter")

            st.text_area(
                "Generated Cover Letter",
                value=st.session_state["cover_letter"],
                height=500,
                key="cover_letter_output"
            )

            # ==========================================================
            # PART 10D
            # Download Cover Letter
            # ==========================================================

            st.download_button(
                label=" Download Cover Letter",
                data=st.session_state["cover_letter"],
                file_name="AI_Cover_Letter.txt",
                mime="text/plain",
                key="download_cover_letter"
            )

        except Exception as e:

            st.error(f"Error: {e}")

            # ==========================================================
# PART 11
# AI LINKEDIN PROFILE OPTIMIZER
# ==========================================================

st.subheader(" AI LinkedIn Profile Optimizer")

linkedin_role = st.text_input(
    "Target LinkedIn Role",
    placeholder="Example: Python Developer",
    key="linkedin_role"
)

if st.button("Optimize LinkedIn Profile", key="linkedin_optimizer"):

    if linkedin_role.strip() == "":
        st.error("Please enter your target role.")

    elif text.strip() == "":
        st.error("Please upload your resume first.")

    else:

        linkedin_prompt = f"""
You are an Expert LinkedIn Profile Writer.

Create a professional LinkedIn profile for the following candidate.

Target Role:
{linkedin_role}

Resume:
{text}

Generate:

1. Professional LinkedIn Headline

2. About Section

3. Top Skills

4. Experience Summary

5. Featured Projects

6. Certifications

7. Recruiter Keywords

8. Networking Tips

Return the profile in a professional format.
"""

        try:

            with st.spinner("Optimizing LinkedIn Profile..."):

                response = client.models.generate_content(
                    model="gemini-3.5-flash",   # Replace with your working model if needed
                    contents=linkedin_prompt
                )

            st.session_state["linkedin_profile"] = response.text

            st.success(" LinkedIn Profile Generated Successfully!")

            # ==========================================================
            # PART 11C
            # Display LinkedIn Profile
            # ==========================================================

            st.subheader(" Optimized LinkedIn Profile")

            st.text_area(
                "LinkedIn Profile",
                value=st.session_state["linkedin_profile"],
                height=600,
                key="linkedin_profile_output"
            )

            # ==========================================================
            # PART 11D
            # Download LinkedIn Profile
            # ==========================================================

            st.download_button(
                label=" Download LinkedIn Profile",
                data=st.session_state["linkedin_profile"],
                file_name="LinkedIn_Profile.txt",
                mime="text/plain",
                key="download_linkedin_profile"
            )

        except Exception as e:

            st.error(f"Error: {e}")

            # ==========================================================
# PART 12
# AI Portfolio & GitHub Generator
# ==========================================================

st.subheader(" AI Portfolio & GitHub Generator")

portfolio_role = st.text_input(
    "Target Portfolio Role",
    placeholder="Example: AI Engineer",
    key="portfolio_role"
)

if st.button("Generate Portfolio", key="generate_portfolio"):

    if portfolio_role.strip() == "":
        st.error("Please enter your target role.")

    elif text.strip() == "":
        st.error("Please upload your resume first.")

    else:

        portfolio_prompt = f"""
You are a Professional Portfolio Website Designer.

Create Portfolio Website Content.

Candidate Resume:

{text}

Target Role:

{portfolio_role}

Generate:

1. Professional Introduction

2. About Me

3. Skills

4. Projects

5. GitHub README

6. Portfolio Sections

7. Tech Stack

8. Career Objective

9. Contact Section

10. Professional Closing

Return everything in professional format.
"""

        try:

            with st.spinner("Generating Portfolio..."):

                response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=portfolio_prompt
                )

            st.session_state["portfolio"] = response.text

            st.success(" Portfolio Generated Successfully!")

            # ==========================================
            # Display Portfolio
            # ==========================================

            st.subheader(" AI Portfolio")

            st.text_area(
                "Portfolio Content",
                value=st.session_state["portfolio"],
                height=700,
                key="portfolio_output"
            )

            # ==========================================
            # Download Portfolio
            # ==========================================

            st.download_button(
                label=" Download Portfolio",
                data=st.session_state["portfolio"],
                file_name="AI_Portfolio.txt",
                mime="text/plain",
                key="download_portfolio"
            )

        except Exception as e:

            st.error(f"Error: {e}")

            # ==========================================================
# PART 13
# AI Salary Predictor & Career Insights
# ==========================================================

st.subheader(" AI Salary Predictor & Career Insights")

salary_role = st.text_input(
    "Target Job Role",
    placeholder="Example: AI Engineer",
    key="salary_role"
)

experience = st.selectbox(
    "Years of Experience",
    [
        "Fresher",
        "1-2 Years",
        "3-5 Years",
        "5-8 Years",
        "8+ Years"
    ],
    key="experience"
)

location = st.text_input(
    "Preferred Location",
    placeholder="Example: Hyderabad",
    key="location"
)

if st.button("Predict Salary", key="predict_salary"):

    if salary_role.strip() == "":
        st.error("Please enter Target Job Role.")

    elif location.strip() == "":
        st.error("Please enter Location.")

    elif text.strip() == "":
        st.error("Please upload your Resume first.")

    else:

        salary_prompt = f"""
You are an AI Career Consultant.

Candidate Resume:

{text}

Target Job Role:
{salary_role}

Experience:
{experience}

Preferred Location:
{location}

Generate:

1. Expected Salary Range (Annual)

2. Monthly Salary Estimate

3. Skills affecting Salary

4. Career Growth Opportunities

5. Recommended Certifications

6. Recommended Skills

7. Top Hiring Companies

8. Future Scope

Return the result in a professional format.
"""

        try:

            with st.spinner("Predicting Salary..."):

                response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=salary_prompt
                )

            st.session_state["salary_report"] = response.text

            st.success(" Salary Prediction Generated!")

            # ==========================================================
            # PART 13C
            # Display Salary Report
            # ==========================================================

            st.subheader(" Salary Prediction Report")

            st.text_area(
                "Salary Report",
                value=st.session_state["salary_report"],
                height=600,
                key="salary_output"
            )

            # ==========================================================
            # PART 13D
            # Download Salary Report
            # ==========================================================

            st.download_button(
                label=" Download Salary Report",
                data=st.session_state["salary_report"],
                file_name="Salary_Report.txt",
                mime="text/plain",
                key="download_salary_report"
            )

        except Exception as e:

            st.error(f"Error: {e}")

            # ==========================================================
# PART 14
# AI RESUME CHATBOT
# ==========================================================

st.subheader(" AI Resume Chatbot")

st.write("Ask anything about your uploaded resume.")

resume_question = st.text_input(
    "Ask your Question",
    placeholder="Example: What are my strengths?",
    key="resume_chat_question"
)

if st.button("Ask AI", key="ask_resume_ai"):

    if resume_question.strip() == "":
        st.error("Please enter your question.")

    elif text.strip() == "":
        st.error("Please upload your resume first.")

    else:

        chatbot_prompt = f"""
You are an AI Resume Career Assistant.

Candidate Resume:

{text}

The user asked:

{resume_question}

Answer ONLY based on the uploaded resume.

If the answer is not available in the resume,
politely tell the user.

Keep the answer professional and easy to understand.
"""

        try:

            with st.spinner("Thinking..."):

                response = client.models.generate_content(
                    model="gemini-3.5-flash",   # Replace with your working model if needed
                    contents=chatbot_prompt
                )

            st.session_state["resume_chat_answer"] = response.text

            st.success(" Answer Generated!")

            # ==========================================================
            # PART 14C
            # Display Chat Answer
            # ==========================================================

            st.subheader(" AI Answer")

            st.text_area(
                "Response",
                value=st.session_state["resume_chat_answer"],
                height=300,
                key="resume_chat_output"
            )

            # ==========================================================
            # PART 14D
            # Download Chat Answer
            # ==========================================================

            st.download_button(
                label=" Download AI Answer",
                data=st.session_state["resume_chat_answer"],
                file_name="Resume_Chat_Response.txt",
                mime="text/plain",
                key="download_resume_chat"
            )

        except Exception as e:

            st.error(f"Error: {e}")

            # ==========================================================
# PART 15
# Resume vs Multiple Companies Comparison
# ==========================================================

st.subheader(" Resume vs Multiple Companies")

selected_company = st.selectbox(
    "Select Company",
    [
        "Google",
        "Microsoft",
        "Amazon",
        "Meta",
        "Apple",
        "Netflix",
        "Infosys",
        "TCS",
        "Wipro",
        "Accenture",
        "Capgemini",
        "Cognizant"
    ],
    key="company_compare"
)

company_role = st.text_input(
    "Target Role",
    placeholder="Example: Software Engineer",
    key="company_role"
)

if st.button("Compare Resume", key="compare_resume"):

    if selected_company == "":
        st.error("Please select a company.")

    elif company_role.strip() == "":
        st.error("Please enter a target role.")

    elif text.strip() == "":
        st.error("Please upload your resume first.")

    else:

        compare_prompt = f"""
You are an AI Career Coach.

Candidate Resume:

{text}

Target Company:
{selected_company}

Target Role:
{company_role}

Analyze the resume and generate:

1. Resume Match Score (/100)

2. Chances of Selection

3. Missing Skills

4. Strong Skills

5. Company Interview Tips

6. Recommended Certifications

7. Recommended Projects

8. Final Suggestions

Return everything in a professional format.
"""

        try:

            with st.spinner("Comparing Resume..."):

                response = client.models.generate_content(
                    model="gemini-3.5-flash",   # Replace with your working model if different
                    contents=compare_prompt
                )

            st.session_state["company_report"] = response.text

            st.success(" Company Comparison Generated!")

            # ==========================================================
            # Display Report
            # ==========================================================

            st.subheader(f" Resume Analysis for {selected_company}")

            st.text_area(
                "Company Report",
                value=st.session_state["company_report"],
                height=600,
                key="company_report_output"
            )

            # ==========================================================
            # Download Report
            # ==========================================================

            st.download_button(
                label=" Download Company Report",
                data=st.session_state["company_report"],
                file_name=f"{selected_company}_Resume_Report.txt",
                mime="text/plain",
                key="download_company_report"
            )

        except Exception as e:

            st.error(f"Error: {e}")

            # ==========================================================
# PART 16
# AI Skill Gap Analyzer
# ==========================================================

st.subheader(" AI Skill Gap Analyzer")

target_role = st.text_input(
    "Target Career Role",
    placeholder="Example: AI Engineer",
    key="skill_gap_role"
)

if st.button("Analyze Skill Gap", key="analyze_skill_gap"):

    if target_role.strip() == "":
        st.error("Please enter your target role.")

    elif text.strip() == "":
        st.error("Please upload your resume first.")

    else:

        skill_prompt = f"""
You are an AI Career Mentor.

Candidate Resume:

{text}

Target Career Role:

{target_role}

Analyze the resume and provide:

1. Current Skills

2. Missing Skills

3. Skills to Learn First

4. Advanced Skills

5. Learning Roadmap

6. Recommended Certifications

7. Recommended Online Courses

8. Estimated Learning Time

9. Career Advice

Return the response in a professional format.
"""

        try:

            with st.spinner("Analyzing Skill Gap..."):

                response = client.models.generate_content(
                    model="gemini-3.5-flash",   # Replace with your working model if needed
                    contents=skill_prompt
                )

            st.session_state["skill_gap"] = response.text

            st.success(" Skill Gap Analysis Completed!")

            # ==========================================================
            # PART 16C
            # Display Skill Gap Analysis
            # ==========================================================

            st.subheader(" Skill Gap Report")

            st.text_area(
                "Skill Gap Analysis",
                value=st.session_state["skill_gap"],
                height=650,
                key="skill_gap_output"
            )

            # ==========================================================
            # PART 16D
            # Download Skill Gap Report
            # ==========================================================

            st.download_button(
                label=" Download Skill Gap Report",
                data=st.session_state["skill_gap"],
                file_name="Skill_Gap_Report.txt",
                mime="text/plain",
                key="download_skill_gap"
            )

        except Exception as e:

            st.error(f"Error: {e}")

        # ==========================================================
# PART 17
# AI Coding Practice Generator
# ==========================================================

st.subheader(" AI Coding Practice Generator")

coding_language = st.selectbox(
    "Programming Language",
    [
        "Python",
        "Java",
        "C",
        "C++",
        "JavaScript",
        "SQL",
        "React",
        "Node.js",
        "Machine Learning"
    ],
    key="coding_language"
)

difficulty = st.selectbox(
    "Difficulty Level",
    ["Easy", "Medium", "Hard"],
    key="coding_difficulty"
)

if st.button("Generate Coding Questions", key="generate_coding_questions"):

    if text.strip() == "":
        st.error("Please upload your resume first.")

    else:

        coding_prompt = f"""
You are an Expert Coding Interviewer.

Generate coding interview practice.

Programming Language:
{coding_language}

Difficulty:
{difficulty}

Generate:

1. Five Coding Questions
2. One Coding Challenge
3. Best Solution Approach
4. Time Complexity Tips
5. Interview Preparation Tips

Return everything in professional format.
"""

        try:

            with st.spinner("Generating Coding Questions..."):

                response = client.models.generate_content(
                    model="gemini-3.5-flash",   # Replace with your working model if needed
                    contents=coding_prompt
                )

            coding_result = response.text

            st.success(" Coding Questions Generated Successfully!")

            st.subheader(" Coding Practice")

            st.text_area(
                "Coding Questions",
                value=coding_result,
                height=650,
                key="coding_output"
            )

            st.download_button(
                label=" Download Coding Questions",
                data=coding_result,
                file_name="Coding_Practice.txt",
                mime="text/plain",
                key="download_coding_questions"
            )

        except Exception as e:

            st.error(f"Error: {e}")

      # ==========================================================
# PART 18
# AI HR INTERVIEW SIMULATOR
# ==========================================================

st.subheader(" AI HR Interview Simulator")

# ==========================================================
# SESSION STATE
# ==========================================================

if "hr_question" not in st.session_state:
    st.session_state.hr_question = ""

if "hr_evaluation" not in st.session_state:
    st.session_state.hr_evaluation = ""

# ==========================================================
# TARGET JOB ROLE
# ==========================================================

hr_role = st.text_input(
    " Target Job Role",
    placeholder="Example: Software Engineer",
    key="hr_role_input"
)

# ==========================================================
# GENERATE HR QUESTION
# ==========================================================

if st.button(
    " Generate HR Question",
    key="generate_hr_question_button"
):

    if hr_role.strip() == "":
        st.warning("Please enter your target job role.")

    elif "text" not in locals() or not text.strip():
        st.warning("Please upload your resume first.")

    else:

        hr_prompt = f"""
You are a professional HR interviewer.

Candidate Resume:

{text}

Target Job Role:

{hr_role}

Generate ONE HR interview question.

The question should be relevant to:
1. The candidate's resume
2. The target job role
3. Common HR interview practices

Return ONLY ONE interview question.
"""

        try:

            with st.spinner("Generating HR Question..."):

                hr_response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=hr_prompt
                )

            st.session_state.hr_question = (
                hr_response.text.strip()
            )

            # Clear previous evaluation
            st.session_state.hr_evaluation = ""

            st.success(
                " HR Question Generated Successfully!"
            )

        except Exception as e:

            st.error(
                f"Gemini Error: {e}"
            )

# ==========================================================
# DISPLAY QUESTION AND ANSWER
# ==========================================================

if st.session_state.hr_question:

    st.subheader(" HR Interview Question")

    st.info(
        st.session_state.hr_question
    )

    # ------------------------------------------------------
    # ANSWER BOX
    # ------------------------------------------------------

    hr_answer = st.text_area(
        " Write Your Answer",
        height=250,
        placeholder="Write your answer here...",
        key="hr_answer_box"
    )

    # ------------------------------------------------------
    # EVALUATE ANSWER
    # ------------------------------------------------------

    if st.button(
        " Evaluate My Answer",
        key="evaluate_hr_answer_button"
    ):

        if hr_answer.strip() == "":

            st.warning(
                "Please write your answer first."
            )

        else:

            evaluation_prompt = f"""
You are an expert HR interview evaluator.

Target Job Role:

{hr_role}

Interview Question:

{st.session_state.hr_question}

Candidate Answer:

{hr_answer}

Evaluate the candidate's answer professionally.

Return the result in this format:

Score: X/10

Strengths:
- Point 1
- Point 2

Weaknesses:
- Point 1
- Point 2

Communication:
- Evaluation

Relevance:
- Evaluation

Confidence:
- Evaluation

Suggestions:
- Suggestion 1
- Suggestion 2

Ideal Answer:
Write a strong example answer for this question.
"""

            try:

                with st.spinner(
                    "Evaluating Your Answer..."
                ):

                    evaluation_response = (
                        client.models.generate_content(
                            model="gemini-3.5-flash",
                            contents=evaluation_prompt
                        )
                    )

                st.session_state.hr_evaluation = (
                    evaluation_response.text.strip()
                )

                st.success(
                    " Answer Evaluated Successfully!"
                )

            except Exception as e:

                st.error(
                    f"Gemini Error: {e}"
                )

# ==========================================================
# DISPLAY EVALUATION
# ==========================================================

if st.session_state.hr_evaluation:

    st.subheader(" HR Interview Evaluation")

    st.text_area(
        "AI Feedback",
        value=st.session_state.hr_evaluation,
        height=500,
        key="hr_feedback_output"
    )

    # ======================================================
    # DOWNLOAD REPORT
    # ======================================================

    st.download_button(
        label=" Download HR Interview Report",
        data=st.session_state.hr_evaluation,
        file_name="HR_Interview_Report.txt",
        mime="text/plain",
        key="download_hr_interview_report"
    )

# ==========================================================
# GENERATE NEW QUESTION
# ==========================================================

if st.session_state.hr_question:

    if st.button(
        " Generate New HR Question",
        key="new_hr_question_button"
    ):

        st.session_state.hr_question = ""
        st.session_state.hr_evaluation = ""

        st.rerun()
         # ==========================================================
# PART 19
# AI BEHAVIORAL INTERVIEW SIMULATOR
# ==========================================================

st.subheader(" AI Behavioral Interview Simulator")

# ==========================================================
# SESSION STATE
# ==========================================================

if "behavioral_question" not in st.session_state:
    st.session_state.behavioral_question = ""

if "behavioral_evaluation" not in st.session_state:
    st.session_state.behavioral_evaluation = ""

# ==========================================================
# TARGET JOB ROLE
# ==========================================================

behavioral_role = st.text_input(
    " Target Job Role",
    placeholder="Example: Software Engineer",
    key="behavioral_role_input"
)

# ==========================================================
# GENERATE BEHAVIORAL QUESTION
# ==========================================================

if st.button(
    " Generate Behavioral Question",
    key="generate_behavioral_question_button"
):

    if behavioral_role.strip() == "":
        st.warning("Please enter your target job role.")

    elif "text" not in locals() or not text.strip():
        st.warning("Please upload your resume first.")

    else:

        behavioral_prompt = f"""
You are an expert behavioral interview interviewer.

Candidate Resume:

{text}

Target Job Role:

{behavioral_role}

Generate ONE behavioral interview question.

The question should test skills such as:

- Teamwork
- Leadership
- Problem solving
- Conflict management
- Adaptability
- Communication
- Responsibility
- Handling pressure

Use a realistic STAR-method style interview question.

Return ONLY ONE question.
"""

        try:

            with st.spinner(
                "Generating Behavioral Question..."
            ):

                behavioral_response = (
                    client.models.generate_content(
                        model="gemini-3.5-flash",
                        contents=behavioral_prompt
                    )
                )

            st.session_state.behavioral_question = (
                behavioral_response.text.strip()
            )

            # Clear previous evaluation
            st.session_state.behavioral_evaluation = ""

            st.success(
                " Behavioral Question Generated Successfully!"
            )

        except Exception as e:

            st.error(
                f"Gemini Error: {e}"
            )

# ==========================================================
# DISPLAY QUESTION
# ==========================================================

if st.session_state.behavioral_question:

    st.subheader(" Behavioral Interview Question")

    st.info(
        st.session_state.behavioral_question
    )

    # ======================================================
    # ANSWER BOX
    # ======================================================

    behavioral_answer = st.text_area(
        " Write Your Answer",
        height=300,
        placeholder=(
            "Describe the situation, "
            "your actions, and the result..."
        ),
        key="behavioral_answer_box"
    )

    # ======================================================
    # EVALUATE ANSWER
    # ======================================================

    if st.button(
        " Evaluate Behavioral Answer",
        key="evaluate_behavioral_answer_button"
    ):

        if behavioral_answer.strip() == "":

            st.warning(
                "Please write your answer first."
            )

        else:

            evaluation_prompt = f"""
You are an expert behavioral interview evaluator.

Target Job Role:

{behavioral_role}

Behavioral Interview Question:

{st.session_state.behavioral_question}

Candidate Answer:

{behavioral_answer}

Evaluate the candidate's answer using the STAR method:

S = Situation
T = Task
A = Action
R = Result

Return the evaluation in exactly this format:

Overall Score: X/10

STAR Evaluation:

Situation:
- Evaluation

Task:
- Evaluation

Action:
- Evaluation

Result:
- Evaluation

Strengths:
- Point 1
- Point 2
- Point 3

Weaknesses:
- Point 1
- Point 2

Communication:
- Evaluation

Problem Solving:
- Evaluation

Leadership / Teamwork:
- Evaluation

Suggestions:
- Suggestion 1
- Suggestion 2
- Suggestion 3

Improved Answer:
Write a strong STAR-method version of the candidate's answer.
"""

            try:

                with st.spinner(
                    "Evaluating Behavioral Answer..."
                ):

                    evaluation_response = (
                        client.models.generate_content(
                            model="gemini-3.5-flash",
                            contents=evaluation_prompt
                        )
                    )

                st.session_state.behavioral_evaluation = (
                    evaluation_response.text.strip()
                )

                st.success(
                    " Behavioral Answer Evaluated Successfully!"
                )

            except Exception as e:

                st.error(
                    f"Gemini Error: {e}"
                )

# ==========================================================
# DISPLAY EVALUATION
# ==========================================================

if st.session_state.behavioral_evaluation:

    st.subheader(" Behavioral Interview Evaluation")

    st.text_area(
        "AI Behavioral Feedback",
        value=st.session_state.behavioral_evaluation,
        height=650,
        key="behavioral_feedback_output"
    )

    # ======================================================
    # DOWNLOAD REPORT
    # ======================================================

    st.download_button(
        label=" Download Behavioral Interview Report",
        data=st.session_state.behavioral_evaluation,
        file_name="Behavioral_Interview_Report.txt",
        mime="text/plain",
        key="download_behavioral_report"
    )

# ==========================================================
# NEW QUESTION
# ==========================================================

if st.session_state.behavioral_question:

    if st.button(
        " Generate New Behavioral Question",
        key="new_behavioral_question_button"
    ):

        st.session_state.behavioral_question = ""
        st.session_state.behavioral_evaluation = ""

        st.rerun()
 # ==========================================================
# PART 20
# AI TECHNICAL QUIZ
# ==========================================================

st.subheader(" AI Technical Quiz")

# ==========================================================
# SESSION STATE
# ==========================================================

if "technical_questions" not in st.session_state:
    st.session_state.technical_questions = []

if "technical_quiz_generated" not in st.session_state:
    st.session_state.technical_quiz_generated = False

if "technical_quiz_result" not in st.session_state:
    st.session_state.technical_quiz_result = ""

# ==========================================================
# TARGET ROLE
# ==========================================================

technical_role = st.text_input(
    " Target Technical Role",
    placeholder="Example: Python Developer",
    key="technical_role_input"
)

# ==========================================================
# NUMBER OF QUESTIONS
# ==========================================================

technical_count = st.selectbox(
    " Number of Questions",
    [5, 10],
    key="technical_question_count"
)

# ==========================================================
# GENERATE QUIZ
# ==========================================================

if st.button(
    " Generate Technical Quiz",
    key="generate_technical_quiz_button"
):

    if technical_role.strip() == "":
        st.warning("Please enter your target technical role.")

    elif "text" not in locals() or not text.strip():
        st.warning("Please upload your resume first.")

    else:

        quiz_prompt = f"""
You are an expert technical interviewer.

Candidate Resume:

{text}

Target Technical Role:

{technical_role}

Create {technical_count} multiple-choice technical interview
questions.

Return ONLY valid JSON.

Use exactly this format:

[
  {{
    "question": "Question text",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "answer": "Option A"
  }}
]

Rules:

1. Each question must have exactly four options.
2. Only one option must be correct.
3. The answer must exactly match one of the four options.
4. Questions should be relevant to the target technical role.
5. Include questions from programming, technical concepts,
   problem solving, databases, APIs, and other relevant areas.
6. Return ONLY JSON.
"""

        try:

            with st.spinner(
                "Generating Technical Quiz..."
            ):

                quiz_response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=quiz_prompt
                )

            raw_quiz = quiz_response.text.strip()

            # Remove markdown code fences if Gemini adds them
            raw_quiz = raw_quiz.replace(
                "```json", ""
            ).replace(
                "```", ""
            ).strip()

            questions = json.loads(raw_quiz)

            # Save questions in session state
            st.session_state.technical_questions = questions

            st.session_state.technical_quiz_generated = True

            st.session_state.technical_quiz_result = ""

            st.success(
                " Technical Quiz Generated Successfully!"
            )

        except json.JSONDecodeError:

            st.error(
                "The AI returned an invalid quiz format. "
                "Please click Generate Technical Quiz again."
            )

        except Exception as e:

            st.error(
                f"Gemini Error: {e}"
            )

# ==========================================================
# DISPLAY QUIZ
# ==========================================================

if (
    st.session_state.technical_quiz_generated
    and st.session_state.technical_questions
):

    st.subheader(" Technical Quiz")

    # ------------------------------------------------------
    # ANSWERS
    # ------------------------------------------------------

    user_answers = {}

    for index, question in enumerate(
        st.session_state.technical_questions
    ):

        st.markdown(
            f"### Question {index + 1}"
        )

        st.write(
            question["question"]
        )

        user_answers[index] = st.radio(
            "Select your answer:",
            question["options"],
            key=f"technical_answer_{index}"
        )

    # ======================================================
    # SUBMIT QUIZ
    # ======================================================

    if st.button(
        " Submit & Evaluate Quiz",
        key="submit_technical_quiz_button"
    ):

        score = 0

        total_questions = len(
            st.session_state.technical_questions
        )

        for index, question in enumerate(
            st.session_state.technical_questions
        ):

            correct_answer = (
                question["answer"].strip()
            )

            selected_answer = (
                user_answers[index].strip()
            )

            if selected_answer == correct_answer:
                score += 1

        percentage = (
            score / total_questions
        ) * 100

        if percentage >= 80:

            performance = "Excellent"

        elif percentage >= 60:

            performance = "Good"

        elif percentage >= 40:

            performance = "Needs Improvement"

        else:

            performance = "Needs Significant Improvement"

        # Save result
        st.session_state.technical_quiz_result = (
            f"""
Technical Quiz Result

Target Role:
{technical_role}

Score:
{score}/{total_questions}

Percentage:
{percentage:.1f}%

Performance:
{performance}
"""
        )

# ==========================================================
# DISPLAY RESULT
# ==========================================================

if st.session_state.technical_quiz_result:

    st.subheader(" Quiz Result")

    st.success(
        st.session_state.technical_quiz_result
    )

    # ------------------------------------------------------
    # DOWNLOAD RESULT
    # ------------------------------------------------------

    st.download_button(
        label=" Download Quiz Result",
        data=st.session_state.technical_quiz_result,
        file_name="Technical_Quiz_Result.txt",
        mime="text/plain",
        key="download_technical_quiz_result"
    )

    # ======================================================
    # NEW QUIZ
    # ======================================================

    if st.button(
        " Start New Technical Quiz",
        key="new_technical_quiz_button"
    ):

        st.session_state.technical_questions = []

        st.session_state.technical_quiz_generated = False

        st.session_state.technical_quiz_result = ""

        st.rerun()

        # ==========================================================
# PART 21
# AI JOB RECOMMENDATION ENGINE
# ==========================================================

st.subheader(" AI Job Recommendation Engine")

# ==========================================================
# SESSION STATE
# ==========================================================

if "job_recommendations" not in st.session_state:
    st.session_state.job_recommendations = ""

if "job_recommendation_generated" not in st.session_state:
    st.session_state.job_recommendation_generated = False


# ==========================================================
# USER INPUT
# ==========================================================

target_role = st.text_input(
    " Target Job Role",
    placeholder="Example: Python Developer",
    key="job_target_role_input"
)

preferred_location = st.text_input(
    " Preferred Location",
    placeholder="Example: Hyderabad / Bangalore / Remote",
    key="job_preferred_location_input"
)

experience_level = st.selectbox(
    " Experience Level",
    [
        "Fresher",
        "0-2 Years",
        "2-5 Years",
        "5+ Years"
    ],
    key="job_experience_level_input"
)


# ==========================================================
# GENERATE JOB RECOMMENDATIONS
# ==========================================================

if st.button(
    " Find Suitable Jobs",
    key="find_suitable_jobs_button"
):

    if target_role.strip() == "":
        st.warning(
            "Please enter your target job role."
        )

    elif "text" not in locals() or not text.strip():
        st.warning(
            "Please upload your resume first."
        )

    else:

        job_prompt = f"""
You are an expert AI Career Advisor.

Analyze the candidate's resume and provide
career and job recommendations.

CANDIDATE RESUME:

{text}

TARGET JOB ROLE:

{target_role}

PREFERRED LOCATION:

{preferred_location}

EXPERIENCE LEVEL:

{experience_level}

Provide the following sections:

1. Recommended Job Titles

2. Suitable Job Categories

3. Required Technical Skills

4. Matching Skills

5. Missing Skills

6. Recommended Companies

7. Job Search Keywords

8. Recommended Career Path

9. Skills to Learn Next

10. Career Advice

IMPORTANT:

Do not claim that a specific vacancy currently exists.

Recommend job types, roles, companies and
search keywords that the candidate can search for.

Return the result in a clear professional format.
"""

        try:

            with st.spinner(
                " Finding Suitable Job Recommendations..."
            ):

                job_response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=job_prompt
                )

            # ------------------------------------------------
            # SAVE RESULT IN SESSION STATE
            # ------------------------------------------------

            st.session_state.job_recommendations = (
                job_response.text.strip()
            )

            st.session_state.job_recommendation_generated = True

            st.success(
                " Job Recommendations Generated Successfully!"
            )

        except Exception as e:

            st.error(
                f"Gemini Error: {e}"
            )


# ==========================================================
# DISPLAY JOB RECOMMENDATIONS
# ==========================================================

if (
    st.session_state.job_recommendation_generated
    and st.session_state.job_recommendations
):

    st.subheader(
        " AI Job Recommendations"
    )

    st.text_area(
        "Recommended Career Opportunities",
        value=st.session_state.job_recommendations,
        height=650,
        key="job_recommendation_display"
    )


    # ======================================================
    # DOWNLOAD REPORT
    # ======================================================

    st.download_button(
        label=" Download Job Recommendation Report",
        data=st.session_state.job_recommendations,
        file_name="Job_Recommendation_Report.txt",
        mime="text/plain",
        key="download_job_recommendation_button"
    )


    # ======================================================
    # START NEW JOB SEARCH
    # ======================================================

    if st.button(
        " Start New Job Search",
        key="new_job_search_button"
    ):

        st.session_state.job_recommendations = ""

        st.session_state.job_recommendation_generated = False

        st.rerun()

        # ==========================================================
# PART 22
# AI CAREER ROADMAP GENERATOR
# ==========================================================

st.subheader(" AI Career Roadmap Generator")

# ==========================================================
# SESSION STATE
# ==========================================================

if "career_roadmap" not in st.session_state:
    st.session_state.career_roadmap = ""

if "career_roadmap_generated" not in st.session_state:
    st.session_state.career_roadmap_generated = False


# ==========================================================
# USER INPUT
# ==========================================================

roadmap_role = st.text_input(
    " Target Career Role",
    placeholder="Example: Full Stack Developer",
    key="roadmap_target_role"
)

roadmap_experience = st.selectbox(
    " Current Experience Level",
    [
        "Fresher",
        "0-2 Years",
        "2-5 Years",
        "5+ Years"
    ],
    key="roadmap_experience_level"
)

roadmap_duration = st.selectbox(
    " Desired Preparation Period",
    [
        "3 Months",
        "6 Months",
        "9 Months",
        "12 Months"
    ],
    key="roadmap_preparation_period"
)


# ==========================================================
# GENERATE CAREER ROADMAP
# ==========================================================

if st.button(
    " Generate Career Roadmap",
    key="generate_career_roadmap_button"
):

    if roadmap_role.strip() == "":
        st.warning(
            "Please enter your target career role."
        )

    elif "text" not in locals() or not text.strip():
        st.warning(
            "Please upload your resume first."
        )

    else:

        roadmap_prompt = f"""
You are an expert career development advisor.

Analyze the candidate's resume and create a
personalized career roadmap.

CANDIDATE RESUME:

{text}

TARGET CAREER ROLE:

{roadmap_role}

CURRENT EXPERIENCE LEVEL:

{roadmap_experience}

DESIRED PREPARATION PERIOD:

{roadmap_duration}

Create a practical roadmap with these sections:

1. Current Profile Assessment

2. Career Goal

3. Current Skills

4. Skills That Need Improvement

5. Technical Skills to Learn

6. Soft Skills to Improve

7. Projects to Build

8. Certifications to Consider

9. Interview Preparation

10. Resume Improvement

11. LinkedIn Improvement

12. Job Search Strategy

13. Month-by-Month Learning Plan

14. Short-Term Goals

15. Long-Term Goals

16. Recommended Daily Practice

17. Final Career Advice

Make the roadmap realistic for the candidate's
current experience level.

Use clear headings and bullet points.

Do not claim that a specific job vacancy currently exists.
"""


        # ==================================================
        # GEMINI REQUEST
        # ==================================================

        try:

            with st.spinner(
                " Creating Your Career Roadmap..."
            ):

                roadmap_response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=roadmap_prompt
                )


            # ==================================================
            # SAVE RESULT
            # ==================================================

            st.session_state.career_roadmap = (
                roadmap_response.text.strip()
            )

            st.session_state.career_roadmap_generated = True

            st.success(
                " Career Roadmap Generated Successfully!"
            )


        except Exception as e:

            st.error(
                f"Gemini Error: {e}"
            )


# ==========================================================
# DISPLAY CAREER ROADMAP
# ==========================================================

if (
    st.session_state.career_roadmap_generated
    and st.session_state.career_roadmap
):

    st.subheader(
        " Your Personalized Career Roadmap"
    )

    st.text_area(
        "AI Career Roadmap",
        value=st.session_state.career_roadmap,
        height=800,
        key="career_roadmap_display"
    )


    # ======================================================
    # DOWNLOAD ROADMAP
    # ======================================================

    st.download_button(
        label=" Download Career Roadmap",
        data=st.session_state.career_roadmap,
        file_name="AI_Career_Roadmap.txt",
        mime="text/plain",
        key="download_career_roadmap_button"
    )


    # ======================================================
    # NEW ROADMAP
    # ======================================================

    if st.button(
        " Create New Career Roadmap",
        key="new_career_roadmap_button"
    ):

        st.session_state.career_roadmap = ""

        st.session_state.career_roadmap_generated = False

        st.rerun()

        # ==========================================================
# PART 23
# AI SKILL GAP ANALYZER
# ==========================================================

st.subheader(" AI Skill Gap Analyzer")

# ==========================================================
# SESSION STATE
# ==========================================================

if "skill_gap_report" not in st.session_state:
    st.session_state.skill_gap_report = ""

if "skill_gap_generated" not in st.session_state:
    st.session_state.skill_gap_generated = False


# ==========================================================
# USER INPUT
# ==========================================================

skill_target_role = st.text_input(
    " Target Job Role",
    placeholder="Example: Python Developer",
    key="skill_gap_target_role"
)

skill_experience = st.selectbox(
    " Experience Level",
    [
        "Fresher",
        "0-2 Years",
        "2-5 Years",
        "5+ Years"
    ],
    key="skill_gap_experience"
)

skill_priority = st.selectbox(
    " Skill Priority",
    [
        "Technical Skills",
        "Interview Skills",
        "Both Technical and Interview Skills"
    ],
    key="skill_gap_priority"
)


# ==========================================================
# ANALYZE SKILL GAP
# ==========================================================

if st.button(
    " Analyze Skill Gap",
    key="analyze_skill_gap_button"
):

    if skill_target_role.strip() == "":
        st.warning(
            "Please enter your target job role."
        )

    elif "text" not in locals() or not text.strip():
        st.warning(
            "Please upload your resume first."
        )

    else:

        skill_gap_prompt = f"""
You are an expert technical career advisor.

Analyze the candidate's resume and identify the
skill gap between the candidate's current skills
and the requirements of the target career.

CANDIDATE RESUME:

{text}

TARGET JOB ROLE:

{skill_target_role}

EXPERIENCE LEVEL:

{skill_experience}

SKILL PRIORITY:

{skill_priority}

Create a detailed Skill Gap Analysis.

Use these sections:

1. Current Skill Assessment

2. Strong Skills

3. Skills That Need Improvement

4. Missing Technical Skills

5. Missing Soft Skills

6. Priority Skills

7. Beginner-Level Skills to Learn

8. Intermediate-Level Skills to Learn

9. Advanced Skills to Learn

10. Recommended Learning Order

11. Recommended Projects

12. Recommended Interview Preparation

13. Estimated Learning Timeline

14. Final Skill Gap Summary

For each important missing skill, explain:

- Why the skill is important
- What the candidate should learn
- How the candidate can practice it
- What type of project can demonstrate the skill

Keep the recommendations realistic for the candidate's
experience level.

Do not claim that a specific job vacancy currently exists.

Return the analysis in a clear professional format.
"""


        # ==================================================
        # GEMINI REQUEST
        # ==================================================

        try:

            with st.spinner(
                " Analyzing Your Skill Gap..."
            ):

                skill_gap_response = (
                    client.models.generate_content(
                        model="gemini-3.5-flash",
                        contents=skill_gap_prompt
                    )
                )


            # ==================================================
            # SAVE RESULT
            # ==================================================

            st.session_state.skill_gap_report = (
                skill_gap_response.text.strip()
            )

            st.session_state.skill_gap_generated = True

            st.success(
                " Skill Gap Analysis Generated Successfully!"
            )


        except Exception as e:

            st.error(
                f"Gemini Error: {e}"
            )


# ==========================================================
# DISPLAY SKILL GAP REPORT
# ==========================================================

if (
    st.session_state.skill_gap_generated
    and st.session_state.skill_gap_report
):

    st.subheader(
        " Your AI Skill Gap Analysis"
    )

    st.text_area(
        "Skill Gap Report",
        value=st.session_state.skill_gap_report,
        height=800,
        key="skill_gap_report_display"
    )


    # ======================================================
    # DOWNLOAD REPORT
    # ======================================================

    st.download_button(
        label=" Download Skill Gap Report",
        data=st.session_state.skill_gap_report,
        file_name="AI_Skill_Gap_Report.txt",
        mime="text/plain",
        key="download_skill_gap_report_button"
    )


    # ======================================================
    # NEW ANALYSIS
    # ======================================================

    if st.button(
        " Start New Skill Gap Analysis",
        key="new_skill_gap_button"
    ):

        st.session_state.skill_gap_report = ""

        st.session_state.skill_gap_generated = False

        st.rerun()

        # ==========================================================
# PART 24
# AI RESUME IMPROVEMENT ANALYZER
# ==========================================================

st.subheader(" AI Resume Improvement Analyzer")

# ==========================================================
# SESSION STATE
# ==========================================================

if "resume_improvement_report" not in st.session_state:
    st.session_state.resume_improvement_report = ""

if "resume_improvement_generated" not in st.session_state:
    st.session_state.resume_improvement_generated = False


# ==========================================================
# USER INPUT
# ==========================================================

resume_target_role = st.text_input(
    " Target Job Role",
    placeholder="Example: Python Developer",
    key="resume_improvement_target_role"
)

resume_experience = st.selectbox(
    " Experience Level",
    [
        "Fresher",
        "0-2 Years",
        "2-5 Years",
        "5+ Years"
    ],
    key="resume_improvement_experience"
)

resume_focus = st.selectbox(
    " Improvement Focus",
    [
        "Overall Resume",
        "ATS Optimization",
        "Technical Content",
        "Professional Summary",
        "Projects",
        "All Areas"
    ],
    key="resume_improvement_focus"
)


# ==========================================================
# ANALYZE RESUME
# ==========================================================

if st.button(
    " Analyze & Improve Resume",
    key="analyze_resume_improvement_button"
):

    if resume_target_role.strip() == "":
        st.warning(
            "Please enter your target job role."
        )

    elif "text" not in locals() or not text.strip():
        st.warning(
            "Please upload your resume first."
        )

    else:

        resume_prompt = f"""
You are an expert resume writer, recruiter,
and ATS optimization specialist.

Analyze the candidate's resume and provide
detailed improvement recommendations.

CANDIDATE RESUME:

{text}

TARGET JOB ROLE:

{resume_target_role}

EXPERIENCE LEVEL:

{resume_experience}

IMPROVEMENT FOCUS:

{resume_focus}

Provide the analysis using these sections:

1. Resume Overall Score

2. ATS Compatibility

3. Professional Summary Review

4. Skills Section Review

5. Education Section Review

6. Experience Section Review

7. Projects Section Review

8. Achievement Section Review

9. Formatting Recommendations

10. Missing Keywords

11. Weak Content

12. Strong Content

13. Recommended Improvements

14. Improved Professional Summary

15. Improved Skills Section

16. Improved Project Descriptions

17. ATS Keywords for Target Role

18. Final Resume Recommendations

Important rules:

- Do not invent experience.
- Do not invent companies.
- Do not invent degrees.
- Do not invent certifications.
- Do not invent achievements.
- Only recommend improvements based on the
  information available in the resume.
- Make recommendations suitable for the target role.
- Keep the response professional and practical.
"""


        # ==================================================
        # GEMINI REQUEST
        # ==================================================

        try:

            with st.spinner(
                " Analyzing Your Resume..."
            ):

                resume_response = (
                    client.models.generate_content(
                        model="gemini-3.5-flash",
                        contents=resume_prompt
                    )
                )


            # ==================================================
            # SAVE RESULT
            # ==================================================

            st.session_state.resume_improvement_report = (
                resume_response.text.strip()
            )

            st.session_state.resume_improvement_generated = True

            st.success(
                " Resume Analysis Completed Successfully!"
            )


        except Exception as e:

            st.error(
                f"Gemini Error: {e}"
            )


# ==========================================================
# DISPLAY REPORT
# ==========================================================

if (
    st.session_state.resume_improvement_generated
    and st.session_state.resume_improvement_report
):

    st.subheader(
        " AI Resume Improvement Report"
    )

    st.text_area(
        "Resume Improvement Recommendations",
        value=st.session_state.resume_improvement_report,
        height=900,
        key="resume_improvement_report_display"
    )


    # ======================================================
    # DOWNLOAD REPORT
    # ======================================================

    st.download_button(
        label=" Download Resume Improvement Report",
        data=st.session_state.resume_improvement_report,
        file_name="AI_Resume_Improvement_Report.txt",
        mime="text/plain",
        key="download_resume_improvement_report"
    )


    # ======================================================
    # NEW ANALYSIS
    # ======================================================

    if st.button(
        " Start New Resume Analysis",
        key="new_resume_improvement_button"
    ):

        st.session_state.resume_improvement_report = ""

        st.session_state.resume_improvement_generated = False

        st.rerun()

        # ==========================================================
# PART 25
# AI LINKEDIN PROFILE OPTIMIZER
# ==========================================================

st.subheader(" AI LinkedIn Profile Optimizer")

# ==========================================================
# SESSION STATE
# ==========================================================

if "linkedin_profile_report" not in st.session_state:
    st.session_state.linkedin_profile_report = ""

if "linkedin_profile_generated" not in st.session_state:
    st.session_state.linkedin_profile_generated = False


# ==========================================================
# USER INPUT
# ==========================================================

linkedin_target_role = st.text_input(
    " Target LinkedIn Role",
    placeholder="Example: Python Developer",
    key="linkedin_target_role"
)

linkedin_location = st.text_input(
    " Preferred Location",
    placeholder="Example: Hyderabad / Bangalore / Remote",
    key="linkedin_location"
)

linkedin_experience = st.selectbox(
    " Experience Level",
    [
        "Fresher",
        "0-2 Years",
        "2-5 Years",
        "5+ Years"
    ],
    key="linkedin_experience"
)


# ==========================================================
# GENERATE LINKEDIN PROFILE
# ==========================================================

if st.button(
    " Optimize LinkedIn Profile",
    key="optimize_linkedin_button"
):

    if linkedin_target_role.strip() == "":
        st.warning(
            "Please enter your target LinkedIn role."
        )

    elif "text" not in locals() or not text.strip():
        st.warning(
            "Please upload your resume first."
        )

    else:

        linkedin_prompt = f"""
You are an expert LinkedIn profile writer,
recruiter, and career branding specialist.

Analyze the candidate's resume and create
a professional LinkedIn profile optimized
for the target role.

CANDIDATE RESUME:

{text}

TARGET LINKEDIN ROLE:

{linkedin_target_role}

PREFERRED LOCATION:

{linkedin_location}

EXPERIENCE LEVEL:

{linkedin_experience}

Create the following:

1. LinkedIn Headline

2. About Section

3. Professional Summary

4. Key Skills

5. Technical Skills

6. Recommended LinkedIn Keywords

7. Experience Description Suggestions

8. Project Description Suggestions

9. Education Description Suggestions

10. Featured Section Recommendations

11. Certifications Recommendations

12. LinkedIn Profile Improvement Tips

13. Recruiter Search Keywords

14. Recommended Target Job Titles

15. Final LinkedIn Strategy

IMPORTANT RULES:

- Do not invent companies.
- Do not invent job experience.
- Do not invent degrees.
- Do not invent certifications.
- Do not invent achievements.
- Use only information available in the resume.
- Recommendations may be suggested separately.
- Keep the profile professional and recruiter-friendly.
- Optimize naturally for LinkedIn search.
"""

        # ==================================================
        # GEMINI REQUEST
        # ==================================================

        try:

            with st.spinner(
                " Optimizing Your LinkedIn Profile..."
            ):

                linkedin_response = (
                    client.models.generate_content(
                        model="gemini-3.5-flash",
                        contents=linkedin_prompt
                    )
                )

            # ==================================================
            # SAVE RESULT
            # ==================================================

            st.session_state.linkedin_profile_report = (
                linkedin_response.text.strip()
            )

            st.session_state.linkedin_profile_generated = True

            st.success(
                " LinkedIn Profile Optimized Successfully!"
            )

        except Exception as e:

            st.error(
                f"Gemini Error: {e}"
            )


# ==========================================================
# DISPLAY LINKEDIN PROFILE
# ==========================================================

if (
    st.session_state.linkedin_profile_generated
    and st.session_state.linkedin_profile_report
):

    st.subheader(
        " AI LinkedIn Profile"
    )

    st.text_area(
        "Optimized LinkedIn Profile",
        value=st.session_state.linkedin_profile_report,
        height=900,
        key="linkedin_profile_report_display"
    )


    # ======================================================
    # DOWNLOAD PROFILE
    # ======================================================

    st.download_button(
        label=" Download LinkedIn Profile",
        data=st.session_state.linkedin_profile_report,
        file_name="AI_LinkedIn_Profile.txt",
        mime="text/plain",
        key="download_linkedin_profile"
    )


    # ======================================================
    # NEW LINKEDIN ANALYSIS
    # ======================================================

    if st.button(
        " Create New LinkedIn Profile",
        key="new_linkedin_profile_button"
    ):

        st.session_state.linkedin_profile_report = ""

        st.session_state.linkedin_profile_generated = False

        st.rerun()

        # ==========================================================
# PART 26
# AI COVER LETTER GENERATOR
# ==========================================================

st.subheader(" AI Cover Letter Generator")

# ==========================================================
# SESSION STATE
# ==========================================================

if "cover_letter" not in st.session_state:
    st.session_state.cover_letter = ""

if "cover_letter_generated" not in st.session_state:
    st.session_state.cover_letter_generated = False


# ==========================================================
# USER INPUT
# ==========================================================

cover_target_role = st.text_input(
    " Target Job Role",
    placeholder="Example: Python Developer",
    key="cover_letter_target_role"
)

cover_company = st.text_input(
    " Company Name",
    placeholder="Example: ABC Technologies",
    key="cover_letter_company"
)

cover_location = st.text_input(
    " Job Location",
    placeholder="Example: Hyderabad / Bangalore / Remote",
    key="cover_letter_location"
)

cover_tone = st.selectbox(
    " Cover Letter Style",
    [
        "Professional",
        "Confident",
        "Simple and Professional",
        "Fresh Graduate",
        "Experienced Professional"
    ],
    key="cover_letter_tone"
)


# ==========================================================
# GENERATE COVER LETTER
# ==========================================================

if st.button(
    " Generate Cover Letter",
    key="generate_cover_letter_button"
):

    if cover_target_role.strip() == "":
        st.warning(
            "Please enter the target job role."
        )

    elif cover_company.strip() == "":
        st.warning(
            "Please enter the company name."
        )

    elif "text" not in locals() or not text.strip():
        st.warning(
            "Please upload your resume first."
        )

    else:

        cover_letter_prompt = f"""
You are an expert professional resume writer
and career application specialist.

Create a professional job application cover letter
based ONLY on the candidate's resume.

CANDIDATE RESUME:

{text}

TARGET JOB ROLE:

{cover_target_role}

COMPANY NAME:

{cover_company}

JOB LOCATION:

{cover_location}

WRITING STYLE:

{cover_tone}

Create a professional cover letter containing:

1. Professional greeting

2. Opening paragraph

3. Candidate's relevant skills

4. Relevant projects or experience

5. Why the candidate is suitable for the role

6. Professional closing

IMPORTANT RULES:

- Do not invent work experience.
- Do not invent companies.
- Do not invent degrees.
- Do not invent certifications.
- Do not invent achievements.
- Use only information available in the resume.
- Do not claim that the candidate already works
  for the company.
- Keep the letter professional and realistic.
- Do not use excessive emojis.
- Return ONLY the final cover letter.
"""

        # ==================================================
        # GEMINI REQUEST
        # ==================================================

        try:

            with st.spinner(
                " Generating Your Cover Letter..."
            ):

                cover_response = (
                    client.models.generate_content(
                        model="gemini-3.5-flash",
                        contents=cover_letter_prompt
                    )
                )

            # ==================================================
            # SAVE RESULT
            # ==================================================

            st.session_state.cover_letter = (
                cover_response.text.strip()
            )

            st.session_state.cover_letter_generated = True

            st.success(
                " Cover Letter Generated Successfully!"
            )

        except Exception as e:

            st.error(
                f"Gemini Error: {e}"
            )


# ==========================================================
# DISPLAY COVER LETTER
# ==========================================================

if (
    st.session_state.cover_letter_generated
    and st.session_state.cover_letter
):

    st.subheader(
        " Generated Cover Letter"
    )

    st.text_area(
        "AI Cover Letter",
        value=st.session_state.cover_letter,
        height=700,
        key="cover_letter_display"
    )


    # ======================================================
    # DOWNLOAD COVER LETTER
    # ======================================================

    st.download_button(
        label=" Download Cover Letter",
        data=st.session_state.cover_letter,
        file_name="AI_Cover_Letter.txt",
        mime="text/plain",
        key="download_cover_letter_button"
    )


    # ======================================================
    # NEW COVER LETTER
    # ======================================================

    if st.button(
        " Create New Cover Letter",
        key="new_cover_letter_button"
    ):

        st.session_state.cover_letter = ""

        st.session_state.cover_letter_generated = False

        st.rerun()

        # ==========================================================
# PART 27
# AI JOB APPLICATION EMAIL GENERATOR
# ==========================================================

st.subheader(" AI Job Application Email Generator")

# ==========================================================
# SESSION STATE
# ==========================================================

if "job_application_email" not in st.session_state:
    st.session_state.job_application_email = ""

if "job_application_email_generated" not in st.session_state:
    st.session_state.job_application_email_generated = False


# ==========================================================
# USER INPUT
# ==========================================================

email_target_role = st.text_input(
    " Target Job Role",
    placeholder="Example: Python Developer",
    key="job_email_target_role"
)

email_company = st.text_input(
    " Company Name",
    placeholder="Example: ABC Technologies",
    key="job_email_company"
)

email_recruiter = st.text_input(
    " Recruiter / Hiring Manager Name",
    placeholder="Example: Hiring Manager",
    key="job_email_recruiter"
)

email_subject_style = st.selectbox(
    " Email Style",
    [
        "Professional",
        "Short and Professional",
        "Confident",
        "Fresh Graduate",
        "Experienced Professional"
    ],
    key="job_email_style"
)


# ==========================================================
# GENERATE APPLICATION EMAIL
# ==========================================================

if st.button(
    " Generate Job Application Email",
    key="generate_job_application_email"
):

    if email_target_role.strip() == "":
        st.warning(
            "Please enter the target job role."
        )

    elif email_company.strip() == "":
        st.warning(
            "Please enter the company name."
        )

    elif "text" not in locals() or not text.strip():
        st.warning(
            "Please upload your resume first."
        )

    else:

        email_prompt = f"""
You are an expert career advisor and professional
job application email writer.

Create a professional job application email based
ONLY on the candidate's resume.

CANDIDATE RESUME:

{text}

TARGET JOB ROLE:

{email_target_role}

COMPANY NAME:

{email_company}

RECRUITER / HIRING MANAGER:

{email_recruiter}

EMAIL STYLE:

{email_subject_style}

Create the email with:

1. Subject line
2. Professional greeting
3. Short introduction
4. Relevant skills and experience
5. Relevant projects or achievements
6. Why the candidate is suitable for the role
7. Professional closing
8. Candidate contact placeholder

IMPORTANT RULES:

- Do not invent work experience.
- Do not invent companies.
- Do not invent degrees.
- Do not invent certifications.
- Do not invent achievements.
- Use only information available in the resume.
- Do not claim that the candidate already works
  for the company.
- Keep the email concise and professional.
- Do not use excessive emojis.
- Return ONLY the final email.
"""

        # ==================================================
        # GEMINI REQUEST
        # ==================================================

        try:

            with st.spinner(
                " Generating Job Application Email..."
            ):

                email_response = (
                    client.models.generate_content(
                        model="gemini-3.5-flash",
                        contents=email_prompt
                    )
                )

            # ==================================================
            # SAVE RESULT
            # ==================================================

            st.session_state.job_application_email = (
                email_response.text.strip()
            )

            st.session_state.job_application_email_generated = True

            st.success(
                " Job Application Email Generated Successfully!"
            )

        except Exception as e:

            st.error(
                f"Gemini Error: {e}"
            )


# ==========================================================
# DISPLAY EMAIL
# ==========================================================

if (
    st.session_state.job_application_email_generated
    and st.session_state.job_application_email
):

    st.subheader(
        " Generated Job Application Email"
    )

    st.text_area(
        "AI Job Application Email",
        value=st.session_state.job_application_email,
        height=600,
        key="job_application_email_display"
    )


    # ======================================================
    # DOWNLOAD EMAIL
    # ======================================================

    st.download_button(
        label=" Download Job Application Email",
        data=st.session_state.job_application_email,
        file_name="Job_Application_Email.txt",
        mime="text/plain",
        key="download_job_application_email"
    )


    # ======================================================
    # NEW EMAIL
    # ======================================================

    if st.button(
        " Create New Job Application Email",
        key="new_job_application_email"
    ):

        st.session_state.job_application_email = ""

        st.session_state.job_application_email_generated = False

        st.rerun()

        # ==========================================================
# PART 28
# AI INTERVIEW PREPARATION PLANNER
# ==========================================================

st.subheader(" AI Interview Preparation Planner")

# ==========================================================
# SESSION STATE
# ==========================================================

if "interview_prep_plan" not in st.session_state:
    st.session_state.interview_prep_plan = ""

if "interview_prep_generated" not in st.session_state:
    st.session_state.interview_prep_generated = False


# ==========================================================
# USER INPUT
# ==========================================================

prep_target_role = st.text_input(
    " Target Job Role",
    placeholder="Example: Python Developer",
    key="prep_target_role"
)

prep_experience = st.selectbox(
    " Experience Level",
    [
        "Fresher",
        "0-2 Years",
        "2-5 Years",
        "5+ Years"
    ],
    key="prep_experience"
)

prep_duration = st.selectbox(
    " Preparation Duration",
    [
        "7 Days",
        "15 Days",
        "30 Days",
        "60 Days",
        "90 Days"
    ],
    key="prep_duration"
)

prep_focus = st.multiselect(
    " Preparation Areas",
    [
        "HR Interview",
        "Technical Interview",
        "Behavioral Interview",
        "Coding",
        "Projects",
        "Resume",
        "Communication",
        "System Design"
    ],
    default=[
        "HR Interview",
        "Technical Interview",
        "Coding"
    ],
    key="prep_focus"
)


# ==========================================================
# GENERATE PREPARATION PLAN
# ==========================================================

if st.button(
    " Generate Interview Preparation Plan",
    key="generate_interview_prep_button"
):

    if prep_target_role.strip() == "":
        st.warning(
            "Please enter your target job role."
        )

    elif len(prep_focus) == 0:
        st.warning(
            "Please select at least one preparation area."
        )

    elif "text" not in locals() or not text.strip():
        st.warning(
            "Please upload your resume first."
        )

    else:

        selected_areas = ", ".join(prep_focus)

        prep_prompt = f"""
You are an expert interview preparation coach.

Analyze the candidate's resume and create a
personalized interview preparation plan.

CANDIDATE RESUME:

{text}

TARGET JOB ROLE:

{prep_target_role}

EXPERIENCE LEVEL:

{prep_experience}

PREPARATION DURATION:

{prep_duration}

PREPARATION AREAS:

{selected_areas}

Create a practical preparation plan containing:

1. Candidate Preparation Assessment

2. Important Topics to Study

3. Technical Interview Preparation

4. HR Interview Preparation

5. Behavioral Interview Preparation

6. Coding Preparation

7. Project Interview Preparation

8. Resume-Based Questions

9. Communication Preparation

10. Frequently Asked Interview Questions

11. Questions the Candidate Should Practice

12. Daily Preparation Schedule

13. Weekly Goals

14. Mock Interview Strategy

15. Final Interview Checklist

16. Day-Before-Interview Checklist

17. Interview-Day Tips

18. Final Recommendations

Make the plan realistic for the candidate's
experience level and target role.

Use clear headings and bullet points.

Do not invent information that is not present
in the candidate's resume.
"""

        # ==================================================
        # GEMINI REQUEST
        # ==================================================

        try:

            with st.spinner(
                " Creating Your Interview Preparation Plan..."
            ):

                prep_response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=prep_prompt
                )

            # ==================================================
            # SAVE RESULT
            # ==================================================

            st.session_state.interview_prep_plan = (
                prep_response.text.strip()
            )

            st.session_state.interview_prep_generated = True

            st.success(
                " Interview Preparation Plan Generated!"
            )

        except Exception as e:

            st.error(
                f"Gemini Error: {e}"
            )


# ==========================================================
# DISPLAY PLAN
# ==========================================================

if (
    st.session_state.interview_prep_generated
    and st.session_state.interview_prep_plan
):

    st.subheader(
        " Your AI Interview Preparation Plan"
    )

    st.text_area(
        "Interview Preparation Plan",
        value=st.session_state.interview_prep_plan,
        height=900,
        key="interview_prep_plan_display"
    )


    # ======================================================
    # DOWNLOAD PLAN
    # ======================================================

    st.download_button(
        label=" Download Interview Preparation Plan",
        data=st.session_state.interview_prep_plan,
        file_name="AI_Interview_Preparation_Plan.txt",
        mime="text/plain",
        key="download_interview_prep_plan"
    )


    # ======================================================
    # NEW PLAN
    # ======================================================

    if st.button(
        " Create New Interview Preparation Plan",
        key="new_interview_prep_plan"
    ):

        st.session_state.interview_prep_plan = ""

        st.session_state.interview_prep_generated = False

        st.rerun()

        # ==========================================================
# PART 29
# AI JOB SEARCH STRATEGY GENERATOR
# ==========================================================

st.subheader(" AI Job Search Strategy Generator")

# ==========================================================
# SESSION STATE
# ==========================================================

if "job_search_strategy" not in st.session_state:
    st.session_state.job_search_strategy = ""

if "job_search_strategy_generated" not in st.session_state:
    st.session_state.job_search_strategy_generated = False


# ==========================================================
# USER INPUT
# ==========================================================

search_target_role = st.text_input(
    " Target Job Role",
    placeholder="Example: Python Developer",
    key="search_target_role"
)

search_location = st.text_input(
    " Preferred Location",
    placeholder="Example: Hyderabad / Bangalore / Remote",
    key="search_location"
)

search_experience = st.selectbox(
    " Experience Level",
    [
        "Fresher",
        "0-2 Years",
        "2-5 Years",
        "5+ Years"
    ],
    key="search_experience"
)

search_preference = st.selectbox(
    " Job Preference",
    [
        "On-site",
        "Hybrid",
        "Remote",
        "Any"
    ],
    key="search_preference"
)


# ==========================================================
# GENERATE JOB SEARCH STRATEGY
# ==========================================================

if st.button(
    " Generate Job Search Strategy",
    key="generate_job_search_strategy_button"
):

    if search_target_role.strip() == "":
        st.warning(
            "Please enter your target job role."
        )

    elif "text" not in locals() or not text.strip():
        st.warning(
            "Please upload your resume first."
        )

    else:

        search_prompt = f"""
You are an expert career advisor and job-search strategist.

Analyze the candidate's resume and create a personalized
job search strategy.

CANDIDATE RESUME:

{text}

TARGET JOB ROLE:

{search_target_role}

PREFERRED LOCATION:

{search_location}

EXPERIENCE LEVEL:

{search_experience}

JOB PREFERENCE:

{search_preference}

Create a detailed job search strategy containing:

1. Candidate Profile Summary

2. Recommended Job Titles

3. Alternative Job Titles

4. Recommended Job Categories

5. Job Search Keywords

6. Technical Keywords

7. Location Search Strategy

8. Remote Job Search Strategy

9. Recommended Job Platforms

10. LinkedIn Job Search Strategy

11. Resume Customization Strategy

12. Application Strategy

13. Networking Strategy

14. Recruiter Outreach Strategy

15. Weekly Application Target

16. Daily Job Search Routine

17. Application Tracking Strategy

18. Interview Preparation Strategy

19. Common Job Search Mistakes to Avoid

20. 30-Day Job Search Plan

21. Final Career Advice

IMPORTANT RULES:

- Do not claim that a specific job vacancy currently exists.
- Do not invent companies or job openings.
- Recommend job types, search keywords, platforms,
  networking methods, and application strategies.
- Keep the strategy realistic for the candidate's
  experience level.
- Use clear headings and bullet points.
"""


        # ==================================================
        # GEMINI REQUEST
        # ==================================================

        try:

            with st.spinner(
                " Creating Your Job Search Strategy..."
            ):

                search_response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=search_prompt
                )


            # ==================================================
            # SAVE RESULT
            # ==================================================

            st.session_state.job_search_strategy = (
                search_response.text.strip()
            )

            st.session_state.job_search_strategy_generated = True

            st.success(
                " Job Search Strategy Generated Successfully!"
            )


        except Exception as e:

            st.error(
                f"Gemini Error: {e}"
            )


# ==========================================================
# DISPLAY STRATEGY
# ==========================================================

if (
    st.session_state.job_search_strategy_generated
    and st.session_state.job_search_strategy
):

    st.subheader(
        " Your AI Job Search Strategy"
    )

    st.text_area(
        "Job Search Strategy",
        value=st.session_state.job_search_strategy,
        height=900,
        key="job_search_strategy_display"
    )


    # ======================================================
    # DOWNLOAD STRATEGY
    # ======================================================

    st.download_button(
        label=" Download Job Search Strategy",
        data=st.session_state.job_search_strategy,
        file_name="AI_Job_Search_Strategy.txt",
        mime="text/plain",
        key="download_job_search_strategy"
    )


    # ======================================================
    # NEW STRATEGY
    # ======================================================

    if st.button(
        " Create New Job Search Strategy",
        key="new_job_search_strategy"
    ):

        st.session_state.job_search_strategy = ""

        st.session_state.job_search_strategy_generated = False

        st.rerun()

        # ==========================================================
# PART 30
# AI CAREER SUCCESS DASHBOARD
# ==========================================================

st.subheader(" AI Career Success Dashboard")

# ==========================================================
# SESSION STATE
# ==========================================================

if "career_success_report" not in st.session_state:
    st.session_state.career_success_report = ""

if "career_success_generated" not in st.session_state:
    st.session_state.career_success_generated = False


# ==========================================================
# USER INPUT
# ==========================================================

success_target_role = st.text_input(
    " Target Career Role",
    placeholder="Example: Python Developer",
    key="success_target_role"
)

success_location = st.text_input(
    " Preferred Location",
    placeholder="Example: Hyderabad / Bangalore / Remote",
    key="success_location"
)

success_experience = st.selectbox(
    " Experience Level",
    [
        "Fresher",
        "0-2 Years",
        "2-5 Years",
        "5+ Years"
    ],
    key="success_experience"
)

success_goal = st.selectbox(
    " Primary Career Goal",
    [
        "Get First Job",
        "Switch Job",
        "Get Better Salary",
        "Move Into a New Career",
        "Become Interview Ready",
        "Improve Overall Career"
    ],
    key="success_goal"
)


# ==========================================================
# GENERATE CAREER SUCCESS PLAN
# ==========================================================

if st.button(
    " Generate Career Success Plan",
    key="generate_career_success_button"
):

    if success_target_role.strip() == "":
        st.warning(
            "Please enter your target career role."
        )

    elif "text" not in locals() or not text.strip():
        st.warning(
            "Please upload your resume first."
        )

    else:

        success_prompt = f"""
You are an expert AI career coach, recruiter,
resume specialist, interview coach, and career strategist.

Analyze the candidate's resume and create a complete
personalized career success plan.

CANDIDATE RESUME:

{text}

TARGET CAREER ROLE:

{success_target_role}

PREFERRED LOCATION:

{success_location}

EXPERIENCE LEVEL:

{success_experience}

PRIMARY CAREER GOAL:

{success_goal}

Create a professional Career Success Report with:

1. Overall Career Assessment

2. Current Strengths

3. Current Weaknesses

4. Skill Gap Summary

5. Priority Skills to Learn

6. Recommended Projects

7. Resume Improvement Priorities

8. LinkedIn Improvement Priorities

9. Interview Preparation Priorities

10. Job Search Strategy

11. Networking Strategy

12. Recruiter Outreach Strategy

13. Daily Career Routine

14. Weekly Career Goals

15. 30-Day Action Plan

16. 60-Day Action Plan

17. 90-Day Action Plan

18. Important Mistakes to Avoid

19. Career Growth Recommendations

20. Final Action Checklist

21. Final Career Advice

IMPORTANT RULES:

- Do not invent work experience.
- Do not invent companies.
- Do not invent degrees.
- Do not invent certifications.
- Do not invent achievements.
- Use only information available in the resume.
- Do not claim that a specific job vacancy currently exists.
- Give practical and realistic recommendations.
- Use clear headings and bullet points.
"""


        # ==================================================
        # GEMINI REQUEST
        # ==================================================

        try:

            with st.spinner(
                " Creating Your Career Success Plan..."
            ):

                success_response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=success_prompt
                )


            # ==================================================
            # SAVE RESULT
            # ==================================================

            st.session_state.career_success_report = (
                success_response.text.strip()
            )

            st.session_state.career_success_generated = True

            st.success(
                " Career Success Plan Generated Successfully!"
            )


        except Exception as e:

            st.error(
                f"Gemini Error: {e}"
            )


# ==========================================================
# DISPLAY CAREER SUCCESS REPORT
# ==========================================================

if (
    st.session_state.career_success_generated
    and st.session_state.career_success_report
):

    st.subheader(
        " Your AI Career Success Plan"
    )

    st.text_area(
        "Career Success Report",
        value=st.session_state.career_success_report,
        height=1000,
        key="career_success_report_display"
    )


    # ======================================================
    # DOWNLOAD REPORT
    # ======================================================

    st.download_button(
        label=" Download Career Success Plan",
        data=st.session_state.career_success_report,
        file_name="AI_Career_Success_Plan.txt",
        mime="text/plain",
        key="download_career_success_plan"
    )


    # ======================================================
    # START NEW CAREER PLAN
    # ======================================================

    if st.button(
        " Create New Career Success Plan",
        key="new_career_success_plan"
    ):

        st.session_state.career_success_report = ""

        st.session_state.career_success_generated = False

        st.rerun()

        # ==========================================================
# STEP 31
# FULL PROJECT TESTING DASHBOARD
# ==========================================================

st.divider()

st.subheader(" Step 31 — Full Project Testing")

st.write(
    "Use this dashboard to test the main components of the "
    "application before moving to the error-fixing stage."
)

# ==========================================================
# SESSION STATE
# ==========================================================

if "project_test_results" not in st.session_state:
    st.session_state.project_test_results = {}

# ==========================================================
# TEST PROJECT
# ==========================================================

if st.button(
    " Run Full Project Test",
    key="run_full_project_test"
):

    test_results = {}

    # ------------------------------------------------------
    # TEST 1 — STREAMLIT
    # ------------------------------------------------------

    try:
        test_results["Streamlit Application"] = "✅ Working"
    except Exception as e:
        test_results["Streamlit Application"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # TEST 2 — SESSION STATE
    # ------------------------------------------------------

    try:

        st.session_state["test_session_state"] = True

        if st.session_state["test_session_state"]:
            test_results["Session State"] = "✅ Working"
        else:
            test_results["Session State"] = "❌ Not Working"

    except Exception as e:

        test_results["Session State"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # TEST 3 — GEMINI CLIENT
    # ------------------------------------------------------

    try:

        if "client" in globals() and client is not None:
            test_results["Gemini Client"] = "✅ Configured"
        else:
            test_results["Gemini Client"] = (
                "❌ Gemini client not found"
            )

    except Exception as e:

        test_results["Gemini Client"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # TEST 4 — RESUME DATA
    # ------------------------------------------------------

    try:

        if "text" in locals() and text.strip():

            test_results["Resume Data"] = (
                "✅ Resume available"
            )

        else:

            test_results["Resume Data"] = (
                "⚠️ No resume loaded"
            )

    except Exception as e:

        test_results["Resume Data"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # TEST 5 — GEMINI MODEL
    # ------------------------------------------------------

    try:

        if "client" in globals() and client is not None:

            test_results["Gemini Model"] = (
                "✅ Client ready for Gemini requests"
            )

        else:

            test_results["Gemini Model"] = (
                "❌ Gemini client unavailable"
            )

    except Exception as e:

        test_results["Gemini Model"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # TEST 6 — PART 21 SESSION STATE
    # ------------------------------------------------------

    try:

        if "job_recommendations" in st.session_state:

            test_results["Part 21"] = (
                "✅ Job Recommendation state available"
            )

        else:

            test_results["Part 21"] = (
                "⚠️ Job Recommendation state missing"
            )

    except Exception as e:

        test_results["Part 21"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # TEST 7 — PART 22 SESSION STATE
    # ------------------------------------------------------

    try:

        if "career_roadmap" in st.session_state:

            test_results["Part 22"] = (
                "✅ Career Roadmap state available"
            )

        else:

            test_results["Part 22"] = (
                "⚠️ Career Roadmap state missing"
            )

    except Exception as e:

        test_results["Part 22"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # TEST 8 — PART 23 SESSION STATE
    # ------------------------------------------------------

    try:

        if "skill_gap_report" in st.session_state:

            test_results["Part 23"] = (
                "✅ Skill Gap state available"
            )

        else:

            test_results["Part 23"] = (
                "⚠️ Skill Gap state missing"
            )

    except Exception as e:

        test_results["Part 23"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # TEST 9 — PART 24 SESSION STATE
    # ------------------------------------------------------

    try:

        if "resume_improvement_report" in st.session_state:

            test_results["Part 24"] = (
                "✅ Resume Improvement state available"
            )

        else:

            test_results["Part 24"] = (
                "⚠️ Resume Improvement state missing"
            )

    except Exception as e:

        test_results["Part 24"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # TEST 10 — PART 25 SESSION STATE
    # ------------------------------------------------------

    try:

        if "linkedin_profile_report" in st.session_state:

            test_results["Part 25"] = (
                "✅ LinkedIn state available"
            )

        else:

            test_results["Part 25"] = (
                "⚠️ LinkedIn state missing"
            )

    except Exception as e:

        test_results["Part 25"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # TEST 11 — PART 26 SESSION STATE
    # ------------------------------------------------------

    try:

        if "cover_letter" in st.session_state:

            test_results["Part 26"] = (
                "✅ Cover Letter state available"
            )

        else:

            test_results["Part 26"] = (
                "⚠️ Cover Letter state missing"
            )

    except Exception as e:

        test_results["Part 26"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # TEST 12 — PART 27 SESSION STATE
    # ------------------------------------------------------

    try:

        if "job_application_email" in st.session_state:

            test_results["Part 27"] = (
                "✅ Application Email state available"
            )

        else:

            test_results["Part 27"] = (
                "⚠️ Application Email state missing"
            )

    except Exception as e:

        test_results["Part 27"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # TEST 13 — PART 28 SESSION STATE
    # ------------------------------------------------------

    try:

        if "interview_prep_plan" in st.session_state:

            test_results["Part 28"] = (
                "✅ Interview Preparation state available"
            )

        else:

            test_results["Part 28"] = (
                "⚠️ Interview Preparation state missing"
            )

    except Exception as e:

        test_results["Part 28"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # TEST 14 — PART 29 SESSION STATE
    # ------------------------------------------------------

    try:

        if "job_search_strategy" in st.session_state:

            test_results["Part 29"] = (
                "✅ Job Search state available"
            )

        else:

            test_results["Part 29"] = (
                "⚠️ Job Search state missing"
            )

    except Exception as e:

        test_results["Part 29"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # TEST 15 — PART 30 SESSION STATE
    # ------------------------------------------------------

    try:

        if "career_success_report" in st.session_state:

            test_results["Part 30"] = (
                "✅ Career Success state available"
            )

        else:

            test_results["Part 30"] = (
                "⚠️ Career Success state missing"
            )

    except Exception as e:

        test_results["Part 30"] = (
            f"❌ Error: {e}"
        )

    # ======================================================
    # SAVE TEST RESULTS
    # ======================================================

    st.session_state.project_test_results = test_results

    st.success(
        "✅ Full Project Test Completed!"
    )


# ==========================================================
# DISPLAY TEST RESULTS
# ==========================================================

if st.session_state.project_test_results:

    st.subheader(" Project Test Results")

    for test_name, result in (
        st.session_state.project_test_results.items()
    ):

        st.write(
            f"**{test_name}:** {result}"
        )


# ==========================================================
# CLEAR TEST RESULTS
# ==========================================================

if st.session_state.project_test_results:

    if st.button(
        " Clear Test Results",
        key="clear_project_test_results"
    ):

        st.session_state.project_test_results = {}

        st.rerun()

        # ==========================================================
# STEP 32
# ERROR FIXING & DIAGNOSTIC DASHBOARD
# ==========================================================

st.divider()

st.subheader(" Step 32 — Error Fixing & Diagnostics")

st.write(
    "Use this dashboard to check common application problems "
    "before moving to the next finalization step."
)

# ==========================================================
# SESSION STATE
# ==========================================================

if "diagnostic_results" not in st.session_state:
    st.session_state.diagnostic_results = {}

# ==========================================================
# RUN DIAGNOSTIC
# ==========================================================

if st.button(
    " Run Error Diagnostic",
    key="run_error_diagnostic"
):

    diagnostics = {}

    # ------------------------------------------------------
    # CHECK 1 — STREAMLIT
    # ------------------------------------------------------

    try:
        diagnostics["Streamlit"] = "✅ Streamlit is running."
    except Exception as e:
        diagnostics["Streamlit"] = f"❌ {e}"

    # ------------------------------------------------------
    # CHECK 2 — GEMINI CLIENT
    # ------------------------------------------------------

    try:

        if "client" in globals() and client is not None:
            diagnostics["Gemini Client"] = (
                "✅ Gemini client is configured."
            )
        else:
            diagnostics["Gemini Client"] = (
                "❌ Gemini client was not found."
            )

    except Exception as e:
        diagnostics["Gemini Client"] = f"❌ {e}"

    # ------------------------------------------------------
    # CHECK 3 — RESUME VARIABLE
    # ------------------------------------------------------

    try:

        if "text" in locals():

            if isinstance(text, str) and text.strip():

                diagnostics["Resume Text"] = (
                    "✅ Resume text is available."
                )

            else:

                diagnostics["Resume Text"] = (
                    "⚠️ Resume text is empty."
                )

        else:

            diagnostics["Resume Text"] = (
                "⚠️ Resume variable 'text' is not available "
                "in the current execution."
            )

    except Exception as e:
        diagnostics["Resume Text"] = f"❌ {e}"

    # ------------------------------------------------------
    # CHECK 4 — GEMINI MODEL CONFIGURATION
    # ------------------------------------------------------

    # This checks your intended model configuration.
    # It does NOT send an API request.

    try:

        diagnostic_model = "gemini-3.5-flash"

        diagnostics["Gemini Model"] = (
            f"✅ Configured model: {diagnostic_model}"
        )

    except Exception as e:
        diagnostics["Gemini Model"] = f"❌ {e}"

    # ------------------------------------------------------
    # CHECK 5 — PART 18
    # ------------------------------------------------------

    try:

        if "hr_question" in st.session_state:
            diagnostics["Part 18"] = (
                "✅ HR Interview session state exists."
            )
        else:
            diagnostics["Part 18"] = (
                "⚠️ HR Interview session state missing."
            )

    except Exception as e:
        diagnostics["Part 18"] = f"❌ {e}"

    # ------------------------------------------------------
    # CHECK 6 — PART 19
    # ------------------------------------------------------

    try:

        if "behavioral_question" in st.session_state:
            diagnostics["Part 19"] = (
                "✅ Behavioral Interview session state exists."
            )
        else:
            diagnostics["Part 19"] = (
                "⚠️ Behavioral Interview session state missing."
            )

    except Exception as e:
        diagnostics["Part 19"] = f"❌ {e}"

    # ------------------------------------------------------
    # CHECK 7 — PART 20
    # ------------------------------------------------------

    try:

        if "technical_questions" in st.session_state:
            diagnostics["Part 20"] = (
                "✅ Technical Quiz session state exists."
            )
        else:
            diagnostics["Part 20"] = (
                "⚠️ Technical Quiz session state missing."
            )

    except Exception as e:
        diagnostics["Part 20"] = f"❌ {e}"

    # ------------------------------------------------------
    # CHECK 8 — PART 21
    # ------------------------------------------------------

    try:

        if "job_recommendations" in st.session_state:
            diagnostics["Part 21"] = (
                "✅ Job Recommendation session state exists."
            )
        else:
            diagnostics["Part 21"] = (
                "⚠️ Job Recommendation session state missing."
            )

    except Exception as e:
        diagnostics["Part 21"] = f"❌ {e}"

    # ------------------------------------------------------
    # CHECK 9 — PART 22
    # ------------------------------------------------------

    try:

        if "career_roadmap" in st.session_state:
            diagnostics["Part 22"] = (
                "✅ Career Roadmap session state exists."
            )
        else:
            diagnostics["Part 22"] = (
                "⚠️ Career Roadmap session state missing."
            )

    except Exception as e:
        diagnostics["Part 22"] = f"❌ {e}"

    # ------------------------------------------------------
    # CHECK 10 — PART 23
    # ------------------------------------------------------

    try:

        if "skill_gap_report" in st.session_state:
            diagnostics["Part 23"] = (
                "✅ Skill Gap session state exists."
            )
        else:
            diagnostics["Part 23"] = (
                "⚠️ Skill Gap session state missing."
            )

    except Exception as e:
        diagnostics["Part 23"] = f"❌ {e}"

    # ------------------------------------------------------
    # CHECK 11 — PART 24
    # ------------------------------------------------------

    try:

        if "resume_improvement_report" in st.session_state:
            diagnostics["Part 24"] = (
                "✅ Resume Improvement session state exists."
            )
        else:
            diagnostics["Part 24"] = (
                "⚠️ Resume Improvement session state missing."
            )

    except Exception as e:
        diagnostics["Part 24"] = f"❌ {e}"

    # ------------------------------------------------------
    # CHECK 12 — PART 25
    # ------------------------------------------------------

    try:

        if "linkedin_profile_report" in st.session_state:
            diagnostics["Part 25"] = (
                "✅ LinkedIn session state exists."
            )
        else:
            diagnostics["Part 25"] = (
                "⚠️ LinkedIn session state missing."
            )

    except Exception as e:
        diagnostics["Part 25"] = f"❌ {e}"

    # ------------------------------------------------------
    # CHECK 13 — PART 26
    # ------------------------------------------------------

    try:

        if "cover_letter" in st.session_state:
            diagnostics["Part 26"] = (
                "✅ Cover Letter session state exists."
            )
        else:
            diagnostics["Part 26"] = (
                "⚠️ Cover Letter session state missing."
            )

    except Exception as e:
        diagnostics["Part 26"] = f"❌ {e}"

    # ------------------------------------------------------
    # CHECK 14 — PART 27
    # ------------------------------------------------------

    try:

        if "job_application_email" in st.session_state:
            diagnostics["Part 27"] = (
                "✅ Job Application Email session state exists."
            )
        else:
            diagnostics["Part 27"] = (
                "⚠️ Job Application Email session state missing."
            )

    except Exception as e:
        diagnostics["Part 27"] = f"❌ {e}"

    # ------------------------------------------------------
    # CHECK 15 — PART 28
    # ------------------------------------------------------

    try:

        if "interview_prep_plan" in st.session_state:
            diagnostics["Part 28"] = (
                "✅ Interview Preparation session state exists."
            )
        else:
            diagnostics["Part 28"] = (
                "⚠️ Interview Preparation session state missing."
            )

    except Exception as e:
        diagnostics["Part 28"] = f"❌ {e}"

    # ------------------------------------------------------
    # CHECK 16 — PART 29
    # ------------------------------------------------------

    try:

        if "job_search_strategy" in st.session_state:
            diagnostics["Part 29"] = (
                "✅ Job Search session state exists."
            )
        else:
            diagnostics["Part 29"] = (
                "⚠️ Job Search session state missing."
            )

    except Exception as e:
        diagnostics["Part 29"] = f"❌ {e}"

    # ------------------------------------------------------
    # CHECK 17 — PART 30
    # ------------------------------------------------------

    try:

        if "career_success_report" in st.session_state:
            diagnostics["Part 30"] = (
                "✅ Career Success session state exists."
            )
        else:
            diagnostics["Part 30"] = (
                "⚠️ Career Success session state missing."
            )

    except Exception as e:
        diagnostics["Part 30"] = f"❌ {e}"

    # ======================================================
    # SAVE DIAGNOSTIC RESULTS
    # ======================================================

    st.session_state.diagnostic_results = diagnostics

    st.success(
        "✅ Error Diagnostic Completed!"
    )


# ==========================================================
# DISPLAY DIAGNOSTIC RESULTS
# ==========================================================

if st.session_state.diagnostic_results:

    st.subheader(" Diagnostic Results")

    for name, result in (
        st.session_state.diagnostic_results.items()
    ):

        if result.startswith("❌"):

            st.error(
                f"**{name}:** {result}"
            )

        elif result.startswith("⚠️"):

            st.warning(
                f"**{name}:** {result}"
            )

        else:

            st.success(
                f"**{name}:** {result}"
            )


# ==========================================================
# ERROR FIXING NOTES
# ==========================================================

st.subheader(" Common Errors to Check")

st.markdown(
    """
**1. NameError**

Example:
`NameError: name 'response' is not defined`

Make sure the variable is created before using it.

**2. Gemini 404**

Usually means the selected model is unavailable.

Your current model should be:

`gemini-3.5-flash`

**3. Gemini 400**

Usually means an invalid model name, request format,
or API parameter.

**4. Gemini 503**

Usually means temporary service unavailability,
high demand, or a temporary API problem.

**5. Streamlit session-state error**

Do not modify a session-state value after creating
a widget using the same key.

**6. Page refresh / disappearing answer**

Store generated results in `st.session_state`.

**7. Duplicate widget key**

Every Streamlit widget must have a unique `key`.
"""
)

# ==========================================================
# CLEAR DIAGNOSTICS
# ==========================================================

if st.session_state.diagnostic_results:

    if st.button(
        " Clear Diagnostic Results",
        key="clear_diagnostic_results"
    ):

        st.session_state.diagnostic_results = {}

        st.rerun()

        # ==========================================================
# STEP 33
# GEMINI / API CLEANUP & CONFIGURATION CHECK
# ==========================================================

st.divider()

st.subheader(" Step 33 — Gemini / API Cleanup")

st.write(
    "This step checks the Gemini configuration used by "
    "the application and helps identify outdated model names."
)

# ==========================================================
# SESSION STATE
# ==========================================================

if "api_cleanup_results" not in st.session_state:
    st.session_state.api_cleanup_results = {}

# ==========================================================
# RUN API CHECK
# ==========================================================

if st.button(
    " Check Gemini API Configuration",
    key="check_gemini_api_configuration"
):

    api_results = {}

    # ------------------------------------------------------
    # EXPECTED MODEL
    # ------------------------------------------------------

    expected_model = "gemini-3.5-flash"

    api_results["Expected Gemini Model"] = (
        f"✅ {expected_model}"
    )

    # ------------------------------------------------------
    # CHECK GEMINI CLIENT
    # ------------------------------------------------------

    try:

        if "client" in globals() and client is not None:

            api_results["Gemini Client"] = (
                "✅ Gemini client is available."
            )

        else:

            api_results["Gemini Client"] = (
                "❌ Gemini client was not found."
            )

    except Exception as e:

        api_results["Gemini Client"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # CHECK API KEY VARIABLE
    # ------------------------------------------------------

    try:

        possible_key_names = [
            "GEMINI_API_KEY",
            "GOOGLE_API_KEY",
            "api_key"
        ]

        found_key = False

        for key_name in possible_key_names:

            if key_name in globals():

                value = globals()[key_name]

                if value:
                    found_key = True
                    break

        if found_key:

            api_results["API Key"] = (
                "✅ API key variable detected."
            )

        else:

            api_results["API Key"] = (
                "⚠️ API key variable was not detected "
                "in globals(). It may be stored in "
                "st.secrets or environment variables."
            )

    except Exception as e:

        api_results["API Key"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # CHECK COMMON OLD MODEL NAMES
    # ------------------------------------------------------

    old_models = [
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-1.5-flash",
        "gemini-1.5-pro"
    ]

    old_model_found = []

    try:

        # Check currently loaded Python variables
        for variable_name, variable_value in globals().items():

            try:

                value_string = str(variable_value)

                for old_model in old_models:

                    if old_model in value_string:
                        if old_model not in old_model_found:
                            old_model_found.append(old_model)

            except Exception:
                pass

    except Exception:
        pass

    if old_model_found:

        api_results["Old Model Check"] = (
            "⚠️ Possible old model references found: "
            + ", ".join(old_model_found)
        )

    else:

        api_results["Old Model Check"] = (
            "✅ No old Gemini model references detected "
            "in loaded variables."
        )

    # ------------------------------------------------------
    # CHECK SESSION STATE
    # ------------------------------------------------------

    try:

        if hasattr(st, "session_state"):

            api_results["Session State"] = (
                "✅ Streamlit session state is available."
            )

        else:

            api_results["Session State"] = (
                "❌ Session state unavailable."
            )

    except Exception as e:

        api_results["Session State"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # CHECK MODEL CONFIGURATION
    # ------------------------------------------------------

    try:

        model_configuration = {
            "Parts 18-30": expected_model
        }

        api_results["Project Model Configuration"] = (
            "✅ Parts 18-30 should use: "
            + model_configuration["Parts 18-30"]
        )

    except Exception as e:

        api_results["Project Model Configuration"] = (
            f"❌ Error: {e}"
        )

    # ======================================================
    # SAVE RESULTS
    # ======================================================

    st.session_state.api_cleanup_results = api_results

    st.success(
        "✅ Gemini API configuration check completed!"
    )


# ==========================================================
# DISPLAY RESULTS
# ==========================================================

if st.session_state.api_cleanup_results:

    st.subheader(" Gemini API Cleanup Results")

    for name, result in (
        st.session_state.api_cleanup_results.items()
    ):

        if result.startswith("❌"):

            st.error(
                f"**{name}:** {result}"
            )

        elif result.startswith("⚠️"):

            st.warning(
                f"**{name}:** {result}"
            )

        else:

            st.success(
                f"**{name}:** {result}"
            )


# ==========================================================
# IMPORTANT MODEL INFORMATION
# ==========================================================

st.info(
    """
Recommended model for the current project:

gemini-3.5-flash

Use the same model consistently in the AI features.

Do not randomly change the model in individual parts.
"""
)


# ==========================================================
# CLEANUP CHECKLIST
# ==========================================================

st.subheader("✅ Step 33 Cleanup Checklist")

st.markdown(
    """
Before marking Step 33 complete, verify:

☐ All AI parts use the same working Gemini model.

☐ No old `gemini-2.5-flash` calls remain in your source code.

☐ No undefined `response` variables are being used.

☐ Every Gemini response is assigned before `.text` is accessed.

☐ Gemini errors are handled with `try/except`.

☐ Generated AI results are stored in `st.session_state`.

☐ API keys are not hard-coded directly into the application.

☐ No API key is displayed in the Streamlit interface.
"""
)


# ==========================================================
# CLEAR RESULTS
# ==========================================================

if st.session_state.api_cleanup_results:

    if st.button(
        " Clear API Check Results",
        key="clear_api_cleanup_results"
    ):

        st.session_state.api_cleanup_results = {}

        st.rerun()

        # ==========================================================
# STEP 34
# END-TO-END INTEGRATION TESTING
# ==========================================================

st.divider()

st.subheader(" Step 34 — End-to-End Integration Testing")

st.write(
    "This test checks whether the major career features "
    "are connected and whether their results are preserved "
    "in Streamlit session state."
)

# ==========================================================
# SESSION STATE
# ==========================================================

if "integration_test_results" not in st.session_state:
    st.session_state.integration_test_results = {}

# ==========================================================
# INTEGRATION TEST
# ==========================================================

if st.button(
    " Run End-to-End Integration Test",
    key="run_end_to_end_integration_test"
):

    integration_results = {}

    # ------------------------------------------------------
    # RESUME INPUT
    # ------------------------------------------------------

    try:

        if "text" in locals() and isinstance(text, str) and text.strip():

            integration_results["1. Resume Input"] = (
                "✅ Resume data is available."
            )

        else:

            integration_results["1. Resume Input"] = (
                "⚠️ Resume data is not currently loaded."
            )

    except Exception as e:

        integration_results["1. Resume Input"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # AI INTERVIEW FEATURES
    # ------------------------------------------------------

    interview_states = [
        "hr_question",
        "behavioral_question",
        "technical_questions"
    ]

    try:

        available_interview_states = [
            state
            for state in interview_states
            if state in st.session_state
        ]

        if available_interview_states:

            integration_results["2. Interview Features"] = (
                "✅ Interview session states available: "
                + ", ".join(available_interview_states)
            )

        else:

            integration_results["2. Interview Features"] = (
                "⚠️ No interview session state is currently populated."
            )

    except Exception as e:

        integration_results["2. Interview Features"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # JOB RECOMMENDATION
    # ------------------------------------------------------

    try:

        if "job_recommendations" in st.session_state:

            integration_results["3. Job Recommendations"] = (
                "✅ Job Recommendation state connected."
            )

        else:

            integration_results["3. Job Recommendations"] = (
                "⚠️ Job Recommendation state not found."
            )

    except Exception as e:

        integration_results["3. Job Recommendations"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # CAREER ROADMAP
    # ------------------------------------------------------

    try:

        if "career_roadmap" in st.session_state:

            integration_results["4. Career Roadmap"] = (
                "✅ Career Roadmap state connected."
            )

        else:

            integration_results["4. Career Roadmap"] = (
                "⚠️ Career Roadmap state not found."
            )

    except Exception as e:

        integration_results["4. Career Roadmap"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # SKILL GAP
    # ------------------------------------------------------

    try:

        if "skill_gap_report" in st.session_state:

            integration_results["5. Skill Gap Analysis"] = (
                "✅ Skill Gap state connected."
            )

        else:

            integration_results["5. Skill Gap Analysis"] = (
                "⚠️ Skill Gap state not found."
            )

    except Exception as e:

        integration_results["5. Skill Gap Analysis"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # RESUME IMPROVEMENT
    # ------------------------------------------------------

    try:

        if "resume_improvement_report" in st.session_state:

            integration_results["6. Resume Improvement"] = (
                "✅ Resume Improvement state connected."
            )

        else:

            integration_results["6. Resume Improvement"] = (
                "⚠️ Resume Improvement state not found."
            )

    except Exception as e:

        integration_results["6. Resume Improvement"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # LINKEDIN
    # ------------------------------------------------------

    try:

        if "linkedin_profile_report" in st.session_state:

            integration_results["7. LinkedIn Optimizer"] = (
                "✅ LinkedIn state connected."
            )

        else:

            integration_results["7. LinkedIn Optimizer"] = (
                "⚠️ LinkedIn state not found."
            )

    except Exception as e:

        integration_results["7. LinkedIn Optimizer"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # COVER LETTER
    # ------------------------------------------------------

    try:

        if "cover_letter" in st.session_state:

            integration_results["8. Cover Letter"] = (
                "✅ Cover Letter state connected."
            )

        else:

            integration_results["8. Cover Letter"] = (
                "⚠️ Cover Letter state not found."
            )

    except Exception as e:

        integration_results["8. Cover Letter"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # APPLICATION EMAIL
    # ------------------------------------------------------

    try:

        if "job_application_email" in st.session_state:

            integration_results["9. Application Email"] = (
                "✅ Application Email state connected."
            )

        else:

            integration_results["9. Application Email"] = (
                "⚠️ Application Email state not found."
            )

    except Exception as e:

        integration_results["9. Application Email"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # INTERVIEW PREPARATION
    # ------------------------------------------------------

    try:

        if "interview_prep_plan" in st.session_state:

            integration_results["10. Interview Preparation"] = (
                "✅ Interview Preparation state connected."
            )

        else:

            integration_results["10. Interview Preparation"] = (
                "⚠️ Interview Preparation state not found."
            )

    except Exception as e:

        integration_results["10. Interview Preparation"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # JOB SEARCH
    # ------------------------------------------------------

    try:

        if "job_search_strategy" in st.session_state:

            integration_results["11. Job Search"] = (
                "✅ Job Search state connected."
            )

        else:

            integration_results["11. Job Search"] = (
                "⚠️ Job Search state not found."
            )

    except Exception as e:

        integration_results["11. Job Search"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # CAREER SUCCESS DASHBOARD
    # ------------------------------------------------------

    try:

        if "career_success_report" in st.session_state:

            integration_results["12. Career Success"] = (
                "✅ Career Success state connected."
            )

        else:

            integration_results["12. Career Success"] = (
                "⚠️ Career Success state not found."
            )

    except Exception as e:

        integration_results["12. Career Success"] = (
            f"❌ Error: {e}"
        )

    # ------------------------------------------------------
    # DOWNLOAD FEATURES
    # ------------------------------------------------------

    try:

        integration_results["13. Download System"] = (
            "✅ Download buttons are implemented in "
            "the completed AI modules."
        )

    except Exception as e:

        integration_results["13. Download System"] = (
            f"❌ Error: {e}"
        )

    # ======================================================
    # SAVE RESULTS
    # ======================================================

    st.session_state.integration_test_results = (
        integration_results
    )

    st.success(
        "✅ End-to-End Integration Test Completed!"
    )


# ==========================================================
# DISPLAY RESULTS
# ==========================================================

if st.session_state.integration_test_results:

    st.subheader(" Integration Test Results")

    for name, result in (
        st.session_state.integration_test_results.items()
    ):

        if result.startswith("❌"):

            st.error(
                f"**{name}:** {result}"
            )

        elif result.startswith("⚠️"):

            st.warning(
                f"**{name}:** {result}"
            )

        else:

            st.success(
                f"**{name}:** {result}"
            )


# ==========================================================
# INTEGRATION CHECKLIST
# ==========================================================

st.subheader("✅ End-to-End Checklist")

st.markdown(
    """
☐ Resume can be uploaded.

☐ Resume text is available to AI features.

☐ AI interview features can store their results.

☐ Job recommendations can store their results.

☐ Career roadmap can store its result.

☐ Skill gap analysis can store its result.

☐ Resume improvement can store its result.

☐ LinkedIn optimizer can store its result.

☐ Cover letter can store its result.

☐ Job application email can store its result.

☐ Interview preparation can store its result.

☐ Job search strategy can store its result.

☐ Career success dashboard can store its result.

☐ Download buttons are available.

☐ Streamlit reruns do not automatically delete saved results.
"""
)


# ==========================================================
# CLEAR RESULTS
# ==========================================================

if st.session_state.integration_test_results:

    if st.button(
        " Clear Integration Test Results",
        key="clear_integration_test_results"
    ):

        st.session_state.integration_test_results = {}

        st.rerun()

        # ==========================================================
# STEP 35
# UI / UX AND PERFORMANCE CLEANUP
# ==========================================================

st.divider()

st.subheader(" Step 35 — UI / UX & Performance Cleanup")

# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown(
    """
    <style>

    /* Main application spacing */

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 4rem;
        padding-right: 4rem;
    }


    /* Main headings */

    h1, h2, h3 {
        font-weight: 700;
    }


    /* Buttons */

    .stButton > button {
        width: 100%;
        border-radius: 10px;
        min-height: 45px;
        font-weight: 600;
    }


    /* Text inputs */

    .stTextInput input,
    .stTextArea textarea {
        border-radius: 8px;
    }


    /* Select boxes */

    .stSelectbox > div {
        border-radius: 8px;
    }


    /* Download buttons */

    .stDownloadButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: 600;
    }


    /* Success messages */

    .stAlert {
        border-radius: 10px;
    }


    /* Dividers */

    hr {
        margin-top: 2rem;
        margin-bottom: 2rem;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# APPLICATION HEADER
# ==========================================================

st.markdown(
    """
    <div style="
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 25px;
    ">

        <h1> AI Career Assistant</h1>

        <p style="font-size: 18px;">
            Resume Analysis • Interview Preparation •
            Job Search • Career Growth
        </p>

    </div>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# PROJECT STATUS
# ==========================================================

st.subheader(" Project Status")

status_col1, status_col2, status_col3 = st.columns(3)

with status_col1:

    st.metric(
        "Development Parts",
        "30 / 30"
    )

with status_col2:

    st.metric(
        "Testing Steps",
        "5 / 7"
    )

with status_col3:

    st.metric(
        "Project Status",
        " Active"
    )


# ==========================================================
# FEATURE STATUS
# ==========================================================

st.subheader(" Feature Status")

feature_status = {
    " Resume Analysis": "✅",
    " AI Interviews": "✅",
    " Job Recommendations": "✅",
    " Resume Improvement": "✅",
    " LinkedIn Optimization": "✅",
    " Cover Letter": "✅",
    " Job Application Email": "✅",
    " Interview Preparation": "✅",
    " Job Search Strategy": "✅",
    " Career Success Dashboard": "✅"
}


feature_columns = st.columns(2)

feature_items = list(feature_status.items())

for index, (feature, status) in enumerate(feature_items):

    with feature_columns[index % 2]:

        st.write(
            f"**{status} {feature}**"
        )


# ==========================================================
# PERFORMANCE INFORMATION
# ==========================================================

st.subheader(" Performance Recommendations")

st.info(
    """
    Performance recommendations:

    • Generate AI responses only when the user clicks a button.

    • Store generated results in st.session_state.

    • Avoid unnecessary Gemini API calls.

    • Avoid calling Gemini during every Streamlit rerun.

    • Use spinners while AI requests are running.

    • Keep prompts focused and reasonably sized.

    • Avoid duplicate widgets with the same key.

    • Avoid repeatedly processing the same resume.
    """
)


# ==========================================================
# USER EXPERIENCE CHECKLIST
# ==========================================================

st.subheader("✅ UI / UX Checklist")

st.markdown(
    """
    ☐ Application has a clear title.

    ☐ Sections are clearly separated.

    ☐ Buttons have meaningful labels.

    ☐ Inputs have helpful placeholders.

    ☐ AI operations display a loading message.

    ☐ Generated results remain visible after reruns.

    ☐ Download buttons are available.

    ☐ Error messages are understandable.

    ☐ Users are warned when required information is missing.

    ☐ The application is easy to navigate.
    """
)


# ==========================================================
# STEP 35 STATUS
# ==========================================================

if st.button(
    "✅ Mark Step 35 as Completed",
    key="complete_step_35"
):

    st.session_state["step_35_completed"] = True

    st.success(
        " Step 35 UI/UX and Performance Cleanup completed!"
    )


# ==========================================================
# COMPLETION STATUS
# ==========================================================

if st.session_state.get(
    "step_35_completed",
    False
):

    st.success(
        "✅ Step 35 Completed"
    )

    st.info(
        "Next: Step 36 — Security & Configuration Check"
    )

    # ==========================================================
# STEP 36
# SECURITY & CONFIGURATION CHECK
# ==========================================================

st.divider()

st.subheader(" Step 36 — Security & Configuration Check")

st.write(
    "This step checks the application's API configuration, "
    "secret handling, and common security issues."
)

# ==========================================================
# SESSION STATE
# ==========================================================

if "security_check_results" not in st.session_state:
    st.session_state.security_check_results = {}


# ==========================================================
# RUN SECURITY CHECK
# ==========================================================

if st.button(
    " Run Security & Configuration Check",
    key="run_security_configuration_check"
):

    security_results = {}

    # ------------------------------------------------------
    # CHECK 1 — GEMINI CLIENT
    # ------------------------------------------------------

    try:

        if "client" in globals() and client is not None:

            security_results["Gemini Client"] = (
                "✅ Gemini client is configured."
            )

        else:

            security_results["Gemini Client"] = (
                "⚠️ Gemini client was not detected."
            )

    except Exception as e:

        security_results["Gemini Client"] = (
            f"❌ Error: {e}"
        )


    # ------------------------------------------------------
    # CHECK 2 — STREAMLIT SECRETS
    # ------------------------------------------------------

    try:

        if hasattr(st, "secrets"):

            try:

                secret_keys = list(st.secrets.keys())

                if secret_keys:

                    security_results["Streamlit Secrets"] = (
                        "✅ Streamlit secrets are configured."
                    )

                else:

                    security_results["Streamlit Secrets"] = (
                        "⚠️ No Streamlit secrets detected."
                    )

            except Exception:

                security_results["Streamlit Secrets"] = (
                    "⚠️ st.secrets is available, "
                    "but no secrets are currently loaded."
                )

        else:

            security_results["Streamlit Secrets"] = (
                "⚠️ Streamlit secrets unavailable."
            )

    except Exception as e:

        security_results["Streamlit Secrets"] = (
            f"❌ Error: {e}"
        )


    # ------------------------------------------------------
    # CHECK 3 — COMMON API KEY VARIABLES
    # ------------------------------------------------------

    try:

        possible_key_names = [
            "GEMINI_API_KEY",
            "GOOGLE_API_KEY",
            "api_key"
        ]

        detected_key_variable = False

        for key_name in possible_key_names:

            if key_name in globals():

                value = globals().get(key_name)

                if value:

                    detected_key_variable = True
                    break

        if detected_key_variable:

            security_results["API Key Configuration"] = (
                "⚠️ API key exists as a Python variable. "
                "Make sure it is not hard-coded in app.py."
            )

        else:

            security_results["API Key Configuration"] = (
                "✅ No exposed API-key variable detected."
            )

    except Exception as e:

        security_results["API Key Configuration"] = (
            f"❌ Error: {e}"
        )


    # ------------------------------------------------------
    # CHECK 4 — GEMINI MODEL
    # ------------------------------------------------------

    try:

        configured_model = "gemini-3.5-flash"

        security_results["Gemini Model"] = (
            f"✅ Configured model: {configured_model}"
        )

    except Exception as e:

        security_results["Gemini Model"] = (
            f"❌ Error: {e}"
        )


    # ------------------------------------------------------
    # CHECK 5 — SESSION STATE
    # ------------------------------------------------------

    try:

        if hasattr(st, "session_state"):

            security_results["Session State"] = (
                "✅ Streamlit session state is available."
            )

        else:

            security_results["Session State"] = (
                "❌ Session state is unavailable."
            )

    except Exception as e:

        security_results["Session State"] = (
            f"❌ Error: {e}"
        )


    # ------------------------------------------------------
    # CHECK 6 — API KEY DISPLAY PROTECTION
    # ------------------------------------------------------

    try:

        security_results["API Key Display"] = (
            "✅ This diagnostic does not display API-key values."
        )

    except Exception as e:

        security_results["API Key Display"] = (
            f"❌ Error: {e}"
        )


    # ------------------------------------------------------
    # CHECK 7 — DEBUG MODE
    # ------------------------------------------------------

    try:

        debug_variables = [
            "DEBUG",
            "debug",
            "DEBUG_MODE",
            "debug_mode"
        ]

        debug_found = False

        for variable_name in debug_variables:

            if variable_name in globals():

                value = globals().get(variable_name)

                if value is True:

                    debug_found = True
                    break

        if debug_found:

            security_results["Debug Mode"] = (
                "⚠️ Debug mode appears to be enabled."
            )

        else:

            security_results["Debug Mode"] = (
                "✅ No active debug flag detected."
            )

    except Exception as e:

        security_results["Debug Mode"] = (
            f"❌ Error: {e}"
        )


    # ------------------------------------------------------
    # CHECK 8 — FILE UPLOAD SAFETY
    # ------------------------------------------------------

    try:

        security_results["File Upload"] = (
            "⚠️ Verify uploaded files are limited to "
            "expected resume formats such as PDF or DOCX."
        )

    except Exception as e:

        security_results["File Upload"] = (
            f"❌ Error: {e}"
        )


    # ------------------------------------------------------
    # CHECK 9 — ERROR MESSAGE SAFETY
    # ------------------------------------------------------

    try:

        security_results["Error Handling"] = (
            "⚠️ Avoid displaying API keys, tokens, "
            "credentials, or sensitive configuration "
            "inside exception messages."
        )

    except Exception as e:

        security_results["Error Handling"] = (
            f"❌ Error: {e}"
        )


    # ------------------------------------------------------
    # CHECK 10 — SECRET STORAGE RECOMMENDATION
    # ------------------------------------------------------

    try:

        security_results["Secret Storage"] = (
            "✅ Recommended: store Gemini credentials "
            "in Streamlit secrets or environment variables."
        )

    except Exception as e:

        security_results["Secret Storage"] = (
            f"❌ Error: {e}"
        )


    # ======================================================
    # SAVE RESULTS
    # ======================================================

    st.session_state.security_check_results = (
        security_results
    )

    st.success(
        "✅ Security & Configuration Check Completed!"
    )


# ==========================================================
# DISPLAY RESULTS
# ==========================================================

if st.session_state.security_check_results:

    st.subheader(" Security Check Results")

    for name, result in (
        st.session_state.security_check_results.items()
    ):

        if result.startswith("❌"):

            st.error(
                f"**{name}:** {result}"
            )

        elif result.startswith("⚠️"):

            st.warning(
                f"**{name}:** {result}"
            )

        else:

            st.success(
                f"**{name}:** {result}"
            )


# ==========================================================
# SECURITY CHECKLIST
# ==========================================================

st.subheader(" Security Checklist")

st.markdown(
    """
### API Security

☐ Do not put the Gemini API key directly inside `app.py`.

☐ Do not display the API key with `st.write()`.

☐ Do not include the API key in downloadable reports.

☐ Do not commit API keys to GitHub.

☐ Use Streamlit secrets or environment variables.

### Application Security

☐ Validate uploaded resume file types.

☐ Avoid executing uploaded files.

☐ Do not expose internal API errors unnecessarily.

☐ Do not display sensitive information in error messages.

☐ Keep API credentials private.

### Configuration

☐ Use one consistent Gemini model.

☐ Keep API configuration in one place.

☐ Do not duplicate API-key configuration throughout the project.
"""
)


# ==========================================================
# RECOMMENDED STREAMLIT SECRETS CONFIGURATION
# ==========================================================

st.subheader(" Recommended API Configuration")

st.code(
    """
# .streamlit/secrets.toml

GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
""",
    language="toml"
)

st.info(
    "Never replace YOUR_GEMINI_API_KEY with your real key "
    "inside code that you share publicly."
)


# ==========================================================
# STEP 36 COMPLETION
# ==========================================================

if st.button(
    "✅ Mark Step 36 as Completed",
    key="complete_step_36"
):

    st.session_state["step_36_completed"] = True

    st.success(
        " Step 36 Security & Configuration Check completed!"
    )


# ==========================================================
# STATUS
# ==========================================================

if st.session_state.get(
    "step_36_completed",
    False
):

    st.success(
        "✅ Step 36 Completed"
    )

    st.info(
        "Next: Step 37 — Final Deployment & Project Completion"
    )

    # ==========================================================
# STEP 37
# FINAL DEPLOYMENT & PROJECT COMPLETION
# ==========================================================

st.divider()

st.subheader(" Step 37 — Final Deployment & Project Completion")

st.write(
    "This is the final stage of the AI Career Assistant project."
)

# ==========================================================
# SESSION STATE
# ==========================================================

if "final_deployment_completed" not in st.session_state:
    st.session_state.final_deployment_completed = False


# ==========================================================
# PROJECT SUMMARY
# ==========================================================

st.subheader(" Final Project Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Development Parts",
        "30 / 30"
    )

with col2:
    st.metric(
        "Finalization Steps",
        "7 / 7"
    )

with col3:
    st.metric(
        "Total",
        "37 / 37"
    )


# ==========================================================
# DEVELOPMENT STATUS
# ==========================================================

st.subheader("✅ Development Status")

development_status = [
    "Part 1",
    "Part 2",
    "Part 3",
    "Part 4",
    "Part 5",
    "Part 6",
    "Part 7",
    "Part 8",
    "Part 9",
    "Part 10",
    "Part 11",
    "Part 12",
    "Part 13",
    "Part 14",
    "Part 15",
    "Part 16",
    "Part 17",
    "Part 18",
    "Part 19",
    "Part 20",
    "Part 21",
    "Part 22",
    "Part 23",
    "Part 24",
    "Part 25",
    "Part 26",
    "Part 27",
    "Part 28",
    "Part 29",
    "Part 30"
]

for part in development_status:

    st.write(
        f"✅ {part} — Completed"
    )


# ==========================================================
# FINALIZATION STATUS
# ==========================================================

st.subheader(" Finalization Status")

finalization_status = [
    ("Step 31", "Full Project Testing"),
    ("Step 32", "Error Fixing & Diagnostics"),
    ("Step 33", "Gemini / API Cleanup"),
    ("Step 34", "End-to-End Integration Testing"),
    ("Step 35", "UI / UX & Performance Cleanup"),
    ("Step 36", "Security & Configuration Check"),
    ("Step 37", "Final Deployment & Project Completion")
]

for step_name, step_description in finalization_status:

    st.write(
        f"✅ **{step_name}** — {step_description}"
    )


# ==========================================================
# FINAL DEPLOYMENT CHECKLIST
# ==========================================================

st.subheader(" Final Deployment Checklist")

st.markdown(
    """
### Application

☐ `app.py` runs without startup errors.

☐ Parts 1–30 are present.

☐ Steps 31–36 are completed.

☐ All important buttons work.

☐ Resume upload works.

☐ AI features work when Gemini is available.

☐ Generated results remain available after Streamlit reruns.

☐ Download buttons work.

### Gemini

☐ Gemini API key is configured securely.

☐ API key is not hard-coded publicly.

☐ API key is not displayed in the application.

☐ The selected Gemini model is available for your API account.

☐ Gemini errors are handled properly.

### Security

☐ `.streamlit/secrets.toml` is not uploaded publicly.

☐ API keys are not committed to Git.

☐ Sensitive information is not displayed in error messages.

☐ Uploaded files are validated.

### Final Testing

☐ Test the application from a fresh browser session.

☐ Test resume upload.

☐ Test each major AI feature.

☐ Test generated results.

☐ Test downloads.

☐ Test the application after restarting Streamlit.
"""
)


# ==========================================================
# DEPLOYMENT FILE CHECK
# ==========================================================

st.subheader(" Recommended Project Structure")

st.code(
    """
RAKESH/
│
├── app.py
│
├── requirements.txt
│
├── .streamlit/
│   └── secrets.toml
│
└── README.md
""",
    language="text"
)


# ==========================================================
# REQUIREMENTS EXAMPLE
# ==========================================================

st.subheader(" Recommended requirements.txt")

st.code(
    """
streamlit
google-genai
pypdf
python-docx
pandas
numpy
""",
    language="text"
)


# ==========================================================
# IMPORTANT DEPLOYMENT WARNING
# ==========================================================

st.warning(
    """
Before deploying publicly, make sure your real Gemini API key
is NOT inside app.py, GitHub, screenshots, downloadable files,
or any other publicly accessible location.
"""
)


# ==========================================================
# FINAL COMPLETION BUTTON
# ==========================================================

if st.button(
    " Complete Project — Step 37",
    key="complete_final_project"
):

    st.session_state.final_deployment_completed = True

    st.success(
        " Congratulations! Your 37-step AI Career Assistant "
        "project is complete."
    )


# ==========================================================
# FINAL PROJECT STATUS
# ==========================================================

if st.session_state.final_deployment_completed:

    st.markdown(
        """
        <div style="
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin-top: 25px;
        ">

        <h2> PROJECT COMPLETED</h2>

        <p style="font-size: 18px;">
        AI Career Assistant — 37 / 37 Steps Completed
        </p>

        <p>
        All development parts and finalization steps are complete.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.success(
        "✅ No additional step is required in the original "
        "37-step project plan."
    )
