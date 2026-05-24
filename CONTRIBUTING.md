# Contributing: Methodology Standards

This document establishes the methodology standards for the multi-agent safety study. All contributors must adhere to these standards. Deviations require explicit PI approval and documentation.

## Experimental Rigor

### Multi-Seed Runs
- Every experimental condition must be run with a minimum of 3 seeds (target: 5)
- Seeds must be pre-specified in the experiment configuration, not chosen post-hoc
- Use deterministic seeds where possible (temperature=0 for reproducibility checks, then sampled temperatures for variance estimation)

### Variance Reporting
- Report mean, standard deviation, and 95% confidence intervals for all quantitative metrics
- Never report a mean without its variance
- For binary outcomes (jailbreak success/failure), report proportions with exact binomial confidence intervals

### Contamination Checks
- Before using any benchmark task, test whether the model can solve it without the jailbreak framing
- Document contamination check results in experiment logs
- If a model demonstrates prior knowledge of a benchmark task, flag it and discuss in the limitations section

## Data Handling

### What Gets Committed
- Experiment configurations (parameters, seeds, system prompts)
- Sanitized results (success/failure labels, metrics, coded categories)
- Analysis scripts and statistical code
- Documentation and methodology notes

### What Does NOT Get Committed
- Raw model outputs (may contain harmful content)
- Jailbreak prompt templates (until ethics review is complete)
- Any content that could serve as a how-to guide for attacks
- Credentials, API keys, or access tokens

### Experiment Logging
- Every run must be logged with: timestamp, configuration ID, seed, jailbreak technique, task ID, all parameters
- Logs are append-only during an experiment; do not modify historical entries
- Use structured JSON format for machine-readable experiment logs

## Statistical Analysis

### Pre-Specification
- All primary analyses must be specified in the pre-registration before data collection begins
- Exploratory analyses are permitted but must be clearly labeled as such in the paper

### Multiple Comparisons
- Apply Benjamini-Hochberg correction for the primary analysis (5 configurations x 3-5 techniques)
- Report both corrected and uncorrected p-values
- Pre-specify the family of comparisons in the pre-registration

### Effect Sizes
- Report effect sizes (odds ratios for binary outcomes) with confidence intervals
- Do not rely solely on p-values for interpretation
- Report practical significance alongside statistical significance

### Null Results
- Null results are publishable findings, not failures
- Do not modify hypotheses post-hoc to avoid null results
- Report all pre-registered analyses regardless of outcome

## Code Quality

### Experiment Code
- All experiment harness code must be version-controlled
- Configuration is separated from code (YAML/JSON config files, not hardcoded parameters)
- Experiment code must be deterministic given the same seed and configuration

### Analysis Code
- Analysis scripts must reproduce results from raw data
- Use standard libraries (scipy, statsmodels, or R equivalents)
- Pin dependency versions in requirements files

## Review Process

### Internal Verification
- All deliverables go through Generator-Evaluator-Reviser loop before PI review
- The evaluator must not have access to the generator's reasoning (CoT decoupling)
- Document verification outcomes in version control

### PI Review Gates
- Literature review summary -> PI approval before repo setup
- Pre-registration draft -> PI approval before filing
- Pilot results -> PI approval before full experiments
- Paper draft -> PI review before submission pipeline

## AI Assistance Disclosure

- All AI-assisted work is disclosed in the methods section
- Claude (as research engineer) contributions: infrastructure, experiment execution, drafting
- PI contributions: research question, methodology decisions, interpretation, operational analysis, final writing
- The closed-loop concern (Claude studying Claude) is explicitly addressed in methodology
