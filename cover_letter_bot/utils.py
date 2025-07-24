

def load_latex_template(path: str) -> str:
    """
    Loads a LaTeX template file as a string from the given path.
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()