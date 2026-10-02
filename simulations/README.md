# NexBank Conversational Simulation & Synthetic Traffic Suite

This directory contains simulation frameworks, synthetic user personas, and load generators used to stress test the conversational agent against edge cases, peak loads, and adversarial probes.

## Planned Simulation Modules
1. **Multi-Turn User Persona Simulator**: Generates diverse synthetic customers (anxious first-time home buyers, hurried commercial treasurers, frustrated dispute filers).
2. **Adversarial Red-Team Simulator**: Executes automated jailbreaks, prompt injections, and PII leakage probes against the staging environment.
3. **Peak Surge Load Generator**: Simulates 1x (18k/day), 10x (180k/day), and 100x (1.8M/day) concurrent conversational sessions to benchmark latency budgets and auto-scaling rules.
