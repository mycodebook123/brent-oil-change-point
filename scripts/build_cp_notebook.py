import nbformat as nbf

nb = nbf.v4.new_notebook()
cells = []

cells.append(nbf.v4.new_markdown_cell(
"""# Task 2: Bayesian Change Point Modeling of Brent Oil Log Returns

**Birhan Energies - Change Point Analysis Project**

This notebook builds a single change-point Bayesian model in PyMC to detect
a structural break in Brent oil log returns, checks convergence, and
associates the detected change point with researched events.
"""))

cells.append(nbf.v4.new_code_cell(
"""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pymc as pm
import arviz as az

plt.style.use('seaborn-v0_8-darkgrid')
%matplotlib inline
"""))

cells.append(nbf.v4.new_markdown_cell("## 1. Load Processed Data"))

cells.append(nbf.v4.new_code_cell(
"""df = pd.read_csv('../data/processed_brent_prices.csv')
df['Date'] = pd.to_datetime(df['Date'])
df = df.dropna(subset=['LogReturn']).reset_index(drop=True)

events = pd.read_csv('../data/events.csv')
events['Date'] = pd.to_datetime(events['Date'])

print(f"Log return series length: {len(df)}")
df.head()
"""))

cells.append(nbf.v4.new_markdown_cell(
"""## 2. Build the Bayesian Change Point Model

We model the log returns as coming from a Normal distribution whose mean
switches at an unknown point `tau`. `tau` has a discrete uniform prior over
all valid time indices. We use a shared `sigma` for simplicity in this core
model (a natural extension is to let sigma also switch, to capture the
volatility regime shifts we saw in the EDA)."""))

cells.append(nbf.v4.new_code_cell(
"""returns = df['LogReturn'].values
n = len(returns)
idx = np.arange(n)

with pm.Model() as cp_model:
    tau = pm.Categorical('tau', p=np.ones(n) / n)

    mu_1 = pm.Normal('mu_1', mu=0, sigma=0.05)
    mu_2 = pm.Normal('mu_2', mu=0, sigma=0.05)
    sigma = pm.HalfNormal('sigma', sigma=0.05)

    mu = pm.math.switch(tau >= idx, mu_1, mu_2)

    likelihood = pm.Normal('likelihood', mu=mu, sigma=sigma, observed=returns)
"""))

cells.append(nbf.v4.new_markdown_cell(
"""## 3. Run the Sampler

Note: `tau` is discrete, so PyMC will use a compound step (Metropolis for
`tau`, NUTS for the continuous parameters). This is slower than a pure NUTS
model but is the standard approach for change point detection. With ~9000
observations this may take several minutes — this is expected, not an
error."""))

cells.append(nbf.v4.new_code_cell(
"""with cp_model:
    step_tau = pm.CategoricalGibbsMetropolis(vars=[tau])
    step_cont = pm.NUTS(vars=[mu_1, mu_2, sigma], target_accept=0.95)
    trace = pm.sample(2000, tune=2000, chains=4, cores=1, step=[step_tau, step_cont], return_inferencedata=True, random_seed=42)
"""))

cells.append(nbf.v4.new_markdown_cell("## 4. Check Convergence"))

cells.append(nbf.v4.new_code_cell(
"""summary = az.summary(trace, var_names=['tau', 'mu_1', 'mu_2', 'sigma'])
summary
"""))

cells.append(nbf.v4.new_markdown_cell(
"""**How to read this:** r_hat values close to 1.0 (ideally < 1.01) indicate
the chains have converged to the same distribution. If r_hat is notably
above 1.01 for any parameter, the model needs more samples/tuning before
its results can be trusted."""))

cells.append(nbf.v4.new_code_cell(
"""az.plot_trace(trace, var_names=['tau', 'mu_1', 'mu_2', 'sigma'])
plt.tight_layout()
plt.savefig('../data/cp_trace_plot.png', dpi=150)
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell("## 5. Identify the Change Point"))

cells.append(nbf.v4.new_code_cell(
"""tau_samples = trace.posterior['tau'].values.flatten()
tau_mode = int(pd.Series(tau_samples).mode()[0])
tau_date = df.iloc[tau_mode]['Date']

print(f"Most probable tau index: {tau_mode}")
print(f"Corresponding date: {tau_date.date()}")

fig, ax = plt.subplots(figsize=(12, 5))
ax.hist(tau_samples, bins=100, color='#1f4e79')
ax.axvline(tau_mode, color='red', linestyle='--', label=f'Mode: {tau_date.date()}')
ax.set_title('Posterior Distribution of Change Point (tau)', fontsize=13, fontweight='bold')
ax.set_xlabel('Time Index')
ax.set_ylabel('Frequency')
ax.legend()
plt.tight_layout()
plt.savefig('../data/tau_posterior.png', dpi=150)
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell(
"""**Interpreting the shape:** a sharp, narrow peak in this histogram
indicates high certainty about exactly when the change occurred. A wide or
multi-modal distribution suggests the model is uncertain, or that there may
genuinely be more than one structural break in the series (motivating a
multiple change-point extension)."""))

cells.append(nbf.v4.new_markdown_cell("## 5b. Multiple Candidate Change Points"))

cells.append(nbf.v4.new_markdown_cell(
"""A single change-point model forces the posterior to pick one break, even
if the true series has several. Rather than reporting only the single mode,
we bin the tau posterior and report the top candidate regions by posterior
mass. This gives a more honest picture: with 35 years of data and multiple
known historical shocks, we expect the posterior to spread its mass across
more than one plausible break, and each of those is worth reporting as a
hypothesis rather than discarding in favor of one "winner"."""))

cells.append(nbf.v4.new_code_cell(
"""n_bins = 60
counts, bin_edges = np.histogram(tau_samples, bins=n_bins, range=(0, n - 1))
bin_centers = ((bin_edges[:-1] + bin_edges[1:]) / 2).astype(int)

top_bin_order = np.argsort(counts)[::-1]
candidates = []
used_indices = []
for b in top_bin_order:
    idx_center = bin_centers[b]
    if any(abs(idx_center - u) < n // 20 for u in used_indices):
        continue
    used_indices.append(idx_center)
    candidates.append((idx_center, counts[b] / len(tau_samples)))
    if len(candidates) == 3:
        break

print('Top candidate change points (index, approx posterior mass share, date):')
for idx_c, mass in candidates:
    date_c = df.iloc[min(idx_c, len(df)-1)]['Date'].date()
    print(f'  index={idx_c:5d}  mass={mass:.1%}  date={date_c}')
"""))

cells.append(nbf.v4.new_code_cell(
"""mu_1_samples = trace.posterior['mu_1'].values.flatten()
mu_2_samples = trace.posterior['mu_2'].values.flatten()

mu_1_mean, mu_2_mean = mu_1_samples.mean(), mu_2_samples.mean()
pct_change = (mu_2_mean - mu_1_mean) / abs(mu_1_mean) * 100 if mu_1_mean != 0 else float('nan')

prob_increase = (mu_2_samples > mu_1_samples).mean()

print(f"Mean log return BEFORE tau: {mu_1_mean:.6f}")
print(f"Mean log return AFTER tau:  {mu_2_mean:.6f}")
print(f"Probability that the mean return increased after tau: {prob_increase:.2%}")

fig, ax = plt.subplots(figsize=(10, 5))
ax.hist(mu_1_samples, bins=50, alpha=0.6, label='mu_1 (before)', color='#238b45')
ax.hist(mu_2_samples, bins=50, alpha=0.6, label='mu_2 (after)', color='#a63603')
ax.set_title('Posterior Distributions: Before vs After Mean Log Return', fontsize=13, fontweight='bold')
ax.legend()
plt.tight_layout()
plt.savefig('../data/before_after_posteriors.png', dpi=150)
plt.show()
"""))

cells.append(nbf.v4.new_markdown_cell("## 7. Associate Change Point with Researched Events"))

cells.append(nbf.v4.new_code_cell(
"""events['DaysFromTau'] = (events['Date'] - tau_date).dt.days
events_sorted = events.reindex(events['DaysFromTau'].abs().sort_values().index)

print(f"Detected change point date: {tau_date.date()}\\n")
print("Closest researched events (sorted by proximity):")
events_sorted[['Date', 'Event', 'Category', 'DaysFromTau']].head(5)
"""))

cells.append(nbf.v4.new_markdown_cell(
"""**Write your hypothesis here** once you see which event(s) are closest in
time to the detected `tau`. Remember: proximity is suggestive, not proof —
frame this as "the detected change point coincides with X, suggesting a
plausible link" rather than a definitive causal claim (see the
correlation-vs-causation discussion in `docs/analysis_workflow.md`)."""))

cells.append(nbf.v4.new_markdown_cell("## 8. Save Model Results for Dashboard (Task 3)"))

cells.append(nbf.v4.new_code_cell(
"""results = {
    'tau_index': int(tau_mode),
    'tau_date': str(tau_date.date()),
    'mu_1_mean': float(mu_1_mean),
    'mu_2_mean': float(mu_2_mean),
    'pct_change': float(pct_change),
    'prob_increase': float(prob_increase),
}

import json
with open('../data/change_point_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("Saved change_point_results.json")
results
"""))

nb['cells'] = cells
nbf.write(nb, 'notebooks/02_change_point_model.ipynb')
print("done")
