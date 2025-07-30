import os
import subprocess
import glob

def load_latex_template(path: str) -> str:
    """
    Loads a LaTeX template file as a string from the given path.
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
def clear_aux_files():
    """
    Removes all auxiliary LaTeX files from output/ and templates/ directories.
    Keeps .log files for debugging purposes.
    """
    aux_extensions = [".aux", ".out", ".toc", ".synctex.gz", ".nav", ".snm", ".fls", ".fdb_latexmk", ".bbl", ".blg", ".idx", ".ind", ".ilg", ".glo", ".gls", ".glg", ".acn", ".acr", ".alg", ".ist", ".lot", ".lof", ".bcf", ".run.xml"]
    
    directories = ["output", "templates"]
    
    for directory in directories:
        if os.path.exists(directory):
            for ext in aux_extensions:
                pattern = os.path.join(directory, f"*{ext}")
                for aux_file in glob.glob(pattern):
                    try:
                        os.remove(aux_file)
                        print(f"Removed auxiliary file: {aux_file}")
                    except Exception as e:
                        print(f"Could not remove {aux_file}: {e}")

def render_pdf_from_latex(latex_path: str, out_dir="output"):
    """
    Renders a PDF from a LaTeX file using pdflatex.
    """

    print("LATEX PATH: ", latex_path)

    if not latex_path.endswith(".tex"):
        print("changing latex path")
        latex_path = latex_path + ".tex"

    print(f"Rendering PDF from {latex_path} to {out_dir}")
    try: 
        os.makedirs(out_dir, exist_ok=True)
    except Exception as e:
        print(f"Error creating output directory {out_dir}: {e}")
    
    try:
        result = subprocess.run(
            [
                "pdflatex",
                "-interaction=nonstopmode",  # Don't stop for errors
                "-output-directory", out_dir,
                os.path.join(out_dir, latex_path)
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
        print(f"Check the log file in {out_dir} for more details.")

    # Clean up auxiliary files except .log
    aux_extensions = [".aux", ".out", ".toc", ".synctex.gz", ".nav", ".snm", ".fls", ".fdb_latexmk"]
    base_name = os.path.splitext(os.path.basename(latex_path))[0]
    for ext in aux_extensions:
        aux_file = os.path.join(out_dir, base_name + ext)
        if os.path.exists(aux_file):
            try:
                subprocess.run(["rm", aux_file], check=True)
            except Exception as cleanup_e:
                print(f"Could not remove {aux_file}: {cleanup_e}")