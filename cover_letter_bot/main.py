import argparse
import os
from pathlib import Path
import subprocess
from dotenv import load_dotenv
from scraper import scrape_job_description
from generator import build_prompt, generate_cover_letter, save_cover_letter, load_latex_template

def render_pdf_from_latex(latex_path: str, output_dir: str = "output"):
    """
    Renders a PDF from a LaTeX file using pdflatex.
    """

    os.makedirs(output_dir, exist_ok=True)
    try:
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",  # Don't stop for errors
                "-output-directory", output_dir,
                latex_path
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print("PDFLaTeX failed with the following output:")
        print(e.stdout)
        print(e.stderr)
        print(f"Check the log file in {output_dir} for more details.")
        # Optionally, re-raise or handle as needed

    # Clean up auxiliary files except .log
    aux_extensions = [".aux", ".out", ".toc", ".synctex.gz", ".nav", ".snm", ".fls", ".fdb_latexmk"]
    base_name = os.path.splitext(os.path.basename(latex_path))[0]
    for ext in aux_extensions:
        aux_file = os.path.join(output_dir, base_name + ext)
        if os.path.exists(aux_file):
            try:
                subprocess.run(["rm", aux_file], check=True)
            except Exception as cleanup_e:
                print(f"Could not remove {aux_file}: {cleanup_e}")

def main():
    parser = argparse.ArgumentParser(description="Cover Letter Bot CLI")
    parser.add_argument("--job-url", required=True, help="URL of the LinkedIn job listing")
    parser.add_argument("--cv", required=True, help="Path to the LaTeX CV template")
    parser.add_argument("--cover-letter", required=False, help="Path to the LaTeX cover letter template")
    parser.add_argument("--limit", required=False, help="Limit on the length of the cover letter")
    parser.add_argument("--tone", required=False, help="Tone of the cover letter")
    parser.add_argument("--focus", required=False, help="Focus of the cover letter")
    parser.add_argument("--output-latex", default="output/cover_letter.tex", help="Path to save the generated LaTeX cover letter")
    parser.add_argument("--output-pdf", default="output/cover_letter.pdf", help="Path to save the generated PDF cover letter")
    parser.add_argument("--debug", default=False, help="Debug mode")
    args = parser.parse_args()

    paths = {
        "out_latex": args.output_latex,
        "out_pdf": args.output_pdf,
        "cv": Path("./templates") / Path(args.cv),
        "cover_letter": Path("./templates") / Path(args.cover_letter) if args.cover_letter else None
    }

    # Step 1: Scrape job description
    print("Scraping job description...")
    job_description = scrape_job_description(args.job_url)
    print("Job description extracted.")

    # Step 2: Generate cover letter LaTeX file using the LLM
    print("Generating cover letter using LLM...")

    prompt_kwargs = {}
    if args.cover_letter:
        prompt_kwargs['template'] = load_latex_template(paths["cover_letter"])
    if args.tone:
        prompt_kwargs['tone'] = args.tone
    if args.focus:
        prompt_kwargs['focus'] = args.focus
    if args.limit:
        prompt_kwargs['limit'] = args.limit

    prompt = build_prompt(
        job_desc=job_description,
        cv=args.cv,
        **prompt_kwargs
    )

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

    if not args.debug:
        cover_letter = generate_cover_letter(prompt, api_key)
        save_cover_letter(cover_letter, paths["out_latex"])
        print(f"Cover letter LaTeX saved to {paths['out_latex']}")
    else:
        print("Debug mode enabled. Prompt:")
        print(prompt)
        paths["out_latex"] = "output/example_cover_letter.tex"
        paths["out_pdf"] = "output/example_cover_letter.pdf"

    # Step 3: Render PDF from LaTeX
    print("Rendering PDF from LaTeX...")
    render_pdf_from_latex(paths["out_latex"], output_dir=os.path.dirname(paths["out_pdf"]) or "output")
    print(f"PDF saved to {paths['out_pdf']}")

if __name__ == "__main__":
    main()