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


for time :

4. Add time specificity (ONLY when time expressions are present):

   CRITICAL DISTINCTION - Plural vs Singular Time References:
   
   A) PLURAL TIME WINDOWS (returns multiple events in a time range):
      * "soon" → "in the next 30 days"
      * "upcoming" → "in the next 90 days"
      * "coming up" → "in the next 90 days"
      * "in the near future" → "in the next 90 days"
      * "recently" → "in the last 90 days"
      
      Pattern: Uses plural or implies multiple events
      SQL: WHERE date BETWEEN start_date AND end_date
      Returns: All events in the time window
   
   B) SINGULAR NEXT EVENT (returns only the chronologically first event):
      * "next release" → "next vesting date" (DO NOT add time window)
      * "next vesting" → "next vesting date" (DO NOT add time window)
      * "first release" → "next vesting date"
      * "first vesting" → "next vesting date"
      * "when is the next..." → "next vesting date"
      
      Pattern: Uses singular "next" or "first"
      SQL: WHERE date >= today ORDER BY date ASC LIMIT 1
      Returns: Only the single next event
   
   EXAMPLES:
   
   ✅ Correct (Plural - Time Window):
   Input: "show me upcoming releases for john"
   Output: "Show me grants vesting in the next 90 days for John"
   → Returns all vesting events in next 90 days
   
   ✅ Correct (Singular - Next Event):
   Input: "show me next release for john"
   Output: "Show me next vesting date for John"
   → Returns only the chronologically first vesting date
   
   ✅ Correct (Singular - Next Event):
   Input: "when does john's equity vest next"
   Output: "When is John's next vesting date?"
   → Returns only the next single vesting event
   
   ❌ Wrong (Don't add time window to singular):
   Input: "show me next release for john"
   Wrong Output: "Show me grants vesting in the next 30 days for John"
   Why wrong: "next" means singular first event, not all events in 30 days
   
   ❌ Wrong (Don't treat plural as singular):
   Input: "show me upcoming releases"
   Wrong Output: "Show me next vesting date"
   Why wrong: "upcoming releases" (plural) means all events in window, not just first
   
   DISAMBIGUATION KEYWORDS:
   Plural indicators: "upcoming", "soon", "coming", "releases" (plural), "vestings" (plural)
   Singular indicators: "next", "first", "the release" (singular), "the vesting" (singular)
   
   If NO time expression in query, DO NOT add one.
