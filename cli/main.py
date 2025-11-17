"""Command-line interface for ReviewInsight Core."""

import click
from pathlib import Path
from rich.console import Console
from rich.table import Table

from config.settings import Config
from src.analyzers.anthropic_analyzer import AnthropicAnalyzer
from src.analyzers.mock_analyzer import MockAnalyzer
from src.scrapers.outscraper_scraper import OutscraperScraper
from src.scrapers.csv_loader import CSVLoader
from src.processors.orchestrator import Orchestrator
from src.exporters.excel_exporter import ExcelExporter
from src.exporters.json_exporter import JSONExporter
from src.utils.cost_calculator import CostCalculator

console = Console()


@click.group()
def cli():
    """ReviewInsight Core - AI-powered review analysis."""
    pass


@cli.command()
@click.option('--input', '-i', required=True, type=click.Path(exists=True), help='Input CSV/Excel file')
@click.option('--output', '-o', type=click.Path(), help='Output directory (default: data/output/)')
@click.option('--workers', '-w', default=10, type=int, help='Number of parallel workers (default: 10)')
@click.option('--mock', is_flag=True, help='Use mock analyzer (no API calls)')
@click.option('--format', type=click.Choice(['excel', 'json', 'both']), default='excel', help='Output format')
def analyze(input, output, workers, mock, format):
    """Analyze reviews from a CSV or Excel file."""
    
    console.print("\n[bold blue]🚀 ReviewInsight Analysis[/bold blue]\n")
    
    # Load reviews
    loader = CSVLoader()
    reviews = loader.scrape(input)
    
    if len(reviews) == 0:
        console.print("[red]❌ No reviews found in file[/red]")
        return
    
    # Estimate cost
    if not mock:
        cost = CostCalculator.estimate_total_cost(len(reviews), include_outscraper=False)
        console.print(f"\n[yellow]💰 Estimated Cost:[/yellow]")
        console.print(f"   Claude API: ${cost.claude_total:.2f}")
        console.print(f"   Total: ${cost.total:.2f}\n")
        
        if not click.confirm("Continue with analysis?"):
            return
    
    # Initialize analyzer
    if mock:
        analyzer = MockAnalyzer()
        console.print("[yellow]⚠️  Using mock analyzer (no API calls)[/yellow]\n")
    else:
        analyzer = AnthropicAnalyzer()
    
    # Run analysis
    orchestrator = Orchestrator(analyzer)
    df_results = orchestrator.analyze(reviews, max_workers=workers)
    
    # Export results
    output_dir = Path(output) if output else Config.OUTPUT_DIR
    
    if format in ['excel', 'both']:
        excel_path = ExcelExporter.export(df_results, output_path=output_dir / "results.xlsx")
        console.print(f"\n[green]✅ Excel saved: {excel_path}[/green]")
    
    if format in ['json', 'both']:
        json_path = JSONExporter.export(df_results, output_path=output_dir / "results.json")
        console.print(f"[green]✅ JSON saved: {json_path}[/green]")


@cli.command()
@click.option('--name', '-n', required=True, help='Restaurant name')
@click.option('--location', '-l', default='', help='Location (e.g., "Paris, France")')
@click.option('--max-reviews', '-m', default=1000, type=int, help='Max reviews to scrape')
@click.option('--competitors', '-c', multiple=True, help='Competitor names (can specify multiple)')
@click.option('--output', '-o', type=click.Path(), help='Output directory')
@click.option('--workers', '-w', default=10, type=int, help='Number of parallel workers')
@click.option('--analyze-now', is_flag=True, help='Analyze immediately after scraping')
def scrape(name, location, max_reviews, competitors, output, workers, analyze_now):
    """Scrape Google Maps reviews and optionally analyze them."""
    
    console.print("\n[bold blue]🗺️  Google Maps Scraping[/bold blue]\n")
    
    # Initialize scraper
    scraper = OutscraperScraper()
    
    # Scrape main restaurant
    queries = [name] + list(competitors)
    
    # Estimate scraping cost
    total_reviews = len(queries) * max_reviews
    scraping_cost = CostCalculator.estimate_outscraper_cost(total_reviews)
    
    console.print(f"[yellow]📊 Scraping Plan:[/yellow]")
    console.print(f"   Main: {name}")
    if competitors:
        console.print(f"   Competitors: {len(competitors)}")
    console.print(f"   Max reviews per location: {max_reviews}")
    console.print(f"   Estimated cost: ${scraping_cost:.2f}\n")
    
    if not click.confirm("Continue with scraping?"):
        return
    
    # Scrape
    results = scraper.scrape_multiple(
        queries=queries,
        location=location,
        max_reviews_per_query=max_reviews
    )
    
    # Combine all reviews
    all_reviews = []
    for query, reviews in results.items():
        all_reviews.extend(reviews)
    
    console.print(f"\n[green]✅ Total reviews scraped: {len(all_reviews)}[/green]")
    
    # Save scraped data
    import pandas as pd
    df_scraped = pd.DataFrame(all_reviews)
    
    output_dir = Path(output) if output else Config.OUTPUT_DIR
    scraped_file = output_dir / "scraped_reviews.xlsx"
    df_scraped.to_excel(scraped_file, index=False)
    
    console.print(f"[green]💾 Scraped data saved: {scraped_file}[/green]")
    
    # Analyze if requested
    if analyze_now:
        console.print("\n[bold blue]🤖 Starting Analysis...[/bold blue]\n")
        
        # Estimate analysis cost
        cost = CostCalculator.estimate_total_cost(len(all_reviews), include_outscraper=False)
        console.print(f"[yellow]💰 Analysis Cost:[/yellow]")
        console.print(f"   Claude API: ${cost.claude_total:.2f}\n")
        
        if not click.confirm("Continue with analysis?"):
            return
        
        analyzer = AnthropicAnalyzer()
        orchestrator = Orchestrator(analyzer)
        df_results = orchestrator.analyze(all_reviews, max_workers=workers)
        
        # Export
        excel_path = ExcelExporter.export(df_results, output_path=output_dir / "analysis_results.xlsx")
        console.print(f"\n[green]✅ Analysis saved: {excel_path}[/green]")


@cli.command()
@click.option('--reviews', '-r', required=True, type=int, help='Number of reviews')
@click.option('--scraping', is_flag=True, help='Include scraping costs')
def estimate(reviews, scraping):
    """Estimate costs for an analysis."""
    
    console.print("\n[bold blue]💰 Cost Estimation[/bold blue]\n")
    
    cost = CostCalculator.estimate_total_cost(reviews, include_outscraper=scraping)
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Item", style="cyan")
    table.add_column("Cost (USD)", justify="right", style="green")
    
    if scraping:
        table.add_row("Outscraper (scraping)", f"${cost.outscraper_cost:.2f}")
    
    table.add_row("Claude API (input)", f"${cost.claude_input_cost:.2f}")
    table.add_row("Claude API (output)", f"${cost.claude_output_cost:.2f}")
    table.add_row("Claude API (cache write)", f"${cost.claude_cache_write_cost:.2f}")
    table.add_row("Claude API (cache read)", f"${cost.claude_cache_read_cost:.2f}")
    table.add_row("[bold]TOTAL[/bold]", f"[bold]${cost.total:.2f}[/bold]")
    
    console.print(table)
    console.print(f"\n[dim]Note: Costs assume 98% cache hit rate after first review[/dim]")


@cli.command()
def config():
    """Show current configuration."""
    
    console.print("\n[bold blue]⚙️  Configuration[/bold blue]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("Anthropic Model", Config.ANTHROPIC_MODEL)
    table.add_row("Max Tokens", str(Config.MAX_TOKENS))
    table.add_row("Max Workers", str(Config.MAX_WORKERS))
    table.add_row("Cache Enabled", str(Config.CACHE_ENABLED))
    table.add_row("Output Directory", str(Config.OUTPUT_DIR))
    table.add_row("Cache Directory", str(Config.CACHE_DIR))
    
    console.print(table)


if __name__ == '__main__':
    cli()