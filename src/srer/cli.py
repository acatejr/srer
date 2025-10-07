import typer
import requests
from bs4 import BeautifulSoup
import csv
import json
import os

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

if __name__ == "__main__":
    cli()