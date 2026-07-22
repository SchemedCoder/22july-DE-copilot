import os
import pandas as pd
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas
from dotenv import load_dotenv

load_dotenv()

def deduplicate_users(users_df: pd.DataFrame) -> pd.DataFrame:
    print("--- 1. Deduplicating Users ---")
    users_df['updated_at'] = pd.to_datetime(users_df['updated_at'])
    sorted_df = users_df.sort_values(by=['user_id', 'updated_at'], ascending=[True, False])
    deduped = sorted_df.drop_duplicates(subset=['user_id'], keep='first').copy()
    
    # Format dates as strings for safer Snowflake ingestion
    deduped['created_at'] = deduped['created_at'].astype(str)
    deduped['updated_at'] = deduped['updated_at'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    return deduped

def frame_events(events_df: pd.DataFrame) -> pd.DataFrame:
    print("--- 2. Framing Data ---")
    events_df['event_timestamp'] = pd.to_datetime(events_df['event_timestamp'])
    events_df['event_date'] = events_df['event_timestamp'].dt.date
    daily_summary = events_df.groupby(['user_id', 'event_date']).agg(
        total_events=('event_id', 'count'),
        unique_event_types=('event_type', 'nunique'),
        first_event_time=('event_timestamp', 'min'),
        last_event_time=('event_timestamp', 'max')
    ).reset_index()
    
    # Format dates as strings for safer Snowflake ingestion
    daily_summary['event_date'] = daily_summary['event_date'].astype(str)
    daily_summary['first_event_time'] = daily_summary['first_event_time'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    daily_summary['last_event_time'] = daily_summary['last_event_time'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    return daily_summary

def similarise_schema(df: pd.DataFrame) -> pd.DataFrame:
    print("--- 3. Schema Similarisation ---")
    return df.rename(columns={'user_id': 'customer_id'})

def upload_to_snowflake(df: pd.DataFrame, table_name: str):
    print(f"--- 4. Uploading to Snowflake Table: {table_name} ---")
    
    # Snowflake prefers uppercase column names
    df.columns = [c.upper() for c in df.columns]

    try:
        conn = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA', 'PUBLIC')
        )
        print("Connected to Snowflake securely!")
        
        # write_pandas efficiently bulk loads data and can auto-create tables!
        success, nchunks, nrows, _ = write_pandas(
            conn, 
            df, 
            table_name.upper(),
            auto_create_table=True,
            overwrite=True
        )
        if success:
            print(f"✅ Successfully uploaded {nrows} rows to {table_name.upper()} in your Snowflake account!")
            
    except Exception as e:
        print(f"❌ Error uploading to Snowflake: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    if not os.getenv('SNOWFLAKE_ACCOUNT'):
        print("ERROR: Please set your Snowflake credentials in the .env file!")
        exit(1)

    base_dir = os.path.dirname(__file__)
    
    print("Loading local CSV data...")
    users = pd.read_csv(os.path.join(base_dir, 'users.csv'))
    events = pd.read_csv(os.path.join(base_dir, 'events.csv'))
    
    clean_users = deduplicate_users(users)
    framed_events = frame_events(events)
    final_events = similarise_schema(framed_events)
    
    upload_to_snowflake(clean_users, "CLEAN_USERS")
    upload_to_snowflake(final_events, "DAILY_EVENTS_DATAMART")
    
    print("Pipeline Complete! Log into your Snowflake Web UI to query your new tables.")
