#import "@preview/touying:0.7.1": *
#import "@preview/fletcher:0.5.8" as fletcher: diagram, node, edge
#import themes.simple: *
#let indep = $perp #h(-1em) perp$
#show: simple-theme.with(aspect-ratio: "16-9")
#show link: set text(fill: blue)

= Data integration and meta-analysis

$"DAIR"^3$

Kerby Shedden\
Professor of Statistics\
University of Michigan

== Python notebook

Many of the methods and analyses in this notebook are implemented in 
#link("https://github.com/DAIR3/DAIR3-Workshop/blob/main/resources/unit_6/birthweight_meta.ipynb")[this] Python notebook.

== Learning objectives 1

- Identify settings where data integration is possible and likely to be informative.

- Identify _subpopulations_ across which data integration can be conducted.

- Explain several methods for evidence integration and propose uses for them in an investigation of the NCHS data.

== Data integration in the NCHS birth weight data

Consider a parameter $theta$ such as mean birth weight: $theta$ has a true but unknown value in the US population.

Now suppose that we partition the overall population into more homogeneous subpopulations.

Each subpopulation has a mean birth weight.

- $theta_i$ is the mean birth weight for subpopulation $i$.  

- $hat(theta)_i$ is the estimate based only on data from subpopulation $i$

== Data integration in the NCHS birth weight data

It may be of interest to characterize heterogeneity among the subpopulations, i.e. the variation among $theta_1, ..., theta_m$.

This heterogeneity is associated with between-population "stable factors", both measured and unmeasured.

In the NCHS data we will define subpopulations as all strata defined by year (4) $times$ sex (2) $times$ maternal race (4) $times$ and county ($approx 3100$).

The sample sizes per stratum vary widely (1-30,000), with median around 25.

== Data aggregation and integration

Some data sets are only available in aggregated form (e.g. for confidentiality).

If individual-level data are available, it is possible to aggregate the data, but it is usually preferable to analyze the disaggregated data.

Aggregation may lead to _ecological biases_ -- a famous example is voting behavior versus wealth in the US -- wealthy individuals lean right but wealthy states lean left.

== Multilevel data

When working with aggregated data, the _unit of analysis_ is the stratum, and the _unit of measurement_ is the individual (e.g. an individual whose birth weight is in the NCHS data).

The data are _clustered_, and if we have access to the individual measurements, constitute a _multilevel_ data set, with the levels being individuals within clusters (a.k.a. strata or subpopulations).

If we have access to the individual data, we can do a multilevel analysis.  Otherwise we are conducting an analysis of the clusters -- if the findings are presented as being about the individuals, ecological bias is possible.


== Estimates and measures of evidence

- $theta$ is the population (true) value of a parameter of interest, e.g. mean birth weight or the 75th percentile of birth weight (in a specified population)

- $hat(theta) = hat(theta) ("data")$ is an estimate of $theta$ based on the data

- $"SE"$ is the standard error (aka standard deviation) of $hat(theta)$ -- it is the primary measure of estimation precision and uncertainty

- $hat("SE")$ is an estimate of the standard error


== Estimates and measures of evidence

- A $Z$-score is a measure of evidence defined as $Z = frac((hat(theta) - theta_0), "SE", style: "horizontal")$, it approximately follows a standard normal distribution when the null hypothesis is true. Larger values (in either direction) imply stronger evidence against the null hypothesis.

- A _test statistic_ $T = T("data")$ is a function of the data measuring evidence against  a null hypothesis.  Larger values of $T$ constitute stronger evidence against the null hypothesis.

- A $p$-value is a calibrated test statistic, so that $p$ is uniformly distributed on $[0, 1]$ when the null hypothesis is true.


== Pooling estimates (simple averaging)

Suppose we have estimates $hat(theta)_1, ..., hat(theta)_m$ for statistics $theta_1, ..., theta_m$ in $m$ subpopulations.

To obtain a consensus estimate that reflects the whole population, we might use $hat(theta)_"avg" = "Avg"_j (hat(theta)_j)$.

The standard error of $hat(theta)_"avg"$ is $frac(sqrt(m^(-1) sum "SE"_j^2), sqrt(m), style: "horizontal") = frac(A^(1/2), sqrt(m), style: "horizontal")$.

- $A^(1/2) = sqrt(m^(-1) sum "SE"_j^2)$ is a consensus standard error

- $frac(1, sqrt(m), style: "horizontal")$ is the benefit of pooling

== Pooling estimates with inverse variance weights

Let $sigma_j^2 = "Var"(hat(theta)_j)$ be the variance of $hat(theta)_j$.  The statistically most efficient consensus estimate is obtained by using weights proportional to the inverses of the variances:

$
hat(theta)_"ivw" = frac(sum_j sigma_j^(-2) hat(theta)_j, sum_j sigma_j^(-2), style: "horizontal").
$

The standard error of this estimator is $frac(H^(1/2), sqrt(m), style: "horizontal")$, where $H = frac(1, "Avg"_j (frac(1, "SE"_j^2, style: "horizontal")), style: "horizontal")$ is the harmonic mean of the $"SE"_j^2$: $"Var"(hat(theta)_"ivw") <= "Var"(hat(theta)_"avg")$.

== Pooling estimates in the NCHS data

*Sex differences in birth weight (positive control):*

How different are the average birth weights of boy and girl babies?

$theta_j$: the difference of mean female and mean male birthweights in stratum $j$, of $m=4395$ strata.

Using simple averaging, $hat(theta)_"avg" = -111.4$ grams, $A^(1/2) = 65.1$ grams, so $"SE"(hat(theta)_"avg") = 0.98$ grams. 

Using inverse variance weighting, $hat(theta)_"ivw" = -109.3$ grams, $H^(1/2) = 35.6$ grams, so $"SE"(hat(theta)_"avg") = 0.54$ grams.

== Pooling estimates in the NCHS data

These estimates refer to subpopulation means, e.g. if we are using $hat(theta)_"ivw"$, we can conclude that in the average subpopulation, girl babies are estimated to weight $109.3$ grams less than boy babies.

Using the sample mean of individual data, girl babies are estimated to weigh $109.5$ grams less than boy babies.  

In this case, the individually-weighted mean difference is very similar to the cluster-weighted mean difference (which weights people from cluster $i$ with weight $frac(1, |c_i|, style: "horizontal")$).

== Pooling estimates in the NCHS data

A note on effect sizes:

In 95% of the subpopulations, the mean weight of girl babies is less than the mean weight of boy babies.

The effect appears much weaker when looking at individuals:

43.5% of the time, selecting a girl baby and a boy baby at random, the girl will weigh more than the boy.



== Pooling estimates in the NCHS data

*Sex differences in maternal age (negative control):*

Letting $theta_i$ denote the difference of mean female and mean male maternal ages in stratum $i$, of $m=4395$ strata.

Using simple averaging, $hat(theta)_"avg" = 0.012$ years, $A^(1/2) = 0.502$ years, so $"SE"(hat(theta)_"avg") = 0.008$ years. 

Using inverse variance weighting, $hat(theta)_"ivw" = 0.005$ years, $H^(1/2) = 0.306$ years, so $"SE"(hat(theta)_"avg") = 0.005$ years.

== Pooling p-values

Suppose we conduct a hypothesis test for a null hypothesis in each NCHS subpopulation, yielding p-values $p_1, ..., p_m$.

The _global null hypothesis_ is true if the null hypothesis is true in every subpopulation. This implies that each p-value is uniformly distributed on $[0, 1]$.

If the p-values are independent, then the global null hypothesis can be assessed with the _Fisher's combination test statistic_ $-2sum_j log p_j$, which follows a $chi^2_(2m)$ distribution when the global null is true.

== Combination rules

Other combination rules for combining p-values are: 

- $m dot "min"(p_j)$ (the Bonferroni statistic)

- $2 dot "Avg"(p_j)$

- $e dot (product p_j)^(1/m)$

- $frac(log(m), "Avg" (p_1^(-1), ..., p_m^(-1)), style: "horizontal")$

These all yield p-values for testing the global null hypothesis and do not require independence of the test statistics.

== Pooling p-values in the NCHS data

*Testing the global null hypothesis of no sex differences:*

#align(center + horizon)[
#table(
  columns: (auto, auto, auto),
  stroke: none,
  row-gutter: 3pt,
  column-gutter: 10pt,
  inset: (top: 10pt, bottom: 10pt, rest: 5pt),
  align: (x, y) =>
    if y == 0 { center } else { if x == 0 or x == 3 { left } else { right }},
  table.header([], [Birth weight], [Maternal age]),
  table.hline(),
  [$1 - F_(chi^2)(-2 sum_j log(p_j))$], [$<10^(-5)$], [$0.70$],
  [$m dot "min"(p_j)$], [$<10^(-5)$], [$0.34$],
  [$2 dot "Avg"(p_j)$], [$0.26$], [$1.01$],
  [$e dot (product p_j)^(1/m)$], [$0.004$], [$1.01$],
  [$frac(log(m), "Avg" (p_1^(-1), ..., p_m^(-1)), style: "horizontal")$], [$<10^(-5)$], [$0.60$],
  table.hline()
  )
]

== Accounting for uncertainty in the standard errors

When the subpopulation standard errors $"SE"_j$ are estimated, we emphasize this by writing them as $hat("SE")_j$.  Uncertainty in the standard errors ("second order uncertainty") inflates the uncertainty in $hat(theta)_"ivw"$, which can be written in the form

$
tilde("SE")_"ivw" = sqrt(frac(H(1+F), m, style: "horizontal"))
$

$
F = 4m^(-1)H^2 "Avg"_j {frac(w_j (frac(m, H, style: "horizontal") - w_j), k^prime_j, style: "horizontal")}\
k_j^prime = k_j - 4frac((m-2), (m-1), style: "horizontal")
$

== Accounting for uncertainty in the standard errors

In the NCHS data, $F approx 0.004$ for birth weight and $F approx 0.005$ for maternal age.

The SE of $hat(theta)_"ivw"$ changes from $0.536$ to $0.538$ for birth weight and for maternal age the difference is in the fifth decimal place.

Note that $F$ is $o(frac(1, m, style: "horizontal"))$ and for the NCHS, $m = 4395$.


== False Discovery Rates

Now we turn to testing the individual subpopulations, while accounting for "multiple testing." 

We have $m$ subpopulations, in each of them the null hypothesis can be true ($H_0(j) = 1$) or false ($H_0(j) = 0$).

We may wish to produce a list of all the subpopulations where we are highly confident that the null hypothesis is false.

We do not want this list to contain too many false positives.

== False Discovery Rates

Conventional approaches control the _family-wise error rate_ -- the probability that no true null hypothesis will be (falsely) rejected. 

This is appropriate in settings where making even one false positive claim has serious negative consequences (e.g. drug safety).

In some settings, we can aim to control something less stringent. The False Discovery Rate (FDR) is the proportion of rejected null hypotheses that are falsely rejected.

== False Discovery Rates

If $H_0(j) = 1$ when null hypothesis $i$ is true and $H_0(j) = 0$ otherwise, the FDR is

$
(sum_j "I"(p_j < c " & " H_0(j) = 1)) / (sum_j "I"(p_j < c)) = "# false rejections"/"# rejections"
$

where $c$ is a threshold that defines the rejection region.

e.g. if we control the FDR at 0.1, then 10% of our claimed findings will be wrong.

== False Discovery Rates

Equivalently, the FDR can be defined in terms of Z-scores:

$
(sum_j "I"(Z_j >= T " & " H_0(j) = 1)) / (sum_j "I"(Z_j >= c)) = "# false rejections"/"# rejections"
$

== False Discovery Rates

To estimate the FDR, a conservative estimate of the numerator is

$
sum_j "I"(p_j < c " & " H_0(j) = 1) approx m dot c.
$

or

$
sum_j "I"(Z_j > c " & " H_0(j) = 1) approx m dot (1 - F_0(c)).
$

The denominator can be estimated directly.


== False Discovery Rates

*Testing the null hypothesis of no sex difference in birth weight:*

Call $Z_j > T$ a "positive":

#align(center + horizon)[
#table(
  columns: (auto, auto, auto, auto),
  stroke: none,
  row-gutter: 3pt,
  column-gutter: 20pt,
  inset: (top: 5pt, bottom: 5pt, rest: 3pt),
  align: (x, y) =>
    if y == 0 { center } else { if x == 0 or x == 3 { left } else { right }},
  table.header([$T$], [FDR\ denominator], [FDR\ numerator], [FDR]),
  table.hline(),
  [$2$], [$2361$], [$100.0$], [$0.042$],
  [$2.5$], [$1857$], [$27.3$], [$0.015$],
  [$3$], [$1435$], [$5.9$], [$0.004$],
  [$3.5$], [$1104$], [$1.0$], [$0.001$],
  table.hline()
  )
]

== False Discovery Rates

*Testing the null hypothesis of no sex difference in maternal age:*

Call $Z_j > T$ a "positive":

#align(center + horizon)[
#table(
  columns: (auto, auto, auto, auto),
  stroke: none,
  row-gutter: 3pt,
  column-gutter: 20pt,
  inset: (top: 5pt, bottom: 5pt, rest: 3pt),
  align: (x, y) =>
    if y == 0 { center } else { if x == 0 or x == 3 { left } else { right }},
  table.header([$T$], [FDR\ denominator], [FDR\ numerator], [FDR]),
  table.hline(),
  [$2$], [$99$], [$100.0$], [$1.01$],
  [$2.5$], [$34$], [$27.3$], [$0.82$],
  [$3$], [$13$], [$5.9$], [$0.46$],
  [$3.5$], [$2$], [$1.0$], [$0.51$],
  table.hline()
  )
]

== Local False Discovery Rates

The _local FDR_ is based on test statistic densities (rather than on cumulative probabilities).

For simplicity, evidence here is always presented in the form of Z-scores.

Let $f(Z)$ denote the density of $Z$ scores in our data, and let $f_0(Z)$ denote the distribution of Z-scores under the null hypothesis (typically standard normal).  

The local FDR at $Z$ is $pi dot frac(f_0(Z), f(Z), style: "horizontal")$, where $pi = P(H_0 = 1)$.

== Local False Discovery Rates

*Testing the null hypothesis of no sex difference in birth weight:*

Call $Z_j approx T$ a "positive":

#align(center + horizon)[
#table(
  columns: (auto, auto, auto, auto),
  stroke: none,
  row-gutter: 3pt,
  column-gutter: 20pt,
  inset: (top: 5pt, bottom: 5pt, rest: 3pt),
  align: (x, y) =>
    if y == 0 { center } else { if x == 0 or x == 3 { left } else { right }},
  table.header([$T$], [$f$], [$f_0$], [$frac(pi dot f_0, f, style: "horizontal")$]),
  table.hline(),
  [$2$], [$0.225$], [$0.054$], [$0.240$],
  [$2.5$], [$0.201$], [$0.018$], [$0.087$],
  [$3$], [$0.171$], [$0.006$], [$0.026$],
  [$3.5$], [$0.138$], [$0.002$], [$0.006$],
  table.hline()
  )
]

== Local False Discovery Rates

*Testing the null hypothesis of no sex difference in maternal age:*

Call $Z_j approx T$ a "positive":

#align(center + horizon)[
#table(
  columns: (auto, auto, auto, auto),
  stroke: none,
  row-gutter: 3pt,
  column-gutter: 20pt,
  inset: (top: 5pt, bottom: 5pt, rest: 3pt),
  align: (x, y) =>
    if y == 0 { center } else { if x == 0 or x == 3 { left } else { right }},
  table.header([$T$], [$f$], [$f_0$], [$frac(pi dot f_0, f, style: "horizontal")$]),
  table.hline(),
  [$2$], [$0.054$], [$0.054$], [$1.00$],
  [$2.5$], [$0.018$], [$0.018$], [$0.97$],
  [$3$], [$0.006$], [$0.004$], [$0.77$],
  [$3.5$], [$0.002$], [$0.001$], [$0.45$],
  table.hline()
  )
]

== Assessment 1

- In one or two sentences, define a research aim that could be addressed using subpopulation estimates of a quantity related to birth weights, where the subpopulations are defined in a way that you specify.

- Write a roughly half-page memo to yourself identifying one or two key challenges that would arise when attempting to resolve your research aim, and indicating how these challenges could be overcome using methods discussed in this unit.

== Learning objectives 2

- Define the terms _uncertainty_ and _estimation imprecision_, and contrast these with the notion of _heterogeneity_ among the subpopulations.

- Explain the basis and purpose for the intraclass correlation coefficient, and contrast it with the variance of true parameter values across subpopulations.


== Unbiased assessment of subpopulation heterogeneity

Let $theta_i$ and $hat(theta)_i$ denote the expected (true) and sample mean birth weight in subpopulation $i$.

We can adopt the model $hat(theta)_i = theta_i + eta_i$, where the $theta_i$ follow an unknown distribution $F_theta$, and the $eta_i$ are random variables with expected value $0$ and standard deviation $"SE"_i$ (and $theta_i indep eta_i$).

In this framework, the $hat(theta)_i$ are unbiased for the $theta_i$ ($E[hat(theta_i)] = theta_i$), and we must be able to calculate or estimate the standard errors $"SE"_i$ which capture the _estimation imprecision_. If we want to emphasize that the standard errors are estimated, we denote them as $hat("SE")_i$.

== Unbiased assessment of subpopulation heterogeneity

Suppose we wish to estimate $tau^2 = "Var"(theta_i)$ (with respect to $F_theta$), a statistic describing the variation of $theta_i$ over the subpopulations.

The interest in $tau^2$ stems from it reflecting _differential_ susceptibility, sensitivity, or resilience across the subpopulations.

E.g. if $tau^2$ is large for the association between maternal age and birth weight, then some subpopulations are more susceptible to the adverse consequences of low maternal age.

== Unbiased assessment of subpopulation heterogeneity

It is natural to use $hat(tau)^2_0 = hat("Var")(hat(theta)_i)$ as an estimator of $tau^2$, but it is upwardly biased since

$
hat("Var")(hat(theta)_i) = "Var"(theta_i) + "Var"(eta_i).
$

To obtain an unbiased estimate we take

$
hat(tau)^2 = hat("Var")(hat(theta)_i) - "Avg"_i {"SE"_i^2}.
$

== Unbiased assessment of subpopulation heterogeneity

This result can be seen as an application of the law of total variation:

$
"Var"(hat(theta)) &= "Var"[E(hat(theta)|s)] + E["Var"(hat(theta)|s)] \
&= "Var"(theta) + E["SE"^2],
$

where $s$ defines the subpopulation.



== Subpopulation heterogeneity in the NCHS data

#align(center + horizon)[
#table(
  columns: (auto, auto, auto, auto),
  stroke: none,
  row-gutter: 7pt,
  align: (x, y) =>
    if y == 0 { center } else { if x == 0 or x == 3 { left } else { right }},
  table.header([], [$hat(tau)$], [$hat(tau)_#text(size: 0.7em)[0]$],
  [Units]),
  table.hline(),
  [Birth weight], [133.9], [163.1], [grams],
  [Maternal age], [2.1], [2.2], [years],
  [Paternal age], [2.2], [2.4], [years],
  table.hline()
  )
]

== Heterogeneity for quantities other than the mean

The subpopulation statistic $theta_i$ can be any statistic that may vary among the subpopulations.  If we can unbiasedly estimate $theta_i$ with an estimator $hat(theta)_i$, and obtain a standard error $"SE"_i$ (or an estimated standard error $hat("SE")_i$), then we can estimate $tau^2 = "Var"(theta_i)$, using $hat(tau)^2 = hat("Var")(hat(theta)_i) - "Avg" (hat("SE")_i^2)$.

In the NCHS data we can consider the tau correlation between maternal age and birth weight, here using only births where the maternal age is 30 or younger: $"Avg"(hat(theta)_i) approx 0.045$, $hat(tau)_0 = hat("SD")(hat(theta_i)) approx 0.038$, and $hat(tau) approx 0.019$.

== Relative measures of heterogeneity

The statistic $tau^2$ has units (the square of the data units).

A dimension-free measure of heterogeneity is the _intraclass correlation coefficient_ (ICC).  It can be obtained by another application of the law of total variation:

$
"Var"(Y) &= "Var"[E(Y|s)] + E["Var"(Y|s)]\
"total"  &= "between" + "within".
$

Here, $Y$ denotes an individual value (e.g. one measured birth weight), and $s$ indicates a stratum, so that $theta_i = E[Y | s=i]$.

== Relative measures of heterogeneity

- $"Var"[E(Y|s)] = "Var"(theta)$ is "between group variation" -- this is the heterogeneity driven by "stable factors".

- $E["Var"(Y|s)]$ is "within group variation" -- this is the "residual variation" that may be heteroscedastic.

Due to the law of total variation, $frac("Var"[E(Y|s)], "Var"(Y), style: "horizontal")$ and $frac(E["Var"(Y|s)], "Var"(Y), style: "horizontal")$ are a _partition of unity_.

== Relative measures of heterogeneity

At the population level,

$
"ICC" = ("Var" E[Y|s])/ "Var"(Y) = "Var"(theta) / "Var"(Y) = "between"/("between" + "within"),
$

where $0 <= "ICC" <= 1$ with 0 and 1 indicating "no clustering" and "perfect clustering", respectively.

We can estimate $"ICC"$ as $hat("ICC") = frac(hat(tau)^2, hat("Var")(Y), style: "horizontal")$.  

There are many estimators of the ICC -- it is a challenging estimation and inference problem.

== Relative measures of heterogeneity

In the NCHS data, the estimated ICC for birth weight, maternal age, and paternal age are $0.06$, $0.2$, and $0.15$, respectively. 

- 6% of variation in birth weight is associated with stable, stratum-level factors. 

- 20% of variation in maternal age is associated with stable, stratum-level factors

- 15% of variation in paternal age is associated with stable, stratum-level factors

== Assessment 2

- In one or two sentences, propose a brief research aim for the NCHS data centering on heterogeneity.

- Write a brief reflection discussing an analytic approach that you would employ to resolve your research aim, discussing at least one potential challenge that is likely to arise and how you would overcome it.


== Learning objectives 3

- Explain and contrast the definitions of p-values and E-values, and identify some advantages and effective uses for each.

- Articulate the purpose and main idea behind empirical likelihood approaches for data integration.

- Explain the rationale for partitioning variance using estimated variance components, and explain the meanings of _explained variation_, _random main effects_, and _idiosyncratic variation_.

== E-values

_Expectation values_ (E-values) are an emerging approach to statistical inference that addresses some long-standing concerns with the traditional approach to hypothesis testing with p-values.

An E-value is a non-negative statistic whose expected value is $<= 1$ when the null is true (this is much less constraining than the requirement that a p-value be uniform on $[0, 1]$ when the null is true).

To interpret an $E$-value (roughly), consider $frac(1, E, style: "horizontal")$ as a p-value, so $E=20-100$ corresponds to $p=0.01-0.05$.

== E-values

Some claimed advantages of E-values:

- Less sensitive to analytic assumptions since the requirement to be an E-value is weaker than the requirement to be a $p$-value

- Robust to non-independence when combining evidence

- Can always be averaged to form another E-value; under independence (or slightly weaker) the product is also an E-value

- Can be used as a stopping rule in sequential research

== E-value growth

When many of the null hypotheses are false, it is desirable for the E-process to grow rapidly.

If the subpopulations are independent, then letting $mu_i = E[E_i]$, the log E-process is the partial sums of the $log(mu_i)$.  

If the $mu_i$ are identical, then the log E-process grows at a linear rate, with slope equal to the common value of the $log(mu_i)$.

In the NCHS data, considering sex differences in birth weight, $log(mu) = 1.29$ and considering sex differences in maternal age, $log(mu) = -0.006$.


== Jack-knifing

Let $theta$ denote a statistic that is challenging from an inference perspective, like the ICC.

If $hat(theta)$ is an unbiased estimator of $theta$, we can "jack-knife" it so that $hat(theta)_(-i)$ is $hat(theta)$ computed using all data except observation $i$.

The jack-knife pseudo-observation is $eta_i = n hat(theta) - (n-1) hat(theta)_(-i)$.  The $eta_i$ are approximately independent and represent the independent contributions of the data values to the overall estimator.

== Jack-knifing

The average $overline(eta) = frac((eta_1 + dots + eta_m), m, style: "horizontal")$ is a debiased estimator of $theta$.

The psuedo-values allow us to "linearize" any statistical estimator.

$hat("SD")frac((eta_1, ..., eta_m), sqrt(m), style: "horizontal")$ is the jack-knife standard error for $overline(eta)$.

In the NCHS data, the point estimate for $tau^2 = "Var"[theta_i]$ is $hat(tau)^2 = 4457.814$, the jack-knife estimate is $overline(eta) = 4457.813$, and the jack-knife standard error estimate is $306.1$.  The point estimates $hat(tau)$ and $overline(eta)$ are both $66.8$ and the jack-knife standard error is $2.3$.

== Jack-knife empirical likelihood

Jack-knife empirical likelihood (JEL) uses discrete distributions of the form $sum_j p_j delta_(eta_j)$ for inference about $theta$, where $p_1 + dots + p_m = 1$ are probability values and the $eta_j$ are the pseudo-observations.

We can test the null hypothesis $eta = eta_0$ by imposing the constraint $sum_j p_j eta_j = eta_0$ and maximizing the likelihood $sum log(p_j)$ subject to this constraint.

We can form a confidence interval by inverting these tests, e.g. to form a 95% CI we include all $theta_0$ for which the test does not reject at the $5%$ level.

== Jack-knife empirical likelihood

Using the NCHS birth weight data and focusing on the parameter $tau = "SD"(theta_i)$, the JEL 95% confidence interval for $tau$ is $(47.5, 75)$ while the conventional jack-knife confidence interval is $(49.5, 69.2)$.

== Variance components and idiosyncratic differences

Consider the distribution of mean birthweights in subpopulations defined by county, year, sex, and maternal race.

Systematic effects of year, sex and maternal race can be captured through main effects in a regression analysis.  

County effects would be more difficult to capture as regression main effects, due to the large number of counties and (often) small sample size per county.

== Variance components and idiosyncratic differences

In the NCHS data, the main effects (mean differences) in birth weights for race groups (within county $times$ sex $times$ year groups) are:

#align(center + horizon)[
#table(
  columns: (auto, auto),
  stroke: none,
  row-gutter: 3pt,
  column-gutter: 10pt,
  inset: (top: 10pt, bottom: 10pt, rest: 5pt),
  align: (x, y) =>
    if y == 0 { center } else { if x == 0 or x == 3 { left } else { right }},
  table.header([], [Mean difference]),
  table.hline(),
  [Black $-$ Asian], [$-88.4$],
  [Native $-$ Asian], [$157.4$],
  [White $-$ Asian], [$166.4$],
  table.hline()
  )
]

== Variance components and idiosyncratic differences

Let $theta_(i j)$ denote the mean birth weight within year $times$ sex $times$ county stratum $i$ for race $j$


The _idiosyncratic variation_ for race is

$
"Avg"_i "Avg"_(j < j^prime) (theta_(i j) - theta_(i j^prime))^2.
$


== Variance components and idiosyncratic differences

Let $hat(theta)_(i j)$ denote the sample mean estimate of $theta_(i j)$ and let $sigma_(i j)$ denote the corresponding SEM (standard error of the mean).

An approximately unbiased estimate of $(theta_(i j) - theta_(i j^prime))^2$ is

$
(hat(theta)_(i j) - hat(theta)_(i j^prime))^2 - sigma_(i j)^2 - sigma_(i j^prime)^2.
$

The idiosyncratic variation associated with race can be estimated as

$
"Avg"_i "Avg"_(j < j^prime) {(hat(theta)_(i j) - hat(theta)_(i j^prime))^2 - hat(sigma)_(i j)^2 - hat(sigma)_(i j^prime)^2}.
$

== Variance components and idiosyncratic differences

On the standard deviation scale, an unbiased estimate of the idiosyncratic SD for birth weight between races (within county, year, sex) is $32.5$ grams.

The analogous unbiased estimate of idiosyncratic SD for maternal age between races is $1.03$ years.






