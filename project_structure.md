# Market Research App - Project Structure

## Overview
An application that performs automated market research by:
1. Accepting natural language queries (e.g., "analyze Starbucks in Paris for price perception and cleanliness")
2. Extracting locations and reviews from Google Maps
3. Analyzing reviews with Anthropic AI
4. Presenting results in an interactive web app

## High-Level Architecture

```
┌─────────────────┐
│   User Input    │  "Analyze Starbucks in Paris for price & cleanliness"
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Query Parser    │  Extract: business_type, location, analysis_dimensions
│   (Claude AI)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Collector │  Search & fetch from Google Maps API
│  (Google Maps)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Review Analyzer │  Analyze reviews based on specified dimensions
│  (Claude AI)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Report Builder  │  Aggregate results, generate insights
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Web Frontend  │  Interactive dashboard with visualizations
└─────────────────┘
```

## Recommended Tech Stack

### Backend
- **Framework**: FastAPI (async, fast, great API docs)
- **Database**: PostgreSQL + SQLAlchemy (store searches, cache results)
- **Task Queue**: Celery + Redis (handle long-running searches)
- **Cache**: Redis (API response caching)

### Frontend
- **Framework**: React or Next.js
- **UI Library**: Shadcn/ui, Tailwind CSS
- **Charts**: Recharts or Chart.js
- **State Management**: React Query (for API calls)

### APIs
- **Google Maps API** (Places, Geocoding, Place Details)
- **Anthropic Claude API** (query parsing, review analysis)

## Project Structure

```
market-research-app/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                    # FastAPI app entry point
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes/
│   │   │   │   ├── search.py          # POST /api/search
│   │   │   │   ├── reports.py         # GET /api/reports/{id}
│   │   │   │   └── status.py          # GET /api/status/{task_id}
│   │   │
│   │   ├── core/
│   │   │   ├── config.py              # Settings, API keys
│   │   │   ├── database.py            # DB connection
│   │   │   └── cache.py               # Redis cache
│   │   │
│   │   ├── services/
│   │   │   ├── query_parser.py        # Parse natural language → structured query
│   │   │   ├── gmaps_service.py       # Google Maps API wrapper
│   │   │   ├── review_analyzer.py     # Claude AI review analysis
│   │   │   └── report_generator.py    # Aggregate & generate insights
│   │   │
│   │   ├── models/
│   │   │   ├── search.py              # Search request/result models
│   │   │   ├── location.py            # Location data models
│   │   │   └── analysis.py            # Analysis result models
│   │   │
│   │   ├── schemas/
│   │   │   ├── search_request.py      # Pydantic schemas for API
│   │   │   └── report_response.py
│   │   │
│   │   ├── tasks/
│   │   │   └── search_task.py         # Celery background tasks
│   │   │
│   │   └── utils/
│   │       ├── validators.py
│   │       └── helpers.py
│   │
│   ├── migrations/                     # Alembic migrations
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx               # Home page with search
│   │   │   └── reports/
│   │   │       └── [id]/
│   │   │           └── page.tsx       # Report detail page
│   │   │
│   │   ├── components/
│   │   │   ├── SearchForm.tsx         # Natural language search input
│   │   │   ├── LoadingState.tsx       # Progress indicator
│   │   │   ├── ReportDashboard.tsx    # Main report view
│   │   │   ├── LocationMap.tsx        # Map with pins
│   │   │   ├── MetricsGrid.tsx        # Key metrics cards
│   │   │   ├── ReviewsTable.tsx       # Analyzed reviews
│   │   │   ├── ChartsSection.tsx      # Visualizations
│   │   │   └── InsightsSummary.tsx    # AI-generated insights
│   │   │
│   │   ├── lib/
│   │   │   ├── api.ts                 # API client
│   │   │   └── types.ts               # TypeScript types
│   │   │
│   │   └── hooks/
│   │       ├── useSearch.ts
│   │       └── useReport.ts
│   │
│   ├── public/
│   ├── package.json
│   └── next.config.js
│
├── docker-compose.yml                  # Redis, PostgreSQL, app services
├── .gitignore
└── README.md
```

## Data Flow in Detail

### 1. Query Parsing Phase

**Input Examples**: 
- "Analyze Starbucks in Paris for price perception and cleanliness"
- "Find all Italian restaurants in Manhattan under $30 with rating above 4.0 and analyze their service quality"
- "Show me mid-range coffee shops in London and analyze their ambiance"

**Process**:
```python
# Use Claude to parse the query into structured data
{
    "search_mode": "specific_brand",  # or "category", "mixed"
    "business_name": "Starbucks",  # if specific brand
    "business_category": null,  # e.g., "italian restaurant", "coffee shop", "bakery"
    "location": {
        "city": "Paris",
        "neighborhood": null,  # optional: "Manhattan", "Marais"
        "country": "France",
        "radius_km": 5
    },
    "filters": {
        "price_level": null,  # 1-4 ($ to $$$$) or range [2,3]
        "min_rating": null,  # e.g., 4.0
        "max_rating": null,  # e.g., 4.5
        "open_now": false,
        "min_reviews": null  # e.g., 50 (only places with enough data)
    },
    "analysis_dimensions": [
        "price_perception",
        "cleanliness"
    ],
    "competitor_analysis": false,  # compare similar businesses
    "max_locations": 20  # configurable
}
```

**Claude Prompt Structure**:
```
Parse this market research query into structured JSON:
"{user_query}"

Extract:
1. SEARCH MODE:
   - "specific_brand": User wants a specific business (Starbucks, McDonald's)
   - "category": User wants a type of business (Italian restaurants, coffee shops)
   - "mixed": Both category with optional specific brands to include/exclude

2. BUSINESS IDENTIFICATION:
   - business_name: Specific brand name (null if category search)
   - business_category: Type of business (null if specific brand)
   - Examples: "italian restaurant", "coffee shop", "bakery", "fast food"

3. LOCATION:
   - city: Main city name
   - neighborhood: Optional specific area
   - country: Country name
   - radius_km: Search radius (default 5, extract if mentioned)

4. FILTERS:
   - price_level: Extract from terms like "cheap", "affordable", "mid-range", "expensive", "luxury"
     * "cheap/budget" → 1
     * "affordable/moderate" → 2
     * "mid-range/upscale" → 3
     * "expensive/luxury/fine dining" → 4
     * Can be a range: [2,3] for "affordable to mid-range"
   - min_rating: Extract from "above 4.0", "at least 4 stars", "highly rated" (4.0+)
   - max_rating: Extract from "below 4.5", "not too popular"
   - open_now: true if mentioned "open now", "currently open"
   - min_reviews: Extract from "well-reviewed", "popular" (e.g., 50+)

5. ANALYSIS DIMENSIONS:
   - Extract aspects to analyze: food quality, service, cleanliness, ambiance, etc.
   - If not specified, default to: ["overall_experience", "value", "service_quality"]

6. COMPETITOR ANALYSIS:
   - true if query mentions "compare", "vs", "versus", "competition"

7. MAX LOCATIONS:
   - Extract if specified, otherwise default to 20

Return only valid JSON.
```

### 2. Data Collection Phase

**Process**:
```
Step 1: Build Google Maps Query
   - If specific_brand: "{business_name} in {location}"
   - If category: "{business_category} in {location}"
   
Step 2: Execute Places API Search with Filters
   - Query: Built from Step 1
   - Type: Map category to Google Places types
     * "italian restaurant" → type=restaurant + keyword=italian
     * "coffee shop" → type=cafe
     * "bakery" → type=bakery
   - Filters applied:
     * min_price / max_price (price_level: 0-4)
     * rating filter (client-side, API doesn't support min_rating directly)
   
Step 3: Filter & Sort Results
   - Apply rating filters (min_rating, max_rating)
   - Apply review count filter (min_reviews)
   - Remove duplicates
   - Sort by relevance or rating
   - Take top N (max_locations)
   
Step 4: Get Place Details for Each Location
   - Extract: name, address, coordinates, rating, price_level, reviews
   - Get up to 5 reviews per location (API limit)
   
Step 5: Cache Results
   - Store in Redis (fast access) and PostgreSQL (persistence)
   - Cache key: hash of search parameters
   - TTL: 7 days (reviews don't change often, but new places open)
```

**Google Maps API Mapping**:
```python
CATEGORY_TYPE_MAPPING = {
    # Restaurants
    "restaurant": "restaurant",
    "italian restaurant": ("restaurant", "italian"),
    "french restaurant": ("restaurant", "french"),
    "chinese restaurant": ("restaurant", "chinese"),
    "mexican restaurant": ("restaurant", "mexican"),
    "fast food": ("restaurant", "fast food"),
    "fine dining": ("restaurant", "fine dining"),
    
    # Cafes & Bakeries
    "coffee shop": "cafe",
    "cafe": "cafe",
    "bakery": "bakery",
    "patisserie": "bakery",
    
    # Bars & Nightlife
    "bar": "bar",
    "pub": "bar",
    "wine bar": ("bar", "wine"),
    "cocktail bar": ("bar", "cocktail"),
    
    # Retail
    "grocery store": "grocery_or_supermarket",
    "convenience store": "convenience_store",
    "clothing store": "clothing_store",
    "bookstore": "book_store",
    
    # Services
    "gym": "gym",
    "hair salon": "hair_care",
    "spa": "spa"
}

PRICE_LEVEL_MAPPING = {
    1: "$",      # Inexpensive (< $10 per person)
    2: "$$",     # Moderate ($10-25)
    3: "$$$",    # Expensive ($25-50)
    4: "$$$$"    # Very Expensive (> $50)
}
```

**Example Searches**:

**Query 1**: "Italian restaurants in Manhattan under $30 with rating above 4.0"
```python
# Parsed
{
    "search_mode": "category",
    "business_category": "italian restaurant",
    "location": {"city": "Manhattan", "radius_km": 5},
    "filters": {
        "price_level": [1, 2],  # $ to $$
        "min_rating": 4.0
    }
}

# Google Maps API Call
gmaps.places(
    query="italian restaurant in Manhattan",
    type="restaurant",
    keyword="italian",
    region="us"
)

# Then filter results:
- Keep only: price_level in [1, 2] AND rating >= 4.0
- Result: 15 locations found
```

**Query 2**: "Mid-range coffee shops in London"
```python
# Parsed
{
    "search_mode": "category",
    "business_category": "coffee shop",
    "location": {"city": "London", "radius_km": 5},
    "filters": {
        "price_level": [2, 3]  # $$ to $$$
    }
}

# Google Maps API Call
gmaps.places(
    query="coffee shop in London",
    type="cafe",
    region="uk"
)

# Filter: price_level in [2, 3]
```

**Query 3**: "Starbucks locations with rating below 4.0" (find underperformers)
```python
# Parsed
{
    "search_mode": "specific_brand",
    "business_name": "Starbucks",
    "location": {"city": "Paris", "radius_km": 10},
    "filters": {
        "max_rating": 4.0  # Find problematic locations
    }
}
```

**Data Structure**:
```python
{
    "search_id": "uuid",
    "query": "...",
    "parsed_query": { ... },  # Store the structured query
    "locations": [
        {
            "place_id": "...",
            "name": "Trattoria Bella Vista",
            "address": "123 Main St, Manhattan, NY",
            "coordinates": {"lat": 40.7, "lng": -74.0},
            "rating": 4.3,
            "price_level": 2,  # $$
            "price_label": "$$",
            "total_ratings": 450,
            "business_status": "OPERATIONAL",
            "types": ["restaurant", "food", "point_of_interest"],
            "phone": "+1-212-555-0123",
            "website": "https://...",
            "opening_hours": {
                "open_now": true,
                "weekday_text": [...]
            },
            "photos": [...],
            "reviews": [
                {
                    "author": "John D.",
                    "rating": 5,
                    "text": "Amazing pasta! Authentic Italian...",
                    "date": "2024-01-15",
                    "relative_time": "2 weeks ago"
                }
            ]
        }
    ],
    "search_metadata": {
        "total_found": 47,
        "total_returned": 20,
        "filters_applied": {
            "price_level": [1, 2],
            "min_rating": 4.0
        },
        "search_duration_seconds": 12.5
    }
}
```

### 3. Analysis Phase

**Process**:
```
For each location:
1. Batch reviews by location
2. Send to Claude with analysis dimensions
3. Get structured scores (1-5) + insights
4. Aggregate across all locations
```

**Claude Analysis Prompt**:
```
Analyze these reviews for {business_name} at {address}.

Reviews:
{reviews_text}

Rate the following dimensions (1-5 or N/A):
- price_perception: How customers perceive value/pricing
- cleanliness: Hygiene and tidiness

For each dimension:
1. Score (1-5)
2. Key themes (list)
3. Representative quotes (if any)
4. Sentiment (positive/negative/mixed)

Return JSON only.
```

**Analysis Output**:
```python
{
    "location_id": "...",
    "dimensions": {
        "price_perception": {
            "score": 3.5,
            "sentiment": "mixed",
            "themes": ["expensive", "comparable to others", "worth it for quality"],
            "quotes": ["A bit pricey but expected for the location"]
        },
        "cleanliness": {
            "score": 4.2,
            "sentiment": "positive",
            "themes": ["well-maintained", "clean bathrooms", "organized"],
            "quotes": ["Always spotless"]
        }
    }
}
```

### 4. Report Generation Phase

**Aggregation**:
```
- Average scores across all locations
- Identify best/worst performers
- Extract common themes
- Generate comparative insights
- Create visualizations data
```

**Final Report Structure**:
```python
{
    "report_id": "uuid",
    "query": "...",
    "generated_at": "timestamp",
    "summary": {
        "total_locations": 15,
        "total_reviews_analyzed": 75,
        "overall_scores": {
            "price_perception": 3.4,
            "cleanliness": 4.1
        }
    },
    "locations": [...],  # detailed location data
    "insights": {
        "key_findings": [
            "Cleanliness scores are consistently high across Paris",
            "Price perception varies by neighborhood (tourist vs local)"
        ],
        "recommendations": [
            "Focus marketing on cleanliness as a strength",
            "Address pricing concerns in tourist-heavy locations"
        ],
        "standout_locations": {
            "best": [...],
            "needs_improvement": [...]
        }
    },
    "visualizations": {
        "score_distribution": {...},
        "location_heatmap": {...},
        "themes_wordcloud": {...}
    }
}
```

## API Endpoints

### POST /api/search
```json
// Example 1: Specific brand
{
    "query": "Analyze Starbucks in Paris for price and cleanliness",
    "options": {
        "max_locations": 20,
        "include_competitors": false
    }
}

// Example 2: Category with filters (all in natural language)
{
    "query": "Find Italian restaurants in Manhattan under $30 with rating above 4.0 and analyze their service quality and food quality"
}

// Example 3: Advanced filters (optional structured format)
{
    "query": "Analyze coffee shops in London",
    "filters": {
        "price_level": [2, 3],  // Override/supplement NL parsing
        "min_rating": 4.0,
        "min_reviews": 50
    },
    "analysis_dimensions": ["ambiance", "service", "value"],
    "options": {
        "max_locations": 30
    }
}

Response:
{
    "task_id": "uuid",
    "status": "processing",
    "estimated_time_minutes": 5,
    "parsed_query": {
        "search_mode": "category",
        "business_category": "coffee shop",
        "location": {"city": "London"},
        "filters": {...},
        "analysis_dimensions": [...]
    }
}
```

### GET /api/status/{task_id}
```json
{
    "task_id": "uuid",
    "status": "processing|completed|failed",
    "progress": 45,  // percentage
    "current_step": "analyzing_reviews",
    "report_id": "uuid"  // when completed
}
```

### GET /api/reports/{report_id}
```json
{
    "report": { ... },  // full report structure
    "cached": true
}
```

### GET /api/reports
```json
{
    "reports": [
        {
            "id": "uuid",
            "query": "...",
            "created_at": "...",
            "summary": { ... }
        }
    ]
}
```

## Database Schema

### searches
```sql
id              UUID PRIMARY KEY
query           TEXT                          -- Original natural language query
parsed_query    JSONB                         -- Structured parsed query (includes filters)
search_mode     VARCHAR                       -- 'specific_brand', 'category', 'mixed'
business_name   VARCHAR                       -- If specific brand
business_category VARCHAR                     -- If category search
location        JSONB                         -- {city, neighborhood, country, radius_km}
filters         JSONB                         -- {price_level, min_rating, max_rating, etc}
analysis_dims   JSONB                         -- Array of dimensions to analyze
status          VARCHAR                       -- 'pending', 'processing', 'completed', 'failed'
created_at      TIMESTAMP
completed_at    TIMESTAMP
user_id         VARCHAR                       -- Optional, for multi-user
error_message   TEXT                          -- If failed
```

### locations
```sql
id              UUID PRIMARY KEY
search_id       UUID REFERENCES searches
place_id        VARCHAR UNIQUE                -- Google place_id for deduplication
name            VARCHAR
address         TEXT
coordinates     POINT (PostGIS)
rating          DECIMAL
price_level     INTEGER                       -- 1-4 (NULL if not available)
total_ratings   INTEGER
business_status VARCHAR                       -- 'OPERATIONAL', 'CLOSED_TEMPORARILY', etc
types           JSONB                         -- Array of Google place types
phone           VARCHAR
website         TEXT
opening_hours   JSONB                         -- Full opening hours data
photos          JSONB                         -- Array of photo references
raw_data        JSONB                         -- Full API response for reference
created_at      TIMESTAMP
updated_at      TIMESTAMP

INDEX idx_locations_place_id ON locations(place_id);
INDEX idx_locations_search ON locations(search_id);
INDEX idx_locations_rating ON locations(rating);
INDEX idx_locations_price ON locations(price_level);
SPATIAL INDEX idx_locations_coords ON locations(coordinates);
```

### reviews
```sql
id              UUID PRIMARY KEY
location_id     UUID REFERENCES locations
author          VARCHAR
rating          INTEGER
text            TEXT
date            DATE
source          VARCHAR (google_maps)
created_at      TIMESTAMP
```

### analyses
```sql
id              UUID PRIMARY KEY
location_id     UUID REFERENCES locations
dimension       VARCHAR (price_perception, cleanliness, etc)
score           DECIMAL
sentiment       VARCHAR
themes          JSONB
quotes          JSONB
raw_analysis    JSONB
created_at      TIMESTAMP
```

### reports
```sql
id              UUID PRIMARY KEY
search_id       UUID REFERENCES searches
summary         JSONB
insights        JSONB
visualizations  JSONB
created_at      TIMESTAMP
```

## Frontend Views

### 1. Home / Search Page
```
┌────────────────────────────────────────────────────────┐
│  🔍 Market Research AI                                 │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ What would you like to analyze?                  │ │
│  │                                                  │ │
│  │ [Text input with autocomplete suggestions]      │ │
│  │                                                  │ │
│  │ Examples:                                        │ │
│  │ • Analyze Starbucks in Paris for cleanliness    │ │
│  │ • Italian restaurants in NYC under $30           │ │
│  │ • Coffee shops in London, rating above 4.0       │ │
│  │ • Mid-range bakeries in SF with good service     │ │
│  │ • Find underperforming McDonald's locations      │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  [Advanced Filters ▼]                                  │
│  ┌──────────────────────────────────────────────────┐ │
│  │ Price Range:  [$ $$ $$$ $$$$]                   │ │
│  │ Min Rating:   [3.0 ▼] [Slider: ★★★★☆]          │ │
│  │ Min Reviews:  [ 50 reviews minimum ]             │ │
│  │ Search Radius: [5 km ▼]                          │ │
│  │ Open Now:     [ ] Only show open locations       │ │
│  │                                                  │ │
│  │ Analysis Focus:                                  │ │
│  │ [×] Service Quality    [×] Food Quality          │ │
│  │ [ ] Cleanliness        [ ] Ambiance              │ │
│  │ [×] Value for Money    [ ] Custom...             │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  Recent Searches:                                      │
│  • Starbucks Paris (18 locations) - 2 days ago        │
│  • Italian restaurants Manhattan - 1 week ago         │
│  • Coffee shops London £££ - 2 weeks ago              │
└────────────────────────────────────────────────────────┘
```

### 2. Processing Page
```
┌────────────────────────────────────────┐
│  Analyzing Starbucks in Paris...       │
├────────────────────────────────────────┤
│                                        │
│  [████████░░░░░░] 45%                  │
│                                        │
│  ✓ Query parsed                        │
│  ✓ Found 18 locations                  │
│  ⟳ Collecting reviews (12/18)         │
│  ○ Analyzing with AI                   │
│  ○ Generating report                   │
│                                        │
│  Estimated time: 3 minutes remaining   │
└────────────────────────────────────────┘
```

### 3. Report Dashboard
```
┌──────────────────────────────────────────────────────────────────┐
│  Italian Restaurants in Manhattan (Under $30, Rating 4.0+)      │
│  Generated: Jan 15, 2025  |  15 locations analyzed              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📊 Key Metrics                                                  │
│  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                 │
│  │ 4.3  │ │ 4.1  │ │ 3.8  │ │  15  │ │  73  │                 │
│  │Food  │ │Serv. │ │Value │ │Locs  │ │Revs  │                 │
│  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘                 │
│                                                                  │
│  💰 Price Distribution                [Filter by: All ▼]        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  $:  ████ 4 locations                                    │  │
│  │  $$: ████████████ 11 locations                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  🗺️  Location Map & Heat Map           [View: Scores ▼]        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         [Interactive map with colored pins]              │  │
│  │  🟢 = High score (4.5+)  🟡 = Medium  🔴 = Low (<4.0)   │  │
│  │                                                          │  │
│  │  [Cluster view of Manhattan with hotspots]              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  📈 Score Breakdown by Dimension                                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Food Quality     ████████████░░  4.3                    │  │
│  │  Service Quality  ██████████░░░░  4.1                    │  │
│  │  Value for Money  ████████░░░░░░  3.8                    │  │
│  │  Ambiance         ███████████░░░  4.2                    │  │
│  │  Authenticity     ████████████░░  4.4                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  💡 Key Insights                                                 │
│  • Food quality consistently praised across all locations       │
│  • Service can be slow during peak hours (mentioned in 8/15)   │
│  • Best value found in Little Italy neighborhood               │
│  • Most authentic: Trattoria Bella Vista (4.7★)                │
│  • Price vs Rating: Correlation coefficient: 0.23 (weak)       │
│                                                                  │
│  🏆 Top Performers                   🚨 Needs Attention         │
│  1. Trattoria Bella Vista  4.7★     1. Mario's Kitchen  3.9★  │
│  2. La Piazza             4.6★     2. Pasta Paradise   3.9★  │
│  3. Nonna's Kitchen       4.5★                                 │
│                                                                  │
│  📍 Location Details                            [Sort: Rating ▼]│
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 🟢 Trattoria Bella Vista                    4.7★  $$    │  │
│  │    123 Mulberry St, Little Italy                         │  │
│  │    Food: 4.9  Service: 4.5  Value: 4.6  Ambiance: 4.7   │  │
│  │    📝 "Authentic!", "Best pasta in Manhattan"            │  │
│  │    [View Details] [See on Map]                           │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ 🟢 La Piazza                                4.6★  $$     │  │
│  │    456 Macdougal St, Greenwich Village                   │  │
│  │    Food: 4.5  Service: 4.7  Value: 4.4  Ambiance: 4.6   │  │
│  │    ...                                                   │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ 🔴 Mario's Kitchen                          3.9★  $$     │  │
│  │    789 9th Ave, Hell's Kitchen                           │  │
│  │    Food: 4.0  Service: 3.5  Value: 3.8  Ambiance: 4.1   │  │
│  │    ⚠️ Issues: Slow service, inconsistent portions        │  │
│  │    ...                                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  📊 Detailed Analytics                                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  [Common Themes Word Cloud]                              │  │
│  │  "authentic" "fresh pasta" "cozy" "slow service"         │  │
│  │                                                          │  │
│  │  [Sentiment Over Time - if historical data]              │  │
│  │  [Price vs Rating Scatter Plot]                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  [Export PDF] [Export CSV] [Share] [Save Search] [Set Alert]    │
└──────────────────────────────────────────────────────────────────┘
```

## Query Pattern Examples & Handling

### Common Query Patterns

**1. Specific Brand Analysis**
```
"Analyze Starbucks in Paris"
"Find McDonald's locations in NYC with low ratings"
"Show me all Apple Stores in California"

→ search_mode: "specific_brand"
→ Filter by exact brand name
```

**2. Category Analysis**
```
"Italian restaurants in Manhattan under $30"
"Coffee shops in London with rating above 4.0"
"Luxury hotels in Dubai"
"Cheap sushi in Tokyo"

→ search_mode: "category"
→ Search by business type + filters
```

**3. Mixed Analysis**
```
"Compare Starbucks vs local coffee shops in Seattle"
"Italian restaurants near Times Square, including Olive Garden"

→ search_mode: "mixed"
→ Multiple queries combined
```

**4. Competitive Analysis**
```
"Compare McDonald's vs Burger King in Chicago"
"Starbucks vs Dunkin' Donuts in Boston"

→ search_mode: "competitor_comparison"
→ Run parallel searches, compare results
```

**5. Trend/Issue Detection**
```
"Find Starbucks locations with service complaints"
"Which Whole Foods have cleanliness issues"
"Underperforming McDonald's in California"

→ search_mode: "issue_detection"
→ Filter by low scores in specific dimensions
```

### Natural Language Extraction Mapping

**Price Terms → price_level**
```
"cheap", "budget", "inexpensive", "affordable" → 1 ($)
"moderate", "mid-range", "reasonable" → 2 ($$)
"upscale", "pricey", "expensive" → 3 ($$$)
"luxury", "fine dining", "high-end", "very expensive" → 4 ($$$$)

Range examples:
"under $20" → [1, 2]
"$25-50 per person" → [2, 3]
"affordable to mid-range" → [2, 3]
```

**Rating Terms → min_rating**
```
"highly rated" → 4.0
"well-reviewed" → 4.0
"top rated" → 4.5
"above 4 stars" → 4.0
"at least 3.5" → 3.5
"poorly rated" → max_rating: 3.0 (invert for finding problems)
```

**Popularity Terms → min_reviews**
```
"popular" → 100
"well-known" → 100
"established" → 50
"new places" → max_reviews: 20 (invert)
"hidden gems" → Low reviews but high rating
```

**Location Specificity**
```
"in Manhattan" → neighborhood: "Manhattan", radius: 2km
"near Times Square" → geocode address, radius: 1km
"in NYC" → city: "New York", radius: 10km
"Paris 8th arrondissement" → neighborhood: "8th arrondissement"
```

**Analysis Dimension Terms**
```
"service" → ["service_speed", "service_quality", "staff_friendliness"]
"food" → ["food_quality", "food_freshness", "portion_size"]
"value" → ["price_perception", "value_for_money"]
"atmosphere" → ["ambiance", "cleanliness", "comfort", "noise_level"]
"experience" → ["overall_experience"] (aggregate)
```

## Implementation Phases

### Phase 1: MVP (Core Functionality)
- [ ] Basic query parser (simple regex, then upgrade to Claude)
- [ ] Google Maps integration (search + details + reviews)
- [ ] Claude analysis for 2-3 basic dimensions
- [ ] Simple FastAPI backend
- [ ] Basic React frontend with search + results
- [ ] No database (in-memory cache only)

### Phase 2: Enhanced Features
- [ ] PostgreSQL database for persistence
- [ ] Celery + Redis for background tasks
- [ ] Advanced Claude query parsing
- [ ] Configurable analysis dimensions
- [ ] Better UI with charts
- [ ] Report history

### Phase 3: Advanced Features
- [ ] Competitor comparison
- [ ] Custom dimension creation
- [ ] Export to PDF/Excel
- [ ] Multi-user support with auth
- [ ] Saved searches & alerts
- [ ] API rate limiting & caching
- [ ] Sentiment trend analysis over time

## Key Considerations

### 1. API Cost Management
- **Google Maps**: ~$0.017 per Places API call, $0.017 per Place Details
  - Budget for 20 locations: ~$0.68 per search
- **Anthropic**: ~$0.003 per 1K tokens (Haiku) or $0.015 (Sonnet)
  - Budget for 100 reviews: ~$0.30-1.50 per search
- **Solution**: Implement aggressive caching, user rate limits

### 2. Performance
- Searches can take 3-10 minutes for 20 locations
- Use Celery for async processing
- Show real-time progress updates via WebSockets or polling

### 3. Scalability
- Cache Google Maps results (places rarely change)
- Cache analysis results (reviews don't change)
- Use Redis for fast retrieval
- Consider CDN for frontend

### 4. Error Handling
- Google Maps quota exceeded → graceful degradation
- Claude API timeout → retry logic
- Partial results → still show what's available

## Environment Variables

```bash
# .env.example
GOOGLE_MAPS_API_KEY=your_key
ANTHROPIC_API_KEY=your_key

DATABASE_URL=postgresql://user:pass@localhost/marketresearch
REDIS_URL=redis://localhost:6379

CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379

MAX_LOCATIONS_PER_SEARCH=50
DEFAULT_SEARCH_RADIUS_KM=5
CACHE_EXPIRY_DAYS=30

# Optional
SENTRY_DSN=  # Error tracking
MAPBOX_TOKEN=  # For frontend maps
```

## Next Steps

1. **Prototype** the query parser with Claude
2. **Build** the Google Maps service wrapper
3. **Create** a simple FastAPI endpoint that chains: parse → search → analyze
4. **Test** end-to-end with 2-3 locations
5. **Build** basic React UI to visualize results
6. **Iterate** on the analysis prompt until results are good
7. **Add** database persistence
8. **Deploy** MVP

This structure gives you:
- ✅ Clear separation of concerns
- ✅ Async processing for long tasks
- ✅ Extensible architecture
- ✅ Good caching strategy
- ✅ Professional UI/UX
- ✅ Room to grow

Ready to start coding? Which component would you like to tackle first?