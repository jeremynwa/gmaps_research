"""Configuration settings for ReviewInsight Core."""

import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Global configuration."""
    
    # API Keys
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OUTSCRAPER_API_KEY = os.getenv("OUTSCRAPER_API_KEY")
    
    # Model Configuration
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
    
    # Processing
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "10"))
    CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
    CACHE_DIR = Path(os.getenv("CACHE_DIR", DATA_DIR / "cache"))
    OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", DATA_DIR / "output"))
    
    # Create directories
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Cache files
    CACHE_FILE = CACHE_DIR / "analysis_cache.json"
    BDD_FILE = DATA_DIR / "input" / "BDD_reviews.xlsx"
    
    # Criteria (21 criteria to analyze)
    CRITERIA: List[str] = [
        "offre_profondeur_score", "offre_profondeur_keyword",
        "offre_renouvellement_score", "offre_renouvellement_keyword",
        "offre_clarte_score", "offre_clarte_keyword",
        "offre_fraicheur_score", "offre_fraicheur_keyword",
        "nourriture_qualite_score", "nourriture_qualite_keyword",
        "nourriture_sante_score", "nourriture_sante_keyword",
        "nourriture_quantite_score", "nourriture_quantite_keyword",
        "nourriture_presentation_score", "nourriture_presentation_keyword",
        "prix_niveau_global_score", "prix_niveau_global_keyword",
        "prix_niveau_menus_score", "prix_niveau_menus_keyword",
        "prix_rapport_qualite_score", "prix_rapport_qualite_keyword",
        "prix_promotions_score", "prix_promotions_keyword",
        "rapidite_service_score", "rapidite_service_keyword",
        "atmosphere_entretien_score", "atmosphere_entretien_keyword",
        "atmosphere_confort_score", "atmosphere_confort_keyword",
        "atmosphere_parcours_score", "atmosphere_parcours_keyword",
        "force_vente_score", "force_vente_keyword",
        "hygiene_score", "hygiene_keyword",
        "proprete_vitrine_score", "proprete_vitrine_keyword",
        "nps_score", "nps_keyword",
        "produit_cher_score", "produit_cher_keyword",
    ]
    
    # Cost tracking
    MAX_COST_PER_RUN = float(os.getenv("MAX_COST_PER_RUN", "500"))
    WARN_COST_THRESHOLD = float(os.getenv("WARN_COST_THRESHOLD", "100"))
    
    # Pricing (per million tokens)
    CLAUDE_INPUT_PRICE = 3.0
    CLAUDE_OUTPUT_PRICE = 15.0
    CLAUDE_CACHE_WRITE_MULTIPLIER = 1.25
    CLAUDE_CACHE_READ_MULTIPLIER = 0.10
    OUTSCRAPER_PRICE_PER_1K = 1.50
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required")
        return True


# Validate on import
Config.validate()