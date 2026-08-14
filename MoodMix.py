import sys
import os
import webbrowser
import urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flet as ft
import time
from assets.data.data_loader import load_dataset, get_unique_genres
from assets.logic.recommender import recommend_songs, get_random_playlist
from assets.ui.themes import THEMES

def main(page: ft.Page):
    # --- LOAD DATASET & UNIQUE GENRES ONCE AT STARTUP ---
    df = load_dataset()
    unique_genres = get_unique_genres(df)

    page.title = "MoodMix"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 20
    page.window_width = 480
    page.window_height = 800

    # --- THEME MANAGEMENT STATE ---
    # Index of current active theme in THEMES list (from assets/ui/themes.py)
    current_theme_index = [0]

    def get_current_theme():
        """Returns the dictionary object representing the currently active theme."""
        return THEMES[current_theme_index[0]]

    theme = get_current_theme()
    page.bgcolor = theme["bg"]

    page.fonts = {
        "helv": "fonts/Helvetica.ttf",
        "helv_title": "fonts/Helvetica-Bold.ttf",
        "jetbrains": "fonts/JetBrainsMono-Regular.ttf",
        "inter": "fonts/Inter_24pt-ExtraBold.ttf",
        "inter_sub" : "fonts/Inter_18pt-Regular.ttf",
        "grotesk" : "fonts/SpaceGrotesk-Regular.ttf"
    }

    # Configure Flet global Theme
    page.theme = ft.Theme(
        font_family="grotesk",
        color_scheme=ft.ColorScheme(
            surface=theme["surface"],
            on_surface=theme["text_primary"],
            surface_container=theme["surface"],
            surface_container_highest=theme["surface_variant"],
            on_surface_variant=theme["text_muted"],
            primary=theme["accent"],
            on_primary=theme["bg"],
            secondary=theme["accent_secondary"],
            on_secondary="#ffffff",
            outline=theme["border"],
            outline_variant=theme["border"],
        ),
    )

    # --- TOP-RIGHT THEME TOGGLE BUTTON ---
    theme_button = ft.IconButton(
        icon=ft.Icons.PALETTE_OUTLINED,
        icon_color=theme["accent"],
        tooltip="Change theme",
        on_click=lambda e: cycle_theme(e),
    )

    # --- 1. WARM ACCENT GRADIENT HEADER BANNER ---
    header_icon = ft.Icon(ft.Icons.MUSIC_NOTE, color=theme["bg"], size=28)
    header_icon_box = ft.Container(
        content=header_icon,
        bgcolor=theme["accent"],
        padding=10,
        border_radius=10,
    )
    header_title = ft.Text("MoodMix", size=26, weight=ft.FontWeight.BOLD,
                            color=theme["accent"], font_family="inter")
    header_subtitle = ft.Text("Your Personalized Music Recommendation Engine",
                               size=12, color=theme["text_muted"], font_family="grotesk")

    header_banner = ft.Container(
        content=ft.Row([
            header_icon_box,
            ft.Column([
                header_title,
                header_subtitle,
            ], spacing=2, expand=True),
            theme_button,
        ], alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
        padding=16,
        border_radius=14,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[theme["gradient_start"], theme["gradient_end"]],
        ),
        border=ft.Border.all(1, theme["border"]),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=12, color="#00000044", offset=ft.Offset(0, 4)),
    )

    # --- 2. CONTAINER-WRAPPED DROPDOWNS ---
    genre_dropdown_control = ft.Dropdown(
        label="Genre",
        options=[ft.dropdown.Option(key=g, text=g.capitalize()) for g in unique_genres],
        value=unique_genres[0] if unique_genres else None,
        expand=True,
        border=ft.InputBorder.NONE,
        focused_border_color=theme["accent"],
        text_style=ft.TextStyle(font_family="grotesk"),
    )

    genre_dropdown_container = ft.Container(
        content=genre_dropdown_control,
        bgcolor=theme["surface"],
        border_radius=10,
        border=ft.Border.all(1, theme["border"]),
        padding=ft.Padding(left=12, top=2, right=12, bottom=2),
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=6, color="#00000033", offset=ft.Offset(0, 2))
    )

    # --- 3. MOOD CARDS / CHIPS ---
    selected_mood = {"value": "Happy"}

    mood_options = [
        {"value": "Happy", "label": "Happy / Energetic", "icon": ft.Icons.WB_SUNNY},
        {"value": "Sad", "label": "Sad / Melancholic", "icon": ft.Icons.WATER_DROP},
        {"value": "Chill", "label": "Chill / Relaxed", "icon": ft.Icons.COFFEE},
        {"value": "Angry", "label": "Angry / Intense", "icon": ft.Icons.LOCAL_FIRE_DEPARTMENT},
    ]

    mood_card_containers = {}

    def update_mood_cards():
        """Updates background, border, and text colors of mood selection cards based on active selection and current theme."""
        current_t = get_current_theme()
        for opt in mood_options:
            val = opt["value"]
            card = mood_card_containers[val]
            is_active = (selected_mood["value"] == val)
            card.bgcolor = current_t["mood_active_bg"] if is_active else current_t["surface"]
            card.border = ft.Border.all(2 if is_active else 1, current_t["accent"] if is_active else current_t["border"])
            card.shadow = ft.BoxShadow(spread_radius=1, blur_radius=10, color="#db7b5455", offset=ft.Offset(0, 0)) if is_active else None
            
            # Update inner icon and text colors
            icon_ctrl = card.content.controls[0]
            text_ctrl = card.content.controls[1]
            icon_ctrl.color = current_t["accent"] if is_active else current_t["text_muted"]
            text_ctrl.color = current_t["text_primary"] if is_active else current_t["text_muted"]
            text_ctrl.weight = ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL

    def make_mood_card(opt):
        val = opt["value"]
        
        def on_click(e):
            selected_mood["value"] = val
            update_mood_cards()
            page.update()

        card = ft.Container(
            content=ft.Row([
                ft.Icon(opt["icon"], size=20, color=theme["text_muted"]),
                ft.Text(opt["label"], size=13, color=theme["text_muted"], font_family="grotesk"),
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
            padding=ft.Padding(left=14, top=12, right=14, bottom=12),
            border_radius=10,
            bgcolor=theme["surface"],
            border=ft.Border.all(1, theme["border"]),
            on_click=on_click,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            expand=True,
        )
        mood_card_containers[val] = card
        return card

    # Build 2x2 grid of mood cards
    mood_cards_grid = ft.Column([
        ft.Row([make_mood_card(mood_options[0]), make_mood_card(mood_options[1])], spacing=10),
        ft.Row([make_mood_card(mood_options[2]), make_mood_card(mood_options[3])], spacing=10),
    ], spacing=10)

    # Initialize card styles
    update_mood_cards()

    # Section Headers
    mood_label = ft.Text("Select Mood:", weight=ft.FontWeight.BOLD, color=theme["text_primary"], font_family="grotesk")
    size_label = ft.Text("Playlist Size:", weight=ft.FontWeight.BOLD, color=theme["text_primary"], font_family="grotesk")

    # --- SLIDER CONTROL ---
    size_slider = ft.Slider(
        min=5, 
        max=25, 
        divisions=4, 
        value=10, 
        label="{value} songs",
        active_color=theme["accent"],
        inactive_color=theme["surface_variant"],
    )

    # --- 4. ACTION BUTTONS ("Get Recommendations" & "Surprise Me") ---
    button_icon = ft.Icon(ft.Icons.MUSIC_NOTE, color=theme["bg"], size=20)
    button_text = ft.Text("Get Recommendations", color=theme["bg"], weight=ft.FontWeight.BOLD, size=14, font_family="grotesk")
    button_container = ft.Container(
        content=ft.Row([
            button_icon,
            button_text,
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
        bgcolor=theme["accent"],
        padding=ft.Padding(left=14, top=12, right=14, bottom=12),
        border_radius=10,
        border=ft.Border.all(1, theme["accent"]),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color="#db7b5444", offset=ft.Offset(0, 2)),
        animate=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
        alignment=ft.Alignment.CENTER,
    )

    # TASK 2: "Surprise Me" button, styled cohesively with the get recommendation button
    surprise_icon = ft.Icon(ft.Icons.CASINO, color=theme["bg"], size=20)
    surprise_text = ft.Text("Surprise Me", color=theme["bg"], weight=ft.FontWeight.BOLD, size=14, font_family="grotesk")
    surprise_button_container = ft.Container(
        content=ft.Row([
            surprise_icon,
            surprise_text,
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
        bgcolor=theme["accent"],
        padding=ft.Padding(left=14, top=12, right=14, bottom=12),
        border_radius=10,
        border=ft.Border.all(1, theme["accent"]),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color="#db7b5444", offset=ft.Offset(0, 2)),
        animate=ft.Animation(250, ft.AnimationCurve.EASE_OUT),
        animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT),
        alignment=ft.Alignment.CENTER,
    )

    def trigger_button_glow(e):
        current_t = get_current_theme()
        button_container.border = ft.Border.all(3, current_t["text_primary"])
        button_container.shadow = ft.BoxShadow(spread_radius=4, blur_radius=20, color="#db7b54bb", offset=ft.Offset(0, 0))
        button_container.scale = 1.04
        page.update()

        time.sleep(0.18)

        button_container.border = ft.Border.all(1, current_t["accent"])
        button_container.shadow = ft.BoxShadow(spread_radius=1, blur_radius=8, color="#db7b5444", offset=ft.Offset(0, 2))
        button_container.scale = 1.0
        page.update()

        show_results(e, is_random=False)

    def trigger_surprise_glow(e):
        """Triggers click animation for 'Surprise Me' button and generates random song playlist."""
        current_t = get_current_theme()
        surprise_button_container.border = ft.Border.all(3, current_t["text_primary"])
        surprise_button_container.shadow = ft.BoxShadow(spread_radius=4, blur_radius=20, color="#db7b54bb", offset=ft.Offset(0, 0))
        surprise_button_container.scale = 1.04
        page.update()

        time.sleep(0.18)

        surprise_button_container.border = ft.Border.all(1, current_t["accent"])
        surprise_button_container.shadow = ft.BoxShadow(spread_radius=1, blur_radius=8, color="#db7b5444", offset=ft.Offset(0, 2))
        surprise_button_container.scale = 1.0
        page.update()

        show_results(e, is_random=True)

    button_container.on_click = trigger_button_glow
    surprise_button_container.on_click = trigger_surprise_glow

    centered_button_row = ft.Row(
        [button_container, surprise_button_container],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
    )

    # --- ACTIVE VIEW STATE & LIVE THEME SWITCHING LOGIC ---
    current_view_state = {
        "name": "input",
        "is_random": False
    }

    def cycle_theme(e):
        """
        TASK 3: Cycles to the next theme in THEMES list (wrapping back to the first after the last)
        and updates all colors live instantly across the entire app.
        """
        current_theme_index[0] = (current_theme_index[0] + 1) % len(THEMES)
        apply_theme()

    def apply_theme():
        """
        Updates control color properties dynamically for the active theme and calls page.update().
        """
        current_t = get_current_theme()

        page.bgcolor = current_t["bg"]
        page.theme = ft.Theme(
            font_family="grotesk",
            color_scheme=ft.ColorScheme(
                surface=current_t["surface"],
                on_surface=current_t["text_primary"],
                surface_container=current_t["surface"],
                surface_container_highest=current_t["surface_variant"],
                on_surface_variant=current_t["text_muted"],
                primary=current_t["accent"],
                on_primary=current_t["bg"],
                secondary=current_t["accent_secondary"],
                on_secondary="#ffffff",
                outline=current_t["border"],
                outline_variant=current_t["border"],
            ),
        )

        # Update Header Banner colors
        header_icon_box.bgcolor = current_t["accent"]
        header_icon.color = current_t["bg"]
        header_title.color = current_t["accent"]
        header_subtitle.color = current_t["text_muted"]
        header_banner.gradient = ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[current_t["gradient_start"], current_t["gradient_end"]],
        )
        header_banner.border = ft.Border.all(1, current_t["border"])
        theme_button.icon_color = current_t["accent"]

        # Update Dropdown & Section Labels colors
        genre_dropdown_control.focused_border_color = current_t["accent"]
        genre_dropdown_container.bgcolor = current_t["surface"]
        genre_dropdown_container.border = ft.Border.all(1, current_t["border"])
        mood_label.color = current_t["text_primary"]
        size_label.color = current_t["text_primary"]

        # Update Mood Cards colors
        update_mood_cards()

        # Update Slider colors
        size_slider.active_color = current_t["accent"]
        size_slider.inactive_color = current_t["surface_variant"]

        # Update Action Button colors
        button_container.bgcolor = current_t["accent"]
        button_container.border = ft.Border.all(1, current_t["accent"])
        button_icon.color = current_t["bg"]
        button_text.color = current_t["bg"]

        surprise_button_container.bgcolor = current_t["accent"]
        surprise_button_container.border = ft.Border.all(1, current_t["accent"])
        surprise_icon.color = current_t["bg"]
        surprise_text.color = current_t["bg"]

        # If results view is currently open, re-render it so song cards and buttons update live
        if current_view_state["name"] == "results":
            show_results(None, is_random=current_view_state["is_random"])
        else:
            page.update()

    # --- VIEW SWITCHING LOGIC ---
    def show_results(e, is_random=False):
        current_view_state["name"] = "results"
        current_view_state["is_random"] = is_random

        current_t = get_current_theme()
        playlist_size = int(size_slider.value)

        # TASK 2: Execute standard recommendation engine or random playlist sampler based on mode
        if is_random:
            recs_df, message = get_random_playlist(df, playlist_size)
            info_str = f"Mode: Surprise Me (Random)  •  Size: {playlist_size} tracks"
        else:
            selected_genre = genre_dropdown_control.value or ""
            selected_mood_val = selected_mood["value"]
            recs_df, message = recommend_songs(df, selected_genre, selected_mood_val, playlist_size)
            info_str = f"Selected Mood: {selected_mood_val}  •  Genre: {selected_genre.capitalize()}  •  Size: {playlist_size} tracks"

        # TASK 1: Display-only helper function to split semicolon-separated artists and join with comma & space
        def format_artists(artist_str):
            """
            Splits semicolon-separated artist names and joins them with ', ' for display only.
            Example: 'Ingrid Michaelson;ZAYN' -> 'Ingrid Michaelson, ZAYN'
            """
            artists = [a.strip() for a in str(artist_str).split(';') if a.strip()]
            return ", ".join(artists)

        def format_genres(genre_str):
            tags = [t.strip().capitalize() for t in str(genre_str).split(';') if t.strip()]
            return ", ".join(tags[:3])

        def play_song(track_name: str, artists_raw: str):
            """
            Opens a YouTube search in the user's default web browser for the song title and primary artist.
            Splits semicolon-separated artists to use only the first artist for a clean query.
            """
            first_artist = str(artists_raw).split(';')[0].strip() if artists_raw else ""
            query = f"{track_name} {first_artist}".strip()
            encoded_query = urllib.parse.quote_plus(query)
            youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            webbrowser.open(youtube_url)

        # Build UI tiles for each recommended song using formatted artist names
        song_tiles = [
            ft.Container(
                content=ft.ListTile(
                    leading=ft.Container(
                        content=ft.Icon(ft.Icons.ALBUM, color=current_t["accent_secondary"], size=24),
                        padding=8,
                        bgcolor=current_t["surface_variant"],
                        border_radius=8,
                    ),
                    title=ft.Text(row["track_name"], weight=ft.FontWeight.BOLD, color=current_t["text_primary"], font_family="helv"),
                    subtitle=ft.Text(f"{format_artists(row['artists'])} • {format_genres(row['track_genre'])}", color=current_t["text_muted"], font_family="grotesk"),
                    trailing=ft.IconButton(
                        icon=ft.Icons.PLAY_CIRCLE_FILL_ROUNDED,
                        icon_color=current_t["accent"],
                        tooltip="Play on YouTube",
                        on_click=lambda _, t=row["track_name"], a=row["artists"]: play_song(t, a),
                    ),
                ),
                bgcolor=current_t["surface"],
                border_radius=10,
                margin=ft.Margin(left=0, top=0, right=0, bottom=10),
                border=ft.Border.all(1, current_t["border"]),
                shadow=ft.BoxShadow(spread_radius=0, blur_radius=6, color="#00000033", offset=ft.Offset(0, 2)),
            )
            for _, row in recs_df.iterrows()
        ]

        # Results header row with Back button
        results_content = [
            ft.Row([
                ft.IconButton(ft.Icons.ARROW_BACK, icon_color=current_t["accent"], on_click=lambda _: go_to_inputs()),
                ft.Text("Your Recommendation", size=20, weight=ft.FontWeight.BOLD, color=current_t["text_primary"], font_family="grotesk", expand=True),
            ]),
            ft.Divider(color=current_t["border"]),
            ft.Container(
                content=ft.Text(info_str, color=current_t["accent"], size=13, font_family="grotesk"),
                padding=ft.Padding(left=12, top=6, right=12, bottom=6),
                bgcolor=current_t["surface_variant"],
                border_radius=8,
                border=ft.Border.all(1, current_t["border"]),
            ),
        ]

        if message:
            results_content.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INFO_OUTLINE, color=current_t["accent"], size=20),
                        ft.Text(message, color=current_t["text_primary"], size=13, font_family="grotesk", expand=True),
                    ], spacing=10),
                    padding=12,
                    bgcolor=current_t["surface_variant"],
                    border_radius=10,
                    border=ft.Border.all(1, current_t["accent"]),
                )
            )

        results_content.extend([
            ft.Container(height=6),
            ft.ListView(controls=song_tiles, expand=True, height=420),
            ft.Row([
                ft.Button(
                    "Regenerate", 
                    icon=ft.Icons.REFRESH, 
                    on_click=lambda e: show_results(e, is_random=is_random),
                    style=ft.ButtonStyle(
                        color=current_t["bg"], 
                        bgcolor=current_t["accent"],
                        shape=ft.RoundedRectangleBorder(radius=10)
                    )
                )
            ], alignment=ft.MainAxisAlignment.CENTER)
        ])

        results_view = ft.Column(results_content, spacing=10)

        page.clean()
        page.add(results_view)

    def go_to_inputs():
        current_view_state["name"] = "input"
        page.clean()
        page.add(input_view)

    # --- MAIN INPUT SCREEN ---
    input_view = ft.Column([
        header_banner,
        ft.Container(height=6),
        genre_dropdown_container,
        ft.Container(height=4),
        mood_label,
        mood_cards_grid,
        ft.Container(height=4),
        size_label,
        size_slider,
        ft.Container(height=12),
        centered_button_row,
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    # Add initial input view to page
    page.add(input_view)

ft.run(main)
