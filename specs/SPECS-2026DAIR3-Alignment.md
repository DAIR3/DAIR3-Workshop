# SPECS-2026DAIR3-Alignment.md

## Overview

Align `/challenge2026/2026DAIR-3.tex` with the authoritative curriculum documents:
- **Primary source:** `Curriculum_with_Learning_Objectives-_2026_DRAFT.docx`
- **Secondary source:** `Curriculum_SLO_and_Assessment_2026_DRAFT.xlsx` (sheet: "Edited UNITS - 2026")
- **Unit 7 supplement:** `EthicsOfAgents.tex` (for Section 7.1 content)

## Current State Analysis

### Current Structure of 2026DAIR-3.tex

```
Chapter 1: 2022 Data Challenge - Vital Statistics  [PROBLEM: says "2022" should be "2026"]
  - Section: Problem Description
  - Section: Data Description  
  - Section: Identifying Underweight Cutoff Points
  - Section: Data Files
  - Section: Criteria

Chapter 2: Analysis Activities  [PROBLEM: duplicated chapter title]
  - Section: A single year of vital statistics

Chapter 3: Analysis Activities  [PROBLEM: duplicated chapter title, incomplete units]
  - Section 1: Unit 1 - RCR and Ethics (partial)
  - Section 2: Unit 2 - Data Management (missing)
  - Section 3: Unit 3 - Rigorous Statistical Design (missing)
  - Section 4: Unit 4 - Predictive Models (missing)
  - Section 5: Unit 5 - Reproducible Workflows (missing)
  - Section 6: Unit 6 - Meta-analysis (missing)
  - Section 7: Unit 7 - Transformer AI (outdated, needs 7.1 Ethics content)
```

### Target Structure (from Word Document)

```
Chapter 1: 2026 Data Challenge - Vital Statistics
  - Problem Description
  - Data Description
  - Identifying Underweight Cutoff Points
  - Data Files
  - Criteria

Chapter 2: Foundational Analysis Activities
  - A single year of vital statistics (existing content, keep)

Chapter 3: Unit 1 - Responsible Conduct of Research (3 hours)
  - 1.1 RCR in the context of biomedical data science
  - 1.2 What are ethics? Ethical issues in biomedical data science

Chapter 4: Unit 2 - Foundations of Data in Biomedical Research (7 hours)
  - 2.1 Data Management - Introduction to the Jackson Heart Study
  - 2.2 Metadata - Data About Data
  - 2.3 Data Representation
  - 2.4 Data Sharing

Chapter 5: Unit 3 - Rigorous Statistical Design (5.5 hours)
  - 3.1 Principles of study design for empirical research
  - 3.2 Analytic plans and statistical power
  - 3.3 Sources of bias and causal interpretation

Chapter 6: Unit 4 - Designing Interpretable Predictive Models (5 hours)
  - 4.0 Pre-reading materials
  - 4.1 Foundations of Supervised Learning
  - 4.2 Feature Engineering
  - 4.3 Feature Selection and Model Explainability
  - 4.4 Model Evaluation, Comparison, and Reporting

Chapter 7: Unit 5 - Reproducible Workflows (5.5 hours)
  - 5.1 Goals of Reproducible Analyses
  - 5.2 Reproducibility via Code Notebooks
  - 5.3 Best practices for Reproducible Programming
  - 5.4 Version Control
  - 5.5 Containers
  - 5.6 Assembling a full analysis pipeline

Chapter 8: Unit 6 - Meta-analysis (3.5 hours)
  - 6.1 Key concepts in research synthesis
  - 6.2 Accounting for heterogeneity
  - 6.3 Accounting for non-independence and network effects

Chapter 9: Unit 7 - Transformer-based AI in Biomedical Research (3 hours)
  - 7.1 The Ethics of AI Agents
  - 7.2 AI Agents for Technical Tasks - Consensus in LLMs
  - 7.3 LLMs in Biomedical Research - Building Consensus Pipelines
```

---

## Phase 1: Fix Chapter 1 Title and Verify Content

### Task 1.1: Update chapter title from "2022" to "2026"

**Location:** Around line 57 in current file

**Find:**
```latex
\chapter{2022 Data Challenge - Vital Statistics}  \newpage
```

**Replace with:**
```latex
\chapter{2026 Data Challenge - Vital Statistics}  \newpage
```

### Task 1.2: Verify Problem Description section exists and is complete

The current content appears complete. No changes needed unless discrepancies found.

### Task 1.3: Verify Data Description section is complete

Current content references NCHS, SEER, SEDAC. Appears complete.

### Task 1.4: Verify remaining Chapter 1 sections

- Identifying Underweight Cutoff Points: Present and complete
- Data Files: Present with table
- Criteria: Present with evaluation table

**No changes needed to Chapter 1 content beyond title fix.**

---

## Phase 2: Restructure Chapter 2

### Task 2.1: Rename Chapter 2

**Find:**
```latex
\chapter{Analysis Activities}  \newpage
```
(First occurrence after Chapter 1)

**Replace with:**
```latex
\chapter{Foundational Analysis Activities}  \newpage
```

### Task 2.2: Keep existing "A single year of vital statistics" section

This section contains useful introductory programming exercises. Retain as-is.

---

## Phase 3: Restructure Chapter 3 into Proper Unit Chapters

The current Chapter 3 titled "Analysis Activities" contains incomplete unit stubs. This needs to be completely restructured into separate chapters (one per unit).

### Task 3.1: Replace the entire Chapter 3 section

**Find and delete:** The entire chapter starting with:
```latex
\chapter{Analysis Activities}  \newpage
```
(Second occurrence)

Through to `\end{document}`

**Replace with:** The content specified in Phase 3.2 through Phase 3.8 below.

### Task 3.2: Create Chapter 3 - Unit 1: Responsible Conduct of Research

```latex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\chapter{Unit 1: Responsible Conduct of Research}
\label{chap:unit1}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\textbf{Total Time: 3 hours}

%================================================================
\section{RCR in the Context of Biomedical Data Science}
\label{sec:1.1}
%================================================================

This lesson examines the sociotechnical and ethical aspects of biomedical data science. We will consider ethical issues in the responsible conduct of research that are novel to or pose new challenges in the context of biomedical data science such as reproducibility and privacy. Students will also consider biomedical data science as a sociotechnical system and define roles for themselves and other key constituents.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Explain novel ethical issues in responsible conduct of research for data science such as reproducibility and privacy.
    \item Describe the landscape of biomedical data science as a sociotechnical system and articulate roles.
\end{enumerate}

\subsection{Assessment Instrument}

\begin{itemize}
    \item Compare responses to the data challenge with your peers. What issues arise?
    \item Why was date and time no longer recorded after 1987?
    \item Who decides what data to collect, how to store it and how to access it? What biases could there be in the data (e.g., data collection in rural areas, existence of infrastructure)? What is the difference between bias and trend in these data? Provide examples.
\end{itemize}

%================================================================
\section{What are Ethics? Ethical Issues in Biomedical Data Science}
\label{sec:1.2}
%================================================================

This lesson equips students to address ethical challenges in biomedical data science. Learners will identify strategies for ethical secondary data use, analyze engagement approaches, and develop frameworks for ethical project review, emphasizing anticipatory governance and responsible data science practices. Case studies will be used that draw on the group project selected for the 2026 cohort.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Differentiate between traditional bioethical, sociotechnical, and other ethical approaches to data science research and applications.
    \item Evaluate key ethical challenges in biomedical data science.
    \item Identify and formulate approaches to address ethical issues in secondary use, including anticipatory governance principles.
    \item Develop a framework for ethical review of biomedical data science projects.
\end{enumerate}

\subsection{Assessment Instrument}

The assessment involves designing a governance framework for a data science initiative, selecting one of three projects derived from the course-wide data activity. The framework must address stakeholder engagement, decision-making, monitoring, benefit-sharing, unexpected impacts, and consent, while evaluating ethical considerations, future challenges, and feasibility. The goal is to create an ethical, well-structured, and adaptable governance plan.
```

### Task 3.3: Create Chapter 4 - Unit 2: Foundations of Data in Biomedical Research

```latex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\chapter{Unit 2: Foundations of Data in Biomedical Research}
\label{chap:unit2}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\textbf{Total Time: 7 hours}

%================================================================
\section{Data Management - Introduction to the Jackson Heart Study}
\label{sec:2.1}
%================================================================

\textbf{Time: 3 hours}

This lesson provides an overview of the Jackson Heart Study (JHS), focusing on its design, data collection, and variable interpretation. Students will describe the JHS's purpose, population, and exam structure, summarize clinical, survey, and genetic data collection methods across study phases, and learn to use JHS codebooks to identify variables for research questions.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Describe the JHS Study Design: Explain the purpose, population, and structure of the JHS, including its major exams.
    \item Summarize Data Collection Methods: Identify the types of data collected (e.g., clinical, survey, genetic) and the methods used in different study phases.
    \item Interpret Key Variables and Codebooks: Understand how to use JHS codebooks to find variables relevant to specific research questions.
\end{enumerate}

\subsection{Assessment Instrument}

\begin{enumerate}
    \item Describe in your own words the purpose of the JHS, cohort characteristics, and exam waves.
    \item Describe how JHS collects specific data (e.g., CAC scores, lipid tests) and potential biases in data collection.
    \item Answer the following question: ``Association between hysterectomy and cardiovascular disease in the JHS, adjusting for covariates'' by locating relevant variables in the JHS codebook. Describe the variables chosen and their rationale.
\end{enumerate}

\subsubsection{The Process of Manuscript Development in the Jackson Heart Study}

This lesson covers the process for requesting and obtaining Jackson Heart Study (JHS) data. Students will learn to navigate data access procedures, including submitting manuscript or ancillary study proposals, completing data use agreements, and addressing ethical considerations to ensure responsible use of JHS data.

\textbf{Learning Objective:} Explain Data Access Procedures: Describe the process for requesting and obtaining JHS data, including data use agreements and ethical considerations.

\textbf{Assessment:}
\begin{enumerate}
    \item In your own words, enumerate the steps involved in the process for developing a JHS manuscript.
    \item Using the information acquired from the lecture, draft a mock JHS manuscript proposal, using the Manuscript Proposal Form provided and the sample manuscript proposal.
\end{enumerate}

%================================================================
\section{Metadata - Data About Data}
\label{sec:2.2}
%================================================================

\textbf{Time: 0.75 hours}

This lesson explores the essentials of metadata in biomedical research datasets, covering data collection methods, population, and context. Students will learn to identify high-quality metadata that supports reproducibility and distinguish it from inadequate metadata, ensuring robust and reliable research outcomes.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Understand standard components of metadata on biomedical science research datasets: how the data were collected, on what population, under what circumstances, etc.
    \item Learn to distinguish between good and bad metadata for reproducibility.
\end{enumerate}

\subsection{Assessment Instrument}

\begin{itemize}
    \item List 5 critical metadata categories that researchers need to know when reproducing findings.
    \item From the Mathew E. Hauer article called, ``Data Descriptors: Population projections for U.S. Counties by age, sex, and race,'' what metadata are provided about how the population data were collected?
\end{itemize}

%================================================================
\section{Data Representation}
\label{sec:2.3}
%================================================================

\textbf{Time: 0.75 hours}

This lesson examines how data can be represented in multiple ways, highlighting that each representation impacts task efficiency. Students will learn to select optimal data representations tailored to specific research tasks, balancing ease and complexity.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Understand that the same data can be represented in many ways.
    \item Appreciate that each representation choice makes some tasks easier, but others more difficult.
    \item Learn how to choose a good representation for the task at hand.
\end{enumerate}

\subsection{Assessment Instrument}

The NCHS data are provided as a flat file with more than 100 variables. What is an alternative representation of these same data? Is the original flat file or your alternative schema more conducive to analyses, and why?

%================================================================
\section{Data Sharing}
\label{sec:2.4}
%================================================================

\textbf{Time: 2.5 hours}

\subsubsection{Data Sharing 101}

This lesson introduces the principles of Open Science, focusing on the NIH Data Management \& Sharing Policy's rationale and key components. Students will explore the FAIR Guiding Principles (Findable, Accessible, Interoperable, Reusable), learning their definitions and practical examples to promote transparent and reproducible research.

\textbf{Learning Objectives:}
\begin{itemize}
    \item Appreciate the foundations of Open Science
    \item NIH Data Management \& Sharing Policy: Rationale and Key components
    \item FAIR Guiding Principles: Definition and examples
\end{itemize}

\textbf{Assessment:} Define rationale behind NIH Data Management \& Sharing requirement; list 5 key components you should include in your 2-page Data Management Plan; list the 4 FAIR principles.

\subsubsection{Data Sharing - The Reality}

This lesson examines privacy and confidentiality concerns in Open Science and data sharing. Students will learn to differentiate between biomedical research types: bench science, human clinical trials, and animal models, and understand the unique data sharing implications for each, including ethical considerations and strategies to protect sensitive data while promoting transparency.

\textbf{Learning Objectives:}
\begin{enumerate}
    \item Learn about privacy/confidentiality concerns related to Open Science and data sharing.
    \item Articulate difference in types of biomedical research (bench science, human clinical trials, animal models) and what implications data sharing has for each.
\end{enumerate}

\textbf{Assessment:}
\begin{itemize}
    \item Create a 2-page Data Management and Sharing Plan following the NIH requirements for your analyses of the birthweight data challenge.
    \item Apply the FAIR principles (Findable, Accessible, Interoperable, Reusable) to your datasets.
\end{itemize}
```

### Task 3.4: Create Chapter 5 - Unit 3: Rigorous Statistical Design

```latex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\chapter{Unit 3: Rigorous Statistical Design}
\label{chap:unit3}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\textbf{Total Time: 5.5 hours}

%================================================================
\section{Principles of Study Design for Empirical Research}
\label{sec:3.1}
%================================================================

We will provide a practical introduction to conducting rigorous data-driven research in a health-science setting that is scientifically-grounded and analytically sophisticated. We will focus on methods for data analysis that can be utilized in the setting of population health research, leveraging official statistics or other systematically collected data with spatial and temporal structure.

\subsection{Learning Objectives}

\begin{enumerate}
    \item The learner will be able to rapidly internalize the current state of scientific knowledge about a specific health-related topic. The goal here is not to master every detail that a specialist would know, but rather to develop fluency with the key known mechanisms, to recognize the quantitative strengths of established relationships, and to identify gaps in the current state of knowledge.
    
    \item The learner will be able to rapidly internalize the structure and capacity of one or more datasets that can be used to conduct research on a specific health-related topic. This includes identifying the units of analysis (who is being measured) and the variables or attributes (what is being measured), understanding how the units of analysis were selected, what population they represent, how the variables were measured, and what types of measurement errors may be present.
    
    \item The learner will be able to engage in a sophisticated discussion of quantitative relationships among measured quantities. This includes considering how such relationships can be assessed, how they contribute to achieving research aims, what it means for an association to be causal, and the meanings of confounding and heterogeneity.
    
    \item The learner will have a sophisticated understanding of the opportunities provided by temporal and longitudinal data. This includes understanding notions of spatial and temporal heterogeneity, the specific types of confounding that can be resolved with longitudinal data, and the implications of autocorrelation and other forms of dependence for estimation precision.
    
    \item The learner will be able to develop a rigorous analytic plan to address a hypothesis that adds to the state of knowledge about a health science-relevant topic, using available data and employing sophisticated analytic methods.
    
    \item The learner will have a sophisticated understanding of uncertainty, including (a) \textit{a priori} notions of uncertainty as reflected in statistical power, and (b) uncertainty following data analysis as reflected in statistical measures of confidence, significance, and precision. The learner will understand how uncertainty is influenced by sample size, sampling and experimental design, collinearity, dependence of measurements, measurement error, and heterogeneity, among other factors.
    
    \item The learner will be able to communicate in both speech and writing the high-level message as well as the technical details of a sophisticated, data-driven scientific inquiry in a health science setting. This will include strategies for effectively communicating to different audiences using precise but accessible language, providing complete documentation sufficient for reproducibility, while still having a narrative that does not lose sight of the forest for the trees.
\end{enumerate}

\subsection{Assessment Instrument}

The assessment will be based on the vital statistics data challenge, centered on birth outcomes (underweight birth and infant mortality) in the state of Texas. Learners will be asked to develop a sophisticated but tractable research aim that can be addressed through careful analysis of public datasets from NCHS, SEER, SEDAC, and elsewhere. Learners will then (i) implement the analysis, (ii) interpret findings, and (iii) report their results. Methods and strategies for all three of these requirements will be covered in lectures and written materials provided to the learners.

%================================================================
\section{Analytic Plans and Statistical Power}
\label{sec:3.2}
%================================================================

Further developing topic 6a above, this lesson equips learners with the skills needed to assess the likelihood of success of a rigorous analytical plan that is aligned with a specific scientific research aim. In most empirical research this is known informally as ``power analysis,'' but here we take a much more expansive definition of this concept in order to consider all forms of \textit{a priori} vetting to which an analytic plan can be subjected.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Learners will understand the concepts of effect size, parameter estimation, and estimation precision, as the core theoretical ideas upon which \textit{a priori} power analysis is based.
    
    \item Learners will understand how estimation precision is related to the scope of available data, how these data were collected, and properties of the analytic approach. Learners will be able to articulate what types of data could be collected in the future to most efficiently improve the statistical power.
    
    \item Learners will understand the conventional definition of power as the probability of research success contingent on the unknown true effect size. Learners will also be conversant in alternative notions of power that are directly related to estimation precision or prediction accuracy rather than hypothesis testing.
    
    \item Learners will be able to articulate how assessments of statistical power do and do not reflect the real-world reproducibility of analytic findings.
\end{enumerate}

\subsection{Assessment Instrument}

Carry out a comprehensive assessment of \textit{a priori} power for the analysis conducted in Section~\ref{sec:3.1}. This analysis should not take into account the actual findings of this analysis, but rather should evaluate the proposed research design, situating yourself at the point before the analysis was implemented and executed.

%================================================================
\section{Sources of Bias and Causal Interpretation}
\label{sec:3.3}
%================================================================

This section of the course will revisit and deepen learners' understanding of issues related to bias and causality introduced more briefly in Section~\ref{sec:3.1}. Students will understand how bias is directly related to fundamental notions of causality, while being complementary to the notion of estimation precision as developed in Section~\ref{sec:3.2}. Learners will understand why observational data is nearly always at risk for such bias, but why an ideal experiment is free of such concerns (but is subject to other limitations on validity). Learners will learn to identify potential sources of bias, uncertainty, and non-reproducibility in observational cohort studies, and suggest basic strategies to address these issues.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Learners will be able to identify exposures and outcomes in a research design, and identify plausible confounders (both observed and unobserved) of the exposure/outcome relationship.
    
    \item Learners will be able to articulate how temporal and spatial structure enables deeper understanding of exposure/outcome relationships, and opens new opportunities to reduce or eliminate certain types of bias.
    
    \item Learners will understand the different ways that an auxiliary variable can enter an analysis, such as being colliders and mediators, and will understand when an auxiliary variable is unlikely to introduce confounding bias.
    
    \item Learners will understand how certain forms of bias can be reduced or eliminated analytically, while others cannot.
    
    \item Learners will understand how various methods for sensitivity analysis can bound or provide conditional insights into the likely contributions of unobserved confounders.
\end{enumerate}

\subsection{Assessment Instrument}

Building on the assessments for Sections~\ref{sec:3.1} and~\ref{sec:3.2}, provide specific examples of potential measured confounders or other measured sources of bias. To the extent possible, provide analyses that do, and that do not attempt to compensate for such measured sources of bias, and compare these results. Then, provide some examples of unmeasured sources of bias, and conduct sensitivity analyses to assess the likely potential impact of these sources of bias. Finally, use negative control and/or negative exposure methods to provide further context into any causal associations identified through the analysis that you conducted in Section~\ref{sec:3.1}.
```

### Task 3.5: Create Chapter 6 - Unit 4: Designing Interpretable Predictive Models

```latex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\chapter{Unit 4: Designing Interpretable Predictive Models}
\label{chap:unit4}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\textbf{Total Time: 5 hours} \\
\textbf{Instructional Time: 3.5 hours} \\
\textbf{Unit Project Work Time: 1.5 hours}

This unit will introduce the foundations of supervised machine learning models, with a focus on interpretability and communicating decision-making.

%================================================================
\section{Pre-reading Materials}
\label{sec:4.0}
%================================================================

These pre-reading materials focus on foundational concepts in statistics and machine learning.

\subsection{Learning Objectives}

Learners will be able to:
\begin{enumerate}
    \item Understand ideas from introductory statistics, including measures of central tendency and variability, visualization techniques, and lines of best fit.
    \item Understand how to fit a basic machine learning model in Python using sklearn and real data.
    \item Understand TRIPOD guidelines pertinent to this session.
\end{enumerate}

\subsection{Assessment Instrument}

Learners will be asked to load a dataset into sklearn, fit a linear regression model, and report the model's mean squared error.

%================================================================
\section{Foundations of Supervised Learning}
\label{sec:4.1}
%================================================================

\textbf{Time: 1.5 hours (Instructional: 70 minutes)}

We will start by providing a broad overview of the landscape of machine learning, and practice the general workflow for building a model, starting from raw data.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Understand the landscape of possible machine learning models (supervised vs. unsupervised, regression vs. classification).
    \item Build a linear regression model, understanding how its optimal parameters were chosen and how they can be interpreted.
    \item Practice the workflow for performing a train-test split, training a model on training data, evaluating a model on held-out test data, and the role of cross-validation.
    \item Understand the risks of overfitting and data leakage.
\end{enumerate}

\subsection{Assessment Instrument (20 minutes)}

Learners will build a basic linear regression model using the Vital Statistics dataset, which will serve as a baseline for future work.

%================================================================
\section{Feature Engineering}
\label{sec:4.2}
%================================================================

\textbf{Time: 1 hour (Instructional: 60 minutes)}

Next, we will cover how linear regression can be extended to a variety of other tasks, and how to create new features that capture trends in the data.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Practice interpreting the coefficients of fit models.
    \item Use visualizations to spot patterns in the data that inform feature engineering decisions, while keeping in mind the risks of overfitting.
    \item Understand the differences between encoding strategies (one hot encoding vs. ordinal encoding).
\end{enumerate}

\subsection{Assessment Instrument (20 minutes)}

Learners will be given a practical task and will need to build a small feature engineering Pipeline in sklearn and be asked to document their decision-making process.

%================================================================
\section{Feature Selection and Model Explainability}
\label{sec:4.3}
%================================================================

\textbf{Time: 1.5 hours (Instructional: 60 minutes)}

Building upon Section~\ref{sec:4.2}, students will gain an understanding of the statistical approaches involved in selecting features.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Understand mutual information as a feature selection criterion.
    \item Understand how to apply statistically appropriate techniques to select and justify features, e.g., Pearson, Spearman, and Cram\'er's V correlations, Variance Inflation Factor, multiple $R^2$.
    \item Understand the role of interaction terms.
\end{enumerate}

\subsection{Assessment Instrument (30 minutes)}

Learners will practice generating feature importance analyses and documenting their feature selection rationale.

%================================================================
\section{Model Evaluation, Comparison, and Reporting}
\label{sec:4.4}
%================================================================

\textbf{Time: 1 hour (Instructional: 30 minutes)}

Finally, students will practice communicating the performance and design decisions behind a model to external stakeholders.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Understand how to report and compare different models on the same task (e.g., MSE/RMSE/MAE for regression models, accuracy vs. precision vs. recall vs. ROC-AUC vs. F1 for classification models).
    \item Practice communicating modeling choices and model behavior.
\end{enumerate}

\subsection{Assessment Instrument (30 minutes)}

Students will write a short report documenting and comparing the performances of two models, including relevant visualizations.
```

### Task 3.6: Create Chapter 7 - Unit 5: Reproducible Workflows

```latex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\chapter{Unit 5: Reproducible Workflows}
\label{chap:unit5}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\textbf{Total Time: 5.5 hours}

%================================================================
\section{Goals of Reproducible Analyses}
\label{sec:5.1}
%================================================================

Learn the key goals and challenges of creating reproducible, transparent, and user-friendly analyses that are easy to share and reuse.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Awareness of key challenges and goals when creating reproducible workflows, including making analyses reproducible, user friendly, transparent, reusable, version controlled, and archived.
\end{enumerate}

%================================================================
\section{Reproducibility via Code Notebooks}
\label{sec:5.2}
%================================================================

Gain awareness of Markdown, Jupyter, and Quarto, and learn how these tools integrate to create clear, reproducible workflows for data analysis and reporting.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Awareness of Markdown, Jupyter, Quarto, and how these tools can be integrated into reproducible workflows.
\end{enumerate}

%================================================================
\section{Best Practices for Reproducible Programming}
\label{sec:5.3}
%================================================================

Learn essential best practices for reproducible programming, including writing clear scripts and functions, avoiding magic numbers, using caching and seeding for randomness, and refactoring code to enhance clarity, reliability, and repeatability.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Awareness of best practices for reproducible programming including writing scripts, functions, avoiding magic numbers, caching and seeding randomness, and how to refactor code to align with these practices.
\end{enumerate}

%================================================================
\section{Version Control}
\label{sec:5.4}
%================================================================

Gain a basic understanding of Git, its advantages, and learn to perform essential tasks such as cloning repositories, committing changes, and syncing with remote repositories using push and pull commands.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Familiarity with Git and its benefits, and the ability to begin using it for simple tasks, including cloning, committing changes, pushing and pulling.
\end{enumerate}

%================================================================
\section{Containers}
\label{sec:5.5}
%================================================================

Gain hands-on experience with key dependency management tools (Python virtual environments, renv, and containerization), understanding their pros and cons, and develop the skills to create and run basic Docker images.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Familiarity with various tools for dependency management, including Python virtual environments, renv, and containerization, and their respective strengths and weaknesses. Ability to create and run simple Docker images.
\end{enumerate}

%================================================================
\section{Assembling a Full Analysis Pipeline}
\label{sec:5.6}
%================================================================

Learn key factors in organizing an analysis pipeline and develop the skills to assemble a complete, reusable pipeline template.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Considerations when organizing an analysis pipeline, and the ability to assemble a full template pipeline.
\end{enumerate}

\subsection{Assessment Instrument}

\begin{enumerate}
    \item Describe your progress on the template workflow. What aspects did you find most confusing or challenging? Which tools (e.g., Git, Make, Docker) were hardest to implement, and why?
    \item What is one thing you plan to change or do differently in your own projects after today's session? Give a specific example of an analysis or workflow improvement you intend to make.
\end{enumerate}
```

### Task 3.7: Create Chapter 8 - Unit 6: Meta-analysis

```latex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\chapter{Unit 6: Meta-analysis}
\label{chap:unit6}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\textbf{Total Time: 3.5 hours}

%================================================================
\section{Key Concepts in Research Synthesis}
\label{sec:6.1}
%================================================================

This lesson provides an introduction to meta-analysis as a tool for quantitative research synthesis, with the initial goal being to estimate robust consensus effects and statistical significance levels across methodologically diverse but independent research studies. We will focus on the setting of population health science research, using data sources with a longitudinal and temporal structure. We will consider how independent data reflecting similar or identical outcomes on different populations, potentially collected with disparate measurement methods and/or varying sampling designs can be integrated to improve precision and to uncover heterogeneity and effect modifiers.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Learners will understand how meta-analysis can be seen as a form of evidence combination.
    \item Learners will be able to apply methods for evidence integration when complete data are available.
    \item Learners will understand the basic mathematics behind pooling p-values, standard errors, and confidence intervals from independent sources.
    \item Learners will be able to weight estimates with different precisions to produce an optimal pooled estimate.
    \item Learners will be exposed to newer approaches for pooling evidence including E-values and empirical likelihood methods.
\end{enumerate}

\subsection{Assessment Instrument}

The assessment will be centered on birth outcomes (pre-term birth, underweight birth, and infant mortality), in the United States and internationally, using official statistics or other sources of population-level data. Learners will be guided to appropriate sources of data, and will begin by estimating event rates at local spatial and temporal scales, and providing uncertainty assessments for all point estimates. For the purposes of this assessment, we will treat evidence sources as independent and homogeneous, even if this is unlikely to be the case.

%================================================================
\section{Accounting for Heterogeneity}
\label{sec:6.2}
%================================================================

Students will learn to separate effect size variability into statistical noise (imprecision) and true heterogeneity. We will discuss several summary measures for unexplained effect heterogeneity, and discuss how stratification and regression methods can be used to understand heterogeneity that can be attributed to known factors.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Students will understand how variation in measured effect sizes can be partitioned into the component attributable to statistical variation, and the component attributable to heterogeneity in the true effects.
    \item Students will understand how the level of heterogeneity in true effects can be partitioned into a component that is attributable to known factors, and a component that is unexplained by known factors.
    \item Students will be able to articulate the difference between statistical uncertainty and effect heterogeneity.
    \item Students will be able to utilize stratification and regression to estimate a consensus effect size and significance level from studies with heterogeneous designs and/or effect heterogeneity.
\end{enumerate}

\subsection{Assessment Instrument}

Building on the work done for Section~\ref{sec:6.1}, learners will be asked to consider how and why spatially and temporally local point estimates may be heterogeneous, and to quantify this heterogeneity. They will then identify scales at which partial pooling may be appropriate, calculate statistically efficient pooled estimates of evidence, and assess the extent to which precision was improved. Finally, they will be asked to identify potential explanatory factors for any observed heterogeneity, and to quantify the extent to which the heterogeneity can be attributed to these factors.

%================================================================
\section{Accounting for Non-independence and Network Effects}
\label{sec:6.3}
%================================================================

Grounded in the setting of population health outcomes assessed at different spatial and temporal scales, we will discuss how and why disparate sources of statistical evidence may be non-independent, and how this non-independence presents both obstacles and possibilities.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Learners will understand how non-independence of research results impacts research synthesis in terms of bias, uncertainty, and statistical power, and will be able to identify possible sources of non-independence.
    \item Learners will revisit the task of combining p-values, Z-scores and other sources of summary evidence from Section~\ref{sec:6.1}, considering extensions that accommodate non-independent evidence measures.
    \item Learners will be able to employ marginal and multilevel regression techniques to account for and leverage the presence of non-independence.
    \item Learners will be exposed to modern methods of evidence summarization such as E-values that are robust to non-independence.
\end{enumerate}

\subsection{Assessment Instrument}

Continuing the work from Sections~\ref{sec:6.1} and~\ref{sec:6.2}, students will reconsider the precision of partially pooled estimates of event rates in light of possible non-independence. Then they will consider whether and how explained and unexplained heterogeneity should be re-evaluated if the evidence sources are non-independent.
```

### Task 3.8: Create Chapter 9 - Unit 7: Transformer-based AI in Biomedical Research

```latex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\chapter{Unit 7: Transformer-based AI in Biomedical Research}
\label{chap:unit7}
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\textbf{Total Time: 3 hours}

%================================================================
\section{The Ethics of AI Agents}
\label{sec:7.1}
%================================================================

\textbf{Time: 1 hour (Instructional: 50 minutes, Project Work: 10 minutes)}

This lesson examines the ethical dimensions of using LLM-based AI agents in biomedical data science. Unlike single-turn chatbot interactions, agentic workflows involve planning, tool use, memory, and multi-agent coordination, expanding the ethical surface area considerably. Students will learn to identify invalidation risks (a broader concept than ``hallucination''), understand accountability frameworks for agent-assisted research, and apply governance-by-design principles aligned with Responsible Conduct of Research (RCR) standards.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Define an AI agent in terms of planning, tool use, memory, and multi-agent interaction, and explain why agentic workflows expand ethical risk compared to single-turn model use.
    \item Explain invalidation (factual, logical, normative, structural) as a framework broader than ``hallucination,'' and identify at least three invalidation types relevant to biomedical data science.
    \item Apply an ethics checklist to an agentic research workflow, identifying concrete risks in accuracy, authorship, privacy/confidentiality, bias, security, and sustainability.
    \item Evaluate when multi-agent critique can improve reliability and when it may be inappropriate due to confidentiality constraints, compute burden, or epistemic homogenization.
    \item Draft a compliant disclosure and accountability statement for agent-assisted work aligned with COPE/ICMJE/WAME publication-ethics norms.
\end{enumerate}

\subsection{Assessment Instrument}

\begin{enumerate}
    \item \textbf{Knowledge Check (6 minutes):} A short quiz covering: (a) distinguishing features of agents vs. chatbots, (b) types of invalidation, (c) authorship attribution for AI-assisted work, (d) confidentiality risks in peer review contexts, and (e) multi-agent compute tradeoffs.
    
    \item \textbf{Case-Based Evaluation (12 minutes):} In small groups, analyze a scenario where an agentic pipeline generates a data dictionary, drafts methods text, proposes models, and summarizes results for the vital statistics data challenge. Identify risks and produce a 5-bullet ``agent governance plan'' addressing epistemic risk, confidentiality, authorship, bias/security, and sustainability.
    
    \item \textbf{Disclosure Statement:} Write a one-sentence disclosure describing how AI tools were used in an analysis, suitable for inclusion in a manuscript methods section.
\end{enumerate}

%================================================================
\section{AI Agents for Technical Tasks: Consensus in LLMs}
\label{sec:7.2}
%================================================================

\textbf{Time: 1 hour (Instructional: 45 minutes, Project Work: 15 minutes)}

This lesson introduces the theoretical foundations of transformer models and demonstrates how multiple LLM systems can be orchestrated to achieve consensus on technical tasks. Participants will work hands-on with APIs from multiple providers (e.g., OpenAI GPT, Anthropic Claude) to compare model behaviors and understand how cross-model verification can reduce invalidation. The emphasis is on programmatic integration via APIs rather than web-based interfaces, preparing participants to build robust, verifiable analysis pipelines.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Describe the core architecture of transformer models (attention mechanisms, tokenization, context windows) and explain how transformers evolve into Large Language Models.
    \item Compare and contrast simple Artificial Neural Networks (ANNs) with transformer architectures, articulating the advantages of attention-based models for sequential data.
    \item Set up and authenticate programmatic access to multiple LLM APIs (OpenAI, Anthropic) using Python, demonstrating environment configuration and secure credential management.
    \item Execute a consensus framework across multiple LLMs, either manually via parallel browser sessions or programmatically using provided source code templates.
    \item Analyze convergent and divergent responses from multiple models to identify high-confidence outputs versus areas requiring human review.
\end{enumerate}

\subsection{Assessment Instrument}

\textbf{Pre-workshop requirement:} Complete environment setup for local API access to at least two LLM providers.

\textbf{In-session task (30 minutes):} Using the consensus framework (manual or programmatic), query multiple LLMs about analysis routes for the Jackson Heart Study or vital statistics data. Document: (a) the prompt used, (b) responses from each model, (c) areas of agreement/disagreement, and (d) your synthesis of the consensus recommendation. Refer to step-by-step tutorial in the lesson PDF.

%================================================================
\section{LLMs in Biomedical Research: Building Consensus Pipelines}
\label{sec:7.3}
%================================================================

\textbf{Time: 1 hour (Instructional: 30 minutes, Project Work: 30 minutes)}

Building on the foundations from Sections~\ref{sec:7.1} and~\ref{sec:7.2}, participants will construct a complete consensus analysis pipeline using LLMs to address authentic biomedical research tasks. A step-by-step template is provided that participants can adapt and expand. The session emphasizes that LLMs serve as assistants; humans retain accountability for all outputs, consistent with the ethics framework introduced in Section~\ref{sec:7.1}.

\subsection{Learning Objectives}

\begin{enumerate}
    \item Construct a multi-model consensus pipeline following a provided template, incorporating prompt design, response collection, and synthesis stages.
    \item Apply the consensus pipeline to evaluate an NIH grant proposal, producing structured feedback aligned with review criteria.
    \item Apply the consensus pipeline to draft a Jackson Heart Study manuscript proposal, using LLMs to generate structured content while maintaining human accountability for accuracy and originality.
    \item Implement verification checkpoints within the pipeline to detect and flag potential invalidation (factual errors, logical inconsistencies, normative violations).
    \item Document the pipeline with appropriate provenance logging (prompts, model versions, timestamps) to support reproducibility and accountability.
\end{enumerate}

\subsection{Assessment Instrument}

\textbf{Deliverable (choose one):}

\textbf{Option A: NIH Grant Evaluation Report.} Using your consensus pipeline, evaluate a provided NIH grant proposal. Produce a technical report that includes: (a) consensus scores for each review criterion, (b) identified strengths and weaknesses with model agreement levels, and (c) a synthesis recommendation with confidence assessment.

\textbf{Option B: JHS Manuscript Proposal Draft.} Using your consensus pipeline and JHS guidelines, produce a draft manuscript proposal. Document: (a) the research question generated/refined by LLMs, (b) the proposed methods with model consensus assessment, and (c) a disclosure statement for AI assistance. Note: Participants do not write proposal text directly; all text is generated via the pipeline and reviewed for accuracy.

Refer to step-by-step tutorial in the lesson PDF. Estimated time: 1 hour.


\end{document}
```

---

## Phase 4: Verification Checklist

After all changes are applied:

### Task 4.1: Verify compilation
```bash
cd challenge2026
pdflatex 2026DAIR-3.tex
pdflatex 2026DAIR-3.tex  # Second pass for references
```

### Task 4.2: Verify chapter structure
- [ ] Chapter 1: 2026 Data Challenge (not 2022)
- [ ] Chapter 2: Foundational Analysis Activities
- [ ] Chapter 3: Unit 1 (1.1, 1.2)
- [ ] Chapter 4: Unit 2 (2.1, 2.2, 2.3, 2.4)
- [ ] Chapter 5: Unit 3 (3.1, 3.2, 3.3)
- [ ] Chapter 6: Unit 4 (4.0, 4.1, 4.2, 4.3, 4.4)
- [ ] Chapter 7: Unit 5 (5.1, 5.2, 5.3, 5.4, 5.5, 5.6)
- [ ] Chapter 8: Unit 6 (6.1, 6.2, 6.3)
- [ ] Chapter 9: Unit 7 (7.1, 7.2, 7.3)

### Task 4.3: Verify cross-references
- [ ] All \label{} commands are unique
- [ ] All \ref{} commands resolve correctly
- [ ] Table of contents generates correctly

### Task 4.4: Verify no emdashes
Search for and replace any instances of `---` or `--` used as punctuation (em-dashes or en-dashes) with appropriate alternatives (commas, semicolons, parentheses).

---

## Phase 5: Stage Changes

```bash
git add challenge2026/2026DAIR-3.tex
```

**Do NOT commit.** User will run `gh.bat` after review.

---

## Summary of Changes

| Section | Action | Source |
|---------|--------|--------|
| Chapter 1 title | Fix "2022" → "2026" | Correction |
| Chapter 2 title | Rename to "Foundational Analysis Activities" | Clarity |
| Chapter 3+ | Complete restructure into 7 unit chapters | Word document |
| Unit 1 (1.1, 1.2) | Add complete content | Word document |
| Unit 2 (2.1-2.4) | Add complete content | Word document |
| Unit 3 (3.1-3.3) | Add complete content | Word document |
| Unit 4 (4.0-4.4) | Add complete content | Word document |
| Unit 5 (5.1-5.6) | Add complete content | Word document |
| Unit 6 (6.1-6.3) | Add complete content | Word document |
| Unit 7 (7.1-7.3) | Add refined content | Word document + EthicsOfAgents.tex |

## Notes for Coding Agent

1. **Preserve existing content:** Chapter 1 content (problem description, data, criteria) and Chapter 2 "single year" exercise should be preserved.

2. **Remove duplicate chapter titles:** The current file has two chapters both titled "Analysis Activities."

3. **LaTeX formatting:** Use consistent formatting with the existing document style (same sectioning commands, environments).

4. **Cross-references:** Use \label{} and \ref{} for all section cross-references.

5. **No emdashes:** Use commas, semicolons, colons, or parentheses instead of `---` or `--`.

6. **Image paths:** Existing image references (e.g., `../images/Excel.png`) should remain unchanged.

7. **lstset configurations:** The document already includes lstset configurations via `../common/DAIR3Config.tex`. Code examples should use `\lstinputlisting` or `verbatim` environments as in the original.
