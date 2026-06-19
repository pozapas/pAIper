# pAIper

![pAIper research review console](docs/assets/paiper-readme-hero.png)

pAIper is a venue-aware AI peer review console for research manuscripts. It reads a draft, scores it against a structured editorial rubric, checks citation integrity, evaluates fit for target venues, and turns the result into a prioritized revision plan.

The tool is designed for transportation, computer science, AI, computer vision, NLP, machine learning, robotics, and adjacent applied research manuscripts.

## What pAIper does

pAIper is not a passage-level grammar checker. It is a manuscript readiness system that behaves more like a strict associate editor:

- Reviews the manuscript across contribution, related work, methods, statistical validity, results, reproducibility, ethics, writing quality, technical correctness, and claim integrity.
- Produces an editorial recommendation, overall score, evidence-backed findings, strengths, weaknesses, and revision priorities.
- Checks target-venue fit using curated venue profiles and submission expectations.
- Verifies citations against public scholarly indexes and flags missing, inconsistent, or likely fabricated references.
- Exports results as Markdown, Word, PDF, and JSON.

## Core capabilities

| Capability | Description |
| --- | --- |
| Venue-aware review | Optional venue targeting for transportation journals, TRB, IEEE venues, CVPR, ACL, NeurIPS, ICLR, ICML, AAAI, KDD, SIGSPATIAL, CoRL, and related outlets. |
| Multi-pass review engine | Runs independent review passes so a weak model response cannot collapse the full report. |
| Citation verification | DOI-first checks followed by Crossref, Semantic Scholar, and OpenAlex lookups. |
| Claim-integrity audit | Identifies unsupported claims, overreach, missing evidence, and internal consistency problems. |
| Export pipeline | Generates structured in-app reports plus DOCX, Markdown, PDF, and JSON outputs. |
| Provider flexibility | Supports OpenRouter, Gemini, OpenAI, Anthropic, Mistral, and compatible provider configurations. |

## Supported inputs

- PDF
- DOCX
- LaTeX
- Markdown
- Plain text
- arXiv URLs

PDF parsing uses PyMuPDF by default. OCR and parser behavior are controlled from the application sidebar.

## Quick start

```bash
git clone https://github.com/pozapas/pAIper.git
cd pAIper
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

On macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Basic workflow

1. Select a model provider in the sidebar.
2. Paste an API key for that provider. The key is kept in the browser session and is not stored by the app.
3. Choose review depth: Fast, Standard, or Deep.
4. Optionally select a target venue.
5. Upload a manuscript or paste an arXiv URL.
6. Run the review and inspect the verdict, findings, venue fit, citation checks, and action plan.
7. Export the result in the format needed for revision or collaboration.

## Review depth

| Depth | Intended use | Review coverage |
| --- | --- | --- |
| Fast | Early draft triage | Contribution, methods, results, and writing. |
| Standard | Default pre-submission check | Core editorial dimensions plus venue and citation options. |
| Deep | Final Q1-style readiness pass | Expanded technical correctness and claim-integrity review. |

## Repository layout

```text
app.py                  Streamlit application shell
engine/                 UI-independent review engine
engine/exporters/       Markdown, Word, and PDF exporters
ui/                     Theme, icons, and reusable Streamlit components
ui/assets/              App imagery and local UI assets
data/venues/            Venue profiles and checklists
docs/assets/            README and documentation assets
.streamlit/config.toml  Streamlit runtime theme and upload settings
requirements.txt        Python dependencies
```

## Citation verification

Citation verification is designed to be conservative. pAIper checks references through public scholarly services and reports uncertainty instead of inventing matches. It can help identify:

- Missing DOI or bibliographic metadata.
- Real papers cited with wrong authors or venue details.
- Chimeric citations where the title and metadata do not belong together.
- References that cannot be found in public indexes.

Citation checks depend on external service availability and should be treated as decision support, not a replacement for manual reference review.

## Model and cost notes

pAIper sends review prompts to the provider selected in the sidebar. Costs depend on the chosen model, review depth, manuscript length, and citation-verification settings. For quick testing, OpenRouter and Gemini free-tier models can be used where available.

The app keeps review passes modular so smaller or cheaper models can still complete useful reviews. Stronger models generally produce better evidence synthesis and more reliable revision priorities.

## Privacy

- API keys entered in the sidebar are kept in the browser session.
- The app sends manuscript text to the selected model provider for review.
- Citation verification may query Crossref, Semantic Scholar, and OpenAlex.
- Do not upload confidential or restricted manuscripts unless your chosen provider and deployment environment meet your data-governance requirements.

## Deployment

pAIper is a Streamlit application. It can be deployed to Streamlit Community Cloud, Hugging Face Spaces, Render, Railway, or a private server that supports long-running Python requests.

Minimum deployment requirements:

- Python 3.10 or newer.
- Dependencies from `requirements.txt`.
- A secrets mechanism for provider API keys if you do not want users to paste keys in the UI.
- Enough request time for long manuscripts and deep reviews.

## Development

Run a local syntax check:

```bash
python -m py_compile app.py ui\components.py ui\theme.py engine\engine.py
```

Run the app:

```bash
streamlit run app.py
```

Keep development artifacts out of commits. The repository intentionally excludes `.codex`, `.claude`, `.agents`, virtual environments, logs, local Streamlit secrets, caches, and generated output folders.
