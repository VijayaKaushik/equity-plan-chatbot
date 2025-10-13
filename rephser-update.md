PHASE 3: QUALITY IMPROVEMENT (if NOT ambiguous)

GUIDING PRINCIPLE:
This chatbot operates exclusively in the equity compensation domain. Terms like "participants", "grants", "plans", "vesting" already carry equity context. DO NOT add redundant domain qualifiers like "equity compensation" or "equity plan". Only add specificity when the query would be genuinely ambiguous without it.

Examples of what NOT to do:
❌ "participants" → "participants with equity compensation" (redundant)
❌ "countries" → "countries with equity plans" (over-specified)
❌ "grants" → "equity grants" (unnecessary)
❌ "vesting" → "equity vesting" (redundant)

The equity context is implicit - don't add it explicitly.

IMPROVEMENT STEPS:

1. Fix typos and grammar:
   * Correct spelling errors
   * Fix grammatical issues
   * Capitalize proper nouns
   * Example: "jhon" → "John", "waht all" → "which", "give me this" → "give me list"

2. Expand abbreviations (plan types only):
   * "rsus" → "RSU"
   * "isos" → "ISO"  
   * "nqsos" → "NSO"
   * "espp" → "ESPP"
   * DO NOT add "equity compensation", "equity plan", or similar domain context

3. Formalize language:
   * Use professional phrasing
   * "gimme" → "Show me"
   * "waht all countries" → "Which countries"
   * "have presence of participants" → "have participants in"
   * Remove colloquialisms

4. Add time specificity (ONLY when time expressions are present):
   * "soon" → "in the next 30 days"
   * "upcoming" → "in the next 90 days"
   * "recently" → "in the last 90 days"
   * "this year" → "in 2025"
   * If NO time expression in query, DO NOT add one

5. Status defaults (implicit, applied during filtering):
   * "participants" implies "active participants" (don't add to query text)
   * "grants" implies "active grants" (don't add to query text)
   * "vesting" stays as "vesting" (don't change to "unvested")
   * These are filtering defaults - keep the rephrased query simple

CRITICAL: Keep queries simple and natural. The rephrased query should sound like a professional asking a clear question, NOT like a technical specification with domain qualifiers everywhere.

---
