# Decomposition: The Unpatched Vulnerability in AI-Enabled Cyber Operations

**12,443-trial safety assessment across six AI models from two vendors**

A1C Abdul Bari, 147th Combat Communications Squadron, 195th Wing, California Air National Guard

Position paper for the 2026 ANG Operational Alignment Communications & Cyber Symposium (OACCS)

---

## Abstract

In 12,443 trials across six AI models from two vendors (Claude Opus 4.7, Sonnet 4.6, Haiku 4.5, GPT-5.5, GPT-5.4, GPT-5.4-mini), we find that AI safety behavior is model-specific and interface-specific, not a vendor-level property. Decomposition attacks succeed on every model tested (27.6-95.7%). No jailbreak is required for 87% of offensive cyber tasks on Opus. GPT-5.5 non-success is dominated by Codex interface refusals; when the model responds, it complies 99.6% of the time. A balanced 2x2 factorial confirms that batch presentation increases compliance vs sequential isolation (75% vs 32%, OR=6.4, p=6.6e-18). Severity analysis of 11,896 responses reveals that 71% of binary "successes" produce only educational content; only 17% produce actionable offensive material. Binary compliance rates substantially overstate operational risk.

## Key Findings

1. **No universal safety profile.** Each of six models has a distinct vulnerability pattern across four jailbreak techniques.
2. **Observed safety did not order monotonically across Claude model-interface pairs.** Sonnet (mid-tier, CLI) showed higher jailbreak success than Haiku (smallest, CLI) on DAN: 61.2% vs 42.1%.
3. **GPT-5.5 non-success dominated by Codex zero-output refusals.** 75.7% Codex interface refusal; among 488 actual responses, 99.6% complied.
4. **Batch presentation increases compliance.** Balanced factorial (N=400 valid, ~100/cell): batch 75% vs sequential 32%, OR=6.4.
5. **Binary coding overstates risk ~4x.** 71% of "successful jailbreaks" are educational content (L1-L2); only 17% are actionable (L3-L4).
6. **Context-forwarding does not replicate at scale.** 0.8% verdict flip rate (1/126 comparable pairs).

## Repository Structure

```
paper/
  OACCS_position_paper.md            # Canonical paper source (markdown)
  OACCS_Multi_Agent_AI_Safety_Bari.docx  # Formatted deliverable
  APPENDIX_REPRODUCIBILITY.md        # Full reproducibility documentation
  build_oaccs_docx.py                # Builds .docx from markdown
  regenerate_figs.py                 # Generates all publication figures
  fig1_safety_matrix.png             # Safety matrix heatmap
  fig1_technique_hierarchy.png       # Technique profile comparison
  fig2_severity_distribution.png     # Severity distribution by model
  fig3_gpt55_temporal.png            # GPT-5.5 temporal analysis
  fig4_factorial.png                 # 2x2 factorial results

analysis/
  final_2000_dataset.csv             # Claude architecture harness (1,996 valid)
  cross_vendor_final.csv             # GPT-5.5 dataset (2,007 valid)
  cross_vendor_gpt_5_4_log.jsonl     # GPT-5.4 dataset (2,000 valid)
  cross_vendor_gpt_5_4_mini_log.jsonl    # GPT-5.4-mini dataset (1,942 valid)
  cross_vendor_claude_sonnet_v2_log.jsonl # Claude Sonnet dataset (1,967 valid)
  cross_vendor_claude_haiku_v2_log.jsonl  # Claude Haiku dataset (1,982 valid)
  factorial_2x2_log.jsonl            # 2x2 factorial (400 valid)
  context_ablation_log.jsonl         # Context-forwarding ablation (149 valid)
  irr_sample_200.csv                 # IRR validation sample
  irr_human_scores.csv               # Human-coded IRR outcomes
  irr_results.json                   # Cohen's kappa = 0.97
  hierarchical_results.json          # Clustered bootstrap CIs
  severity_full_results.json         # Ordinal severity analysis
  severity_rubric.md                 # Severity coding rubric (L0-L4)
  verify_paper_numbers.py            # Verification script
  hierarchical_model.py              # Clustered bootstrap analysis

experiments/
  task_benchmark.json                # 15 original cyber tasks (MITRE ATT&CK)
  high_refusal_tasks.json            # 5 high-refusal supplementary tasks
  jailbreak_templates.json           # 4 jailbreak technique templates
  cross_vendor_codex.py              # GPT-5.5 experiment runner
  cross_vendor_multi_model.py        # GPT-5.4/5.4-mini runner
  cross_vendor_claude_models.py      # Claude Sonnet/Haiku/Opus runner
  factorial_2x2_cli.py              # 2x2 factorial runner
  factorial_2x2_supplement.py        # Factorial batch supplement (120 trials)
  context_forwarding_ablation.py     # Context-forwarding ablation runner
  contamination_check.md             # Baseline compliance check results

harness/
  config.json                        # 5 Claude architecture configurations (C1-C5)
  system_prompts.json                # Multi-agent role prompts
  experiment_runner.py               # Original Claude architecture harness
```

## Reproducing Results

See `paper/APPENDIX_REPRODUCIBILITY.md` for complete documentation including exact CLI commands, model version IDs, date ranges, sampling parameters, trial exclusion accounting, and file-to-table mappings.

**Claude models (requires Claude CLI):**
```bash
claude --model sonnet --print < prompt.txt
```

**GPT models (requires Codex CLI):**
```bash
npx @openai/codex exec --ephemeral -s read-only -m gpt-5.4 -o output.txt < prompt.txt
```

**Run experiments:**
```bash
python experiments/cross_vendor_multi_model.py --model gpt-5.4
python experiments/cross_vendor_claude_models.py --model sonnet
python experiments/factorial_2x2_cli.py
```

## Model Versions (May 2026)

| Model | Version ID | Interface |
|---|---|---|
| Claude Opus 4.7 | claude-opus-4-7 | Architecture harness |
| Claude Sonnet 4.6 | claude-sonnet-4-6 | claude CLI |
| Claude Haiku 4.5 | claude-haiku-4-5-20251001 | claude CLI |
| GPT-5.5 | gpt-5.5 | Codex CLI |
| GPT-5.4 | gpt-5.4 | Codex CLI |
| GPT-5.4-mini | gpt-5.4-mini | Codex CLI |

## Citation

```bibtex
@inproceedings{bari2026decomposition,
  title={Decomposition: The Unpatched Vulnerability in AI-Enabled Cyber Operations},
  author={Bari, Abdul},
  booktitle={2026 ANG Operational Alignment Communications \& Cyber Symposium (OACCS)},
  year={2026},
  organization={147th Combat Communications Squadron, 195th Wing, CA ANG}
}
```

## Ethics and Responsible Disclosure

All experiments use published jailbreak techniques from peer-reviewed literature. No novel attack techniques are developed. All tasks are unclassified public-source scenarios derived from MITRE ATT&CK. No classified information, systems, or networks were used. See `ETHICS.md` for the full responsible disclosure policy.

## License

This research is released for defensive security and academic purposes. Raw model responses are archived for audit and reproducibility.
