# SOP-04 — Generate plan JSON (single LLM call)

**Goal:** One Groq call returns a strict-JSON test plan. This is the ONLY
non-deterministic step.

**Inputs:** normalized ticket dict; config with `groq_key`.

**Logic:**
1. Build the user prompt from the ticket (system prompt demands strict JSON, no invented facts).
2. POST to Groq (`openai/gpt-oss-120b`), `response_format: json_object`, temperature 0.2.
3. Parse JSON (tolerate markdown fences / stray prose).
4. Merge with deterministic defaults in `navigation.plan_from_ticket`:
   - scope entries get `justified_by` (from ticket facts or "standard practice")
   - assumptions collected deterministically.

**Edge cases:**
- Groq 401 → auth error; 429 → rate limited; empty/invalid JSON → LLM failure.
- Model omits a key → deterministic default fills it.
- Model invents scope → scope is replaced by deterministic justified entries.

**Owner:** `llm_client.generate_plan_json`, `navigation.plan_from_ticket`
