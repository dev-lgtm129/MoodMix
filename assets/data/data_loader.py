import pandas as pd

def load_dataset(path="assets/dataset_with_moods.csv"):
    """
    Loads and cleans the music dataset CSV file using pandas.
    Strips leading/trailing whitespace from string columns and drops rows with missing essential values.
    """
    # Load dataset from specified path
    df = pd.read_csv(path)
    
    # Strip whitespace from relevant text columns
    string_columns = ['artists', 'track_name', 'track_genre']
    for col in string_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            
    # Drop rows with null values in mandatory fields
    required_fields = ['track_name', 'artists', 'track_genre', 'mood']
    df = df.dropna(subset=required_fields)
    
    return df


def get_unique_genres(df):
    """
    Extracts all individual genre tags by splitting semicolon-separated 'track_genre' values.
    Returns a sorted list of all unique individual genre tags.
    """
    unique_genres = set()
    
    # Split semicolon-separated tags across all rows
    for genre_entry in df['track_genre'].dropna():
        tags = [tag.strip() for tag in str(genre_entry).split(';') if tag.strip()]
        unique_genres.update(tags)
        
    # Return as an alphabetically sorted list
    return sorted(list(unique_genres))
