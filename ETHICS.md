# Ethics and Responsible Disclosure

## Dual-Use Considerations

This study empirically evaluates jailbreak resistance across different multi-agent AI architectures. While the research aims to improve AI safety, the findings could potentially be misused to inform attack strategies. We address this tension directly.

### What This Study Does
- Tests PUBLISHED jailbreak techniques (DAN, role-play, sub-task decomposition, indirect prompt injection) against different Claude architectural configurations
- Measures whether multi-agent composition improves or degrades safety
- Uses publicly available cyber-relevant task benchmarks
- Reports architectural properties, not novel attack techniques

### What This Study Does NOT Do
- Develop novel jailbreak techniques
- Publish working jailbreak prompts or templates
- Execute actual cyberattacks or produce functional exploit code
- Test against non-consenting systems or real targets
- Incorporate classified or non-public information

## Responsible Disclosure Plan

### Pre-Publication
1. Share findings with Anthropic's safety team before public release
2. Allow a reasonable response window (minimum 90 days) for Anthropic to address any significant findings
3. Coordinate disclosure timing with Anthropic if critical vulnerabilities are identified
4. Submit through DoPSR pre-publication review process

### Publication Content
1. Report jailbreak SUCCESS RATES and architectural properties without publishing verbatim successful jailbreak prompts
2. Describe techniques at the category level (e.g., "sub-task decomposition") with enough methodological detail for reproduction by qualified researchers, without providing copy-paste attack templates
3. Sanitize all example outputs to remove actionable harmful content
4. Focus reporting on DEFENSIVE implications (which architectures are more robust)

### If Critical Vulnerabilities Are Found
1. Immediately notify Anthropic's security team via responsible disclosure channels
2. Embargo specific vulnerability details until a fix is available or a coordinated disclosure date is set
3. Do not publish details that would enable immediate exploitation
4. Document the disclosure timeline in the paper's methodology

## Data Handling

### Sensitive Outputs
- Raw model outputs from jailbreak experiments may contain harmful content
- These outputs are stored locally only, never in public repositories
- Access is limited to the PI and authorized research team members
- Outputs are retained only for the duration needed for analysis, then securely deleted

### Benchmark Data
- All benchmark tasks come from publicly available sources
- Task descriptions reference MITRE ATT&CK tactics at the conceptual level
- No operational attack tools, malware, or exploit code is used or produced

## IRB / Ethics Review

- This study does not involve human subjects
- Institutional determination on IRB exemption status: PENDING (PI to confirm with SFSU)
- The PI will consult with SFSU's Office of Research and Sponsored Programs if required

## Conflict of Interest

- This research uses Claude (Anthropic) as both the system under test and the research engineering assistant
- This closed-loop concern is explicitly documented in the methodology section
- Mitigations include: independent evaluation by human PI, subset of experiments designed without AI assistance, transparent disclosure of AI involvement
- The PI has no financial relationship with Anthropic beyond a consumer subscription

## Military Service Disclosure

- The PI is an active-duty Air National Guard member (cyber operations)
- This research is conducted as personal academic work, not under military direction
- All data and methods are unclassified and publicly available
- Pre-publication review (DoPSR) is completed before any external release
- No government resources, classified information, or military systems are used

## Contact

For questions about the ethics of this research or to report concerns:
- Principal Investigator: Abdul Bari, San Francisco State University
