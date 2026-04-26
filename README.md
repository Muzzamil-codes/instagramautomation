# Instagram Automation

Automates the full workflow of creating and publishing shower-thought-style Instagram Reels:
- pulls trending shower thoughts from Reddit,
- generates tags and a related GIF using CrewAI + Gemini,
- lets Discord collaborators optionally override the GIF,
- renders a video reel,
- publishes it through the Instagram Graph API,
- and updates post-performance metrics in CSV.

## Project Workflow

The main flow runs these scripts in sequence:

1. **`data.py`**  
   Refreshes insights/engagement metrics for posts in `instagram_posts.csv`.
2. **`main.py`**  
   Pulls/chooses a shower thought, generates tags, finds a GIF, and writes output to `showerthought.json`.
3. **`reelmaker.py`**  
   Builds `final_video.mp4`, uploads it as a Reel via Instagram Graph API, appends post info to CSV, and sends Discord webhook updates.

Orchestrators:
- **`runthrough.py`**: Linux-style fixed-path runner.
- **`runthrough2.py`**: Windows local-path runner.

## Tech Stack

- Python
- CrewAI + Gemini model integration
- Discord bot (`discord.py`)
- PIL + MoviePy for media rendering
- Instagram Graph API
- Ngrok (temporary public video URL for upload)

## Requirements

- Python 3.10+ (recommended)
- FFmpeg (required by MoviePy)
- An Instagram Business/Creator account connected to Meta Graph API
- Reddit app credentials
- Discord bot token + channel access
- Ngrok available in your environment

Python dependencies are listed in `requirements.txt`.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables

Create a `.env` file in the project root with:

```env
# Reddit
REDDIT_ID=your_reddit_client_id
REDDIT_SECRET_KEY=your_reddit_secret

# Instagram / Meta Graph
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
IG_BUSINESS_ACCOUNT_ID=your_ig_business_account_id

# Discord bot + notifications
DISCORD_BOT_TOKEN=your_discord_bot_token
TARGET_CHANNEL_ID=your_target_channel_id
DISCORD_WEBHOOK_TOKEN=your_discord_webhook_url

# Optional if you move LLM key to env (recommended)
GOOGLE_API_KEY=your_google_api_key
```

## How to Run

### Option 1: Run end-to-end manually

```bash
python data.py
python main.py
python reelmaker.py
```

### Option 2: Use a runner script

Use and adjust one of:
- `runthrough.py` (Linux server path assumptions)
- `runthrough2.py` (Windows path assumptions)

## Output Files

- `showerthoughts.json` — cached Reddit posts pool
- `showerthought.json` — selected thought + generated tags
- `gif.gif` — selected/downloaded GIF
- `twitter_post.png`, `bgimage.png` — intermediate assets
- `final_video.mp4` — generated Reel
- `instagram_posts.csv` — post history + performance metrics

## Notes

- Keep API tokens in `.env`; avoid hardcoding credentials in source files.
- The workflow assumes several local assets exist (`Roboto-Regular.ttf`, `topface.png`, `bgmusic (1).mp3`, etc.).
- If publishing fails, verify token validity, Instagram account permissions, and ngrok tunnel availability.
