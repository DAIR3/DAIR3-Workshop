# DAIR³ - Data Analytics and Interdisciplinary Research

## Repository Structure

```
├── common/          # Shared LaTeX configuration, styles, and common images
├── images/          # Challenge-specific and extracted images
├── challenge2026/   # 2026 Data Challenge: Vital Statistics
├── prereqs/         # Prerequisites and environment setup documentation
└── README.md
```

## Environment Setup

See the [Prerequisites Guide](prereqs/EnvSetup_VisualStudioCode.pdf) or compile `prereqs/DAIR-Prerequisites.tex` for detailed environment setup instructions.

### Quick Start
1. Install Visual Studio Code
2. Set up Python environment using the guide in `prereqs/`
3. Access [ALICE](https://mathresearch.utsa.edu/ALICE) with your DAIR³ credentials (look for an email with the subject *DAIR³ 2026 Cohort*)

## 2026 Data Challenge

The 2026 Data Challenge focuses on **Vital Statistics** - projecting underweight newborns and infant mortality by county in Texas for 2030.

Materials are located in `challenge2026/`.

## Building LaTeX Documents

Compile from within each challenge folder:
```bash
cd challenge2026
pdflatex 2026DAIR-3.tex
```

Documents use shared configuration from `../common/`.

## License

This project is licensed under the GNU General Public License v3.0 - see [LICENSE](LICENSE) for details.
