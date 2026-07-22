-- dbt model: dedupe_users.sql
-- Description: Deduplicates user records taking the most recently updated record.

WITH raw_users AS (
    SELECT * FROM {{ source('raw_data', 'users') }}
),

ranked_users AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (
            PARTITION BY user_id 
            ORDER BY updated_at DESC
        ) as rn
    FROM raw_users
)

SELECT 
    user_id,
    first_name,
    last_name,
    email,
    created_at,
    updated_at
FROM ranked_users
WHERE rn = 1
