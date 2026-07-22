import pandas as pd
import os

def deduplicate_users(users_df: pd.DataFrame) -> pd.DataFrame:
    print("--- 1. Deduplicating Users ---")
    print(f"Original Row Count: {len(users_df)}")
    
    # Sort by user_id and updated_at descending
    users_df['updated_at'] = pd.to_datetime(users_df['updated_at'])
    sorted_df = users_df.sort_values(by=['user_id', 'updated_at'], ascending=[True, False])
    
    # Keep the first row (most recently updated) for each user_id
    deduped_df = sorted_df.drop_duplicates(subset=['user_id'], keep='first')
    
    print(f"Deduplicated Row Count: {len(deduped_df)}")
    print("Resulting Clean Users:")
    print(deduped_df[['user_id', 'email', 'updated_at']])
    print("\n")
    return deduped_df

def frame_events(events_df: pd.DataFrame) -> pd.DataFrame:
    print("--- 2. Framing Data (Aggregating Daily User Events) ---")
    
    events_df['event_timestamp'] = pd.to_datetime(events_df['event_timestamp'])
    events_df['event_date'] = events_df['event_timestamp'].dt.date
    
    daily_summary = events_df.groupby(['user_id', 'event_date']).agg(
        total_events=('event_id', 'count'),
        unique_event_types=('event_type', 'nunique'),
        first_event_time=('event_timestamp', 'min'),
        last_event_time=('event_timestamp', 'max')
    ).reset_index()
    
    print("Daily User Activity Datamart:")
    print(daily_summary)
    print("\n")
    return daily_summary

def similarise_schema(df: pd.DataFrame) -> pd.DataFrame:
    print("--- 3. Schema Similarisation ---")
    print("Mapping 'user_id' -> 'customer_id' and casting dates to string for export.")
    
    df = df.rename(columns={'user_id': 'customer_id'})
    # Simulate standardizing the datetime format to ISO 8601 string
    df['first_event_time'] = df['first_event_time'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    df['last_event_time'] = df['last_event_time'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    print("Transformed Schema Columns:")
    print(df.columns.tolist())
    print("\n")
    return df

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)
    
    # Load Data
    users = pd.read_csv(os.path.join(base_dir, 'users.csv'))
    events = pd.read_csv(os.path.join(base_dir, 'events.csv'))
    
    # Execute Pipeline
    clean_users = deduplicate_users(users)
    framed_events = frame_events(events)
    final_export = similarise_schema(framed_events)
    
    # Save outputs
    clean_users.to_csv(os.path.join(base_dir, 'clean_users.csv'), index=False)
    final_export.to_csv(os.path.join(base_dir, 'export_events.csv'), index=False)
    print("Pipeline Complete! Saved outputs to 'clean_users.csv' and 'export_events.csv'.")
