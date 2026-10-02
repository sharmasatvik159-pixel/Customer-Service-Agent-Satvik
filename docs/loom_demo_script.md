# NexBank Agentic AI Customer Service Agent - 10-Minute Video Demonstration Script

```
Project Code: 1C
Title: Agentic AI Customer Service Agent with Continuous Feedback Loops
Target Audience: Executive Leadership, Model Risk Committee, Technical Evaluation Panel
Presenter: Lead Conversational AI Systems Architect
Duration: 10 Minutes (600 Seconds)
```

---

## Visual & Telemetry Setup
* **Screen 1 (Left)**: Terminal running live `pytest` test suite and FastAPI agent server.
* **Screen 2 (Center)**: NexBank Interactive Mobile & Web Banking Customer Simulator.
* **Screen 3 (Right)**: Grafana Live Telemetry Dashboard & Human Banker Escalation Terminal.

---

## Presentation Breakdown & Chronological Script

### [00:00 - 02:00] Part 1: Executive Overview, Business Need & System Topology
* **Visual**: Show System Topology Diagram from [`docs/architecture/system-topology.md`](file:///c:/Users/Acer/Desktop/Zethetha%20Algorithm/CUSTOMER%20SERVICE%20AGENT%20WITH%20FEEDBACK%20LOOPS/docs/architecture/system-topology.md).
* **Script**:
  > *"Good morning, members of the evaluation committee and leadership team. Today, I am proud to present Project 1C: The NexBank Agentic AI Customer Service Agent with Continuous Feedback Loops.*
  >
  > *Retail banking customer service faces a chronic trilemma: customers demand instant, 24x7 personalized service; regulatory frameworks (RBI, PCI DSS, SEBI) mandate uncompromising safety, zero unauthorized advice, and strict data privacy; while contact centers struggle with surging call volumes, banker burnout, and repetitive customer friction.*
  >
  > *NexBank's solution is an agentic, multi-layered conversational platform that goes far beyond simple chatbot FAQ answering. Built on an event-driven microservices topology, the platform couples an asynchronous FastAPI/Envoy gateway with a deterministic Dialogue State Machine, a hybrid BM25 + Qdrant vector retrieval engine, an immutable multi-layer safety firewall, and an automated continuous learning loop. Let's look under the hood at how the architecture operates."*

---

### [02:00 - 04:00] Part 2: Core Architecture, 6-Layer System Prompt & Dialogue State Machine
* **Visual**: Highlight the 6-Layer Architecture in [`config/system-prompt-spec.md`](file:///c:/Users/Acer/Desktop/Zethetha%20Algorithm/CUSTOMER%20SERVICE%20AGENT%20WITH%20FEEDBACK%20LOOPS/config/system-prompt-spec.md) and state transitions in [`docs/architecture/dialogue-state-machine.md`](file:///c:/Users/Acer/Desktop/Zethetha%20Algorithm/CUSTOMER%20SERVICE%20AGENT%20WITH%20FEEDBACK%20LOOPS/docs/architecture/dialogue-state-machine.md).
* **Script**:
  > *"At the foundation of our conversational integrity is our 6-Layer System Prompt Architecture. Rather than relying on a brittle monolithic prompt, we decompose instructions into distinct operational layers with strict token budgets.*
  >
  > *Crucially, Layers 0 through 2—Core Identity, Safety Invariants, and Regulatory Mandates—are cryptographically hash-locked with SHA-256 checksums. Any attempt by automated fine-tuning or runtime drift to alter these layers immediately halts execution. Tunable dialogue orchestration lives in Layer 3, grounded RAG retrieval rules in Layer 4, and ephemeral session context in Layer 5.*
  >
  > *Every turn is mediated by our Dialogue State Machine, which manages four formal authentication tiers—from Anonymous to Biometric Verified—while maintaining a sub-3.0 second round-trip latency budget across the entire pipeline."*

---

### [04:00 - 06:00] Part 3: Guardrails, Security Rules & Case Study 2 Walk-Through
* **Visual**: Open Simulator with Case Study 2 ([`simulations/conversation_02.json`](file:///c:/Users/Acer/Desktop/Zethetha%20Algorithm/CUSTOMER%20SERVICE%20AGENT%20WITH%20FEEDBACK%20LOOPS/simulations/conversation_02.json)) and side-by-side Live Banker CRM screen.
* **Script**:
  > *"Now, let's observe our security guardrails in action through Case Study 2: An unauthorized international transaction escalating to fraud.*
  >
  > *Here, our user reports a shocking INR 42,000 charge from an electronics store in London while standing in Mumbai. Notice how the agent executes our Empathy-First pattern: Acknowledge the distress, Assure the customer, and immediately Act.*
  >
  > *Before even continuing the conversation, the agent triggers an instant automated card freeze, emitting incident token #FRD-8821. Under Rule 1 of our Account Security Rules, card details are masked. Because this matches Priority P0 trigger ESC-001, the session is warm-transferred to our 24x7 Fraud Investigation Desk within 30 seconds.*
  >
  > *Now look at the right screen: the human investigator's CRM terminal is already pre-populated with our 8-Element Context Package. The banker sees the verified biometric token, the disputed amount, the merchant location, and the frozen card status. The banker says: 'Hello Jane, I see your card was frozen for the London charge; let me file the zero-liability dispute.' Zero repetition. Complete customer reassurance."*

---

### [06:00 - 08:00] Part 4: Multi-Source Feedback Loops, DVC Pipeline & A/B Testing
* **Visual**: Display Feedback Loop architecture in [`docs/learning-pipeline/feedback-loops.md`](file:///c:/Users/Acer/Desktop/Zethetha%20Algorithm/CUSTOMER%20SERVICE%20AGENT%20WITH%20FEEDBACK%20LOOPS/docs/learning-pipeline/feedback-loops.md) and Canary Deployment in [`docs/learning-pipeline/safety-preservation.md`](file:///c:/Users/Acer/Desktop/Zethetha%20Algorithm/CUSTOMER%20SERVICE%20AGENT%20WITH%20FEEDBACK%20LOOPS/docs/learning-pipeline/safety-preservation.md).
* **Script**:
  > *"What truly sets NexBank apart is our continuous learning infrastructure. We operate three closed feedback loops:
  > 1. The Supervisor Correction Loop, sampling low-confidence sessions and complaints with an inter-annotator agreement standard of Cohen's Kappa >= 0.85;
  > 2. The CSAT Signal Engine, tracking real-time sentiment trajectory slopes turn-by-turn; and
  > 3. The Resolution Outcome Engine, monitoring 7, 14, and 30-day repeat contact windows to differentiate true first-contact resolution from frustrated drop-offs.
  >
  > *Incoming conversation logs undergo Presidio PII scrubbing before being versioned in DVC on S3. When a candidate model is trained, it must pass our Fixed Golden Safety Test Suite of 200+ adversarial regression tests with a strict 100% pass rate.
  >
  > *Rollouts proceed across a 4-stage canary deployment: 1% to 5% to 25% to 100%. We continuously run two-sample Kolmogorov-Smirnov drift tests; if latent embedding drift exceeds p < 0.05 or error rates surge, our real-time circuit breaker executes an automated rollback to the stable baseline in under 3.0 seconds."*

---

### [08:00 - 09:00] Part 5: Hinglish Code-Switching, Multi-Session Context & Case Study 6 Walk-Through
* **Visual**: Open Simulator with Case Study 6 ([`simulations/conversation_06.json`](file:///c:/Users/Acer/Desktop/Zethetha%20Algorithm/CUSTOMER%20SERVICE%20AGENT%20WITH%20FEEDBACK%20LOOPS/simulations/conversation_06.json)).
* **Script**:
  > *"Next, let's examine Case Study 6: Vernacular Hinglish code-switching with multi-session context carry-over.
  >
  > *The customer types: 'Namaste, kal maine apna debit card temporary block karwaya tha phone par. Ab mujhe new replacement card order karna hai.'
  >
  > *Notice that the agent does not force the user into English, nor does it ask them to re-explain why the card was blocked. Leveraging our Context Carry-Over pattern, the agent retrieves yesterday's session state, acknowledges the previous block event in natural Hinglish, confirms the registered delivery address in Powai, Mumbai, and executes the replacement card order under Reference #CRD-REP-90812. The interaction is seamless, respectful, and culturally native."*

---

### [09:00 - 10:00] Part 6: KPIs, Observability Dashboards, Audit Logging & Conclusion
* **Visual**: Show Grafana Dashboard Wireframes in [`docs/metrics/dashboard-wireframes.md`](file:///c:/Users/Acer/Desktop/Zethetha%20Algorithm/CUSTOMER%20SERVICE%20AGENT%20WITH%20FEEDBACK%20LOOPS/docs/metrics/dashboard-wireframes.md) and run `pytest -v tests/` in terminal.
* **Script**:
  > *"To ensure operational visibility, we provide three observability consoles: our 5-second interval Real-Time Operations Console, our Daily Performance Pareto report, and our Weekly Executive Review. All interactions are archived in our WORM-compliant 7-year statutory audit ledger with AES-256 HSM double encryption.
  >
  > *As you can see in the terminal, our automated test suite runs 21 unit tests covering state transitions, taxonomy validation, guardrail assertion simulations, RAG schema adherence, prompt layer immutability, and all 20 multi-turn conversation simulations—with 100% passing in under 0.3 seconds.
  >
  > *With Project 1C, NexBank achieves 79% self-service containment, 4.54/5.0 CSAT, and zero unauthorized advice breaches, establishing a new gold standard for autonomous banking AI. Thank you."*
