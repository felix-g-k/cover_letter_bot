import os
import sys
import asyncio
import aiohttp
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
import inquirer
from cover_letter_bot import generator
import glob
import argparse
from dotenv import load_dotenv
from .scraper import scrape_job_description
from .utils import render_pdf_from_latex, clear_aux_files

console = Console()

OUTPUT_DIR = "output"

DEFAULTS = {
    'job_url': '',
    'cv_template': 'templates/example_cv.tex',
    'cover_letter_template': '',
    'limit': None,
    'tone': 'formal',
    'focus': '',
    'output_latex': 'cover_letter.tex'
}

async def scrape_job_description(url):
    """Asynchronously scrape job description from URL"""

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    # Basic extraction - you might want to use a proper HTML parser
                    # This is a simple example - you'd want more sophisticated parsing
                    return f"Job description scraped from: {url}\n\n{html[:1000]}..."  # First 1000 chars
                else:
                    return f"Failed to scrape job description from {url}. Status: {response.status}"
    except Exception as e:
        return f"Error scraping job description: {str(e)}"

def fancy_welcome(debug=False):
    msg = '[bold cyan]Welcome to Cover Letter Bot![/bold cyan]'
    if debug:
        msg += ' [bold red]DEBUG MODE[/bold red]'
    console.print(Panel(msg, expand=False))

def select_template(prompt, directory, default, allow_none=False, debug=False):
    tex_files = [os.path.basename(f) for f in glob.glob(f'{directory}/*.tex')]
    if allow_none:
        tex_files = ['None'] + tex_files
    question = [
        inquirer.List('template', message=f'{prompt} (default: {default})' + (' [DEBUG MODE]' if debug else ''), choices=tex_files, default=os.path.basename(default) if default else 'None')
    ]
    answer = inquirer.prompt(question)
    selected = answer['template']
    if selected == 'None':
        return ''
    return os.path.join(directory, selected)

async def prompt_user(debug=False):
    fancy_welcome(debug)
    
    # Job URL - start scraping immediately after this
    job_url = console.input(f"Enter the URL of the job listing (default: {DEFAULTS['job_url']}): " + ("[DEBUG MODE] " if debug else "")) or DEFAULTS['job_url']
    
    # Start scraping in the background
    scraping_task = None
    if job_url:
        console.print("[yellow]Starting to scrape job description...[/yellow]")
        scraping_task = asyncio.create_task(scrape_job_description(job_url))
    
    # Continue with other prompts while scraping happens
    cv_template = select_template('Select your CV template', 'templates', DEFAULTS['cv_template'], debug=debug)
    cover_letter_template = select_template('Select a cover letter template (or None)', 'templates', DEFAULTS['cover_letter_template'], allow_none=True, debug=debug)
    limit = console.input(f"Enter the word limit for the cover letter (default: {DEFAULTS['limit']}): " + ("[DEBUG MODE] " if debug else "")) or DEFAULTS['limit']
    limit = None if limit in ('', 'None', None) else int(limit)
    tone = console.input(f"Enter the tone (default: {DEFAULTS['tone']}): " + ("[DEBUG MODE] " if debug else "")) or DEFAULTS['tone']
    focus = console.input(f"Enter the focus (default: {DEFAULTS['focus']}): " + ("[DEBUG MODE] " if debug else "")) or DEFAULTS['focus']
    output_latex = console.input(f"Enter the output LaTeX name (default: {DEFAULTS['output_latex']}): " + ("[DEBUG MODE] " if debug else "")) or DEFAULTS['output_latex']
    
    # Wait for scraping to complete if it was started
    job_description = ""
    if scraping_task:
        console.print("[yellow]Waiting for job description to finish scraping...[/yellow]")
        job_description = await scraping_task
        console.print("[green]Job description scraped successfully![/green]")
    
    return {
        'job_url': job_url,
        'cv_template': cv_template,
        'cover_letter_template': cover_letter_template,
        'limit': limit,
        'tone': tone,
        'focus': focus,
        'output_latex': output_latex,
        'job_description': job_description,
    }

async def async_main():
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY', 'sk-...')
    parser = argparse.ArgumentParser(description='Cover Letter Bot CLI')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode (no API call, dummy output)')
    args = parser.parse_args()
    debug = args.debug
    
    user_inputs = await prompt_user(debug)
    
    # Save job description to file
    job_desc_path = 'output/job_description.txt'
    with open(job_desc_path, 'w') as f:
        f.write(user_inputs['job_description'])
    
    # Generate cover letter
    if debug:
        dummy_letter = 'This is a dummy cover letter. [DEBUG MODE]'
        generator.save_cover_letter(dummy_letter, user_inputs['output_latex'])
        console.print(f"Cover letter saved to {user_inputs['output_latex']} [DEBUG MODE]")
        render_pdf_from_latex(user_inputs['output_latex'], out_dir=OUTPUT_DIR)
    else:
        generator.generator_main(
            job_desc_path=job_desc_path,
            cv_path=user_inputs['cv_template'],
            api_key=api_key,
            template_path=user_inputs['cover_letter_template'] or None,
            out_name=user_inputs['output_latex']
        )
        console.print(f"Cover letter saved to {os.path.join(OUTPUT_DIR, user_inputs['output_latex'])}")

        render_pdf_from_latex(user_inputs['output_latex'], out_dir=OUTPUT_DIR)
        
        clear_aux_files()

def main():
    asyncio.run(async_main())

if __name__ == '__main__':
    main() 