"""AI Cover Letter Generator - Streamlit + Gemini API."""

import os

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

MAX_WORDS = 300
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

SYSTEM_INSTRUCTION = (
    "You are an expert career coach who writes concise, genuine, personalized "
    "cover letters for students and fresh graduates. You never invent facts: "
    "you only use the details the applicant provides."
)


def count_words(text: str) -> int:
    return len(text.split())


def build_prompt(data: dict, word_limit: int) -> str:
    return f"""Write a ready-to-send cover letter using ONLY the details below.

APPLICANT
- Name: {data['name']}
- Degree: {data['degree']}
- Skills: {data['skills']}
- Projects / Internships: {data['experience']}

JOB
- Company: {data['company']}
- Role: {data['role']}
- Job description:
{data['jd']}

REQUIREMENTS
- Maximum {word_limit} words in total (hard limit, including greeting and sign-off).
- Start with "Dear Hiring Manager," and end with "Sincerely," followed by the applicant's name.
- Connect the applicant's specific skills, projects and internships to the requirements in the job description.
- Mention the company name and role naturally. Show genuine interest, not generic flattery.
- Professional, confident, warm tone. 3 short paragraphs plus a closing line.
- Do NOT invent experience, numbers, or achievements that were not provided.
- Do NOT include placeholders like [Your Address] or [Date].
- Output ONLY the letter text. No markdown, no headings, no commentary.
"""


def generate_letter(client, model: str, data: dict, temperature: float) -> str:
    """Generate a letter, retrying with a tighter limit if it runs over 300 words."""
    limit = MAX_WORDS - 20  # aim lower so we land safely under the cap
    letter = ""
    for _ in range(3):
        response = client.models.generate_content(
            model=model,
            contents=build_prompt(data, limit),
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=temperature,
            ),
        )
        letter = (response.text or "").strip()
        if letter and count_words(letter) < MAX_WORDS:
            return letter
        limit -= 40  # ask for a shorter letter on the next attempt
    return letter


def main() -> None:
    st.set_page_config(page_title="AI Cover Letter Generator", page_icon="✉️", layout="centered")
    st.title("✉️ AI Cover Letter Generator")
    st.caption("Tell us about you and the job. Get a tailored cover letter in seconds.")

    with st.sidebar:
        st.header("Settings")
        api_key = st.text_input(
            "Gemini API key",
            type="password",
            value=os.getenv("GEMINI_API_KEY", ""),
            help="Get a free key at https://aistudio.google.com/apikey",
        )
        model = st.text_input("Model", value=DEFAULT_MODEL)
        temperature = st.slider("Creativity", 0.0, 1.0, 0.7, 0.1)

    with st.form("letter_form"):
        st.subheader("About you")
        col1, col2 = st.columns(2)
        name = col1.text_input("Full name *", placeholder="Priya Sharma")
        degree = col2.text_input("Degree *", placeholder="B.Tech in Computer Science, 2026")
        skills = st.text_area(
            "Skills *", placeholder="Python, SQL, Machine Learning, React, Git", height=80
        )
        experience = st.text_area(
            "Projects / Internship *",
            placeholder="e.g. Built a sentiment analysis web app using Python and Flask; "
            "3-month data analyst internship at XYZ where I automated weekly reports.",
            height=120,
        )

        st.subheader("The job")
        col3, col4 = st.columns(2)
        company = col3.text_input("Company name *", placeholder="Acme Technologies")
        role = col4.text_input("Job role *", placeholder="Data Analyst Intern")
        jd = st.text_area("Job description *", placeholder="Paste the job description here...", height=180)

        submitted = st.form_submit_button("Generate cover letter", type="primary", use_container_width=True)

    if submitted:
        data = {
            "name": name.strip(),
            "degree": degree.strip(),
            "skills": skills.strip(),
            "experience": experience.strip(),
            "company": company.strip(),
            "role": role.strip(),
            "jd": jd.strip(),
        }
        missing = [k for k, v in data.items() if not v]
        if not api_key:
            st.error("Please enter your Gemini API key in the sidebar.")
        elif missing:
            st.error("Please fill in all fields before generating.")
        else:
            try:
                client = genai.Client(api_key=api_key)
                with st.spinner("Writing your cover letter..."):
                    letter = generate_letter(client, model.strip(), data, temperature)
                if not letter:
                    st.error("The model returned an empty response. Please try again.")
                else:
                    st.session_state["letter"] = letter
                    st.session_state["file_name"] = (
                        f"cover_letter_{data['company'].replace(' ', '_')}_"
                        f"{data['role'].replace(' ', '_')}.txt"
                    )
            except Exception as exc:  # noqa: BLE001
                st.error(f"Something went wrong: {exc}")

    if "letter" in st.session_state:
        st.divider()
        st.subheader("Your cover letter")
        # Editable so the user can tweak before downloading
        edited = st.text_area(
            "Edit if you like", value=st.session_state["letter"], height=380, label_visibility="collapsed"
        )
        words = count_words(edited)
        if words < MAX_WORDS:
            st.caption(f"{words} words (under {MAX_WORDS})")
        else:
            st.warning(f"{words} words - over the {MAX_WORDS}-word target. Consider trimming.")

        st.download_button(
            "⬇️ Download as .txt",
            data=edited,
            file_name=st.session_state["file_name"],
            mime="text/plain",
            use_container_width=True,
        )


if __name__ == "__main__":
    main()
