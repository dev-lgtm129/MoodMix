# assets/ui/themes.py

"""
Theme configuration module for MoodMix.

This file defines color themes used throughout the app.
Each theme is represented as a dictionary containing hex color codes for:
- bg: Background color of the app page
- surface: Card / container background color
- surface_variant: Slightly lighter container fill (for callouts, highlighted tiles)
- text_primary: Primary text color for headings and title labels
- text_muted: Secondary text color for subtitles and captions
- accent: Primary accent color (used for primary buttons, active borders, header titles)
- accent_secondary: Secondary accent color (used for icons, callout highlights)
- border: Subtle border and divider line color
- gradient_start: Start color for top header gradient
- gradient_end: End color for top header gradient
- mood_active_bg: Background color when a mood card is selected

To add a new theme:
1. Define a new theme dictionary following the template below.
2. Add the dictionary to the `THEMES` list at the bottom of this file.
That's it! The app will automatically include your new theme in the rotation.
"""

# Theme 1: Dark Chocolate
THEME_DARK_CHOCOLATE = {
    "name": "Dark Chocolate",
    "bg": "#1e1915",
    "surface": "#26201b",
    "surface_variant": "#342b23",
    "text_primary": "#FCF4E0",
    "text_muted": "#a39281",
    "accent": "#D8C5A9",
    "accent_secondary": "#567c6d",
    "border": "#3e332a",
    "gradient_start": "#362a20",
    "gradient_end": "#1e1915",
    "mood_active_bg": "#3a2c20",
}

# Theme 2: White Chocolate
THEME_WHITE_CHOCOLATE = {
    "name": "White Chocolate",
    "bg": "#F5EFE6",
    "surface": "#E8DFD8",
    "surface_variant": "#D9CDC4",
    "text_primary": "#2D241E",
    "text_muted": "#6E5E52",
    "accent": "#8C5A3C",
    "accent_secondary": "#3E6B5C",
    "border": "#C7B8AD",
    "gradient_start": "#EADCD3",
    "gradient_end": "#F5EFE6",
    "mood_active_bg": "#D9C5B8",
}

# Theme 3: Matcha
THEME_MATCHA = {
    "name": "Matcha",
    "bg": "#222222",
    "surface": "#2a2a2a",
    "surface_variant": "#333333",
    "text_primary": "#f0f4f1",
    "text_muted": "#9ea89f",
    "accent": "#c2d8c4",
    "accent_secondary": "#8fae92",
    "border": "#3a3a3a",
    "gradient_start": "#2d332e",
    "gradient_end": "#222222",
    "mood_active_bg": "#343d35",
}

# Theme 4: Midnight (AMOLED / OLED High Contrast)
THEME_MIDNIGHT = {
    "name": "Midnight",
    "bg": "#000000",
    "surface": "#121212",
    "surface_variant": "#1e1e1e",
    "text_primary": "#ffffff",
    "text_muted": "#888888",
    "accent": "#ffffff",
    "accent_secondary": "#cccccc",
    "border": "#2a2a2a",
    "gradient_start": "#181818",
    "gradient_end": "#000000",
    "mood_active_bg": "#242424",
}

# List of all available themes. The theme toggle button cycles through this list in order.
THEMES = [
    THEME_DARK_CHOCOLATE,
    THEME_WHITE_CHOCOLATE,
    THEME_MATCHA,
    THEME_MIDNIGHT,
]

