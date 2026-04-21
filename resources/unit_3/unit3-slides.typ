#import "@preview/touying:0.7.1": *
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#import themes.simple: *
#show: simple-theme.with(aspect-ratio: "16-9")

= Rigorous Statistical Design

$"DAIR"^3$

Kerby Shedden\
Professor of Statistics\
University of Michigan

== Learning objectives 1

- Internalize the state of scientific knowledge about a health related research topic
- Assess the structure of a dataset and its capacity for achieving research aims
- Propose creative, original, meaningful, and tractable research aims
- Use appropriate terminology to describe aims, data, and methods
- Communicate concisely and rigorously about results and findings

\

All discussion will be centered on the NCHS birth data

== Research on human birth weight

- A wide range of birth weights can be healthy, but low birth weights (below around 2500 grams)
  are associated with
  multiple immediate and long-term risks (infection, developmental delays, chronic
  diseases in adulthood).
- Causes of birth weight are multifactorial (including many genetic and environmental effects and their
  interactions).
- Causes are mostly out of scope for us as we do not measure most of the likely _root causes_;
  however we measure some plausible _correlates_ that _explain variation_
  in birth weight; these may provide some insight about underlying root causes.

== NCHS birth weight dataset

- Detailed birth records for US births (with name redacted) were publicly released by the US National Center
  for Health Statistics (NCHS) until 1988.
- Each birth record is accompanied by birth
  weight and extensive information on the parents.
- Starting in 1989 and then further in 2005, potentially identifying variables including geographic variables were excluded.
- The data are a _census_ as they include all live births.


== NCHS birth weight dataset

- We will focus on these variables:
  - Birthweight (grams)
  - Offspring sex (female, male)
  - Plurality ($1, 2, ...$)
  - Birth order ($1, 2, ...$)
  - Maternal race (recoded as Asian, Black, Native, White)
  - Parental ages (whole years)
  - Year of birth
  - State and county codes

== Some characteristics of the data and study

- The study design is _observational_ (not _interventional_)
- The data are _prospectively_ collected, but research is conducted _retrospectively_
- The data are _administrative_, not originally collected for research
- Variables are _quantitative_, _ordinal_, and _nominal_
- The data are _multilevel_, _spatial_, and _temporal_
- Some of the predictive factors are _modifiable_
- The data are _partially observed_, likely with _informative missingness_
- The data are highly accurate, with minimal _measurement error_

== A speculative causal diagram for birth weight

#align(center + horizon)[
#diagram(
  spacing: (20mm, 15mm),
  node-outset: 3pt,
  node-corner-radius: 5pt,
  node((0, 1), [*Order*], name: <a>, fill: blue.lighten(70%)),
  node((1, 1), [*Birth weight*], name: <b>, fill: olive.lighten(70%)),
  node((0, 2), [*Paternal age*], name: <c>, fill: blue.lighten(70%)),
  node((0, 0), [*Maternal age*], name: <d>, fill: blue.lighten(70%)),
  node((1, 2), [*Sex*], name: <e>, fill: blue.lighten(70%)),
  node((1, 0), [*Plurality*], name: <f>, fill: blue.lighten(70%)),
  edge(<a>, "->", <b>),
  edge(<c.north-east>, "->", <b>, bend: +10deg),
  edge(<d.south-east>, "->", <b>, bend: -10deg),
  edge(<e>, "->", <b>),
  edge(<f>, "->", <b>),
  edge(<c.west>, "<->", <d.west>, bend: +75deg),
  edge(<e.east>, "<->", <f.east>, bend: -75deg),
  edge(<d>, "->", <a>),
  edge(<d>, "->", <f>)
)]

== Developing a research aim

Some ideas:

- Quantify risk differences corresponding to plausible mechanistic factors, e.g. does median birth weight differ by maternal age?

- Identify differential susceptibility to risk factors, e.g. does the association between plurality and birth weight differ by offspring sex?

- Characterize differences in the tail or shape of the birthweight distribution, e.g. does the 10th percentile of birthweight differ by maternal race?

== Developing a research aim (continued)

- Characterize differences in the distributions of risk factors (distribution shift)
  across meaningful strata; e.g. were mothers in 1970 more likely to be under 18 than mothers in 1980?

In all of these, regression analysis will likely play a role -- but the aim should not be to conduct a regression analysis.

== Regression analysis

Model for the relationship between response and predictors.

Most commonly, we focus on the _conditional mean_ of the _response_ $Y$ denoted $E[Y|X_1=x_1, X_2=x_2, ..., X_p=x_p]$, which is a function of _covariates_ $x_1, ..., x_p$.

Other relevant conditional quantities include the _conditional variance_ $"Var"[Y|X_1=x_1, X_2=x_2, ..., X_p=x_p]$ and _conditional quantiles_ $Q_p [Y|X_1=x_1, X_2=x_2, ..., X_p=x_p]$.

== Causal roles of covariates

Covariates can be play various causal roles, including being: _exposures_, _treatment variables_, _confounders_, _control variables_, _moderators_, _colliders_, and _mediators_, among other designations.

These terms can refer to unobserved variables as well as to variables that are available to include in an analysis.

It is rarely possible to identify the causal role of every covariate in a proposed analysis. In most cases, analysis of the data cannot resolve these roles.  External knowledge or substantive theory are the main basis for identifying how variables are causally related.

== Causal roles of covariates

The diagram below shows an _exposure_ $X$ for an _outcome_ $Y$, along with a _confounder_ $Z$.  

A confounder is a _common cause_ of the exposure and the outcome, and should be included in the regression analysis to reduce bias.

#align(center + horizon)[
#diagram(
  spacing: (20mm, 15mm),
  node-outset: 3pt,
  node-corner-radius: 5pt,
  node((0, 0), [$X$], name: <a>, fill: blue.lighten(70%)),
  node((2, 0), [$Y$], name: <b>, fill: blue.lighten(70%)),
  node((1, 1), [$Z$], name: <c>, fill: blue.lighten(70%)),
  edge(<a>, "->", <b>),
  edge(<c>, "->", <a>),
  edge(<c>, "->", <b>),
)]

== Causal roles of covariates

In the NCHS data, maternal age may confound the relationship between paternal age and birth weight.

#align(center + horizon)[
#diagram(
  spacing: (20mm, 15mm),
  node-outset: 3pt,
  node-corner-radius: 5pt,
  node((0, 0), [Paternal age], name: <a>, fill: blue.lighten(70%)),
  node((2, 0), [Birth weight], name: <b>, fill: blue.lighten(70%)),
  node((1, 1), [Maternal age], name: <c>, fill: blue.lighten(70%)),
  edge(<a>, "->", <b>),
  edge(<c>, "->", <a>),
  edge(<c>, "->", <b>),
)]

== Causal roles of covariates

A _precision variable_ $Z$ explains some of the variation in an outcome $Y$, and is unrelated to the exposure $X$.  Including a precision variable in an analysis generally increases power/precision but has no impact on bias.

#align(center + horizon)[
#diagram(
  spacing: (20mm, 15mm),
  node-outset: 3pt,
  node-corner-radius: 5pt,
  node((0, 0), [$X$], name: <a>, fill: blue.lighten(70%)),
  node((1, 0), [$Y$], name: <b>, fill: blue.lighten(70%)),
  node((1, 1), [$Z$], name: <c>, fill: blue.lighten(70%)),
  edge(<a>, "->", <b>),
  edge(<c>, "->", <b>),
)]

== Causal roles of covariates

In the NCHS data, offspring sex may serve as a precision variable when considering the potentially causal effect of birth order on birth weight.

#align(center + horizon)[
#diagram(
  spacing: (20mm, 15mm),
  node-outset: 3pt,
  node-corner-radius: 5pt,
  node((0, 0), [Order], name: <a>, fill: blue.lighten(70%)),
  node((1, 0), [Birth weight], name: <b>, fill: blue.lighten(70%)),
  node((1, 1), [Sex], name: <c>, fill: blue.lighten(70%)),
  edge(<a>, "->", <b>),
  edge(<c>, "->", <b>),
)]

== Causal roles of covariates

A _mediator_ $Z$ lies on the causal pathway between an exposure $X$ and an outcome $Y$.  Including mediators may mask the role of the exposure $X$, but also may explain its mechanism.

#align(center + horizon)[
#diagram(
  spacing: (20mm, 15mm),
  node-outset: 3pt,
  node-corner-radius: 5pt,
  node((0, 0), [$X$], name: <a>, fill: blue.lighten(70%)),
  node((1, 0), [$Z$], name: <b>, fill: blue.lighten(70%)),
  node((2, 0), [$Y$], name: <c>, fill: blue.lighten(70%)),
  edge(<a>, "->", <b>),
  edge(<b>, "->", <c>),
  edge(<a.north>, "->", <c.north>, bend: +40deg)
)]

== Causal roles of covariates

In the NCHS data, birth order may be a mediator in the relationship between maternal age and birth weight.

#align(center + horizon)[
#diagram(
  spacing: (20mm, 15mm),
  node-outset: 3pt,
  node-corner-radius: 5pt,
  node((0, 0), [Maternal age], name: <a>, fill: blue.lighten(70%)),
  node((1, 0), [Order], name: <b>, fill: blue.lighten(70%)),
  node((2, 0), [Birth weight], name: <c>, fill: blue.lighten(70%)),
  edge(<a>, "->", <b>),
  edge(<b>, "->", <c>),
  edge(<a.north>, "->", <c.north>, bend: +40deg)
)]

== Causal roles of covariates

A _moderator_ ($Z$), also called an _effect modifier_, is a variable that changes the relationship between the exposure $X$ and the outcome $Y$.  Including moderators in analysis can reveal _effect heterogeneity_.

#align(center + horizon)[
#diagram(
  spacing: (20mm, 15mm),
  node-outset: 3pt,
  node-corner-radius: 5pt,
  node((0, 0), [$X$], name: <a>, fill: blue.lighten(70%)),
  node((2, 0), [$Y$], name: <b>, fill: blue.lighten(70%)),
  node((1, 1), [$Z$], name: <c>, fill: blue.lighten(70%)),
  edge(<a>, "->", <b>),
  edge(<c>, "->", (1,0)),
)]

== Causal roles of covariates

While young maternal age is a risk factor for low birth weight, it may be that the magnitude of this effect varies with other observables, such as whether the father is present at the birth (a proxy for whether resources from the father were available during the prenatal period).

#align(center + horizon)[
#diagram(
  spacing: (20mm, 15mm),
  node-outset: 3pt,
  node-corner-radius: 5pt,
  node((0, 0), [Maternal age], name: <a>, fill: blue.lighten(70%)),
  node((2, 0), [Birth weight], name: <b>, fill: blue.lighten(70%)),
  node((1, 1), [Father present], name: <c>, fill: blue.lighten(70%)),
  edge(<a>, "->", <b>),
  edge(<c>, "->", (1,0)),
)]

== Causal roles of covariates

A _collider_ ($Z$) is a variable that is caused by the exposure $X$ and the outcome $Y$.  Including a collider in the model introduces bias.

#align(center + horizon)[
#diagram(
  spacing: (20mm, 15mm),
  node-outset: 3pt,
  node-corner-radius: 5pt,
  node((0, 0), [$X$], name: <a>, fill: blue.lighten(70%)),
  node((2, 0), [$Y$], name: <b>, fill: blue.lighten(70%)),
  node((1, 1), [$Z$], name: <c>, fill: blue.lighten(70%)),
  edge(<a>, "->", <b>),
  edge(<c>, "<-", <a>),
  edge(<c>, "<-", <b>),
)]

== Causal roles of covariates

If we knew whether the mother was alive 5 years after the birth, we could create an indicator for this and include it in the analysis.  However this could likely be a collider, in particular because it occurs in the future of the maternal age (at birth) and birth weight variables.

#align(center + horizon)[
#diagram(
  spacing: (20mm, 15mm),
  node-outset: 3pt,
  node-corner-radius: 5pt,
  node((0, 0), [Maternal age], name: <a>, fill: blue.lighten(70%)),
  node((2, 0), [Birth weight], name: <b>, fill: blue.lighten(70%)),
  node((1, 1), [Mother alive], name: <c>, fill: blue.lighten(70%)),
  edge(<a>, "->", <b>),
  edge(<c>, "<-", <a>),
  edge(<c>, "<-", <b>),
)]

== Causal roles of covariates

The scenarios discussed in the preceding slides are idealized and somewhat simplistic.  In reality, complications such as the following can arise:

- Combinations of these idealized relationships occur simultaneously

- Relationships can be bidirectional

- Variables in the causal graph may be unavailable or unknown

== Assessment 1

- In one or two sentences, state a research aim that can be addressed using the NCHS birth weight data.  The aim should emphasize what you intend to learn, not the methods that you will use.

- Write a roughly half-page memo to yourself providing a broader consideration of the dataset, study design, and research domain that provides the foundation for your research aim.

== Learning objectives 2

- You will be able to develop a rigorous analytic plan to address a stated scientific aim.

- You will be able to identify formal comparisons that address a given research aim.

- You will be able to engage in a sophisticated discussion of quantitative relationships among measured quantities.

== Regression effects and contrasts

Regression models are often parameterized by coefficients $beta$, and in the past, the interpretation of a regression model typically was made by inspecting the estimated coefficients $hat(beta)$.

This is not an effective approach for more complex models.  Instead, we can estimate _regression effects_ that address sharp research questions.

Regression effects are not necessarily equal to the _causal effect_ of changing any particular variable through an intervention, since there could be unmeasured confounders.

== Regression effects and contrasts

Suppose $E[Y|X_1, X_2]$ is the expected birth weight of a baby ($Y$) given the mother's age $X_1$ and the parity $X_2$.  

The effect of maternal age can be quantified through _contrasts_ such as

$
E[Y|X_1=35, X_2=1] - E[Y|X_1=25, X_2=1]
$

or alternatively by _ratios_ such as

$
frac(E[Y|X_1=35, X_2=1], E[Y|X_1=25, X_2=1], style: "horizontal").
$

== Difference in difference

More subtle research aims require more complex regression effects.  

If we are interested in whether girls ($X_2=1$) or boys ($X_2=0$) are more sensitive to a difference in maternal age ($X_1=35$ versus $X_1=25$), we can center our analysis on the _difference of differences_:

$
E[Y | X_1=35, X_2=1] - E[Y | X_1=25, X_2=1] -\  (E[Y | X_1=35, X_2=0] - E[Y | X_1=25, X_2=0]) 
$


== Causal effects and potential outcomes

Consider a setting with a single exposure.  We can consider the pair of values $Y(0), Y(1)$, where

- $Y(0)$ is the response a person would have if unexposed

- $Y(1)$ is the response the same person would have if exposed

Only one of $Y(0)$ and $Y(1)$ is observed.  The other is called a _potential outcome_ or a _counterfactual_.  These play a central role in modern causal inference based on the _Neyman-Rubin causal framework_.

== Causal effects and potential outcomes

The _causal effect_ of the exposure for one unit is $Y(1) - Y(0)$ or $frac(Y(1), Y(0), style: "horizontal")$.

The _average causal effect_ or _average treatment effect_ (ATE) is $E[Y(1) - Y(0)]$, where the expectation is taken over a population of interest.

The _conditional average treatment effect_ (CATE) is $E[Y(1) - Y(0) | X]$, where $X$ is a variable such as an effect modifier that may yield different treatment effects on average.

== Causal effects and potential outcomes

Many methods of causal inference aim to make practical use of potential outcomes.  Here are two examples:

_G-computation_: Fit a regression model to the observed data, including exposure status and any measured confounders as predictors.  Use the model to predict the potential outcomes for each unit, and calculate the casual parameter of interest from them.

_Synthetic controls_: For an observed treated case $Y^t_i$, find weights $w_j >= 0$, $sum w_j = 1$ for the control cases such that $X^t_i = sum w_j X^c_j$, then "impute" the potential control outcome for $Y^t_i$ as $sum w_j Y^c_j$.


== Models for the conditional mean

_Linear mean structure model:_

$
E[Y | X=x] = beta^upright(T) x = beta_0  + beta_1 x_1 + dots + beta_p x_p
$

Can be fit using least squares (LS), but many other estimators are available.

Ordinary Least Squares (OLS) works best under _homoscedasticity_ $"Var" (Y | X) = sigma^2$.

We are avoiding writing models in _generative form_ $Y = beta^upright(T) + epsilon$, since this places strong and unnecessary assumptions on the model.

== Models for the conditional mean

The linear mean structure

$
E[Y|X=x] = beta_0  + beta_1 x_1 + dots + beta_p x_p
$

is _bilinear_ -- it is linear in $x$ for fixed $beta$, and it is linear in $beta$ for fixed $x$.  Further, if we use OLS to estimate $beta$, then the estimate $hat(beta)$ is linear in the responses $Y$.

Each of these notions of linearity has its own implications.

== Models for the conditional mean

This highlights the distinct meanings of the terms _additive_ and _linear_.  In an additive model for the conditional mean, the contrast

$
E[Y|X_1=x_1, X_2=x_2] - E[Y|X_1=x'_1, X_2=x_2]
$

does not depend on the value of $x_2$

In a linear mean structure model, the contrast

$
E[Y|X_1=x_1+d, X_2=x_2] - E[Y|X_1=x_1, X_2=x_2]
$

does not depend on the value of $x_1$.

== Models for the conditional mean

Basis functions are a powerful tool that allow "linear models" to accommodate nonlinearity in the relationship between $E[Y|X=x]$ and $x$.  A basic example is _polynomial regression_

$
E[Y|X=x] = beta_0 + beta_1 x_1 + beta_2 x_1^2 + dots
$

However polynomial regression has largely been superceded by approaches using other families of _basis functions_.

== Models for the conditional mean

Basis functions are pre-defined functions, such as _splines_, _radial basis functions_, _truncated power series_, _falling factorials_, or _wavelets_ (among many others), that are used to define models of the form 

$
E[Y|X=x] = beta_0 + sum_j sum_k beta_(j k)f_k (x_j)
$

The conditional mean remains linear in the parameters ($beta_(j k)$) and the OLS estimates of the parameters remain linear in $Y$.  However the conditional mean is not a linear function of the covariates $x_j$, i.e. this is not a linear mean structure.

== Models for the conditional mean

The linear predictor $sum_j sum_k beta_(j k)f_k (x_j)$ represents a _nonlinear additive model_. 

Each term of the form $sum_k beta_(j k)f_k (x_j)$ captures the additive contribution of one covariate $x_j$ to the linear predictor.

Multivariate basis families exist, but rapidly encounter the _curse of dimensionality_.  

== Models for the conditional mean

One tractable approach is to construct a kernel matrix $K_(i j) = "ker"(x_i, x_j)$ using a _kernel function_ such as 

$
"ker"(x_i, x_j) = exp(-lambda^(-2)norm(x_i-x_j)^2).
$  

The leading eigenvectors of $K$ are an adaptive non-linear and non-additive family of basis functions.

With suitable regularization, this is an example of a "reproducing kernel Hilbert space" (RKHS) method for regression modeling.


== Models for the conditional mean

_Generalized Linear Models (GLM)_ were introduced to allow more general _single index_ mean structures, and to accommodate heteroscedasticity.

In a GLM, the mean structure is

$
g(E[Y|X=x]) = beta^upright(T) x = beta_0  + beta_1 x_1 + dots + beta_p x_p
$

for a link function $g$, often the log function.  

== Models for the conditional mean

In a GLM, a _mean/variance relationship_ is specified, such that $"Var"[Y|X] = v(E[Y|X])$ for a _variance function_ $v(dot)$.

Variance functions examples: _constant_ $v(mu) = 1$, _identity_ $v(mu) = mu$, and _power law_ $v(mu) = mu^alpha$ for given $alpha >= 0$.

Residual diagnostics can be used to identify the best fitting variance function.

The variance function captures any _heteroscedasticity_ in the population under study.

== Models for the conditional mean

What are the implications of heteroscedasticity, especially when it is not properly modeled (which is hard to do)?

In a GLM, misspecification of the variance model usually does not bias $hat(beta)$, but it does have two implications: 

- It makes the estimation of the mean parameters less statistically efficient

- It invalidates standard methods for inference (testing and intervals)

== Models for the conditional mean

Correct (or approximate) specification of the variance model allows inverse-variance weighting to provide efficient estimates of $beta$.

Many methods of inference are available that have varying degrees of robustness to incorrect specification of the variance model.


== Models for the conditional mean

Under a linear link, the coefficients ($beta_j$) correspond to additive contrasts, e.g.

$
E[Y | X_1=x_1+1, X_2=x_2, ...] - E[Y | X_1=x_1, X_2=x_2, ...] = beta_1. 
$

If the log link is used, the coefficients correspond to multiplicative effects

$
frac(E[Y | X_1=x_1+1, X_2=x_2, ...], E[Y | X_1=x_1, X_2=x_2, ...], style: "vertical") = 
exp(beta_1). 
$

== Models for conditional quantiles

A very different type of regression that allows the full conditional distribution of $Y$ given $X$ to be explored is _quantile regression_:

$
Q_p [Y|X=x] = beta^upright(T) x = beta_0  + beta_1 x_1 + dots + beta_p x_p
$

where $0 <= p <= 1$ is a _probability point_.

e.g. if $Y$ is birth weight and $p=0.01$, we are estimating the first percentile of a conditional distribution; $Q_0.01 [Y|X=x]$ is the number such that one in one hundred babies born with characteristics $x$ will have birth weight below this value.

== Beyond regression analysis

_Mediation analysis_

#align(center + horizon)[
#diagram(
  spacing: (20mm, 15mm),
  node-outset: 3pt,
  node-corner-radius: 5pt,
  node((0, 0), [X], name: <a>, fill: blue.lighten(70%)),
  node((1, 0), [Z], name: <b>, fill: blue.lighten(70%)),
  node((2, 0), [Y], name: <c>, fill: olive.lighten(70%)),
  edge(<a.east>, "->", <b.west>),
  edge(<b.east>, "->", <c.west>),
  edge(<a.north>, "->", <c.north>, bend: +40deg),
)]

Use regression models for $Y|X, Z$ and for $X|Z$ to identify the "direct effect of $X$ on $Y$" and the "indirect of $X$ on $Y$ through $Z$".

== Beyond regression analysis

Mediation analysis in the NCHS data: how much of the maternal age effect is direct, versus being driven by the fact that older mothers have generally had more children in the past?

#align(center + horizon)[
#diagram(
  spacing: (20mm, 15mm),
  node-outset: 3pt,
  node-corner-radius: 5pt,
  node((0, 0), [Maternal age], name: <a>, fill: blue.lighten(70%)),
  node((1, 0), [Birth order], name: <b>, fill: blue.lighten(70%)),
  node((2, 0), [Birth weight], name: <c>, fill: olive.lighten(70%)),
  edge(<a.east>, "->", <b.west>),
  edge(<b.east>, "->", <c.west>),
  edge(<a.north>, "->", <c.north>, bend: +40deg),
)]

== Beyond regression analysis

Many forms of analysis for longitudinal data focus on measurements made repeatedly on subjects, e.g. $Y(t)$, possibly with time-varying covariates $X(t)$.

There are sophisticated methods for causal analysis such as _marginal structural models_.

Methods for censored or truncated data from _survival analysis_.

== Assessment 2

Develop a brief analytic plan (at most one page in length) that addresses the research aim you posed in Assessment 1, using the NCHS birth weight data. 

Ideally, the analytic plan will be specific enough that the results would be reproducible if implemented by different researchers.

== Learning objectives 3

- You will be able to explain statistical uncertainty, including _a priori_ notions of uncertainty as reflected in statistical power, and statistical uncertainty following data analysis as reflected in statistical measures of confidence, significance, and precision.

- You will be able to articulate how assessments of statistical power do and do not reflect the real-world reproducibility of analytic findings.

- You will be able to express how certain forms of bias can be reduced or eliminated analytically, while others cannot.

== Statistical power

Broadly defined, _statistical power_ refers to our ability to achieve a confident conclusion about a specific research aim, from an analysis of a specific data set (which may not yet be available).

At a high level, statistical power is limited by the quantity and quality of the data, by the difficulty of the research aim, and by the statistical efficiency of the analytic methods being used.

Statistical power does not pre-suppose what conclusion is reached, it focuses only on whether we can reach a confident conclusion given the data, methods, and study design.

== Statistical power

Suppose our goal is to estimate a parameter, such as the mean birth weight for firstborn girls born to Black mothers.

The _standard error of the mean_ (SEM) is $frac(sigma, sqrt(n), style: "horizontal")$ where $sigma$ is the standard deviation and $n$ is the sample size -- this assumes that the data are _iid_ -- independent and identically distributed.

The (estimated) SEM for firstborn girls born to Black mothers is $frac(533.7, sqrt(25955), style: "horizontal") approx 3.31$, assuming _iid_ observations.  The SEM is $approx 5.56$ accounting for dependence within counties.

== Statistical power

The SEM can be viewed as an indication of statistical power.  

Taking 5.56 grams to be the SEM for the mean birth weight for a subpopulation of interest, we can consider whether this is accurate enough for our purposes.

A 95% confidence interval for the mean would be the point estimate $plus.minus 2 dot 5.56 approx 11.12$.  The CI will be $approx 22.24$ units wide.  Is this sufficiently narrow for our purposes?

== Statistical power

A very common setting for statistical power is formal hypothesis testing.  

Suppose we have a null hypothesis $H_0$ and a test statistic $T$ that measures evidence against the null.  We reject the null if $T$ exceeds a threshold $T_0$, selected to control the false positive rate $P_0(T > T_0) = p$, where $P_0$ is probability calculated when the null hypothesis is true. 

The _power_ is $P(T > T_0) = p$, where $P$ is probability for a non-null population.

== Statistical power

The test statistic $T$ often takes the form $T = frac(hat(theta), hat("SE"), style: "horizontal")$, and the rejection region is defined by $T_0 = 2$ to control the false positive rate at level $alpha=0.05$.

One can show that the _detectable effect size_ at 5% false positive rate and 80% power is approximately 3 times the standard error.  

== Statistical power

Suppose we wish to test the null hypothesis that Black and White girl, firstborn, single parity babies have the same population mean birth weight.  The SEMs for these two subpopulations are $5.56$ and $2.09$.

The SEM for the contrast comparing the two races is $sqrt(5.56^2 + 2.09^2) approx 5.94$.  Thus, the detectable effect size when comparing the races is approximately $18$ grams.

We are well powered as long as we believe (or are only interested in) differences that are greater than this value.

== Statistical power

In a least squares regression analysis, power is determined by four factors: sample size $n$, residual scatter $sigma$, dispersion $sigma_(x j)$, and colinearity $"VIF"_j$.

The _variance inflation factor_ $"VIF"_j$ for variable $j$ is $frac(1, (1 - R_j^2), style: "horizontal")$, where $R_j^2$ is the coefficient of determination (multiple $R^2$) for regressing $X_j$ on all the other covariates.

The standard error for $hat(beta)_j$ is $frac("VIF"_j^(1/2) dot sigma, (sigma_(x j) dot n^(1/2)), style: "horizontal")$.

== Statistical power

Suppose we regress birth weight on sex, maternal age, and birth order using the NCHS data for 1971.  The standard error for maternal age in a model fit with OLS is $0.10$ grams / year. 

The $R^2$ for regressing maternal age on sex and birthorder is 0.36, and $"VIF"^(1/2)$ for maternal age is $1.25$.  

The residual standard deviation is 559.5 grams and the dispersion of maternal age is 5.4 years.  

== Statistical power

We can check that

$
0.1 approx  1.25 dot 559.5 / (5.4 dot 1560744^(1/2))
$

The large unexplained SD (559.5 grams) is countered by the very large sample size ($1560744^(1/2) approx 1249.3$), and the SEM is around 25% larger due to the colinearity between maternal age and birth order.


This OLS analysis is for illustration, but one should use GEE here to account for county effects, and then the SE becomes $0.36$ grams / year. 

== Statistical power

Complementing the detectable effect size is the _sufficient sample size_.

Since $"SEM" = frac(sigma, n^(1/2), style: "horizontal")$, we have $n = frac(sigma^2 , "SEM"^2, style: "horizontal")$.  If a desired $"SEM"$ is known, we can use this to determine the sufficient sample size.

In a OLS regression, if we know the target standard error, VIF, residual variance, and covariate dispersion, we can obtain the sufficient sample size as

$
n = frac("VIF"_j dot sigma^2, ("SE"(hat(beta))^2 dot sigma^2_(x j)), style: "horizontal").
$

== Statistical power

Power analysis for large samples can be conducted to good approximation by treating nuisance parameters as known, but for smaller sample sizes the uncertainty resulting from "plugging in" estimates of nuisance parameters should be accounted for.

Statistics that are less linear than OLS, such as GLM and especially quantile regression are more complicated for power analysis, e.g. see the $"DAIR"^3$ curriculum for more information about how the _quantile density_ impacts standard errors for quantile regression.

== Assessment 3

- Conduct a minimal power analysis for your analytic plan.  You may consider a simplified version of the analytic plan to make the power analysis more straightforward.

- Write a short memo to yourself, no more than half a page in length, that summarizes the results of your power analysis, as well as any other reasons unrelated to power that the findings resulting from implementing your analytic plan may be misleading or spurious.