import sys
import os
import webbrowser
import urllib.parse
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flet as ft
from assets.data.data_loader import load_dataset, get_unique_genres
from assets.logic.recommender import recommend_songs, get_random_playlist
from assets.ui.themes import THEMES

def alpha_color(hex_color: str, alpha_hex: str = "40") -> str:
    """
    Converts 6-digit hex color (#RRGGBB) to Flutter/Flet 8-digit ARGB hex string (#AARRGGBB).
    Example: alpha_color("#738a7c", "50") -> "#50738a7c"
    """
    clean = str(hex_color).lstrip("#")
    if len(clean) == 6:
        return f"#{alpha_hex}{clean}"
    return hex_color

def main(page: ft.Page):
    # --- LOAD DATASET & UNIQUE GENRES ONCE AT STARTUP ---
    df = load_dataset()
    unique_genres = get_unique_genres(df)

    page.title = "MoodMix — Music Discovery System"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 16
    page.spacing = 0
    page.window_width = 520
    page.window_height = 860
    page.window_min_width = 380
    page.window_min_height = 650

    # --- THEME MANAGEMENT STATE ---
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
        "grotesk": "fonts/SpaceGrotesk-Regular.ttf",
        "c_grotesk" : "fonts/CriqueGrotesk.ttf",
        "tthoves": "fonts/TTHover.ttf"
    }

    # Configure Flet global Theme
    page.theme = ft.Theme(
        font_family="grotesk",
        scrollbar_theme=ft.ScrollbarTheme(
            thumb_visibility=False,
            track_visibility=False,
            thickness=0,
        ),
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

    # --- TOP-RIGHT THEME DROPDOWN CONTROL ---
    def on_theme_select(idx):
        current_theme_index[0] = idx
        apply_theme()

    def build_theme_menu_items():
        current_t = get_current_theme()
        items = []
        for idx, t in enumerate(THEMES):
            is_selected = (idx == current_theme_index[0])
            items.append(
                ft.PopupMenuItem(
                    content=ft.Row([
                        ft.Icon(
                            ft.Icons.CHECK_ROUNDED if is_selected else ft.Icons.PALETTE_OUTLINED,
                            size=14,
                            color=current_t["accent"] if is_selected else current_t["text_muted"]
                        ),
                        ft.Text(
                            t["name"],
                            size=12,
                            weight=ft.FontWeight.BOLD if is_selected else ft.FontWeight.NORMAL,
                            color=current_t["accent"] if is_selected else current_t["text_primary"],
                            font_family="grotesk"
                        )
                    ], spacing=8),
                    on_click=lambda _, i=idx: on_theme_select(i)
                )
            )
        return items

    theme_badge_text = ft.Text(
        theme["name"].upper(),
        size=10,
        weight=ft.FontWeight.BOLD,
        color=theme["accent"],
        font_family="jetbrains"
    )
    theme_badge_container = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.PALETTE_ROUNDED, size=14, color=theme["accent"]),
            theme_badge_text,
            ft.Icon(ft.Icons.ARROW_DROP_DOWN_ROUNDED, size=16, color=theme["accent"]),
        ], spacing=3, alignment=ft.MainAxisAlignment.CENTER),
        padding=ft.Padding(left=8, top=5, right=6, bottom=5),
        bgcolor=theme["surface_variant"],
        border_radius=20,
        border=ft.Border.all(1, theme["border"]),
        animate=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
        animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT_BACK),
    )

    theme_gesture_detector = ft.GestureDetector(
        content=theme_badge_container,
        on_long_press=lambda e: cycle_theme(e),
    )

    theme_menu_button = ft.PopupMenuButton(
        content=theme_gesture_detector,
        items=build_theme_menu_items(),
        padding=0,
        tooltip="Click to choose theme, hold to cycle",
    )

    # --- 1. HEADER BANNER ---
    header_icon = ft.Icon(ft.Icons.GRAPHIC_EQ_ROUNDED, color=theme["bg"], size=28)
    header_icon_box = ft.Container(
        content=header_icon,
        bgcolor=theme["accent"],
        padding=12,
        border_radius=14,
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=alpha_color(theme["accent"], "35"), offset=ft.Offset(0, 0))
    )
    header_title = ft.Text("MoodMix", size=30, weight=ft.FontWeight.BOLD, color=theme["accent"], font_family="c_grotesk")
    header_subtitle = ft.Text("Your own personalized music discovery and reccomendation system", size=12, color=theme["text_muted"], font_family="grotesk")

    header_banner = ft.Container(
        content=ft.Column([
            ft.Row([
                header_icon_box,
                theme_menu_button,
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Container(height=6),
            header_title,
            header_subtitle,
        ], spacing=2),
        padding=18,
        border_radius=18,
        gradient=ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[theme["gradient_start"], theme["gradient_end"]],
        ),
        border=ft.Border.all(1, theme["border"]),
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=10, color="#25000000", offset=ft.Offset(0, 2)),
    )

    # --- 2. GENRE SECTION ---
    genre_section_label = ft.Row([
        ft.Icon(ft.Icons.DISC_FULL_ROUNDED, size=16, color=theme["accent"]),
        ft.Text("EXPLORE GENRE", size=11, weight=ft.FontWeight.BOLD, color=theme["text_primary"], font_family="jetbrains"),
    ], spacing=6)

    def on_genre_change(e):
        genre_dropdown_container.scale = 1.02
        genre_dropdown_container.border = ft.Border.all(1, get_current_theme()["accent"])
        page.update()
        time.sleep(0.2)
        genre_dropdown_container.scale = 1.0
        genre_dropdown_container.border = ft.Border.all(1, get_current_theme()["border"])
        page.update()

    genre_dropdown_control = ft.Dropdown(
        options=[ft.dropdown.Option(key=g, text=g.capitalize()) for g in unique_genres],
        value=unique_genres[0] if unique_genres else None,
        expand=True,
        border=ft.InputBorder.NONE,
        focused_border_color=theme["accent"],
        color=theme["text_primary"],
        text_style=ft.TextStyle(font_family="grotesk", size=14, weight=ft.FontWeight.W_500, color=theme["text_primary"]),
        on_select=on_genre_change,
    )

    genre_dropdown_container = ft.Container(
        content=ft.Row([
            ft.Icon(ft.Icons.MUSIC_NOTE_ROUNDED, size=20, color=theme["accent_secondary"]),
            genre_dropdown_control,
        ], spacing=10),
        bgcolor=theme["surface"],
        border_radius=14,
        border=ft.Border.all(1, theme["border"]),
        padding=ft.Padding(left=14, top=2, right=14, bottom=2),
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=6, color="#15000000", offset=ft.Offset(0, 2)),
        animate=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
        animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT_BACK),
    )

    # --- 3. MOOD SELECTION SECTION ---
    mood_section_label = ft.Row([
        ft.Icon(ft.Icons.TUNE_ROUNDED, size=16, color=theme["accent"]),
        ft.Text("SELECT YOUR VIBE", size=11, weight=ft.FontWeight.BOLD, color=theme["text_primary"], font_family="jetbrains"),
    ], spacing=6)

    selected_mood = {"value": "Happy"}

    mood_options = [
        {"value": "Happy", "label": "Happy / Energetic", "icon": ft.Icons.WB_SUNNY_ROUNDED, "desc": "Upbeat & High Energy"},
        {"value": "Sad", "label": "Sad / Melancholic", "icon": ft.Icons.WATER_DROP_ROUNDED, "desc": "Reflective & Emotional"},
        {"value": "Chill", "label": "Chill / Relaxed", "icon": ft.Icons.COFFEE_ROUNDED, "desc": "Calm & Mellow Vibing"},
        {"value": "Angry", "label": "Angry / Intense", "icon": ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED, "desc": "Raw Power & Aggressive"},
    ]

    mood_card_containers = {}

    def update_mood_cards():
        """Updates background, border, icon, text colors, and symmetrical uniform accent glow shadow of mood selection cards."""
        current_t = get_current_theme()
        for opt in mood_options:
            val = opt["value"]
            card = mood_card_containers[val]
            is_active = (selected_mood["value"] == val)

            card.bgcolor = current_t["mood_active_bg"] if is_active else current_t["surface"]
            card.border = ft.Border.all(2 if is_active else 1, current_t["accent"] if is_active else current_t["border"])
            # Symmetrical uniform glow on all 4 sides & corners (offset=0,0)
            card.shadow = ft.BoxShadow(spread_radius=1, blur_radius=8, color=alpha_color(current_t["accent"], "45"), offset=ft.Offset(0, 0)) if is_active else None
            card.scale = 1.02 if is_active else 1.0

            content_col = card.content
            row_header = content_col.controls[0]
            icon_ctrl = row_header.controls[0]
            title_ctrl = row_header.controls[1]
            desc_ctrl = content_col.controls[1]

            icon_ctrl.color = current_t["accent"] if is_active else current_t["accent_secondary"]
            title_ctrl.color = current_t["text_primary"]
            title_ctrl.weight = ft.FontWeight.BOLD if is_active else ft.FontWeight.W_600
            desc_ctrl.color = current_t["text_muted"]

    def make_mood_card(opt):
        val = opt["value"]

        def on_click(e):
            selected_mood["value"] = val
            update_mood_cards()
            page.update()

        card = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Icon(opt["icon"], size=22, color=theme["accent_secondary"]),
                    ft.Text(opt["label"], size=13, weight=ft.FontWeight.W_600, color=theme["text_primary"], font_family="grotesk", expand=True),
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=8),
                ft.Text(opt["desc"], size=10, color=theme["text_muted"], font_family="grotesk"),
            ], spacing=4),
            padding=ft.Padding(left=12, top=12, right=12, bottom=12),
            border_radius=14,
            bgcolor=theme["surface"],
            border=ft.Border.all(1, theme["border"]),
            clip_behavior=ft.ClipBehavior.NONE,
            on_click=on_click,
            animate=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_scale=ft.Animation(350, ft.AnimationCurve.EASE_OUT_BACK),
            expand=True,
        )
        mood_card_containers[val] = card
        return card

    mood_cards_grid = ft.Column([
        ft.Row([make_mood_card(mood_options[0]), make_mood_card(mood_options[1])], spacing=10),
        ft.Row([make_mood_card(mood_options[2]), make_mood_card(mood_options[3])], spacing=10),
    ], spacing=10)

    # Outer padding wrapper to ensure box shadow glow is uniform on all 4 sides without clipping
    mood_cards_wrapper = ft.Container(
        content=mood_cards_grid,
        padding=ft.Padding(left=6, top=6, right=6, bottom=6),
        clip_behavior=ft.ClipBehavior.NONE,
    )

    update_mood_cards()

    # --- 4. PLAYLIST SIZE & PRESETS SECTION ---
    size_badge_text = ft.Text("10 TRACKS", size=10, weight=ft.FontWeight.BOLD, color=theme["accent"], font_family="jetbrains")
    size_badge_container = ft.Container(
        content=size_badge_text,
        padding=ft.Padding(left=8, top=3, right=8, bottom=3),
        bgcolor=theme["surface_variant"],
        border_radius=8,
        border=ft.Border.all(1, theme["border"])
    )

    size_section_header = ft.Row([
        ft.Row([
            ft.Icon(ft.Icons.TUNE_ROUNDED, size=16, color=theme["accent"]),
            ft.Text("PLAYLIST LENGTH", size=11, weight=ft.FontWeight.BOLD, color=theme["text_primary"], font_family="jetbrains"),
        ], spacing=6),
        size_badge_container,
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def set_preset_size(size_val):
        size_slider.value = size_val
        size_badge_text.value = f"{size_val} TRACKS"
        update_preset_chips()
        page.update()

    preset_values = [5, 10, 15, 20, 25]
    preset_chip_containers = {}

    def update_preset_chips():
        current_t = get_current_theme()
        curr_val = int(size_slider.value)
        for v in preset_values:
            chip = preset_chip_containers[v]
            is_active = (curr_val == v)
            chip.bgcolor = current_t["accent"] if is_active else current_t["surface"]
            chip.border = ft.Border.all(1, current_t["accent"] if is_active else current_t["border"])
            chip.content.color = current_t["bg"] if is_active else current_t["text_muted"]
            chip.content.weight = ft.FontWeight.BOLD if is_active else ft.FontWeight.NORMAL

    def make_preset_chip(v):
        chip = ft.Container(
            content=ft.Text(f"{v}", size=11, font_family="jetbrains"),
            padding=ft.Padding(left=10, top=6, right=10, bottom=6),
            bgcolor=theme["surface"],
            border_radius=8,
            border=ft.Border.all(1, theme["border"]),
            on_click=lambda _, val=v: set_preset_size(val),
            animate=ft.Animation(400, ft.AnimationCurve.EASE_OUT_CUBIC),
            animate_scale=ft.Animation(300, ft.AnimationCurve.EASE_OUT_BACK),
            expand=True,
            alignment=ft.Alignment.CENTER,
        )
        preset_chip_containers[v] = chip
        return chip

    preset_chips_row = ft.Row([make_preset_chip(v) for v in preset_values], spacing=8)

    def on_slider_change(e):
        val = int(e.control.value)
        size_badge_text.value = f"{val} TRACKS"
        update_preset_chips()
        page.update()

    size_slider = ft.Slider(
        min=5,
        max=25,
        divisions=4,
        value=10,
        label="{value} tracks",
        active_color=theme["accent"],
        inactive_color=theme["surface_variant"],
        on_change=on_slider_change
    )

    update_preset_chips()

    # --- 5. ACTION BUTTONS ---
    button_icon = ft.Icon(ft.Icons.AUTO_AWESOME_ROUNDED, color=theme["bg"], size=18)
    button_text = ft.Text("Get Recommendations", color=theme["bg"], weight=ft.FontWeight.BOLD, size=13, font_family="grotesk")
    button_container = ft.Container(
        content=ft.Row([
            button_icon,
            button_text,
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
        bgcolor=theme["accent"],
        padding=ft.Padding(left=14, top=13, right=14, bottom=13),
        border_radius=14,
        border=ft.Border.all(1, theme["accent"]),
        shadow=ft.BoxShadow(spread_radius=1, blur_radius=8, color=alpha_color(theme["accent"], "40"), offset=ft.Offset(0, 0)),
        animate=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
        animate_scale=ft.Animation(350, ft.AnimationCurve.EASE_OUT_BACK),
        alignment=ft.Alignment.CENTER,
        clip_behavior=ft.ClipBehavior.NONE,
        expand=True,
    )

    surprise_icon = ft.Icon(ft.Icons.CASINO_ROUNDED, color=theme["text_primary"], size=18)
    surprise_text = ft.Text("Surprise Me", color=theme["text_primary"], weight=ft.FontWeight.BOLD, size=13, font_family="grotesk")
    surprise_button_container = ft.Container(
        content=ft.Row([
            surprise_icon,
            surprise_text,
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
        bgcolor=theme["surface_variant"],
        padding=ft.Padding(left=14, top=13, right=14, bottom=13),
        border_radius=14,
        border=ft.Border.all(1, theme["border"]),
        shadow=ft.BoxShadow(spread_radius=0, blur_radius=6, color="#15000000", offset=ft.Offset(0, 0)),
        animate=ft.Animation(450, ft.AnimationCurve.EASE_OUT_CUBIC),
        animate_scale=ft.Animation(350, ft.AnimationCurve.EASE_OUT_BACK),
        alignment=ft.Alignment.CENTER,
        clip_behavior=ft.ClipBehavior.NONE,
        expand=True,
    )

    def trigger_button_glow(e):
        current_t = get_current_theme()
        button_container.border = ft.Border.all(2, current_t["text_primary"])
        button_container.shadow = ft.BoxShadow(spread_radius=2, blur_radius=12, color=alpha_color(current_t["accent"], "75"), offset=ft.Offset(0, 0))
        button_container.scale = 1.03
        page.update()

        time.sleep(0.16)

        button_container.border = ft.Border.all(1, current_t["accent"])
        button_container.shadow = ft.BoxShadow(spread_radius=1, blur_radius=8, color=alpha_color(current_t["accent"], "40"), offset=ft.Offset(0, 0))
        button_container.scale = 1.0
        page.update()

        show_results(e, is_random=False)

    def trigger_surprise_glow(e):
        current_t = get_current_theme()
        surprise_button_container.border = ft.Border.all(2, current_t["accent"])
        surprise_button_container.shadow = ft.BoxShadow(spread_radius=2, blur_radius=12, color=alpha_color(current_t["accent"], "50"), offset=ft.Offset(0, 0))
        surprise_button_container.scale = 1.03
        page.update()

        time.sleep(0.16)

        surprise_button_container.border = ft.Border.all(1, current_t["border"])
        surprise_button_container.shadow = ft.BoxShadow(spread_radius=0, blur_radius=6, color="#15000000", offset=ft.Offset(0, 0))
        surprise_button_container.scale = 1.0
        page.update()

        show_results(e, is_random=True)

    button_container.on_click = trigger_button_glow
    surprise_button_container.on_click = trigger_surprise_glow

    action_buttons_row = ft.Row([
        button_container,
        surprise_button_container,
    ], spacing=10)

    action_buttons_wrapper = ft.Container(
        content=action_buttons_row,
        padding=ft.Padding(left=6, top=6, right=6, bottom=6),
        clip_behavior=ft.ClipBehavior.NONE,
    )

    # --- ACTIVE VIEW STATE & LIVE THEME SWITCHING LOGIC ---
    current_view_state = {
        "name": "input",
        "is_random": False
    }

    def cycle_theme(e):
        current_theme_index[0] = (current_theme_index[0] + 1) % len(THEMES)
        apply_theme()

    def apply_theme():
        current_t = get_current_theme()

        page.bgcolor = current_t["bg"]
        page.theme = ft.Theme(
            font_family="grotesk",
            scrollbar_theme=ft.ScrollbarTheme(
                thumb_visibility=False,
                track_visibility=False,
                thickness=0,
            ),
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

        theme_badge_text.value = current_t["name"].upper()
        theme_badge_text.color = current_t["accent"]
        theme_badge_container.bgcolor = current_t["surface_variant"]
        theme_badge_container.border = ft.Border.all(1, current_t["border"])
        theme_badge_container.content.controls[0].color = current_t["accent"]
        theme_badge_container.content.controls[2].color = current_t["accent"]
        theme_menu_button.items = build_theme_menu_items()

        header_icon_box.bgcolor = current_t["accent"]
        header_icon_box.shadow = ft.BoxShadow(spread_radius=1, blur_radius=8, color=alpha_color(current_t["accent"], "35"), offset=ft.Offset(0, 0))
        header_icon.color = current_t["bg"]
        header_title.color = current_t["accent"]
        header_subtitle.color = current_t["text_muted"]
        header_banner.gradient = ft.LinearGradient(
            begin=ft.Alignment.TOP_LEFT,
            end=ft.Alignment.BOTTOM_RIGHT,
            colors=[current_t["gradient_start"], current_t["gradient_end"]],
        )
        header_banner.border = ft.Border.all(1, current_t["border"])

        genre_section_label.controls[0].color = current_t["accent"]
        genre_section_label.controls[1].color = current_t["text_primary"]
        genre_dropdown_control.focused_border_color = current_t["accent"]
        genre_dropdown_control.color = current_t["text_primary"]
        genre_dropdown_control.text_style = ft.TextStyle(font_family="grotesk", size=14, weight=ft.FontWeight.W_500, color=current_t["text_primary"])
        genre_dropdown_container.bgcolor = current_t["surface"]
        genre_dropdown_container.border = ft.Border.all(1, current_t["border"])
        genre_dropdown_container.content.controls[0].color = current_t["accent_secondary"]

        mood_section_label.controls[0].color = current_t["accent"]
        mood_section_label.controls[1].color = current_t["text_primary"]

        update_mood_cards()

        size_section_header.controls[0].controls[0].color = current_t["accent"]
        size_section_header.controls[0].controls[1].color = current_t["text_primary"]
        size_badge_text.color = current_t["accent"]
        size_badge_container.bgcolor = current_t["surface_variant"]
        size_badge_container.border = ft.Border.all(1, current_t["border"])
        size_slider.active_color = current_t["accent"]
        size_slider.inactive_color = current_t["surface_variant"]
        update_preset_chips()

        button_container.bgcolor = current_t["accent"]
        button_container.border = ft.Border.all(1, current_t["accent"])
        button_container.shadow = ft.BoxShadow(spread_radius=1, blur_radius=8, color=alpha_color(current_t["accent"], "40"), offset=ft.Offset(0, 0))
        button_icon.color = current_t["bg"]
        button_text.color = current_t["bg"]

        surprise_button_container.bgcolor = current_t["surface_variant"]
        surprise_button_container.border = ft.Border.all(1, current_t["border"])
        surprise_icon.color = current_t["text_primary"]
        surprise_text.color = current_t["text_primary"]

        if current_view_state["name"] == "results":
            show_results(None, is_random=current_view_state["is_random"])
        else:
            page.update()

    # --- VIEW SWITCHING & RESULTS GENERATION LOGIC ---
    def show_results(e, is_random=False):
        current_view_state["name"] = "results"
        current_view_state["is_random"] = is_random

        current_t = get_current_theme()
        playlist_size = int(size_slider.value)

        if is_random:
            recs_df, message = get_random_playlist(df, playlist_size)
            info_str = f"Surprise Me  •  {playlist_size} tracks"
        else:
            selected_genre = genre_dropdown_control.value or ""
            selected_mood_val = selected_mood["value"]
            recs_df, message = recommend_songs(df, selected_genre, selected_mood_val, playlist_size)
            info_str = f"Mood: {selected_mood_val}  •  Genre: {selected_genre.capitalize()}  •  {playlist_size} tracks"

        def format_artists(artist_str):
            artists = [a.strip() for a in str(artist_str).split(';') if a.strip()]
            return ", ".join(artists)

        def format_genres(genre_str):
            tags = [t.strip().capitalize() for t in str(genre_str).split(';') if t.strip()]
            return " • ".join(tags[:3])

        def play_song(track_name: str, artists_raw: str):
            first_artist = str(artists_raw).split(';')[0].strip() if artists_raw else ""
            query = f"{track_name} {first_artist}".strip()
            encoded_query = urllib.parse.quote_plus(query)
            youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            webbrowser.open(youtube_url)

        # Thin Horizontal Scroll Progress Indicator Bar (Acts as the sleek divider line)
        scroll_progress_bar = ft.ProgressBar(
            value=0.0,
            color=current_t["accent"],
            bgcolor=current_t["border"],
            height=3,
            border_radius=2,
        )

        def on_list_scroll(e_scroll: ft.OnScrollEvent):
            total = e_scroll.extent_before + e_scroll.extent_after
            if total > 0:
                progress = min(1.0, max(0.0, e_scroll.extent_before / total))
                scroll_progress_bar.value = progress
                scroll_progress_bar.update()

        song_tiles = []
        for idx, (_, row) in enumerate(recs_df.iterrows(), start=1):
            track_num_str = f"#{idx:02d}"
            tile = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(track_num_str, size=11, weight=ft.FontWeight.BOLD, color=current_t["accent"], font_family="jetbrains"),
                        padding=ft.Padding(left=8, top=6, right=8, bottom=6),
                        bgcolor=current_t["surface_variant"],
                        border_radius=8,
                        border=ft.Border.all(1, current_t["border"]),
                    ),
                    ft.Container(
                        content=ft.Icon(ft.Icons.MUSIC_NOTE_ROUNDED, color=current_t["accent_secondary"], size=20),
                        padding=10,
                        bgcolor=current_t["surface_variant"],
                        border_radius=10,
                    ),
                    ft.Column([
                        ft.Text(row["track_name"], weight=ft.FontWeight.BOLD, size=14, color=current_t["text_primary"], font_family="helv", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(format_artists(row["artists"]), size=12, color=current_t["text_muted"], font_family="grotesk", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                        ft.Text(format_genres(row["track_genre"]), size=10, color=current_t["accent_secondary"], font_family="jetbrains", max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ], spacing=2, expand=True),
                    ft.IconButton(
                        icon=ft.Icons.PLAY_CIRCLE_FILL_ROUNDED,
                        icon_color=current_t["accent"],
                        icon_size=28,
                        tooltip="Play on YouTube",
                        on_click=lambda _, t=row["track_name"], a=row["artists"]: play_song(t, a),
                    ),
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=12),
                bgcolor=current_t["surface"],
                border_radius=14,
                padding=ft.Padding(left=12, top=10, right=12, bottom=10),
                margin=ft.Margin(left=0, top=0, right=0, bottom=8),
                border=ft.Border.all(1, current_t["border"]),
                shadow=ft.BoxShadow(spread_radius=0, blur_radius=6, color="#15000000", offset=ft.Offset(0, 2)),
                animate=ft.Animation(350, ft.AnimationCurve.EASE_OUT_CUBIC),
            )
            song_tiles.append(tile)

        results_header = ft.Row([
            ft.IconButton(
                icon=ft.Icons.ARROW_BACK_ROUNDED,
                icon_color=current_t["accent"],
                tooltip="Back to Selection",
                on_click=lambda _: go_to_inputs()
            ),
            ft.Text("Curated Playlist", size=22, weight=ft.FontWeight.BOLD, color=current_t["text_primary"], font_family="c_grotesk", expand=True),
        ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER)

        results_info_pill = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.TUNE_ROUNDED, color=current_t["accent"], size=16),
                ft.Text(info_str, color=current_t["accent"], size=12, weight=ft.FontWeight.W_500, font_family="grotesk", expand=True),
            ], spacing=8),
            padding=ft.Padding(left=12, top=8, right=12, bottom=8),
            bgcolor=current_t["surface_variant"],
            border_radius=10,
            border=ft.Border.all(1, current_t["border"]),
        )

        results_content = [
            results_header,
            results_info_pill,
            scroll_progress_bar,
        ]

        if message:
            results_content.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.INFO_ROUNDED, color=current_t["accent"], size=18),
                        ft.Text(message, color=current_t["text_primary"], size=12, font_family="grotesk", expand=True),
                    ], spacing=10),
                    padding=12,
                    bgcolor=current_t["surface_variant"],
                    border_radius=12,
                    border=ft.Border.all(1, current_t["accent"]),
                )
            )

        results_content.extend([
            ft.Container(height=4),
            ft.ListView(controls=song_tiles, expand=True, height=480, on_scroll=on_list_scroll, scroll=ft.ScrollMode.HIDDEN),
            ft.Container(height=6),
            ft.Row([
                ft.Button(
                    "Reshuffle Tracks",
                    icon=ft.Icons.REFRESH_ROUNDED,
                    on_click=lambda e: show_results(e, is_random=is_random),
                    style=ft.ButtonStyle(
                        color=current_t["bg"],
                        bgcolor=current_t["accent"],
                        shape=ft.RoundedRectangleBorder(radius=12),
                        padding=ft.Padding(left=22, top=12, right=22, bottom=12),
                    )
                )
            ], alignment=ft.MainAxisAlignment.CENTER)
        ])

        results_view_container = ft.Container(
            content=ft.Column(results_content, spacing=10),
            padding=16,
            clip_behavior=ft.ClipBehavior.NONE,
            expand=True,
        )

        page.clean()
        page.add(results_view_container)

    def go_to_inputs():
        current_view_state["name"] = "input"
        page.clean()
        page.add(input_view_container)

    # --- MAIN INPUT SCREEN RESPONSIVE CONTAINER ---
    input_view = ft.Column([
        header_banner,
        ft.Container(height=4),
        genre_section_label,
        genre_dropdown_container,
        ft.Container(height=4),
        mood_section_label,
        mood_cards_wrapper,
        ft.Container(height=4),
        size_section_header,
        preset_chips_row,
        size_slider,
        ft.Container(height=6),
        action_buttons_wrapper,
    ], scroll=ft.ScrollMode.HIDDEN, spacing=10)

    input_view_container = ft.Container(
        content=input_view,
        padding=0,
        alignment=ft.Alignment.TOP_CENTER,
        clip_behavior=ft.ClipBehavior.NONE,
        expand=True,
    )

    # Add initial input view to page
    page.add(input_view_container)

ft.run(main)
