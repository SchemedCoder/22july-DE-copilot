# Schema Similarisation Playbook

## Overview
When merging data from acquisitions or standardizing third-party data, we use a process called "Schema Similarisation" (or schema alignment).

## Steps for Schema Similarisation
1. **Column Mapping**: Identify columns that hold identical logical data but have different names (e.g., `cust_id` vs `user_id`).
2. **Type Casting**: Ensure target types match our central data warehouse (e.g., casting `VARCHAR` dates to `TIMESTAMP`).
3. **Value Normalization**: Standardize enum values (e.g., mapping `['M', 'F']` to `['Male', 'Female']`).

## Example
If migrating a Postgres source to Snowflake:
- Change Postgres `TEXT` to Snowflake `VARCHAR`.
- Change Postgres `JSONB` to Snowflake `VARIANT`.
- Rename `creation_date` to `created_at` for consistency across all dim tables.
