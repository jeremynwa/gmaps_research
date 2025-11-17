"""JSON export functionality."""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
import pandas as pd

from config.settings import Config


class JSONExporter:
    """Export analysis results to JSON."""
    
    @staticmethod
    def export(
        df: pd.DataFrame,
        output_path: Optional[Path] = None,
        include_timestamp: bool = True,
        pretty: bool = True
    ) -> Path:
        """
        Export results to JSON.
        
        Args:
            df: DataFrame with analysis results
            output_path: Output file path (generates if None)
            include_timestamp: Add timestamp to filename
            pretty: Pretty-print JSON
            
        Returns:
            Path to created JSON file
        """
        # Generate filename if not provided
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') if include_timestamp else ''
            filename = f"ReviewInsight_Analysis_{timestamp}.json" if timestamp else "ReviewInsight_Analysis.json"
            output_path = Config.OUTPUT_DIR / filename
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"\n💾 Exporting to JSON...")
        print(f"   File: {output_path.name}")
        
        # Convert DataFrame to dict
        data = df.to_dict('records')
        
        # Write JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                json.dump(data, f, ensure_ascii=False)
        
        print(f"   ✅ Export successful")
        print(f"   • Records: {len(data)}")
        
        return output_path