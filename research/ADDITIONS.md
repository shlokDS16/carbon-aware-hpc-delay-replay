# ADDITIONS: skill and tool recommendations for Paper A (SUSCOM)

Source: A01 report, Part 2 (see /c/Users/Shlok/Downloads/Sustainable Computing papers/paper_A/research/agents/A01_prior_work_and_skills.md). Nothing installed. Each item needs a security review before install.

1. measuring-energy (Zeus, ml-energy/zeus): https://agentmods.dev/skills/ml-energy/zeus/measuring-energy . Skill that uses the Zeus library (ZeusMonitor, PowerMonitor) to measure GPU and CPU energy of code blocks; install command on the page: npx skills add ml-energy/zeus --skill measuring-energy. CPU and DRAM counters need root (RAPL). Needs security review before install.
2. pyJoules (tool, not a skill): https://pypi.org/project/pyJoules/ . Python energy measurement via Intel RAPL and NVIDIA GPU counters. It measures whole-machine energy, so background load must be controlled. Needs security review before install.
3. elsevier-cas: https://github.com/KalarisLabs/research-agent-skills/blob/main/skills/elsevier-cas/SKILL.md . Elsevier submission guidance: elsarticle and CAS templates, highlights, CRediT and generative-AI declarations. Check any template rule against the current SUSCOM Guide for Authors. Needs security review before install.
4. citation-verification: https://github.com/KalarisLabs/research-agent-skills/blob/main/skills/citation-verification/SKILL.md . Checks each .bib entry against Crossref, OpenAlex and arXiv; Python 3.9+ standard library. Needs security review before install.

Not recommended: CodeCarbon has no verified skill URL in these results, so it is omitted.
