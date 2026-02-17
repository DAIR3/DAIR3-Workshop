# DAIR³ — Data Analytics and Interdisciplinary Research

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

**DAIR³** is an NIH R25-funded training program that prepares biomedical researchers to conduct rigorous, reproducible, and ethical data science research. The program brings together faculty and trainees from Jackson State University, University of Michigan, and the University of Texas at San Antonio. 

DAIR³ includes weeklong bootcamps in the summer that focus on ethical issues in biomedical data science; data management, representation, and sharing; rigorous analytical design; the design and reporting of AI models; generative AI; reproducible workflow; and assessing findings across studies. Additionally, the bootcamp also includes grant writing sessions and research collaboration discussions.

## Program Goals

1. **Responsible Conduct of Research:** Equip trainees to navigate ethical challenges unique to data-intensive and AI-assisted biomedical research, including issues of reproducibility, privacy, bias, and accountability.

2. **Technical Proficiency:** Develop practical skills in data management, statistical design, predictive modeling, meta-analysis, and the responsible use of large language models (LLMs).

3. **Reproducible Science:** Train researchers to build transparent, version-controlled, and containerized analysis pipelines that meet contemporary standards for scientific reproducibility.

4. **Applied Learning:** Ground all instruction in an authentic data challenge using real-world vital statistics data, requiring trainees to project health outcomes and identify socioeconomic determinants.

## 2026 Data Challenge: Vital Statistics

The 2026 cohort addresses a planning commission scenario for the State of Texas:

- **Projections of underweight newborns** by county for 2030
- **Projections of infant mortality** by county for 2030
- **Identification of socioeconomic factors** associated with these outcomes
- **Comparison to other states**

### Data Sources

| Source | Description | Coverage |
|--------|-------------|----------|
| **NCHS** | National Center for Health Statistics birth records | 1969–1988 (individual-level) |
| **SEER** | Surveillance, Epidemiology, and End Results population estimates | 1969–2020 |
| **SEDAC** | Socioeconomic Data and Applications Center population projections | 2020–2100 |

Trainees integrate these sources to build a temporal bridge: NCHS → SEER → SEDAC.

## Curriculum Structure

The bootcamp comprises seven instructional units totaling approximately 33 hours:

| Unit | Title | Hours | Key Topics |
|------|-------|-------|------------|
| 1 | Responsible Conduct of Research | 3.0 | RCR in data science, sociotechnical ethics, anticipatory governance |
| 2 | Foundations of Data Mgmt.| 5.0 | Jackson Heart Study, metadata, data representation, FAIR principles, data sharing |
| 3 | Rigorous Statistical Design | 5.5 | Study design, power analysis, bias, causal interpretation |
| 4 | Interpretable Predictive Models | 5.0 | Supervised learning, feature engineering, model evaluation, TRIPOD reporting |
| 5 | Reproducible Workflows | 5.5 | Notebooks, version control (Git), containers (Docker), pipeline assembly |
| 6 | Meta-analysis | 3.5 | Evidence synthesis, heterogeneity, non-independence, network effects |
| 7 | LLMs in Biomedical Research | 4.0 | Ethics of AI agents, LLM consensus methods, building analysis pipelines |

### Unit 7: Ethics of AI Agents

Unit 7.1 introduces a novel framework for responsible use of LLM-based agents in research:

- **Invalidation** (broader than "hallucination"): factual, logical, normative, and structural breaches
- **Multi-agent critique:** verification loops with tradeoffs (privacy, compute, epistemic diversity)
- **Seven risk categories:** epistemic propagation, accountability, provenance, confidentiality, bias, security, sustainability
- **Governance-by-design:** checklists and disclosure templates aligned with COPE/ICMJE/WAME

## Repository Structure

```
DAIR³/
├── common/                     # Shared LaTeX configuration and assets
│   ├── DAIR3Config.tex         # Document configuration, macros, packages
│   ├── DAIR3FrontMatter.tex    # Title pages, front matter
│   ├── lstsetC.tex             # Code listing style (C)
│   ├── lstsetMATLAB.tex        # Code listing style (MATLAB)
│   ├── lstsetPython.tex        # Code listing style (Python)
│   ├── lstsetR.tex             # Code listing style (R)
│   └── [images]                # Shared images (logos, QR codes, covers)
│
├── images/                     # Challenge-specific and extracted images
│   └── ChapterIntroProg/       # Images for programming introduction
│
├── challenge2026/              # 2026 Data Challenge materials
│   └── 2026DAIR-3.tex          # Main challenge document
│
├── prereqs/                    # Prerequisites and environment setup
│   ├── DAIR-Prerequisites.tex  # Main prerequisites document
│   ├── Environment_Setup.tex   # Environment configuration guide
│   ├── ChapterIntroProg.tex    # Introduction to programming
│   └── EnvSetup_VisualStudioCode.pdf
│
├── source/                     # Example source code files
│   ├── IntroProgMatMul.py      # Matrix multiplication (Python)
│   ├── IntroProgMatMul.m       # Matrix multiplication (MATLAB)
│   ├── IntroProgMatMul.r       # Matrix multiplication (R)
│   ├── IntroProgMatMul.c       # Matrix multiplication (C)
│   ├── Transforms.m            # Signal transforms example
│   └── WebScraping.py          # Web scraping example
│
├── specs/                      # Specifications for development
│   └── SPECS1.md               # Repository reorganization specs
│
├── DAIR3.bat                   # Environment activation script
├── gh.bat                      # Git sync script (both remotes)
├── LICENSE                     # GNU GPL v3
├── .gitignore                  # LaTeX artifacts exclusion
└── README.md                   # This file
```

## Environment Setup

### Quick Start

1. **Install prerequisites:**
   - Python 3.x with pip
   - Visual Studio Code (recommended)
   - Git

2. **Clone the repository:**
   ```bash
   git clone https://github.com/DAIR3/DAIR3-Workshop.git
   cd DAIR3-Workshop
   ```

3. **Set up API keys** (for Unit 7 LLM exercises):
   ```bash
   # Windows
   setx OPENAI_API_KEY "your-key-here"
   setx ANTHROPIC_API_KEY "your-key-here"
   setx GROQ_API_KEY "your-key-here"
   
   # Mac/Linux
   echo 'export OPENAI_API_KEY="your-key-here"' >> ~/.zshrc
   source ~/.zshrc
   ```

4. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Mac/Linux
   .venv\Scripts\activate     # Windows
   ```

5. **Install Python packages:**
   ```bash
   pip install numpy pandas matplotlib scipy scikit-learn jupyter openai anthropic
   ```

See `prereqs/Environment_Setup.tex` for detailed instructions.

### ALICE Access

Trainees receive credentials for [ALICE](https://mathresearch.utsa.edu/ALICE), the computational platform supporting DAIR³ exercises. Look for an email with subject line "DAIR³ 2026 Cohort."

## Building LaTeX Documents

Documents are compiled from within their respective folders using relative paths to shared resources:

```bash
# Challenge document
cd challenge2026
pdflatex 2026DAIR-3.tex
pdflatex 2026DAIR-3.tex  # Second pass for references

# Prerequisites document
cd prereqs
pdflatex DAIR-Prerequisites.tex
pdflatex DAIR-Prerequisites.tex
```

### Dependencies

- LaTeX distribution (MiKTeX, TeX Live, or MacTeX)
- Required packages: `geometry`, `hyperref`, `graphicx`, `listings`, `booktabs`, `longtable`, `amsmath`, `xcolor`, `fancyhdr`, `natbib`

## Contributing

### Git Workflow

We have given you a template to synchronizes with multiple remotes. Use the provided script:

```bash
gh.bat "Your commit message"
```

This script:
1. Stages all changes (`git add -A`)
2. Pulls from origin/main
3. Commits with your message
4. Pushes to both `origin` and `biomathematicus` remotes

### File Organization Principles

- **common/**: Only files shared across multiple documents
- **challenge20XX/**: Year-specific challenge materials
- **prereqs/**: Setup documentation (not challenge-specific)
- **images/**: Non-shared images (challenge-specific, chapter-specific)
- **source/**: Runnable code examples referenced by LaTeX documents

## Team

### Faculty

- **Clifton Addison** — Associate Professor of Biostatistics, Jackson State University
- **Yalanda Barner** — Assistant Professor of Health Policy and Management, Jackson State University
- **Johann Gagnon-Bartsch** — Associate Professor of Statistics, University of Michigan
- **Juan B. Gutiérrez** — Principal Investigator; Professor of Mathematics, UT San Antonio
- **Gregory Hunt** — Assistant Professor of Mathematics, College of William and Mary
- **Brenda Jenkins** — Director of Training and Education, Jackson State University
- **Erin Kaleba** — Director, Data Office for Clinical and Translational Research, University of Michigan
- **Jing Liu** — Principal Investigator; MIDAS Executive Director, University of Michigan
- **Jodyn Platt** — Associate Professor of Learning Health Sciences, University of Michigan
- **Suraj Rampure** — Lecturer III in EECS, University of Michigan
- **Kerby Shedden** — Professor of Statistics and Biostatistics, University of Michigan

### Administrative Support

- **Kelly Psilidis** — Faculty Training Program Manager, University of Michigan
- **Michele Randolph** — Evaluation Specialist, Marsal School of Education, University of Michigan

## License

This project is licensed under the **GNU General Public License v3.0**. See [LICENSE](LICENSE) for details.

## Acknowledgments

This work is supported by the National Institutes of Health under R25 award [1R25GM151182](https://reporter.nih.gov/project-details/10723223#history). The content is solely the responsibility of the authors and does not necessarily represent the official views of the NIH.

---

**Contact:** Kelly Psilidis [psilidis@umich.edu](mailto:psilidis@umich.edu)

**Repository:** [https://github.com/DAIR3/DAIR3-Workshop](https://github.com/DAIR3/DAIR3-Workshop)
