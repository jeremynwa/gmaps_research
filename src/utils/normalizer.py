"""Utility for normalizing location names."""

from functools import lru_cache
from typing import Dict


class GareNormalizer:
    """Normalize gare/station names to standard format."""

    # Mapping of variations to standard names
    MAPPINGS: Dict[str, str] = {
        # Paris stations
        "PARIS-GDL": "Paris Gare de Lyon",
        "PARIS-GDN": "Paris Gare du Nord",
        "PARIS-GDE": "Paris Gare de l'Est",
        "PARIS-GSL": "Paris Saint-Lazare",
        "PARIS-GMP": "Paris Montparnasse",
        "PARIS-LA-DEFENSE": "Paris La Défense",

        # Other major stations
        "LYON-PART-DIEU": "Lyon Part-Dieu",
        "LYON-PERRACHE": "Lyon Perrache",
        "MARSEILLE": "Marseille Saint-Charles",
        "LILLE-EUROPE": "Lille Europe",
        "BORDEAUX": "Bordeaux Saint-Jean",
        "TOULOUSE": "Toulouse Matabiau",
        "NICE": "Nice Ville",
        "STRASBOURG": "Strasbourg",
        "NANTES": "Nantes",
        "MONTPELLIER-ST-ROCH": "Montpellier Saint-Roch",
        "ROISSY": "Paris CDG Airport",

        # Add more mappings as needed
    }

    @staticmethod
    @lru_cache(maxsize=256)
    def normalize(gare_name: str) -> str:
        """Normalize a gare name to standard format."""
        if not gare_name or str(gare_name).strip() == "":
            return "Unknown"

        name = str(gare_name).replace("FR ", "").strip()

        if name in GareNormalizer.MAPPINGS:
            return GareNormalizer.MAPPINGS[name]

        parts = name.split()
        if len(parts) > 0:
            station_code = parts[0]
            if station_code in GareNormalizer.MAPPINGS:
                return GareNormalizer.MAPPINGS[station_code]

        return name

    @classmethod
    def add_mapping(cls, code: str, full_name: str) -> None:
        """Add a new mapping."""
        cls.MAPPINGS[code] = full_name
        # Clear the cache since mappings changed
        GareNormalizer.normalize.cache_clear()