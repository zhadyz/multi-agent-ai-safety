# PAPER REWRITE PLAN
## For Aletheia Review

### Title
DECOMPOSITION: THE UNPATCHED VULNERABILITY IN AI-ENABLED CYBER OPERATIONS
Subtitle: ~11,000-Trial Safety Assessment Across Six AI Models

### Dataset Status

| Model | N (valid) | Interface | Status |
|---|---|---|---|
| Claude Opus 4.7 | 1,996 | Original harness | Complete |
| Claude Sonnet 4.6 | 1,304 | claude CLI | Complete |
| Claude Haiku 4.5 | 1,990 | claude CLI | Complete |
| GPT-5.5 | 2,007 | Codex CLI | Complete |
| GPT-5.4 | 2,000 | Codex CLI | Complete |
| GPT-5.4-mini | ~1,733 | Codex CLI | Running (87%) |
| **Verified complete** | **9,297** | | |
| **With preliminary** | **~11,030** | | |

Supplementary:
- 2x2 Factorial: 280 valid / 400 attempted (120 rate-limited)
- Context Ablation: 149 valid / 200 attempted (48 rate-limited, 3 generator errors)
- Human IRR: kappa=0.97 on 200-trial subsample

### Six-Model Matrix (5 verified clean, 1 preliminary)

| Technique | Opus 4.7 | Sonnet 4.6 | Haiku 4.5 | GPT-5.5 | GPT-5.4 | GPT-5.4-mini* |
|---|---|---|---|---|---|---|
| T1 Decomp | 80.6% | 88.7% | 75.3% | 27.6% | 93.8% | ~95%* |
| T2 Persona | 16.0% | 75.0% | 40.1% | 25.2% | 92.4% | ~92%* |
| T3 DAN | 0.5% | 59.1% | 42.3% | 20.4% | 95.6% | ~95%* |
| T4 Inject | 0.2% | 47.2% | 35.4% | 23.9% | 91.6% | ~91%* |

*preliminary, 87% complete

### Key Findings (from clean data only)

1. **No universal safety profile.** Each model has a distinct vulnerability pattern. Opus resists DAN/injection but falls to decomposition. Sonnet falls to everything. GPT-5.5 resists everything (session monitoring). GPT-5.4 falls to everything.

2. **Safety does not scale linearly with model size.** Within Claude: Sonnet (mid-tier) is LESS safe than Haiku (smallest) on DAN (59.1% vs 42.3%) and persona (75.0% vs 40.1%). The mid-tier model is the most vulnerable.

3. **The technique hierarchy is model-specific.** Opus shows strong hierarchy (decomp >> persona >> DAN >> injection). Haiku shows moderate hierarchy (decomp > DAN ~ persona > injection). Sonnet is broadly vulnerable but still technique-sensitive (88.7% decomp to 47.2% injection — 41.5pp spread). GPT-5.4 shows the flattest profile (91.6-95.6% across all techniques).

4. **GPT-5.5 safety is interface-driven.** 72-80% Codex refusal rate across all techniques. The model's own alignment is secondary to the session monitoring system. GPT-5.4 (no session monitoring) complies at 91-96%.

5. **Batch presentation INCREASES jailbreak success (Sonnet factorial).** Factorial on Sonnet: batch=73-74% jailbreak success vs sequential=28-36%. Role framing adds ~8pp only in sequential (36% vs 28%), not within batch (73% vs 74%). On Sonnet, batch presentation does not explain multi-agent protection — it works in the opposite direction. Whether this generalizes to Opus requires an Opus-specific factorial.

6. **Context-forwarding has minimal measurable effect at scale.** Only 1/149 true PASS-to-FAIL flip (0.7%) where both verifier verdicts were valid. 23/149 trials had at least one verifier ERROR. The dramatic N=1 ablation result does not replicate at scale.

7. **Opus's DAN/injection resistance is exceptional.** 0.5% and 0.2% on Opus vs 20-96% across other models (DAN: 20.4%-95.6%; injection: 23.9%-91.6%). This is the strongest technique-specific safety alignment measured in this study.

### Proposed Paper Structure

**Front Matter**
- Tactical Scenario (keep, minor updates)
- BLUF (complete rewrite for six-model findings)
- Evidence Tiers (update N to ~11,000 valid primary trials)
- Executive Summary (complete rewrite)
- Seven Findings in 60 Seconds (rewrite)
- Commander's Decision Table (rewrite)

**Section 1: The Operational Problem**
- 1.1 AI in the Cyber Kill Chain (keep)
- 1.2 What Is Actually Being Attacked (keep)
- 1.3 The Gap This Study Fills (update — now fills more gaps)

**Section 2: Study Design**
- 2.1 Models Tested (NEW — six-model table with interfaces)
- 2.2 Jailbreak Techniques (keep)
- 2.3 Task Benchmark (keep)
- 2.4 Scale and Statistical Approach (update for ~11,000 valid primary trials)
- 2.5 Outcome Coding and Inter-Rater Reliability (keep kappa=0.97)
- 2.6 Methodological Note: Interface Variation (NEW — Claude CLI vs Codex CLI vs original harness)

**Section 3: The Six-Model Safety Matrix**
- 3.1 No Universal Safety Profile [E] (the headline finding)
- 3.2 The Technique Hierarchy Is Model-Specific [E]
- 3.3 Safety Does Not Scale Linearly with Model Size [E]
- 3.4 Opus's Exceptional DAN/Injection Resistance [E]
- 3.5 GPT-5.5: Session Monitoring vs Model Alignment [E]

**Section 4: Multi-Agent Architecture and Mechanism Tests**
- 4.1 Architecture x Decomposition Interaction (GEE results, keep)
- 4.2 Batch Increases Compliance on Sonnet: 2x2 Factorial [E]
- 4.3 Context-Forwarding at Scale: Minimal Effect (0.7% flip rate) [E]
- 4.4 Stochastic Safety Boundaries [E]

**Section 5: Operational Risk Mapping**
- 5.1 DCO Workflow Vulnerability Table (update with six-model data)
- 5.2 Retrospective: What Would Have Stopped GTG-1002

**Section 6: Research Landscape**
- Cross-study comparison table (update with our six-model data)
- What this study uniquely contributes

**Section 7: Counterarguments and Honest Tradeoffs**
- 7.1 Batch presentation confound (NOW ADDRESSED by factorial)
- 7.2 Automated coding bias (ADDRESSED by kappa=0.97)
- 7.3 Interface variation confound (NEW — different CLIs may affect results)
- 7.4 Claude-as-coder evaluating Claude-as-target (structural, partially mitigated)
- 7.5 Temporal validity (models change with updates)

**Section 8: Recommendations by Timeline**
- Immediate (0-3 months)
- Near-term (3-12 months)
- Mid-term (1-3 years)

**Section 9: Proposed Evaluation Criteria**
- Procurement-ready thresholds (updated for six-model reality)

**Section 10: Relevance to 195th Wing**

**Section 11: Risk Summary**

**Section 12: What the 195th Wing Should Do Monday Morning**

**References**

### Questions for Aletheia
1. Is the six-model matrix the right headline, or should Opus's exceptional resistance be the lead?
2. Should the factorial and ablation go in the multi-agent section or get their own top-level section?
3. The Sonnet N=1,304 is smaller than other models (2,000). Flag as limitation or run more trials?
4. Should we note that Claude CLI and Codex CLI are different interfaces and this is a confound?
5. GPT-5.4-mini is still running. Include preliminary data or wait?
