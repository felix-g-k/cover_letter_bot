# cover_letter_bot/openai_api.py
import os
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from utils import load_latex_template

def load_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def build_prompt(job_desc: str, cv: Path, template: Path = None, limit: int = 1000, tone: str = "formal", focus: str = None) -> str:

    # error handling
    if focus and focus not in cv:
        raise ValueError(f"Invalid focus: {focus}. Must be a section of the CV.")
    
    tone_options = ["formal", "enthusiastic", "confident", "humble", "narrative", "data-driven", "creative", "concise"]
    if tone not in tone_options:
        raise ValueError(f"Invalid tone: {tone}. Must be one of: {', '.join(tone_options)}")

    template = "Template cover letter (style, format, tone preference):\n" + template if template else ""

    limit = "There is no limit on the length of the cover letter." if limit is None else f"The cover letter should be no longer than {limit} words."
    focus = "There is no specific focus on the cover letter." if focus is None else f"The cover letter should focus on {focus}."
    
    return f"""
        Given the following:

        CV of the candidate:

        {cv}

        Job listing:

        {job_desc}

        {template}

        Write a tailored, convincing cover letter in the same language as the job listing that:

        Matches the tone and structure of the provided template, adapting language, formality, and layout accordingly.

        Clearly emphasizes the most relevant skills, accomplishments, and experiences from the CV that align with the specific responsibilities and qualifications listed in the job posting.

        Highlights the candidate’s motivation and enthusiasm for the role, the company, and the broader industry—drawing on elements such as past experiences, values alignment, or specific company initiatives.

        Maintains a tone that is {tone}.

        {focus}

        {limit}
        However, the cover letter should be no longer than the template, if provided.

        Return only the final version of the cover letter, ready to be submitted. Do not include commentary or analysis.
        Use the same template as provided and the same file format. Do not output a cover letter inside a code block.
        Make sure to escape special characters like &, %, $, #, etc.
    """

def generate_cover_letter(prompt: str, api_key: str, model: str = "gpt-4.1") -> str:
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=2048,
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()

def save_cover_letter(text: str, output_path: str = "output/cover_letter.txt"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

def main(
    job_desc_path: str,
    cv_path: str,
    api_key: str,
    template_path: str = None,
    output_path: str = "output/cover_letter.txt"
):
    job_desc = load_text_file(job_desc_path)
    cv = load_latex_template(cv_path)
    template = load_latex_template(template_path) if template_path else ""
    prompt = build_prompt(job_desc, cv, template)
    cover_letter = generate_cover_letter(prompt, api_key)
    save_cover_letter(cover_letter, output_path)
    print(f"Cover letter saved to {output_path}")

if __name__ == "__main__":
    # Example usage (replace with argparse or CLI as needed)
    load_dotenv()
    #api_key = os.getenv("OPENAI_API_KEY")
    api_key = "???"
    main(
        job_desc_path="output/job_description.txt",
        cv_path="templates/cv.tex",
        api_key=api_key,
        template_path="templates/cover_letter.tex",
        output_path="output/cover_letter.tex"
    )