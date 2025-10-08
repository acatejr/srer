# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SRER (Santa Rita Experimental Range) is a Python-based CLI tool for downloading and managing repeat photography data from the Santa Rita Experimental Range website (https://santarita.arizona.edu/photos). The project scrapes photographic metadata and images from historical photo stations.

## Technology Stack

- **Python 3.13+**: Primary language
- **uv**: Package manager and dependency management
- **Typer**: CLI framework
- **BeautifulSoup4**: HTML parsing for web scraping
- **Requests**: HTTP client
- **Docker Compose**: PostGIS database for future spatial data integration

## Project Structure

```
srer/
├── src/srer/
│   ├── cli.py              # Main CLI commands and scraping logic
│   └── __init__.py
├── data/
│   ├── photo_station_list.csv           # List of photo station IDs to scrape
│   └── srer/photos/                     # Downloaded images organized by station ID
├── repeat_photography_metadata.json     # Scraped metadata for all photos
├── pyproject.toml                       # Project config and dependencies
└── compose.yml                          # PostGIS database service
```

## CLI Commands

The CLI is built with Typer and available via the `srer` command after installation.

### Running Commands

```bash
# Install dependencies and activate environment
uv sync

# Run commands
uv run srer <command>
```

### Available Commands

- `srer health` - Health check command (returns "ok")
- `srer download-repeat-photography-metadata` - Scrapes photo metadata from the SRER website
  - Reads station IDs from `data/photo_station_list.csv`
  - Scrapes each station's page at `https://santarita.arizona.edu/photos/{station_id}`
  - Extracts photo archive numbers, image URLs, summary text, and direction
  - Outputs to `repeat_photography_metadata.json`
- `srer download-repeat-photo-images` - Downloads images based on metadata
  - Reads from `repeat_photography_metadata.json`
  - Downloads images to `data/srer/photos/{station_id}/`
  - Skips entries with no valid photo links

## Architecture Notes

### Data Flow

1. **Metadata Collection** (`download-repeat-photography-metadata`):
   - Reads station IDs from CSV
   - For each station, scrapes the page looking for `article.node--type-station-photo` elements
   - Extracts structured data from specific HTML classes (field--name-field-photo, field--type-text-with-summary, field--name-field-direction)
   - Stores all metadata in a single JSON file

2. **Image Download** (`download-repeat-photo-images`):
   - Reads metadata JSON
   - Creates station-specific directories
   - Downloads images preserving original filenames from URLs
   - Validates photo URLs before attempting download

### Key Implementation Details

- Output directory (`DEST_OUTPUT_DIR`) is created at module import time
- Web scraping targets specific CSS classes in the SRER website's Drupal structure
- Images are organized by station ID for easy navigation
- Error handling silently continues on download failures
- The CSV station list acts as a whitelist for which stations to process

## Development

### Environment Setup

The project uses `uv` for dependency management and includes a `.python-version` file specifying Python 3.13.

```bash
# Install dependencies
uv sync

# Run a command
uv run srer health
```

### Database

A PostGIS/PostgreSQL database is configured via Docker Compose but not currently integrated into the CLI. Database configuration is in `.env` (not in version control).

```bash
# Start database
docker compose up -d

# Stop database
docker compose down
```
