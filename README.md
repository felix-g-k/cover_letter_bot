# Cover Letter Bot

A CLI tool to automatically generate tailored cover letters in LaTeX and PDF format using your resume, a job listing, and OpenAI's language models.

## Features
- **Scrape** job descriptions from LinkedIn job listings
- **Generate** a cover letter using your resume, job description, and optional LaTeX templates
- **Render** the cover letter as a PDF using LaTeX
- **Customizable**: Control the tone, focus, and length of the generated letter

## Project Structure
```
cover_letter_bot/
├── main.py                # CLI entry point
├── scraper.py             # Job description scraping logic (Selenium + BeautifulSoup)
├── generator.py           # Prompt building and OpenAI API interaction
├── templates/             # LaTeX templates for CV and cover letter
├── output/                # Generated job descriptions and cover letters
├── .env                   # API keys (not committed)
└── README.md              # Project documentation
```

## Requirements
- Python 3.8+
- [Conda](https://docs.conda.io/) or `venv` (recommended)
- Chrome browser and [ChromeDriver](https://sites.google.com/chromium.org/driver/) (for Selenium)
- `pdflatex` (for PDF rendering)

Install dependencies:
```sh
conda env create -f environment.yml
conda activate cover_letter_bot
```
Or with pip:
```sh
pip install -r requirements.txt
```

## Setup
1. **API Key**: Add your OpenAI API key to a `.env` file:
   ```
   OPENAI_API_KEY=sk-...
   ```
2. **Templates**: Place your LaTeX CV and cover letter templates in the `templates/` directory.
3. **Resume**: Prepare your resume as a plain text file.

## Usage
Run the CLI from the project root:
```sh
python -m cover_letter_bot.main \
  --job-url "<LinkedIn Job URL>" \
  --cv cv.tex \
  --cover-letter cover_letter.tex \
  --tone "professional" \
  --focus "data analysis" \
  --limit "1 page" \
  --output-latex output/cover_letter.tex \
  --output-pdf output/cover_letter.pdf
```

### Arguments
- `--job-url` (required): URL of the LinkedIn job listing
- `--cv` (required): Path to your LaTeX CV template (relative to `templates/`)
- `--cover-letter` (optional): Path to your LaTeX cover letter template (relative to `templates/`)
- `--tone` (optional): Desired tone of the cover letter
- `--focus` (optional): Focus area for the cover letter
- `--limit` (optional): Length limit for the cover letter
- `--output-latex` (optional): Output path for the generated LaTeX file
- `--output-pdf` (optional): Output path for the generated PDF file

## Components
- **scraper.py**: Uses Selenium and BeautifulSoup to extract the job description from LinkedIn.
- **generator.py**: Builds the prompt, calls the OpenAI API, and formats the cover letter in LaTeX.
- **main.py**: Orchestrates the workflow, provides the CLI, and renders the PDF.
- **templates/**: Store your LaTeX templates here.
- **output/**: Generated files are saved here.