# Security Policy & Defensive Requirements

The **AI HUMAN FIREWALL** platform adheres to strict enterprise cybersecurity standards.

---

## 🔒 1. Secrets & Credentials Policy

- **Never Commit Secrets**: Do NOT commit API keys, database credentials, or private tokens to Git.
- **Use Environment Variables**: Load secrets using `.env` files locally via `python-dotenv`.
- **Template Config**: Keep `.env.example` updated with mock placeholders.

---

## 🛡️ 2. Safe Simulation & Ethical Boundaries

- **Synthetic Scenarios Only**: All simulated threats (phishing emails, SMS prompts, phone calls) MUST use fake, non-operational domains (e.g., `company-verify.com`, `example-bank.test`).
- **No Real Credentials**: NEVER ask users to submit real passwords, real OTPs, real social security numbers, or real corporate tokens during training simulations.
- **No Malicious Infrastructure**: Do NOT write code that launches actual email spoofing servers, operational phishing links, or malware payloads.

---

## 🤖 3. AI Safety & Non-Authoritative LLM Controls

- **Non-Authoritative Risk Scoring**: The LLM must NEVER serve as the single authoritative source for final enterprise authorization or security compliance scoring. Scoring MUST be calculated deterministically in Python code.
- **Input Sanitization**: User reasoning text is sanitized (`LLMGuardrails.sanitize_input`) to prevent prompt injection attacks.
- **Structured Output Enforcement**: LLM JSON output is strictly validated against Pydantic schemas before processing.

---

## 📝 4. Data Privacy & Logging

- **Sanitized Logging**: Do not log raw user reasoning or PII in unencrypted server logs.
- **Data Minimization**: Store only user attempt metrics, category scores, and aggregated weakness tags.
