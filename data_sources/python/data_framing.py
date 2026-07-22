import pandas as pd

def frame_user_events(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Frames raw user events into a daily aggregated summary dataframe.
    This helps in building the user activity datamart.
    """
    # Ensure timestamp is datetime
    events_df['event_timestamp'] = pd.to_datetime(events_df['event_timestamp'])
    
    # Extract date
    events_df['event_date'] = events_df['event_timestamp'].dt.date
    
    # Group by user and date, aggregating event counts
    daily_summary = events_df.groupby(['user_id', 'event_date']).agg(
        total_events=('event_id', 'count'),
        unique_event_types=('event_type', 'nunique'),
        first_event_time=('event_timestamp', 'min'),
        last_event_time=('event_timestamp', 'max')
    ).reset_index()
    
    return daily_summary

if __name__ == "__main__":
    # Example usage
    sample_data = pd.DataFrame({
        'event_id': [1, 2, 3],
        'user_id': ['u1', 'u1', 'u2'],
        'event_type': ['login', 'click', 'login'],
        'event_timestamp': ['2023-10-01 10:00:00', '2023-10-01 10:05:00', '2023-10-01 11:00:00']
    })
    print(frame_user_events(sample_data))
