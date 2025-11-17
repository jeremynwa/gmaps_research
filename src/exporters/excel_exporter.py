"""Excel export functionality."""

from datetime import datetime
from pathlib import Path
from typing import Optional
import pandas as pd

from config.settings import Config


class ExcelExporter:
    """Export analysis results to Excel."""
    
    @staticmethod
    def export(
        df: pd.DataFrame,
        output_path: Optional[Path] = None,
        include_timestamp: bool = True,
        sort_empty_last: bool = True
    ) -> Path:
        """
        Export results to Excel with two sheets (Scores + Keywords).
        
        Args:
            df: DataFrame with analysis results
            output_path: Output file path (generates if None)
            include_timestamp: Add timestamp to filename
            sort_empty_last: Put empty reviews at bottom
            
        Returns:
            Path to created Excel file
        """
        # Generate filename if not provided
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S') if include_timestamp else ''
            filename = f"ReviewInsight_Analysis_{timestamp}.xlsx" if timestamp else "ReviewInsight_Analysis.xlsx"
            output_path = Config.OUTPUT_DIR / filename
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"\n💾 Exporting to Excel...")
        print(f"   File: {output_path.name}")
        
        # Sort: valid reviews first, empty reviews last
        if sort_empty_last:
            df_sorted = df.copy()
            df_sorted['_has_text'] = df_sorted['Avis'].apply(
                lambda x: 0 if (pd.isna(x) or str(x).strip() == "" or len(str(x).strip()) < 20) else 1
            )
            df_sorted = df_sorted.sort_values('_has_text', ascending=False)
            df_sorted = df_sorted.drop(columns=['_has_text'])
            df_sorted = df_sorted.reset_index(drop=True)
        else:
            df_sorted = df
        
        # Separate info columns and criterion columns
        info_columns = [col for col in df_sorted.columns if col not in Config.CRITERIA]
        score_columns = [col for col in Config.CRITERIA if '_score' in col]
        keyword_columns = [col for col in Config.CRITERIA if '_keyword' in col]
        
        # Create two DataFrames
        df_scores = df_sorted[info_columns + score_columns].copy()
        df_keywords = df_sorted[info_columns + keyword_columns].copy()
        
        # Replace NaN with "N/A"
        df_scores[score_columns] = df_scores[score_columns].fillna("N/A")
        df_keywords[keyword_columns] = df_keywords[keyword_columns].fillna("N/A")
        
        # Write to Excel with two sheets
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df_scores.to_excel(writer, sheet_name='Scores', index=False)
            df_keywords.to_excel(writer, sheet_name='Keywords', index=False)
        
        print(f"   ✅ Export successful")
        print(f"\n📋 SUMMARY:")
        print(f"   • Rows: {len(df_sorted)}")
        print(f"   • Columns: {len(df_sorted.columns)}")
        print(f"   • Sheets: Scores ({len(df_scores.columns)} cols), Keywords ({len(df_keywords.columns)} cols)")
        
        # Calculate some stats
        for criterion in ['nourriture_qualite_score', 'rapidite_service_score', 'prix_rapport_qualite_score']:
            if criterion in df_sorted.columns:
                numeric_values = pd.to_numeric(df_sorted[criterion], errors='coerce')
                valid_count = numeric_values.notna().sum()
                if valid_count > 0:
                    mean_score = numeric_values.mean()
                    print(f"   • {criterion}: {mean_score:.1f}/100 (n={valid_count})")
        
        return output_path