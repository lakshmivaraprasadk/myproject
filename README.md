# AI Cover Letter Generator

A Streamlit app that uses the Gemini API to write a personalized cover letter (under 300 words) for a specific job.

## Inputs
Name, degree, skills, projects/internship, company name, job role, job description.

## Output
A ready-to-send cover letter with a **Download as .txt** button. The letter is editable before download and shows a live word count.

## Setup

1. Create a virtual environment (optional but recommended):
   ```
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Get a free Gemini API key at https://aistudio.google.com/apikey
4. Provide the key, either way:
   - Copy `.env.example` to `.env` and paste your key, or
   - Paste it into the sidebar when the app is running.
5. Run:
   ```
   streamlit run app.py
   ```

## Notes
- The default model is `gemini-2.5-flash`. Change it in the sidebar or with `GEMINI_MODEL` in `.env`.
- If the model's first draft exceeds 300 words, the app automatically asks for a shorter version (up to 3 attempts).
- Never commit your `.env` file or API key.
