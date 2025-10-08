import typer
import requests
from bs4 import BeautifulSoup
import csv
import json
import os
from pathlib import Path

from .image_similarity import ImageSimilarityFinder
from .description_generator import DescriptionGenerator

cli = typer.Typer()

DEST_OUTPUT_DIR = "data/srer/photos"

def create_output_dir():
    if not os.path.exists(DEST_OUTPUT_DIR):
      os.makedirs(DEST_OUTPUT_DIR)

create_output_dir()

@cli.command()
def health() -> None:
    """Health check command."""

    typer.echo("ok")

@cli.command()
def download_repeat_photo_images():
    """Download Repeat Photography images based on metadata file."""

    with open('repeat_photography_metadata.json', 'r', encoding='utf-8') as f:
        photo_metadata_list = json.load(f)
        for photo_metadata in photo_metadata_list:
            station_id = photo_metadata.get("station_id")
            photo_archive_no = photo_metadata.get("photo_archive_no")
            photo_href = photo_metadata.get("photo_href")
            summary_text = photo_metadata.get("summary_text")
            direction = photo_metadata.get("direction")

            photo_dir = f"{DEST_OUTPUT_DIR}/{station_id}"
            if not os.path.exists(photo_dir):
                os.makedirs(photo_dir)

            if not photo_href or 'No link found' in photo_href:
                typer.echo(f"No valid photo link for station {station_id}, archive no {photo_archive_no}. Skipping.")
                continue

            output_path = f"{photo_dir}/{photo_href.split('/')[-1]}"
            response = requests.get(photo_href)
            if response.status_code == 200:
                try:
                    with open(output_path, 'wb') as img_file:
                        img_file.write(response.content)
                    typer.echo(f"Saved image to {output_path}")
                except Exception as e:
                    pass
            else:
                typer.echo(f"Failed to download image from {photo_href}. Status code: {response.status_code}")




@cli.command()
def download_repeat_photography_metadata() -> None:
    """Download Repeat Photography image metadata."""

    photo_metadata_list = []

    url = "https://santarita.arizona.edu/photos"
    typer.echo(f"Fetching photostation list from {url}...")

    station_list_file = "data/photo_station_list.csv"
    stations = None
    with open(station_list_file, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        stations = [row for row in reader]

    if stations:
        for station in stations:
            station_id = station.get("stationid")
            photo_url = f"{url}/{station_id}"

            response = requests.get(photo_url)

            if response.status_code != 200:
                typer.echo(f"Failed to fetch data for station {station_id}. Status code: {response.status_code}")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('article', {"class": "node--type-station-photo"})

            if not articles:
                typer.echo(f"No images found for station {station_id}.")
                continue


            for article in articles:
                header = article.find('header')
                if header:
                    header_text = header.text.strip()
                    photo_archive_no = header_text.strip("Photo Archive No. ")

                node_content = article.find('div', {"class": "node__content"})
                if node_content:
                    photo_div = node_content.find('div', {"class": "field--name-field-photo"})
                    photo_span = node_content.find('span', {"class": "file"}) if photo_div else None
                    photo_anchor = photo_span.find('a') if photo_span else None
                    photo_href = photo_anchor['href'] if photo_anchor else 'No link found'
                    summary = node_content.find('div', {"class": "field--type-text-with-summary"})
                    summary_text = summary.text.strip() if summary else 'No summary found'
                    direction_div = node_content.find("div", {"class": "field--name-field-direction"})
                    direction = direction_div.find("div", {"class": "field__item"}).text.strip() if direction_div else 'No direction found'

                    photo_metadata = {
                        "station_id": station_id,
                        "photo_archive_no": photo_archive_no,
                        "photo_href": f"https://santarita.arizona.edu{photo_href}",
                        "summary_text": summary_text,
                        "direction": direction
                    }

                    photo_metadata_list.append(photo_metadata)

    typer.echo(f"Downloaded metadata for {len(photo_metadata_list)} photos.")
    with open('repeat_photography_metadata.json', 'w', encoding='utf-8') as f:
        json.dump(photo_metadata_list, f, ensure_ascii=False, indent=4)


@cli.command()
def describe_photo(
    image_path: str = typer.Argument(..., help="Path to the photo to describe"),
    top_k: int = typer.Option(5, "--top-k", "-k", help="Number of similar photos to use"),
    max_distance: int = typer.Option(20, "--max-distance", "-d", help="Maximum similarity distance"),
    use_vision: bool = typer.Option(True, "--vision/--no-vision", help="Use vision API to analyze image"),
    provider: str = typer.Option("anthropic", "--provider", "-p", help="AI provider: 'anthropic' or 'ollama'"),
    ollama_model: str = typer.Option("llama3.2-vision", "--ollama-model", help="Ollama model to use"),
    ollama_host: str = typer.Option(None, "--ollama-host", help="Ollama host URL (e.g., http://localhost:11434)"),
    output: str = typer.Option(None, "--output", "-o", help="Output file path (prints to stdout if not specified)")
) -> None:
    """Generate a description for a new photo based on similar existing photos.

    This command finds similar photos in the SRER archive using perceptual hashing,
    then uses AI (Claude or Ollama) to generate a description in the style of existing photo descriptions.

    For Anthropic provider: Requires ANTHROPIC_API_KEY environment variable to be set.
    For Ollama provider: Requires Ollama to be running locally (default: http://localhost:11434).

    Example:
        srer describe-photo /path/to/new_photo.jpg
        srer describe-photo /path/to/new_photo.jpg --provider ollama
        srer describe-photo /path/to/new_photo.jpg --provider ollama --ollama-model llava
        srer describe-photo /path/to/new_photo.jpg --top-k 10 --no-vision
        srer describe-photo /path/to/new_photo.jpg -o description.txt
    """
    query_path = Path(image_path)

    if not query_path.exists():
        typer.echo(f"Error: Image file not found: {image_path}", err=True)
        raise typer.Exit(1)

    # Validate provider
    if provider not in ["anthropic", "ollama"]:
        typer.echo(f"Error: Unknown provider '{provider}'. Use 'anthropic' or 'ollama'", err=True)
        raise typer.Exit(1)

    # Check for API key if using Anthropic
    api_key = None
    if provider == "anthropic":
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            typer.echo("Error: ANTHROPIC_API_KEY environment variable not set", err=True)
            typer.echo("Please set it with: export ANTHROPIC_API_KEY='your-api-key'", err=True)
            raise typer.Exit(1)

    metadata_path = Path("repeat_photography_metadata.json")
    if not metadata_path.exists():
        typer.echo("Error: repeat_photography_metadata.json not found", err=True)
        typer.echo("Please run: srer download-repeat-photography-metadata", err=True)
        raise typer.Exit(1)

    photo_base_dir = Path(DEST_OUTPUT_DIR)
    if not photo_base_dir.exists():
        typer.echo("Error: Photo directory not found", err=True)
        typer.echo("Please run: srer download-repeat-photo-images", err=True)
        raise typer.Exit(1)

    typer.echo(f"Finding similar photos to {image_path}...")

    # Find similar photos
    finder = ImageSimilarityFinder(metadata_path, photo_base_dir)
    similar_photos = finder.find_similar_photos(query_path, top_k=top_k, max_distance=max_distance)

    if not similar_photos:
        typer.echo("No similar photos found. Try increasing --max-distance", err=True)
        raise typer.Exit(1)

    typer.echo(f"Found {len(similar_photos)} similar photos")
    for i, (entry, distance, local_path) in enumerate(similar_photos, 1):
        typer.echo(f"  {i}. Station {entry['station_id']}, Archive No. {entry['photo_archive_no']} (distance: {distance})")

    descriptions = finder.get_photo_descriptions(similar_photos)

    typer.echo(f"\nGenerating description using {provider}...")

    # Generate description
    generator = DescriptionGenerator(
        provider=provider,
        api_key=api_key,
        ollama_model=ollama_model,
        ollama_host=ollama_host
    )

    if use_vision:
        description = generator.generate_description(query_path, descriptions)
    else:
        description = generator.generate_description_text_only(descriptions)

    # Output result
    if output:
        output_path = Path(output)
        output_path.write_text(description)
        typer.echo(f"\nDescription saved to {output}")
    else:
        typer.echo("\n" + "=" * 80)
        typer.echo("GENERATED DESCRIPTION")
        typer.echo("=" * 80)
        typer.echo(description)
        typer.echo("=" * 80)


if __name__ == "__main__":
    cli()