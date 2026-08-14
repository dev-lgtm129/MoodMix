import pandas as pd
import random

# Mapping dictionary to match UI mood keys to CSV dataset mood strings
MOOD_MAP = {
    "Happy": "Happy / Energetic",
    "Sad": "Sad / Melancholic",
    "Chill": "Chill / Relaxed",
    "Angry": "Angry / Intense"
}

def recommend_songs(df: pd.DataFrame, genre: str, mood: str, playlist_size: int):
    """
    Generates music recommendations based on selected genre, mood, and desired playlist size.
    
    Parameters:
        df (pd.DataFrame): Cleaned song dataset.
        genre (str): Selected genre tag (e.g., "pop", "indie").
        mood (str): Selected mood (e.g., "Happy", "Chill", or full string "Happy / Energetic").
        playlist_size (int): Number of songs requested.
        
    Returns:
        tuple: (result_df, message_str_or_None)
            - result_df: DataFrame containing columns ['track_name', 'artists', 'track_genre']
            - message: Informative string if results were limited/empty, or None if full results found.
    """
    if df is None or df.empty:
        empty_df = pd.DataFrame(columns=['track_name', 'artists', 'track_genre'])
        return empty_df, "Dataset is empty or not loaded."

    # 1. Map mood key to exact dataset string if necessary
    target_mood = MOOD_MAP.get(mood, mood)
    
    # 2. Filter by exact mood match
    mood_filtered = df[df['mood'] == target_mood]
    
    # 3. Filter by genre tag membership (split on ';' and check exact tag match)
    if genre:
        target_genre_clean = genre.strip().lower()
        
        def has_genre_tag(genre_str):
            tags = [t.strip().lower() for t in str(genre_str).split(';')]
            return target_genre_clean in tags
            
        genre_mask = mood_filtered['track_genre'].apply(has_genre_tag)
        filtered_df = mood_filtered[genre_mask].copy()
    else:
        filtered_df = mood_filtered.copy()
        
    match_count = len(filtered_df)
    
    # 4. Handle limited or zero results gracefully without crashing
    if match_count == 0:
        message = f"No songs found matching genre '{genre}' and mood '{target_mood}'."
        result_df = pd.DataFrame(columns=['track_name', 'artists', 'track_genre'])
        return result_df, message
        
    if match_count < playlist_size:
        message = f"Only {match_count} song(s) available for '{genre}' ({target_mood}). Displaying all available."
        result_df = filtered_df[['track_name', 'artists', 'track_genre']].copy()
        return result_df, message

    # 5. Standard case: matches >= playlist_size
    # Pick top N from a larger pool (3x playlist_size) based on popularity for high quality & variety
    pool_size = min(match_count, playlist_size * 3)
    top_pool = filtered_df.sort_values(by='popularity', ascending=False).head(pool_size)
    
    # Randomly sample requested playlist_size from top_pool
    sampled_pool = top_pool.sample(n=playlist_size)
    
    # Keep only the requested columns
    result_df = sampled_pool[['track_name', 'artists', 'track_genre']].copy()
    
    return result_df, None


def get_random_playlist(df: pd.DataFrame, playlist_size: int):
    """
    Generates a playlist of completely random songs from the dataset, bypassing genre and mood filters.
    
    Parameters:
        df (pd.DataFrame): Cleaned song dataset.
        playlist_size (int): Desired number of random songs to return.
        
    Returns:
        tuple: (result_df, message)
            - result_df: pd.DataFrame containing columns ['track_name', 'artists', 'track_genre']
            - message: Informative string if dataset is empty or sampling size exceeds available rows, else None.
    """
    # Safety check: Handle empty or missing dataset gracefully
    if df is None or df.empty:
        empty_df = pd.DataFrame(columns=['track_name', 'artists', 'track_genre'])
        return empty_df, "Dataset is empty or not loaded."

    total_available = len(df)
    
    # If requested playlist size is greater than total dataset size, cap it
    if total_available < playlist_size:
        message = f"Only {total_available} song(s) available in dataset. Displaying all."
        result_df = df[['track_name', 'artists', 'track_genre']].copy()
        return result_df, message

    # Randomly sample 'playlist_size' songs from the full dataset without any filtering
    sampled_df = df.sample(n=playlist_size)
    
    # Return only the relevant columns matching recommend_songs() output structure
    result_df = sampled_df[['track_name', 'artists', 'track_genre']].copy()
    
    return result_df, None

