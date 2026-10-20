# Random Quantum Circuits

A self-contained Quarto textbook for senior undergraduates and beginning
graduate students, using Fisher, Khemani, Nahum, and Vijay,
[Random Quantum Circuits (2023)](https://doi.org/10.1146/annurev-conmatphys-031720-030658)
as its backbone.

**Read:** <https://xing-phys.github.io/random-quantum-circuits-book/>

The book expands the review with prerequisites, worked derivations, original
figures, exercises and solutions, and reproducible Julia experiments. A
section-by-section coverage map is in `coverage.qmd`. Statements identify
exact results, controlled limits, phenomenology, and numerical evidence.

## Build and preview

Requires Quarto 1.10.18 (the version used for verification) and a TeX
installation with XeLaTeX for the combined PDF.

```sh
quarto render                 # HTML chapters + combined PDF in _site/
quarto preview --no-browser   # prints the local preview URL
python3 scripts/check_book.py # source and rendered local-link checks
```

The PDF is `_site/random-quantum-circuits.pdf` and is linked from the book
sidebar. Physics macros are kept equivalent in `assets/macros.sty` and
`assets/mathjax-config.html`. Citation metadata is in
`assets/bibliography.bib`; the `refs-*.bib` files preserve authoring provenance.
The pre-render hook assembles those fragments and checks source references.
Edit a fragment rather than the generated combined bibliography.

## Reproduce the numerical figures

Simulation uses Julia standard libraries only (tested with Julia 1.12.6).
The default run uses an explicitly seeded RNG; its CSV includes standard
errors across independent circuit trajectories.

```sh
julia --startup-file=no scripts/circuits.jl
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
.venv/bin/python scripts/make_figures.py
```

Generated CSV, PNG and PDF figure assets are versioned so ordinary book
builds need neither Julia nor Python packages. The small-system experiment
illustrates entanglement growth and suppression by monitoring; it does not
estimate a thermodynamic critical point. See the laboratory chapter for the
algorithm, sampling convention, numerical checks, and limitations.

## Publishing

`.github/workflows/publish.yml` renders and checks the book on pushes to
`main`, uploads `_site/` as a Pages artifact, then deploys with GitHub's Pages
action. Repository Settings → Pages must use **GitHub Actions**. A separate
validation workflow checks pull requests without deployment. Rendered
output is excluded from the source branch.

## Attribution and scope

This is an independent pedagogical companion, with AI-assisted drafting and
verification. The review's authors are the authors of the cited review,
not this book. All figures are original and their provenance is recorded
in `FIGURE_CREDITS.md`. No review or third-party paper PDFs are redistributed.

Book text and original figures: CC BY 4.0. Code: MIT. See `LICENSE` for
details and the separately licensed citation style.
