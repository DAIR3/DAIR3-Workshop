# DAIR³: Data and AI Intensive Research with Rigor and Reproducibility

The Data and AI Intensive Research with Rigor and Reproducibility (DAIR³) program is funded by Award [5R25GM151182](https://reporter.nih.gov/search/iXWJsQBsP0eWTxegRt3AzQ/project-details/11187025#history) of the National Institute of General Medical Sciences, one of the 27 institutes of the National Institutes of Health of the United States. The principal investigators are Jing Liu (University of Michigan) and Juan B. Gutiérrez (University of Texas at San Antonio).

## About the Program

The rigor of scientific research and the reproducibility of research results are essential for the validity of research findings and the trustworthiness of science. However, research rigor and reproducibility remains a significant challenge across scientific fields, especially for research with complex data types from heterogeneous sources, and long data manipulation pipelines. This is especially critical as data science and artificial intelligence (AI) methods emerge at lightning speed and researchers scramble to seize the opportunities that the new methods bring.

While researchers recognize the importance of rigor and reproducibility, they often lack the resources and the technical know-how to achieve this consistently in practice. With funding from the National Institutes of Health, a multi-university team offers a nationwide program to equip faculty and technical staff in biomedical sciences with the skills needed to improve the rigor and reproducibility of their research, and help them transfer such skills to their trainees.

Trainees will then be guided over a one-year period to incorporate the newly acquired mindset, skills and tools into their research; and develop training for their own institutions.

## Summer Bootcamp

The Data and AI Intensive Research with Rigor and Reproducibility (DAIR³) program includes weeklong bootcamps in the summer that focus on ethical issues in biomedical data science; data management, representation, and sharing; rigorous analytical design; the design and reporting of AI models; generative AI; reproducible workflow; and assessing findings across studies. Additionally, the bootcamp also includes grant writing sessions and research collaboration discussions.

For workshop schedules, registration, and related activities, visit [dair-3.org](https://dair-3.org/).

## Team

The DAIR³ team and instructors include faculty and staff research leaders from:

- University of Michigan
- College of William and Mary
- Jackson State University
- University of Texas San Antonio

## Repository Structure

```
/
├── common/                 # Shared LaTeX configuration and images
│   ├── DAIR3Config.tex
│   ├── DAIR3FrontMatter.tex
│   └── lstset*.tex
├── curriculum/             # Curriculum materials and documentation
├── data_challenge/         # Data challenge materials and setup
├── images/                 # Challenge-specific images
├── README.md
├── LICENSE
└── .gitignore
```

## 2026 Data Challenge

The 2026 Data Challenge focuses on **Vital Statistics**: projecting underweight newborns and infant mortality by county in Texas for 2030. This challenge provides trainees with hands-on experience applying rigorous analytical methods and reproducible workflows to real-world biomedical data.

## Building LaTeX Documents

Compile documents from within their respective folders:

```bash
cd curriculum
pdflatex <document>.tex
```

Documents use shared configuration from `../common/`.

## Funding

This project is funded by the National Institutes of Health:

- **Award Number:** 5R25GM151182
- **Institute:** National Institute of General Medical Sciences (NIGMS)
- **Project Details:** [NIH Reporter](https://reporter.nih.gov/search/iXWJsQBsP0eWTxegRt3AzQ/project-details/11187025#history)

## License

This project is licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE) for details.