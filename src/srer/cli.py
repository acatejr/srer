import typer
import os, csv, json
from dotenv import load_dotenv
import requests
import logging
from bs4 import BeautifulSoup
from PIL import Image

load_dotenv()

cli = typer.Typer()

# Set up logging at module level
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

DEST_OUTPUT_DIR = "data/srer/photos"
PHOTO_STATIONS_CSV = "data/srer/photo_station_list.csv"
PHOTO_STATION_BASE_URL = "https://santarita.arizona.edu/photos"
METADATA_OUTPUT_FILE = "data/srer/repeat_photography_metadata.json"


def read_photo_stations():
    """Read the photo stations list from the CSV file.

    Raises:
        FileNotFoundError: If the CSV file does not exist.

    Returns:
        _type_: List of photo stations.
    """

    if not os.path.exists(PHOTO_STATIONS_CSV):
        raise FileNotFoundError(f"Photo stations file not found: {PHOTO_STATIONS_CSV}")

    stations = None
    with open(PHOTO_STATIONS_CSV, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        stations = [row for row in reader]

    return stations


def create_output_dir():
    if not os.path.exists(DEST_OUTPUT_DIR):
        os.makedirs(DEST_OUTPUT_DIR)


def read_photostation_metadata(resp, station_id):
    """Read and parse the HTML response to extract a photo station's metadata."""

    soup = BeautifulSoup(resp.content, "html.parser")
    articles = soup.find_all("article", {"class": "node--type-station-photo"})

    photo_station_metadata_list = []

    if articles:
        for article in articles:
            header = article.find("header")
            if header:
                header_text = header.text.strip()
                photo_archive_no = header_text.strip("Photo Archive No. ")

            node_content = article.find("div", {"class": "node__content"})
            if node_content:
                photo_div = node_content.find(
                    "div", {"class": "field--name-field-photo"}
                )

            photo_span = (
                node_content.find("span", {"class": "file"}) if photo_div else None
            )

            photo_anchor = photo_span.find("a") if photo_span else None
            photo_href = photo_anchor["href"] if photo_anchor else "No link found"
            summary = node_content.find(
                "div", {"class": "field--type-text-with-summary"}
            )
            summary_text = summary.text.strip() if summary else "No summary found"
            direction_div = node_content.find(
                "div", {"class": "field--name-field-direction"}
            )
            direction = (
                direction_div.find("div", {"class": "field__item"}).text.strip()
                if direction_div
                else "No direction found"
            )

            photo_metadata = {
                "station_id": station_id,
                "photo_archive_no": photo_archive_no,
                "photo_href": f"https://santarita.arizona.edu{photo_href}",
                "summary_text": summary_text,
                "direction": direction,
            }

            photo_station_metadata_list.append(photo_metadata)

    return photo_station_metadata_list


@cli.command()
def greet(name: str):
    """Greet a person by name."""
    create_output_dir()
    typer.echo(f"Hello, {name}!")


@cli.command()
def collect_photostation_metadata():
    """Read the list of photo stations and iterate over the list and read/create the
    metadata for each station."""

    create_output_dir()
    stations = read_photo_stations()

    metadata = []

    for station in stations:
        station_id = station.get("stationid")
        url = f"{PHOTO_STATION_BASE_URL}/{station_id}"

        response = requests.get(url)

        if response.status_code != 200:
            logger.error(
                f"Failed to fetch metadata for station {station_id}: "
                f"HTTP {response.status_code} from {url}"
            )
            continue
        else:
            logger.info(f"Successfully fetched metadata for station {station_id}")
            station_metadata = read_photostation_metadata(response, station_id)

            if station_metadata:
                metadata.extend(station_metadata)

    if metadata:
        with open(METADATA_OUTPUT_FILE, "w", encoding="utf-8") as out_file:
            json.dump(metadata, out_file, indent=4)


@cli.command()
def download_srer_photos():
    """Download the photo station photos using station info in the metadata file."""

    with open(METADATA_OUTPUT_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)

        if metadata:
            for rec in metadata:
                station_id = rec.get("station_id")
                photo_href = rec.get("photo_href")

                photo_dir = f"{DEST_OUTPUT_DIR}/{station_id}"
                if not os.path.exists(photo_dir):
                    os.makedirs(photo_dir)

                if not photo_href or "No link found" in photo_href:
                    photo_href = ""
                else:
                    filename = photo_href.split("/")[-1]
                    output_path = f"{photo_dir}/{filename}"
                    response = requests.get(photo_href)
                    with open(output_path, "wb") as img_file:
                        img_file.write(response.content)


@cli.command()
def tif_to_jpg():
    """Convert all repeat photography .tif images in the DEST_OUTPUT_DIR to .jpg format."""

    with open(METADATA_OUTPUT_FILE, "r") as f:
        metadata = json.load(f)

        if metadata:
            for rec in metadata:
                station_id = rec.get("station_id")
                photo_dir = f"{DEST_OUTPUT_DIR}/{station_id}"
                photo_file = rec.get("photo_href").split("/")[-1]
                photo_path = f"{photo_dir}/{photo_file}"

                if os.path.exists(photo_path):
                    if photo_path.lower().endswith(
                        ".tif"
                    ) or photo_path.lower().endswith(".tiff"):
                        print(f"TIFF image found: {photo_path}")
                        jpg_filename = f"{DEST_OUTPUT_DIR}/{station_id}/{os.path.splitext(photo_file)[0]}.jpg"
                        with Image.open(photo_path) as img:
                            rgb_img = img.convert("RGB")
                            rgb_img.save(jpg_filename, "JPEG")


@cli.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand is None:
        typer.echo("Welcome to the CLI application! Use --help for more information.")


if __name__ == "__main__":
    cli()
