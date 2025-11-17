"""Anthropic Claude analyzer with prompt caching."""

import json
import re
from typing import Dict, Optional

import anthropic

from config.settings import Config
from config.prompts import get_prompt
from src.analyzers.base import BaseAnalyzer
from src.utils.normalizer import GareNormalizer


class AnthropicAnalyzer(BaseAnalyzer):
    """Analyze reviews using Anthropic Claude with prompt caching."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize Anthropic analyzer.
        
        Args:
            api_key: Anthropic API key (uses Config.ANTHROPIC_API_KEY if None)
            model: Model name (uses Config.ANTHROPIC_MODEL if None)
        """
        self.client = anthropic.Anthropic(api_key=api_key or Config.ANTHROPIC_API_KEY)
        self.model = model or Config.ANTHROPIC_MODEL
        self.prompt = get_prompt("restaurant")
    
    def analyze_review(
        self,
        establishment: str,
        site: str,
        review_text: str,
        author: str,
        note: int,
        date: str
    ) -> Optional[Dict[str, any]]:
        """Analyze a single review with Claude."""
        
        # Skip empty reviews
        if not review_text or str(review_text).strip() == "" or str(review_text).lower() == "nan":
            return {criterion: "N/A" for criterion in Config.CRITERIA}
        
        # Skip very short reviews
        if len(str(review_text).strip()) < 20:
            return {criterion: "N/A" for criterion in Config.CRITERIA}
        
        # Normalize location name
        gare_name = GareNormalizer.normalize(site)
        
        # Build user message (dynamic part)
        user_content = f"""📋 CONTEXTE:
Établissement: {establishment} | Localisation: {gare_name} | Auteur: {author} | Note: {note}/5 (info seule) | Date: {date}

💬 AVIS: {review_text}"""
        
        try:
            # Call Claude API with prompt caching
            message = self.client.messages.create(
                model=self.model,
                max_tokens=Config.MAX_TOKENS,
                # System prompt with caching
                system=[
                    {
                        "type": "text",
                        "text": self.prompt,
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
            
            # Extract response
            response_text = message.content[0].text.strip()
            
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
            
        except json.JSONDecodeError as e:
            print(f"   ❌ Erreur parsing JSON: {str(e)}")
            return None
        except Exception as e:
            print(f"   ❌ Erreur analyse: {str(e)}")
            return None