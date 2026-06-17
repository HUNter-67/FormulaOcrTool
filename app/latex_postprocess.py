from __future__ import annotations

import re


GREEK_UNICODE_TO_LATEX = {
    "α": r"\alpha",
    "β": r"\beta",
    "γ": r"\gamma",
    "δ": r"\delta",
    "ε": r"\epsilon",
    "ϵ": r"\epsilon",
    "ζ": r"\zeta",
    "η": r"\eta",
    "θ": r"\theta",
    "ϑ": r"\vartheta",
    "ι": r"\iota",
    "κ": r"\kappa",
    "λ": r"\lambda",
    "μ": r"\mu",
    "ν": r"\nu",
    "ξ": r"\xi",
    "π": r"\pi",
    "ϖ": r"\varpi",
    "ρ": r"\rho",
    "ϱ": r"\varrho",
    "σ": r"\sigma",
    "ς": r"\sigma",
    "τ": r"\tau",
    "υ": r"\upsilon",
    "φ": r"\phi",
    "ϕ": r"\varphi",
    "χ": r"\chi",
    "ψ": r"\psi",
    "ω": r"\omega",
    "Γ": r"\Gamma",
    "Δ": r"\Delta",
    "Θ": r"\Theta",
    "Λ": r"\Lambda",
    "Ξ": r"\Xi",
    "Π": r"\Pi",
    "Σ": r"\Sigma",
    "Υ": r"\Upsilon",
    "Φ": r"\Phi",
    "Ψ": r"\Psi",
    "Ω": r"\Omega",
}

GREEK_COMMANDS = {
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
    "varepsilon",
    "zeta",
    "eta",
    "theta",
    "vartheta",
    "iota",
    "kappa",
    "lambda",
    "mu",
    "nu",
    "xi",
    "pi",
    "varpi",
    "rho",
    "varrho",
    "sigma",
    "tau",
    "upsilon",
    "phi",
    "varphi",
    "chi",
    "psi",
    "omega",
    "Gamma",
    "Delta",
    "Theta",
    "Lambda",
    "Xi",
    "Pi",
    "Sigma",
    "Upsilon",
    "Phi",
    "Psi",
    "Omega",
}

COMMON_COMMAND_FIXES = {
    r"\epsion": r"\epsilon",
    r"\eplison": r"\epsilon",
    r"\lamda": r"\lambda",
    r"\lambad": r"\lambda",
    r"\thetha": r"\theta",
    r"\vtheta": r"\vartheta",
    r"\varph": r"\varphi",
}


def normalize_latex_output(latex: str) -> str:
    """Apply conservative cleanup to OCR LaTeX output."""
    text = latex.strip()
    for source, replacement in GREEK_UNICODE_TO_LATEX.items():
        text = text.replace(source, replacement)

    for source, replacement in COMMON_COMMAND_FIXES.items():
        text = text.replace(source, replacement)

    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*([_^{}=+\-*/(),])\s*", r"\1", text)
    return text.strip()


def score_latex_candidate(latex: str) -> int:
    """Prefer plausible formula output without blindly rewriting ambiguous letters."""
    if not latex:
        return -10_000

    score = 0
    score += min(len(latex), 200) // 20

    commands = re.findall(r"\\([A-Za-z]+)", latex)
    score += min(len(commands), 12)
    score += sum(3 for command in commands if command in GREEK_COMMANDS)

    if latex.count("{") == latex.count("}"):
        score += 3
    else:
        score -= 6

    if "$" in latex:
        score -= 2
    if re.search(r"(.)\1{5,}", latex):
        score -= 4

    return score
