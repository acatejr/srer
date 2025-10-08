"""Image similarity detection using perceptual hashing."""

import json
from pathlib import Path
from typing import List, Tuple

import imagehash
from PIL import Image


class ImageSimilarityFinder:
    """Find similar images using perceptual hashing."""

    def __init__(self, metadata_path: Path, photo_base_dir: Path):
        """Initialize with paths to metadata and photo directory.

        Args:
            metadata_path: Path to repeat_photography_metadata.json
            photo_base_dir: Path to base directory containing photos (e.g., data/srer/photos)
        """
        self.metadata_path = metadata_path
        self.photo_base_dir = photo_base_dir
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> List[dict]:
        """Load metadata from JSON file."""
        with open(self.metadata_path, "r") as f:
            return json.load(f)

    def _get_local_image_path(self, photo_entry: dict) -> Path | None:
        """Get local filesystem path for a photo entry.

        Args:
            photo_entry: Metadata entry with station_id and photo_href

        Returns:
            Path to local image file, or None if not found
        """
        if not photo_entry.get("photo_href"):
            return None

        station_id = photo_entry["station_id"]
        url = photo_entry["photo_href"]

        # Extract filename from URL
        filename = url.split("/")[-1]

        # Try different extensions since downloaded files might differ
        base_name = filename.rsplit(".", 1)[0]
        possible_extensions = [".TIF", ".tif", ".jpg", ".JPG", ".jpeg", ".JPEG"]

        station_dir = self.photo_base_dir / station_id

        # First try exact filename
        exact_path = station_dir / filename
        if exact_path.exists():
            return exact_path

        # Try with different extensions
        for ext in possible_extensions:
            test_path = station_dir / f"{base_name}{ext}"
            if test_path.exists():
                return test_path

        return None

    def compute_image_hash(
        self, image_path: Path, hash_size: int = 16
    ) -> imagehash.ImageHash:
        """Compute perceptual hash for an image.

        Args:
            image_path: Path to image file
            hash_size: Size of hash (larger = more precise)

        Returns:
            Perceptual hash of the image
        """
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode != "RGB":
                img = img.convert("RGB")
            # Use average hash (faster) or perceptual hash (more accurate)
            return imagehash.phash(img, hash_size=hash_size)

    def find_similar_photos(
        self, query_image_path: Path, top_k: int = 5, max_distance: int = 20
    ) -> List[Tuple[dict, int, Path]]:
        """Find similar photos to the query image.

        Args:
            query_image_path: Path to the query image
            top_k: Number of similar images to return
            max_distance: Maximum hash distance to consider (lower = more similar)

        Returns:
            List of tuples (metadata_entry, distance, local_image_path) sorted by similarity
        """
        query_hash = self.compute_image_hash(query_image_path)

        results = []

        for entry in self.metadata:
            local_path = self._get_local_image_path(entry)

            if local_path is None:
                continue

            try:
                entry_hash = self.compute_image_hash(local_path)
                distance = query_hash - entry_hash  # Hamming distance

                if distance <= max_distance:
                    results.append((entry, distance, local_path))
            except Exception as e:
                # Skip images that can't be processed
                continue

        # Sort by distance (most similar first) and return top k
        results.sort(key=lambda x: x[1])
        return results[:top_k]

    def get_photo_descriptions(
        self, similar_photos: List[Tuple[dict, int, Path]]
    ) -> List[dict]:
        """Extract descriptions from similar photos.

        Args:
            similar_photos: List of tuples from find_similar_photos

        Returns:
            List of dictionaries with description info
        """
        descriptions = []
        for entry, distance, local_path in similar_photos:
            descriptions.append(
                {
                    "station_id": entry["station_id"],
                    "photo_archive_no": entry["photo_archive_no"],
                    "summary_text": entry["summary_text"],
                    "direction": entry["direction"],
                    "similarity_distance": distance,
                    "image_path": str(local_path),
                }
            )
        return descriptions
