# Hourglass Stealth

Technical calculation scaffold for an "hourglass stealth spacecraft" concept.

This repository is organized around two deliverables:

1. An installable Python package for reusable calculations.
2. A Jupyter notebook that serves as the calculation sheet behind a future blog post.

## Current Status

The repository is scaffolded and organized for implementation. Core modules, test coverage, output directories, and a notebook outline are in place. The detailed implementation plan lives in `docs/development_plan.md`.

## Planned Outputs

- Passive sealed dwell time, in years.
- Detection distance, primarily in Earth-Moon distances.

## First-Pass Assumptions

- Emission is modeled as homogeneous over the spacecraft surface.
- This is intentionally conservative in favor of defense and hides angular structure for now.
- Perfect sun-axis alignment is assumed in all scenarios.
- Angle-dependent observability, mirror exposure, and glint are known limitations deferred to later work.

## Repository Layout

```text
.
├── README.md
├── docs/
│   └── development_plan.md
├── notebooks/
│   └── 01_blog_calcs_sheet.ipynb
├── outputs/
│   └── .gitkeep
├── pyproject.toml
├── hourglass_stealth/
│   ├── __init__.py
│   ├── constants.py
│   ├── detector.py
│   ├── emission.py
│   ├── environment.py
│   ├── heat_store.py
│   ├── optics.py
│   ├── scenarios.py
│   └── tables.py
└── tests/
    ├── conftest.py
    ├── test_detector.py
    ├── test_emission.py
    ├── test_environment.py
    ├── test_heat_store.py
    ├── test_optics.py
    ├── test_package.py
    └── test_scenarios.py
```

## Local Use

Work from the repository root:

```bash
cd /home/arominge/repos/hourglass_stealth
```

### 1. Activate the Python environment

If `.env/` already exists:

```bash
source .env/bin/activate
```

If you need to create it from scratch:

```bash
python -m venv .env
source .env/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

### 2. Confirm the package import works

```bash
python -c "import hourglass_stealth; print(hourglass_stealth.__version__)"
```

### 3. Run the test suite

```bash
pytest -q
```

### 4. Start the notebook server

From the repo root, with the venv activated:

```bash
jupyter notebook
```

or:

```bash
jupyter lab
```

Then open:

```text
notebooks/01_blog_calcs_sheet.ipynb
```

The notebook imports the local editable package, so it should be run from this environment rather than from a system Python install.

### 5. Use the notebook

Expected workflow:

1. Activate `.env`.
2. Start Jupyter from the repo root.
3. Open `notebooks/01_blog_calcs_sheet.ipynb`.
4. Run cells in order.
5. Export generated tables to `outputs/` as notebook functionality is filled in.

## Installed Dependencies

The intended dev stack is:

- `numpy`
- `pandas`
- `matplotlib`
- `jupyter`
- `ipykernel`
- `pytest`
- optional: `scipy`, `openpyxl`

Install them with:

```bash
python -m pip install -e '.[dev]'
```

## Notes

- The current notebook is still a structured stub; the core Python calculation modules are implemented first.
- In this Codex sandbox, `matplotlib` may warn about its cache directory and fall back to `/tmp`. On a normal local machine this should usually resolve through your user config directory.
- If you initialize git later, `.gitignore` already excludes `.env/`, Python caches, and generated table exports.

## Next Work

1. Wire the notebook sections to the implemented calculation modules.
2. Generate assumption tables and baseline scenario outputs from code.
3. Export scenario tables to `outputs/`.
4. Expand the notebook into cislunar heating and viability sweeps.
