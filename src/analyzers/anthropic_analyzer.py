"""Anthropic Claude analyzer with prompt caching."""

import json
import logging
import re
from typing import Any, Dict, Optional

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from config.settings import Config
from config.prompts import get_prompt
from src.analyzers.base import BaseAnalyzer
from src.utils.normalizer import GareNormalizer

logger = logging.getLogger(__name__)


class AnthropicAnalyzer(BaseAnalyzer):
    """Analyze reviews using Anthropic Claude with prompt caching."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Anthropic analyzer.

        Args:
            api_key: Anthropic API key (uses Config.ANTHROPIC_API_KEY if None)
            model: Model name (uses Config.ANTHROPIC_MODEL if None)
        """
        Config.validate()
        self.client = anthropic.Anthropic(api_key=api_key or Config.ANTHROPIC_API_KEY)
        self.model = model or Config.ANTHROPIC_MODEL
        self.prompt = get_prompt("restaurant")

    def _parse_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from Claude's response text.

        Args:
            response_text: Raw response text from the API

        Returns:
            Parsed dictionary or None if parsing fails
        """
        # Clean double braces (Claude sometimes copies example format)
        response_text = response_text.replace('{{', '{').replace('}}', '}')

        # Parse JSON
        start = response_text.find('{')
        end = response_text.rfind('}')

        if start != -1 and end != -1:
            json_str = response_text[start:end+1]
            result = json.loads(json_str)
        else:
            # Fallback: clean markdown
            cleaned = re.sub(r'```json\s*', '', response_text)
            cleaned = re.sub(r'```\s*', '', cleaned).strip()
            cleaned = cleaned.replace('{{', '{').replace('}}', '}')
            result = json.loads(cleaned)

        # Validate result
        if not isinstance(result, dict):
            return None

        # Ensure all criteria are present
        for criterion in Config.CRITERIA:
            if criterion not in result:
                result[criterion] = "N/A"
            elif result[criterion] is None or result[criterion] == "" or str(result[criterion]).strip() == "":
                result[criterion] = "N/A"

        return result

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((anthropic.RateLimitError, anthropic.InternalServerError, anthropic.APIConnectionError)),
    )
    def _call_api(self, system_prompt, user_content):
        """Call the Anthropic API with retry logic.

        Args:
            system_prompt: The system prompt text
            user_content: The user message content

        Returns:
            The API message response
        """
        return self.client.messages.create(
            model=self.model,
            max_tokens=Config.MAX_TOKENS,
            timeout=60.0,
            # System prompt with caching
            system=[
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            # Dynamic user message
            messages=[
                {
                    "role": "user",
                    "content": user_content
                }
            ]
        )

    def _analyze_review_impl(
        self,
        establishment: str,
        site: str,
        review_text: str,
        author: str,
        note: int,
        date: str
    ) -> Optional[Dict[str, Any]]:
        """Analyze a single review with Claude."""

        # Normalize location name
        gare_name = GareNormalizer.normalize(site)

        # Build user message (dynamic part)
        user_content = f"""📋 CONTEXTE:
Établissement: {establishment} | Localisation: {gare_name} | Auteur: {author} | Note: {note}/5 (info seule) | Date: {date}

💬 AVIS: {review_text}"""

        try:
            # Call Claude API with prompt caching and retry
            message = self._call_api(self.prompt, user_content)

            # Extract response
            response_text = message.content[0].text.strip()

            return self._parse_response(response_text)

        except json.JSONDecodeError as e:
            logger.error("JSON parsing error: %s", e)
            return None
        except anthropic.APIError as e:
            logger.error("Anthropic API error: %s", e)
            return None
