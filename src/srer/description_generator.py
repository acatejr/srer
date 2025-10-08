"""Generate photo descriptions using Claude AI or Ollama based on similar photos."""

import base64
import os
from pathlib import Path
from typing import List, Literal

from anthropic import Anthropic
import ollama


class DescriptionGenerator:
    """Generate descriptions for new photos based on similar existing photos."""

    def __init__(
        self,
        provider: Literal["anthropic", "ollama"] = "anthropic",
        api_key: str | None = None,
        ollama_model: str = "llama3.2-vision",
        ollama_host: str | None = None
    ):
        """Initialize the description generator.

        Args:
            provider: AI provider to use ("anthropic" or "ollama")
            api_key: Anthropic API key. If None, will read from ANTHROPIC_API_KEY env var
            ollama_model: Ollama model to use (must support vision for image analysis)
            ollama_host: Ollama host URL (e.g., "http://localhost:11434")
        """
        self.provider = provider
        self.ollama_model = ollama_model
        self.ollama_host = ollama_host

        if provider == "anthropic":
            self.client = Anthropic(api_key=api_key)
        elif provider == "ollama":
            # Ollama client is configured via host parameter in API calls
            pass
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _encode_image(self, image_path: Path) -> tuple[str, str]:
        """Encode image to base64 for API.

        Args:
            image_path: Path to image file

        Returns:
            Tuple of (base64_data, media_type)
        """
        with open(image_path, "rb") as f:
            image_data = f.read()

        base64_data = base64.standard_b64encode(image_data).decode("utf-8")

        # Determine media type from extension
        ext = image_path.suffix.lower()
        media_type_map = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
            ".tif": "image/tiff",
            ".tiff": "image/tiff"
        }
        media_type = media_type_map.get(ext, "image/jpeg")

        return base64_data, media_type

    def generate_description(
        self,
        query_image_path: Path,
        similar_descriptions: List[dict],
        max_tokens: int = 1024
    ) -> str:
        """Generate a description for a new photo based on similar photos.

        Args:
            query_image_path: Path to the new photo
            similar_descriptions: List of description dicts from ImageSimilarityFinder.get_photo_descriptions
            max_tokens: Maximum tokens for the generated description

        Returns:
            Generated description text
        """
        # Build context from similar photos
        context_parts = []
        for i, desc in enumerate(similar_descriptions, 1):
            context_parts.append(
                f"Example {i} (Station {desc['station_id']}, Archive No. {desc['photo_archive_no']}, "
                f"Direction {desc['direction']}, Similarity distance: {desc['similarity_distance']}):\n"
                f"{desc['summary_text']}\n"
            )

        context = "\n".join(context_parts)

        # Build prompt
        prompt = f"""You are analyzing a photograph from the Santa Rita Experimental Range (SRER), a long-term ecological research site in Arizona that documents vegetation changes through repeat photography at fixed photo stations.

I have found {len(similar_descriptions)} similar photos from the SRER archive with their descriptions:

{context}

Please analyze the new photo and write a detailed description in the style of the examples above. The description should include:
1. Photo station identification and direction (if determinable)
2. Vegetation types and species present
3. Landscape features and terrain
4. Notable ecological observations
5. Any temporal changes or comparisons (if applicable)

Be specific about plant species, ecological conditions, and landscape features. Use scientific terminology where appropriate. Match the style and level of detail of the example descriptions provided."""

        if self.provider == "anthropic":
            # Encode the query image for Anthropic API
            image_data, media_type = self._encode_image(query_image_path)

            # Call Claude API with vision
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=max_tokens,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_data,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ],
                    }
                ],
            )

            return message.content[0].text

        elif self.provider == "ollama":
            # Call Ollama API with vision
            kwargs = {}
            if self.ollama_host:
                kwargs['host'] = self.ollama_host

            response = ollama.chat(
                model=self.ollama_model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                        'images': [str(query_image_path)]
                    }
                ],
                options={
                    'num_predict': max_tokens
                },
                **kwargs
            )

            return response['message']['content']

    def generate_description_text_only(
        self,
        similar_descriptions: List[dict],
    ) -> str:
        """Generate a description based only on similar photos (no vision API).

        This is a simpler/cheaper approach that doesn't analyze the query image directly.

        Args:
            similar_descriptions: List of description dicts from ImageSimilarityFinder.get_photo_descriptions

        Returns:
            Generated description text
        """
        # Build context from similar photos
        context_parts = []
        for i, desc in enumerate(similar_descriptions, 1):
            context_parts.append(
                f"Photo {i} (Station {desc['station_id']}, Archive No. {desc['photo_archive_no']}, "
                f"Direction {desc['direction']}, Similarity distance: {desc['similarity_distance']}):\n"
                f"{desc['summary_text']}\n"
            )

        context = "\n".join(context_parts)

        prompt = f"""Based on the following {len(similar_descriptions)} similar photos from the Santa Rita Experimental Range, create a concise description that synthesizes the common elements and observations:

{context}

Please write a single paragraph description that captures the typical characteristics of this type of photo, including vegetation, landscape features, and ecological context. Use the style and terminology from the examples."""

        if self.provider == "anthropic":
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=512,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            )

            return message.content[0].text

        elif self.provider == "ollama":
            kwargs = {}
            if self.ollama_host:
                kwargs['host'] = self.ollama_host

            response = ollama.chat(
                model=self.ollama_model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                options={
                    'num_predict': 512
                },
                **kwargs
            )

            return response['message']['content']
