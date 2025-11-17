"""Utility for normalizing location names."""

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
    
    @classmethod
    def normalize(cls, gare_name: str) -> str:
        """
        Normalize a gare name to standard format.
        
        Args:
            gare_name: Raw gare name (e.g., "FR PARIS-GDL")
            
        Returns:
            Normalized name (e.g., "Paris Gare de Lyon")
        """
        if not gare_name or str(gare_name).strip() == "":
            return "Unknown"
        
        # Remove country prefix
        name = str(gare_name).replace("FR ", "").strip()
        
        # Check if we have a direct mapping
        if name in cls.MAPPINGS:
            return cls.MAPPINGS[name]
        
        # Try to extract the main station name
        # e.g., "PARIS-GDL MCDO" -> "PARIS-GDL"
        parts = name.split()
        if len(parts) > 0:
            station_code = parts[0]
            if station_code in cls.MAPPINGS:
                return cls.MAPPINGS[station_code]
        
        # Return as-is if no mapping found
        return name
    
    @classmethod
    def add_mapping(cls, code: str, full_name: str):
        """Add a new mapping."""
        cls.MAPPINGS[code] = full_name