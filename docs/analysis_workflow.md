# Change Point Analysis of Brent Oil Prices — Analysis Workflow

**Birhan Energies | Task 1: Foundation for Analysis**

## 1. Business Objective

Quantify how major geopolitical events, OPEC policy decisions, and economic
shocks have historically shifted Brent crude oil prices, using Bayesian
change point detection, to support investment, policy, and operational
decisions.

## 2. Data Analysis Workflow

1. **Data Loading & Cleaning** — Load daily Brent price data (1987–2022),
   parse mixed date formats, sort chronologically, check for missing values.
2. **Event Research** — Compile a structured dataset of 10–15 major
   geopolitical/economic events with approximate dates (see `data/events.csv`).
3. **Exploratory Data Analysis** — Plot the raw price series to identify
   visible trends and shocks; test for stationarity (ADF test); compute and
   plot log returns to stabilize variance and check for volatility clustering.
4. **Bayesian Change Point Modeling** — Build a PyMC model with a discrete
   uniform prior on the switch point (tau), separate before/after mean
   parameters, and a Normal likelihood switched via `pm.math.switch`. Sample
   using MCMC and check convergence via r-hat and trace plots.
5. **Interpretation** — Identify the most probable change point date(s) from
   the posterior of tau, quantify the shift in mean price/return, and match
   detected dates against the researched event list to form hypotheses about
   causation.
6. **Dashboard Development** — Serve results via a Flask API and visualize
   them in an interactive React dashboard, allowing stakeholders to explore
   price history, change points, and event correlations.

## 3. Time Series Properties (Initial EDA Findings)

- **Sample size:** 9,011 daily observations, 1987-05-20 to 2022-11-14.
- **Trend:** Raw price series shows a strong long-run upward trend with
  several sharp shocks and multi-year regime shifts (visible around 1990,
  2008, 2014–16, 2020, 2022).
- **Stationarity:** Augmented Dickey-Fuller test on raw prices fails to
  reject the null of a unit root (p ≈ 0.29) — the series is non-stationary,
  as expected for a price level series with trend. Log returns, by contrast,
  are strongly stationary (ADF p ≈ 0.0000), consistent with standard
  financial time series behavior.
- **Volatility:** Log returns show visible volatility clustering — bands of
  high day-to-day variance concentrated around known crisis periods
  (2008–09 financial crisis, 2014–16 oil glut, 2020 COVID collapse) rather
  than constant variance over time.
- **Modeling implication:** Because raw prices are non-stationary, log
  returns are the more defensible input for a Bayesian change point model
  with Normal-likelihood assumptions. Raw prices remain useful for
  visualization and communicating price-level impacts to stakeholders.

## 4. Purpose of Change Point Models

Change point models detect structural breaks in a time series — points
where the underlying statistical properties (mean, variance) shift abruptly.
Rather than assuming a single stable data-generating process across the
entire history, they explicitly model the possibility that the process
changed at some unknown point in time, and estimate both *when* that change
occurred and *how* the parameters differed before and after. In the context
of oil prices, this lets us detect regime shifts driven by real-world shocks
without needing to specify the cause in advance — the model tells us *where*
to look, and researched context (our events dataset) tells us *why*.

## 5. Expected Outputs and Limitations

**Expected outputs:**
- A posterior distribution over the change point date (tau), summarized by
  its most probable date and credible interval.
- Posterior distributions for the "before" and "after" parameters (e.g. mean
  log return), allowing probabilistic statements like "there is a 95%
  probability the average daily return shifted by at least X after tau."
- A quantified before/after comparison (e.g. percentage change in average
  price) associated with the most plausible triggering event.

**Limitations:**
- A single change point model assumes exactly one structural break; the real
  series likely has multiple regime shifts. Extensions (multiple change
  points, or a Markov-switching model) would be needed for a fuller picture.
- The model detects statistical breaks in the data — it does not know about
  real-world events. Associating a detected tau with a specific event is a
  human interpretive step based on temporal proximity, not something the
  model proves.
- Data irregularities: the source CSV changes date format partway through
  (from `DD-Mon-YY` to `"Mon DD, YYYY"` around April 2020) and the data
  extends slightly past the brief's stated end date (through Nov 2022
  instead of Sep 2022) — handled during cleaning but worth noting as a data
  quality caveat.

## 6. Correlation vs. Causation

A detected change point occurring near the date of a known event is
**correlational evidence**, not proof of causation. Oil prices are
influenced by many simultaneous factors (macroeconomic conditions, currency
movements, other commodity markets, speculative trading, weather-driven
demand, etc.), and multiple candidate events can cluster near the same date.
This analysis will treat event-change point alignment as a hypothesis worth
reporting — supported by domain plausibility and timing — rather than a
proven causal claim. A rigorous causal claim would require a
counterfactual framework (e.g. synthetic control, differences-in-differences
against a comparable benchmark) that is outside the scope of this project's
core deliverable but is noted as a valuable direction for future work.

## 7. Communication Channels

Results will be communicated via:
- A GitHub repository containing full code, data, and documentation.
- A written report (blog-post format, suitable for Medium or PDF) summarizing
  methodology, findings, and quantified impacts for a business audience.
- An interactive web dashboard (Flask + React) enabling stakeholders
  (investors, policymakers, energy companies) to explore results themselves.
