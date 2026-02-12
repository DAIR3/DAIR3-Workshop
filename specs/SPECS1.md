# SPECS1.md - Repository Reorganization Specifications

## Overview
Reorganize the DAIR³ repository to separate common/shared files from challenge-specific files, enabling a scalable structure for future data challenges.

## Target Directory Structure
```
/
├── common/                          # Shared LaTeX configuration and images
│   ├── DAIR3Config.tex
│   ├── DAIR3FrontMatter.tex
│   ├── lstsetC.tex
│   ├── lstsetMATLAB.tex
│   ├── lstsetPython.tex
│   ├── lstsetR.tex
│   ├── BackgroundCover.png
│   ├── DatathonCover.png
│   ├── DAIR3_white_solid_clean.png
│   ├── RowdyDatathonLogo.png
│   ├── RowdyDatathonQR.png
│   ├── UTSAVectorOrange.pdf
│   └── UTSAVectorOrange.png
├── images/                          # Non-common images (challenge-specific, extracted from PDFs)
│   └── (images extracted from EnvSetup_VisualStudioCode.pdf)
├── challenge2026/                   # 2026 Data Challenge materials
│   └── 2026DAIR-3.tex
├── prereqs/                         # Prerequisites and environment setup
│   ├── DAIR-Prerequisites.tex       # Main LaTeX document (wrapper)
│   ├── Environment_Setup.tex        # Content converted from PDF
│   └── EnvSetup_VisualStudioCode.pdf
├── README.md                        # Updated with new structure
├── LICENSE
├── .gitignore
├── DAIR3.bat
└── gh.bat
```

---

## Phase 1: Create Directory Structure

### Task 1.1: Create new folders
```bash
mkdir common
mkdir images
mkdir challenge2026
mkdir prereqs
```

---

## Phase 2: Move Common Files to `common/`

### Task 2.1: Move common LaTeX configuration files
Use `git mv` for all operations to preserve git history.

```bash
git mv latex/DAIR3Config.tex common/
git mv latex/DAIR3FrontMatter.tex common/
git mv latex/lstsetC.tex common/
git mv latex/lstsetMATLAB.tex common/
git mv latex/lstsetPython.tex common/
git mv latex/lstsetR.tex common/
```

### Task 2.2: Move common image files
```bash
git mv latex/BackgroundCover.png common/
git mv latex/DatathonCover.png common/
git mv latex/DAIR3_white_solid_clean.png common/
git mv latex/RowdyDatathonLogo.png common/
git mv latex/RowdyDatathonQR.png common/
git mv latex/UTSAVectorOrange.pdf common/
git mv latex/UTSAVectorOrange.png common/
```

**Note:** If any of these image files don't exist in `latex/`, skip them and document which files were missing.

---

## Phase 3: Move Challenge-Specific Files to `challenge2026/`

### Task 3.1: Move remaining non-common files from `latex/`
```bash
git mv latex/2026DAIR-3.tex challenge2026/
```

### Task 3.2: Move any other non-common files
Check for any remaining files in `latex/` that are specific to the 2026 challenge (e.g., `Excel.png` referenced in the document) and move them:
```bash
# Example - adjust based on actual files found
git mv latex/Excel.png images/
```

### Task 3.3: Remove empty `latex/` directory
After all files are moved:
```bash
git rm -r latex/
```
If git complains about non-empty directory, first verify all files have been moved, then use `rmdir latex/` followed by staging the removal.

---

## Phase 4: Create Prerequisites Materials

### Task 4.1: Copy PDF to prereqs folder
```bash
cp EnvSetup_VisualStudioCode.pdf prereqs/
git add prereqs/EnvSetup_VisualStudioCode.pdf
```

### Task 4.2: Extract images from PDF
Use a tool like `pdfimages` (from poppler-utils) or Python with `pdf2image`/`PyMuPDF`:

```bash
# Option A: Using pdfimages (if available)
pdfimages -png EnvSetup_VisualStudioCode.pdf images/envsetup

# Option B: Using Python with PyMuPDF
python -c "
import fitz
doc = fitz.open('EnvSetup_VisualStudioCode.pdf')
for i, page in enumerate(doc):
    for j, img in enumerate(page.get_images()):
        xref = img[0]
        pix = fitz.Pixmap(doc, xref)
        pix.save(f'images/envsetup-{i+1}-{j+1}.png')
"
```

### Task 4.3: Create `prereqs/DAIR-Prerequisites.tex`
Create a LaTeX wrapper document that uses the common configuration:

```latex
\documentclass[letterpaper,12pt]{report} 
\newcommand{\TheTitle}{DAIR$^3$}
\newcommand{\TheSubtitle}{Prerequisites and Environment Setup} 
\newcommand{\TheAuthor}{Juan B. Guti\'errez}  
\newcommand{\ThePageCount}{TBD}
\newcommand{\TheDate}{2026}  
\newcommand{\TheObsolescenceDate}{December 31, 2026}  

% Configure instance type
\newcommand{\CLASSROOM}{1} 
\newcommand{\DATATHON}{2} 
\newcommand{\DocVersion}{\CLASSROOM}

% Include common configuration (adjust path)
\include{../common/DAIR3Config}

\begin{document}
    \input{../common/DAIR3FrontMatter}
    \setcounter{page}{1}
    \tableofcontents 
    \newpage

    \input{Environment_Setup}

\end{document}
```

### Task 4.4: Create `prereqs/Environment_Setup.tex`
Convert the content of `EnvSetup_VisualStudioCode.pdf` to LaTeX format.

**Process:**
1. Extract text content from PDF (use `pdftotext` or Python `PyMuPDF`)
2. Structure content with appropriate LaTeX sectioning
3. Replace embedded images with `\includegraphics{../images/envsetup-X-Y.png}`
4. Format code blocks using the `lstset` configurations
5. Preserve hyperlinks using `\href{}`

**Expected structure:**
```latex
\chapter{Environment Setup}

\section{Introduction}
% Content from PDF...

\section{Installing Visual Studio Code}
% Content from PDF...
% Images referenced as: \includegraphics[width=0.8\textwidth]{../images/envsetup-1-1.png}

\section{Python Environment}
% Content from PDF...

% Continue with remaining sections...
```

---

## Phase 5: Update Path References

### Task 5.1: Update `common/DAIR3Config.tex`
The lstset input statements reference files in the same directory, so no path change needed:
```latex
\input{lstsetC}
\input{lstsetMATLAB}
\input{lstsetR}
\input{lstsetPython}
```

**However**, add graphicspath directive after the document setup section to allow LaTeX to find images when compiling from challenge folders:
```latex
\graphicspath{{../common/}{../images/}}
```

### Task 5.2: Update `common/DAIR3FrontMatter.tex`
No changes needed to image references within this file - the `\graphicspath` directive in DAIR3Config.tex will handle path resolution.

### Task 5.3: Update `challenge2026/2026DAIR-3.tex`
Update include/input paths:
```latex
% Original
\include{DAIR3Config}

% Updated
\include{../common/DAIR3Config}
```

```latex
% Original
\input{DAIR3FrontMatter}

% Updated
\input{../common/DAIR3FrontMatter}
```

Update any image references specific to this document:
```latex
% Original (example)
\includegraphics{Excel.png}

% Updated
\includegraphics{../images/Excel.png}
```

---

## Phase 6: Update README.md

### Task 6.1: Replace README.md content
Update with new structure documentation:

```markdown
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
```

---

## Phase 7: Verification Checklist

### Task 7.1: Verify file moves
- [ ] All common files exist in `common/`
- [ ] All challenge files exist in `challenge2026/`
- [ ] `latex/` directory is removed
- [ ] No broken symlinks or missing files

### Task 7.2: Verify LaTeX compilation
```bash
cd challenge2026
pdflatex 2026DAIR-3.tex
# Should compile without path errors
```

```bash
cd prereqs
pdflatex DAIR-Prerequisites.tex
# Should compile without path errors
```

### Task 7.3: Verify git status
```bash
git status
# All changes should be staged
# No untracked files that should be tracked
```

### Task 7.4: Stage all changes
```bash
git add -A
```

---

## Phase 8: Final Notes

### Do NOT commit yet
The user will run `gh.bat` to commit and push to both remotes after reviewing changes.

### Files that may need manual review:
1. `Environment_Setup.tex` - PDF conversion may need formatting adjustments
2. Image extractions - may need renaming for clarity
3. Any hardcoded paths in LaTeX files not caught by automated updates

### Known dependencies:
- `poppler-utils` or `PyMuPDF` for PDF image extraction
- `pdftotext` for PDF text extraction (or PyMuPDF)
- LaTeX distribution for compilation verification

---

## Execution Order Summary

1. Create directories: `common/`, `images/`, `challenge2026/`, `prereqs/`
2. `git mv` common tex files to `common/`
3. `git mv` common image files to `common/`
4. `git mv` challenge files to `challenge2026/`
5. `git mv` non-common images to `images/`
6. `git rm -r latex/` (after verifying empty)
7. Copy PDF to `prereqs/`
8. Extract images from PDF to `images/`
9. Create `prereqs/DAIR-Prerequisites.tex`
10. Convert PDF content to `prereqs/Environment_Setup.tex`
11. Add `\graphicspath{{../common/}{../images/}}` to `common/DAIR3Config.tex`
12. Update include/input paths in `challenge2026/2026DAIR-3.tex`
13. Update `README.md`
14. Verify LaTeX compilation in both folders
15. `git add -A`
16. User runs `gh.bat "Reorganize repository structure"`
