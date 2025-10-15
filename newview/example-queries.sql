-- ============================================
-- EXAMPLE QUERIES: GRANT MANAGEMENT SYSTEM
-- ============================================

-- ============================================
-- Q1: List of countries with participant counts
-- ============================================
-- Question: "Give me the list of countries that my participants are in, 
--            along with the count of participants per country"

SELECT 
    country_cd,
    COUNT(DISTINCT participant_hub_key) AS participant_count
FROM vparticipant
GROUP BY country_cd
ORDER BY participant_count DESC;


-- ============================================
-- Q2: Participants in US by State
-- ============================================
-- Question: "Give me the participants in US by State"

SELECT 
    state,
    COUNT(DISTINCT participant_hub_key) AS participant_count
FROM vparticipant
WHERE country_cd = 'US'
GROUP BY state
ORDER BY participant_count DESC;


-- ============================================
-- Q3: Count of participants in China
-- ============================================
-- Question: "How many participants are there in China?"

SELECT 
    COUNT(DISTINCT participant_hub_key) AS participant_count
FROM vparticipant
WHERE country_cd = 'CN';


-- ============================================
-- Q4: Participants with vesting in next 60 days
-- ============================================
-- Question: "Of these participants, how many of them have a vesting event 
--            in the upcoming next 60 days?"
-- Context: "These participants" refers to China participants from Q3

SELECT 
    COUNT(DISTINCT g.participant_hub_key) AS participant_count
FROM vGrants g
JOIN vparticipant p ON p.participant_hub_key = g.participant_hub_key
WHERE p.country_cd = 'CN'
    AND g.vesting_dt BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '60 days'
    AND g.is_processed = FALSE;


-- ============================================
-- Q5: Plans associated with participants in China
-- ============================================
-- Question: "What are the plans associated with participants in China?"

SELECT DISTINCT
    g.plan_hub_key,
    g.plan_name,
    g.plan_type,
    g.plan_start_date,
    COUNT(DISTINCT g.participant_hub_key) AS participant_count,
    COUNT(DISTINCT g.grant_id) AS grant_count
FROM vGrants g
JOIN vparticipant p ON p.participant_hub_key = g.participant_hub_key
WHERE p.country_cd = 'CN'
GROUP BY g.plan_hub_key, g.plan_name, g.plan_type, g.plan_start_date
ORDER BY participant_count DESC;


-- ============================================
-- Q6: List of grant types
-- ============================================
-- Question: "What are the total types of grants? Total grants available 
--            and the number of participants under each grant type"

SELECT 
    grant_type_code,
    grant_type_description,
    COUNT(DISTINCT grant_id) AS total_grants,
    COUNT(DISTINCT participant_hub_key) AS participant_count,
    SUM(units_granted_amount) AS total_units_granted
FROM vGrants
GROUP BY grant_type_code, grant_type_description
ORDER BY total_grants DESC;


-- ============================================
-- Q7: Next vesting date for all plans and grants
-- ============================================
-- Question: "What is the next vesting date? Plus all plans and 
--            all the grants under them"

-- Option 1: Get the absolute next vesting date (single value)
SELECT 
    vesting_dt AS next_vesting_date
FROM vGrants
WHERE vesting_dt > CURRENT_DATE
    AND is_processed = FALSE
ORDER BY vesting_dt ASC
LIMIT 1;

-- Option 2: Show all plans and grants with their next vesting dates
SELECT 
    plan_hub_key,
    plan_name,
    plan_type,
    grant_id,
    grant_type_description,
    participant_hub_key,
    vesting_dt AS next_vesting_date
FROM vGrants
WHERE vesting_dt > CURRENT_DATE
    AND is_processed = FALSE
ORDER BY vesting_dt ASC;


-- ============================================
-- Q8: List of plans offered
-- ============================================
-- Question: "Give me list of plans offered"

SELECT 
    plan_name,
    plan_type,
    COUNT(DISTINCT plan_hub_key) AS number_of_plans,
    COUNT(DISTINCT participant_hub_key) AS participant_count,
    COUNT(DISTINCT grant_id) AS grant_count,
    MIN(plan_start_date) AS earliest_plan_start,
    MAX(plan_start_date) AS latest_plan_start
FROM vGrants
GROUP BY plan_name, plan_type
ORDER BY plan_name, plan_type;


-- ============================================
-- ADDITIONAL USEFUL QUERIES
-- ============================================

-- Q9: Participants by KYC status
SELECT 
    kyc_status,
    COUNT(DISTINCT participant_hub_key) AS participant_count
FROM vparticipant
GROUP BY kyc_status
ORDER BY participant_count DESC;


-- Q10: Directors and officers count by country
SELECT 
    country_cd,
    COUNT(DISTINCT CASE WHEN is_director = TRUE THEN participant_hub_key END) AS director_count,
    COUNT(DISTINCT CASE WHEN is_officer = TRUE THEN participant_hub_key END) AS officer_count,
    COUNT(DISTINCT CASE WHEN is_blackout_insider = TRUE THEN participant_hub_key END) AS insider_count
FROM vparticipant
GROUP BY country_cd
ORDER BY country_cd;


-- Q11: Grants expiring in next 90 days
SELECT 
    g.grant_id,
    g.grant_type_description,
    g.expected_expiration_date,
    p.first_nm,
    p.last_nm,
    p.country_cd
FROM vGrants g
JOIN vparticipant p ON p.participant_hub_key = g.participant_hub_key
WHERE g.expected_expiration_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '90 days'
ORDER BY g.expected_expiration_date ASC;


-- Q12: Total grant value by participant
SELECT 
    p.participant_hub_key,
    p.first_nm,
    p.last_nm,
    p.country_cd,
    COUNT(DISTINCT g.grant_id) AS total_grants,
    SUM(g.units_granted_amount) AS total_units,
    SUM(g.units_granted_amount * g.fair_value_price) AS total_grant_value
FROM vparticipant p
JOIN vGrants g ON g.participant_hub_key = p.participant_hub_key
GROUP BY p.participant_hub_key, p.first_nm, p.last_nm, p.country_cd
ORDER BY total_grant_value DESC;


-- Q13: Vesting schedule for a specific participant
-- (Replace 'PARTICIPANT_ID' with actual participant_hub_key)
SELECT 
    grant_id,
    grant_type_description,
    units_granted_amount,
    vesting_dt,
    is_processed,
    CASE 
        WHEN vesting_dt <= CURRENT_DATE THEN 'Past'
        WHEN vesting_dt <= CURRENT_DATE + INTERVAL '30 days' THEN 'Next 30 days'
        WHEN vesting_dt <= CURRENT_DATE + INTERVAL '90 days' THEN 'Next 90 days'
        ELSE 'Future'
    END AS vesting_window
FROM vGrants
WHERE participant_hub_key = 'PARTICIPANT_ID'
ORDER BY vesting_dt ASC;


-- Q14: Plans with most participants
SELECT 
    plan_name,
    plan_type,
    COUNT(DISTINCT participant_hub_key) AS participant_count,
    COUNT(DISTINCT grant_id) AS grant_count,
    SUM(units_granted_amount) AS total_units
FROM vGrants
GROUP BY plan_name, plan_type
ORDER BY participant_count DESC
LIMIT 10;


-- Q15: Acceptance rate by grant type
SELECT 
    grant_type_code,
    grant_type_description,
    COUNT(DISTINCT grant_id) AS total_grants,
    COUNT(DISTINCT CASE WHEN acceptance_status = 'ACCEPTED' THEN grant_id END) AS accepted_grants,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN acceptance_status = 'ACCEPTED' THEN grant_id END) / 
        NULLIF(COUNT(DISTINCT grant_id), 0), 
        2
    ) AS acceptance_rate_pct
FROM vGrants
GROUP BY grant_type_code, grant_type_description
ORDER BY acceptance_rate_pct DESC;


-- Q16: Participants with grants but no upcoming vestings
SELECT 
    p.participant_hub_key,
    p.first_nm,
    p.last_nm,
    p.country_cd,
    COUNT(DISTINCT g.grant_id) AS total_grants,
    MAX(g.vesting_dt) AS last_vesting_date
FROM vparticipant p
JOIN vGrants g ON g.participant_hub_key = p.participant_hub_key
GROUP BY p.participant_hub_key, p.first_nm, p.last_nm, p.country_cd
HAVING MAX(g.vesting_dt) <= CURRENT_DATE
ORDER BY last_vesting_date DESC;


-- Q17: Grant distribution by client
SELECT 
    c.client_name,
    COUNT(DISTINCT g.participant_hub_key) AS participant_count,
    COUNT(DISTINCT g.grant_id) AS grant_count,
    COUNT(DISTINCT g.plan_hub_key) AS plan_count,
    SUM(g.units_granted_amount) AS total_units
FROM vclient c
JOIN vGrants g ON g.client_hub_key = c.client_hub_key
GROUP BY c.client_name
ORDER BY participant_count DESC;


-- Q18: Upcoming vesting events summary (next 30/60/90 days)
SELECT 
    '0-30 days' AS period,
    COUNT(DISTINCT participant_hub_key) AS participants,
    COUNT(DISTINCT grant_id) AS grants,
    SUM(units_granted_amount) AS units_vesting
FROM vGrants
WHERE vesting_dt BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '30 days'
    AND is_processed = FALSE

UNION ALL

SELECT 
    '31-60 days' AS period,
    COUNT(DISTINCT participant_hub_key),
    COUNT(DISTINCT grant_id),
    SUM(units_granted_amount)
FROM vGrants
WHERE vesting_dt BETWEEN CURRENT_DATE + INTERVAL '31 days' AND CURRENT_DATE + INTERVAL '60 days'
    AND is_processed = FALSE

UNION ALL

SELECT 
    '61-90 days' AS period,
    COUNT(DISTINCT participant_hub_key),
    COUNT(DISTINCT grant_id),
    SUM(units_granted_amount)
FROM vGrants
WHERE vesting_dt BETWEEN CURRENT_DATE + INTERVAL '61 days' AND CURRENT_DATE + INTERVAL '90 days'
    AND is_processed = FALSE

ORDER BY period;


-- ============================================
-- HIERARCHICAL RELATIONSHIP QUERIES
-- ============================================
-- These queries demonstrate the client → plan → grant hierarchy

-- Q19: Plans per client
-- Shows how many plans each client has
SELECT 
    c.client_name,
    COUNT(DISTINCT g.plan_hub_key) AS plan_count,
    COUNT(DISTINCT g.grant_id) AS grant_count,
    COUNT(DISTINCT g.participant_hub_key) AS participant_count
FROM vclient c
JOIN vGrants g ON g.client_hub_key = c.client_hub_key
GROUP BY c.client_name
ORDER BY plan_count DESC;


-- Q20: Grants per plan for a specific client
-- Shows the hierarchy: Client → Plans → Grants
-- (Replace 'CLIENT_HUB_KEY' with actual value)
SELECT 
    c.client_name,
    g.plan_name,
    g.plan_type,
    COUNT(DISTINCT g.grant_id) AS grant_count,
    COUNT(DISTINCT g.participant_hub_key) AS participant_count,
    SUM(g.units_granted_amount) AS total_units
FROM vclient c
JOIN vGrants g ON g.client_hub_key = c.client_hub_key
WHERE c.client_hub_key = 'CLIENT_HUB_KEY'
GROUP BY c.client_name, g.plan_name, g.plan_type
ORDER BY grant_count DESC;


-- Q21: Full hierarchy breakdown
-- Shows Client → Plan → Grant Type distribution
SELECT 
    c.client_name,
    g.plan_name,
    g.grant_type_description,
    COUNT(DISTINCT g.grant_id) AS grant_count,
    COUNT(DISTINCT g.participant_hub_key) AS participant_count,
    SUM(g.units_granted_amount) AS total_units
FROM vclient c
JOIN vGrants g ON g.client_hub_key = c.client_hub_key
GROUP BY c.client_name, g.plan_name, g.grant_type_description
ORDER BY c.client_name, g.plan_name, grant_count DESC;


-- Q22: Vesting tranches per grant
-- Shows how one grant_id has multiple rows (vesting tranches)
-- (Replace 'GRANT_ID' with actual value)
SELECT 
    grant_id,
    plan_name,
    grant_type_description,
    vesting_dt,
    units_granted_amount,
    is_processed,
    CASE 
        WHEN vesting_dt <= CURRENT_DATE THEN 'Past'
        WHEN vesting_dt <= CURRENT_DATE + INTERVAL '30 days' THEN 'Next 30 days'
        ELSE 'Future'
    END AS vesting_window
FROM vGrants
WHERE grant_id = 'GRANT_ID'
ORDER BY vesting_dt ASC;


-- Q23: Compare row count vs distinct grant count
-- Demonstrates why DISTINCT is critical
SELECT 
    'Total Rows (Vesting Tranches)' AS metric,
    COUNT(*) AS count
FROM vGrants

UNION ALL

SELECT 
    'Distinct Grants' AS metric,
    COUNT(DISTINCT grant_id) AS count
FROM vGrants

UNION ALL

SELECT 
    'Distinct Participants' AS metric,
    COUNT(DISTINCT participant_hub_key) AS count
FROM vGrants

UNION ALL

SELECT 
    'Distinct Plans' AS metric,
    COUNT(DISTINCT plan_hub_key) AS count
FROM vGrants;


-- Q24: Plans and their grant type distribution
-- Shows which grant types are offered under each plan
SELECT 
    plan_name,
    plan_type,
    grant_type_description,
    COUNT(DISTINCT grant_id) AS grant_count,
    COUNT(DISTINCT participant_hub_key) AS participant_count,
    SUM(units_granted_amount) AS total_units
FROM vGrants
GROUP BY plan_name, plan_type, grant_type_description
ORDER BY plan_name, grant_count DESC;

