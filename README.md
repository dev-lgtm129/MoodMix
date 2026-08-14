<div align="center">
  <img src="assets/icons/appicon.png" width="100" alt="MoodMix icon">
  
  # MoodMix

  *Playlists that match your mood.*

  ![Python](https://img.shields.io/badge/Python-3.11-blue)
  ![License](https://img.shields.io/badge/License-MIT-green)
  ![Framework](https://img.shields.io/badge/UI-Flet-orange)

</div>
A personalized playlist generator that recommends songs based on your preferred language, mood, and genre — built with Python and Flet.

---
## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [How It Works](#how-it-works)
- [Installation](#installation)
- [Usage](#usage)
- [Team](#team)

---

## Overview

MoodMix takes a small set of user preferences and returns a curated playlist from a large song dataset. Instead of scrolling through endless recommendations, users specify what they want — a language, a mood, a genre, and a playlist size — and get a ready-to-listen list in seconds.

---

## Features

- **Language-based filtering** — choose from multiple supported languages
- **Mood-based curation** — playlists are generated using audio feature analysis (valence and energy) mapped to moods like Happy, Sad, Chill, and Intense
- **Genre selection** — narrow results to your preferred genre
- **Adjustable playlist size** — control how many songs you get, from a short list to a full session
- **Clean, minimal interface** — built with Flet for a smooth cross-platform experience

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI | [Flet](https://flet.dev) (Python, built on Flutter) |
| Data Processing | Pandas |
| Dataset | [Spotify Tracks Dataset](https://www.kaggle.com) (Kaggle) |
| Language | Python |

---

## How It Works

1. **Data Layer** — the song dataset is loaded and cleaned, standardizing genre and language fields.
2. **Mood Mapping** — each track is bucketed into a mood category based on its valence and energy values:

   | Mood | Valence | Energy |
   |---|---|---|
   | Happy / Energetic | High | High |
   | Sad | Low | Low |
   | Chill / Relaxed | High | Low |
   | Angry / Intense | Low | High |

3. **Recommendation Engine** — user preferences are matched against the cleaned dataset to filter and return a ranked playlist.
4. **Interface** — the Flet-based UI collects preferences and displays the resulting playlist.

---

## Installation

You need Python installed, along with the project dependencies listed in 
`requirements.txt`.

To install all dependencies at once, run:
```
pip install -r requirements.txt
```
This single command installs everything the project needs — no need to install packages one by one.
## Usage

```bash
python moodmix.py
```

Select your preferred language, mood, genre, and playlist size, then generate your playlist.

---

## Team

| Name | GitHub |
|---|---|
| Devansh Raj Vats | [@dev-lgtm129](https://github.com/dev-lgtm129) | 
| Dhiren Virmani | [@dhirenvirmani](https://github.com/dhirenvirmani) |
| Janhvi Gupta | [@Janhvi-Gupta](https://github.com/Janhvi-Gupta) |
| Aryan Raghav | [@Aryanraghav0330](https://github.com/Aryanraghav0330) |

---

## License

This project is licensed under the MIT License.
