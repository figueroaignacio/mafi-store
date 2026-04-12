# spite

The job market is broken. Everyone knows it. Nobody fixes it.
This is not a fix. This is automation so you don't have to pretend to enjoy the process.

## What it does

Scrapes job listings, scores them with AI, and filters out the corporate noise.
You still have to do the interviews. Sorry. That part is your problem.

## Stack

- **FastAPI** — because your time is worth something
- **Typer + Rich** — a CLI that looks better than the jobs it finds
- **SQLite** — local, fast, no "cloud-native" nonsense
- **Gemini 1.5 Flash** — AI that won't sugarcoat a bad job posting
- **Playwright** — scraping LinkedIn so you don't have to look at it

## Setup

```bash
# Install uv if you somehow don't have it
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/figueroaignacio/spite.git && cd spite
uv sync
uv run playwright install firefox

# Add your Gemini API key
cp .env.example .env

# Verify it works
uv run spite version
```

## Usage

```bash
spite --help
```

## License

MIT. Do whatever you want with it.
If it breaks, that's on you.
