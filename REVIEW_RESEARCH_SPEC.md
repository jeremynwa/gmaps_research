# Review Research — Module Integration Guide

> Ce document est destine a un agent Claude qui integre un module de "recherche d'avis" dans une app Next.js/React existante. L'utilisateur final configure le module via une conversation avec Claude + un formulaire de confirmation.

---

## 1. Ce que le module fait

Analyse des avis clients (Google Maps ou base de donnees existante) par IA, selon des criteres personnalises, et exporte les resultats scores en Excel/JSON.

**En une phrase :** L'utilisateur definit ce qu'il veut analyser (marques, regions, criteres, echelle), le module scrape ou charge les avis, les fait analyser par Claude, et retourne un tableau de scores.

---

## 2. Flow utilisateur dans l'app

```
┌─────────────────────────────────────────────────────────────┐
│  ETAPE 1 — Conversation avec Claude                         │
│                                                             │
│  Claude pose les questions :                                │
│  - Quelle industrie ? (resto, hotel, SaaS, retail...)       │
│  - Quelles marques/enseignes analyser ?                     │
│  - Quels concurrents comparer ?                             │
│  - Quelle region/pays ?                                     │
│  - Tu as deja une base de donnees d'avis ? (CSV/Excel)      │
│  - Quels aspects veux-tu evaluer ? (qualite, prix, service) │
│  - Quelle echelle de notation ? (1-100, 1-5, binaire)       │
│  - Quelle langue pour l'analyse ?                           │
│  - Combien d'avis max ?                                     │
│                                                             │
│  Claude genere une config JSON a partir des reponses        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  ETAPE 2 — Formulaire de confirmation (UI React)            │
│                                                             │
│  Pre-rempli par Claude, modifiable par l'utilisateur :      │
│                                                             │
│  ┌─ Scope ─────────────────────────────────────────────┐    │
│  │ Industrie:     [Restaurant        ▼]                │    │
│  │ Marques:       [McDonald's] [+ Ajouter]             │    │
│  │ Concurrents:   [Burger King] [KFC] [+ Ajouter]     │    │
│  │ Region:        [Paris, France          ]            │    │
│  │ Max avis:      [1000        ]                       │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌─ Criteres d'evaluation ─────────────────────────────┐    │
│  │ ☑ Qualite produit    ☑ Rapport qualite-prix         │    │
│  │ ☑ Rapidite service   ☑ Hygiene                      │    │
│  │ ☑ Accueil/personnel  ☐ Ambiance                     │    │
│  │ ☑ NPS (recommandation)                              │    │
│  │ [+ Ajouter critere personnalise]                    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌─ Echelle ───────────────────────────────────────────┐    │
│  │ (●) 1-100 (x10)  ( ) 1-10  ( ) 1-5  ( ) Binaire   │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌─ Source de donnees ─────────────────────────────────┐    │
│  │ (●) Scraper Google Maps (Outscraper)                │    │
│  │ ( ) Importer fichier existant [Choisir fichier]     │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  ┌─ Estimation de cout ────────────────────────────────┐    │
│  │ Scraping:        $1.50                              │    │
│  │ Analyse Claude:  $9.40                              │    │
│  │ TOTAL:           $10.90                             │    │
│  │ (inclut 90% de reduction via prompt caching)        │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
│  [Lancer l'analyse]                                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  ETAPE 3 — Execution backend (API Python)                   │
│                                                             │
│  1. Scrape ou charge les avis                               │
│  2. Analyse chaque avis avec Claude (parallele, cache)      │
│  3. Retourne les resultats (Excel + JSON)                   │
│  4. Affiche progression en temps reel (websocket/polling)   │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Architecture du module backend (Python)

Le backend est une API Python (FastAPI recommande) que l'app Next.js appelle.

```
review_research/
├── api.py                     # Endpoints FastAPI (POST /analyze, POST /scrape, GET /estimate)
│
├── config/
│   ├── settings.py            # Constantes, pricing, limites de cout
│   └── prompts.py             # <<< LE PROMPT VIT ICI — genere dynamiquement >>>
│
├── scrapers/
│   ├── base.py                # BaseScraper (ABC)
│   ├── csv_loader.py          # Charge CSV/Excel existants
│   └── outscraper_scraper.py  # Scrape Google Maps
│
├── analyzers/
│   ├── base.py                # BaseAnalyzer (ABC + validation input)
│   ├── anthropic_analyzer.py  # Claude Sonnet 4 + prompt caching
│   └── mock_analyzer.py       # Pour tests (scores aleatoires, 0 API calls)
│
├── processors/
│   ├── orchestrator.py        # Threading, cache, analyse 2 phases
│   └── cache_manager.py       # Cache local JSON (reprise apres interruption)
│
├── exporters/
│   ├── excel_exporter.py      # 2 onglets : Scores + Keywords
│   └── json_exporter.py       # Array JSON
│
└── utils/
    ├── cost_calculator.py     # Estimation de cout (Claude + scraping)
    └── progress_tracker.py    # Progression, ETA, stats
```

---

## 4. Points de personnalisation (CRITIQUE)

### 4.1 Le Prompt — Generation dynamique

C'est LE point le plus important. Le prompt est **genere a partir de la config utilisateur**, pas code en dur.

**Fichier :** `config/prompts.py`

**Le prompt doit etre genere a partir de :**
- L'industrie choisie (contexte d'expert)
- La liste de criteres (avec leur question d'evaluation)
- L'echelle de notation
- La langue
- Le format de sortie JSON (base sur les criterion_ids)

**Template de generation :**

```python
def build_analysis_prompt(config: ResearchConfig) -> str:
    """Genere le prompt d'analyse a partir de la config utilisateur."""

    criteria_block = "\n".join(
        f'{i+1}. **{c.id}** - {c.question}'
        for i, c in enumerate(config.criteria)
    )

    scale_block = {
        "1-100": "Score de 10 a 100, par multiples de 10. 100=excellent, 50=acceptable, 10=tres mauvais.",
        "1-10": "Score de 1 a 10. 10=excellent, 5=moyen, 1=tres mauvais.",
        "1-5": "Score de 1 a 5. 5=excellent, 3=moyen, 1=tres mauvais.",
        "binary": "1 si le critere est mentionne positivement, 0 sinon.",
    }[config.scale]

    json_fields = ",\n  ".join(
        f'"{c.id}_score": <score>, "{c.id}_keyword": "<mot-cle>"'
        for c in config.criteria
    )

    return f"""Tu es un expert en analyse d'avis clients dans le secteur {config.industry}.

Pour chaque avis client, evalue les criteres suivants :

{criteria_block}

## Echelle de notation
- {scale_block}
- "N/A" si le critere n'est pas mentionne dans l'avis.

## Mot-cle associe
- 1 a 3 mots identifiant le produit/service concerne.
- "Personnel" si une personne est mentionnee.
- "N/A" si non applicable.

## Regles strictes
- Ne JAMAIS extrapoler ou inventer un score.
- Evaluer UNIQUEMENT sur le texte de l'avis, PAS sur la note numerique.
- Repondre UNIQUEMENT en JSON valide, sans texte additionnel.

## Format de sortie
{{
  {json_fields}
}}"""
```

**IMPORTANT pour le caching :** Ce prompt est envoye comme `system message` avec `cache_control: {"type": "ephemeral"}`. Il doit etre **identique** pour tous les avis d'un meme run. Les infos variables (texte de l'avis, auteur, note, date) vont dans le `user message`.

### 4.2 La Config utilisateur — Schema

Voici le schema de config que Claude genere en conversation et que le formulaire permet de modifier :

```typescript
// types/review-research.ts

interface ResearchConfig {
  // Scope
  industry: string;              // "restaurant", "hotel", "saas", "retail"...
  brands: string[];              // ["McDonald's", "Starbucks"]
  competitors: string[];         // ["Burger King", "KFC"]
  location: string;              // "Paris, France"
  maxReviewsPerBrand: number;    // 1000
  language: string;              // "fr", "en", "de"...

  // Criteres
  criteria: Criterion[];

  // Echelle
  scale: "1-100" | "1-10" | "1-5" | "binary";

  // Source de donnees
  dataSource: "scrape" | "upload";
  uploadedFileUrl?: string;      // Si upload, URL du fichier

  // Avance (optionnel, defauts raisonnables)
  maxWorkers?: number;           // 10 par defaut
  model?: string;                // "claude-sonnet-4-20250514" par defaut
}

interface Criterion {
  id: string;                    // "qualite_produit" (snake_case, pas d'accents)
  label: string;                 // "Qualite du produit" (affichage UI)
  question: string;              // "L'avis mentionne-t-il la qualite des produits ?"
}
```

### 4.3 Criteres — Presets par industrie

Le formulaire propose des presets de criteres selon l'industrie. L'utilisateur peut les modifier.

**Restaurant :**
| ID | Label | Question |
|----|-------|----------|
| `qualite_nourriture` | Qualite nourriture | La nourriture est-elle decrite comme bonne/mauvaise ? |
| `variete_offre` | Variete de l'offre | Assez de choix de produits ? |
| `rapport_qualite_prix` | Rapport qualite-prix | Le prix est-il juste par rapport a la qualite ? |
| `rapidite_service` | Rapidite du service | Le service est-il rapide ou lent ? |
| `accueil_personnel` | Accueil / Personnel | Le personnel est-il aimable et efficace ? |
| `hygiene_proprete` | Hygiene / Proprete | Le lieu est-il propre et hygienique ? |
| `ambiance` | Ambiance | L'atmosphere est-elle agreable ? |
| `nps` | Recommandation | Le client recommanderait-il l'etablissement ? |

**Hotel :**
| ID | Label | Question |
|----|-------|----------|
| `chambre_proprete` | Proprete chambre | La chambre est-elle propre ? |
| `chambre_confort` | Confort chambre | Le lit et la chambre sont-ils confortables ? |
| `petit_dejeuner` | Petit-dejeuner | Le petit-dejeuner est-il bon et varie ? |
| `accueil_reception` | Accueil reception | Le check-in est-il rapide et agreable ? |
| `rapport_qualite_prix` | Rapport qualite-prix | Le prix est-il juste ? |
| `localisation` | Localisation | L'emplacement est-il pratique ? |
| `wifi_equipements` | WiFi / Equipements | WiFi et equipements fonctionnent-ils bien ? |
| `nps` | Recommandation | Le client recommanderait-il l'hotel ? |

**SaaS / App :**
| ID | Label | Question |
|----|-------|----------|
| `facilite_utilisation` | Facilite d'utilisation | Le produit est-il facile a utiliser ? |
| `fiabilite` | Fiabilite | Le produit est-il stable, sans bugs ? |
| `support_client` | Support client | Le support est-il reactif et utile ? |
| `rapport_qualite_prix` | Rapport qualite-prix | Le prix est-il justifie ? |
| `fonctionnalites` | Fonctionnalites | Les features couvrent-elles les besoins ? |
| `onboarding` | Onboarding | La prise en main est-elle facile ? |
| `nps` | Recommandation | L'utilisateur recommanderait-il le produit ? |

L'utilisateur peut **ajouter, supprimer, ou modifier** n'importe quel critere via le formulaire ou la conversation.

### 4.4 Source de donnees — Scraping vs Upload

**Option A : Scraper Google Maps**
- Utilise l'API Outscraper
- Necessite `OUTSCRAPER_API_KEY`
- L'utilisateur fournit : nom de marque + localisation + max avis
- Cout : ~$1.50 / 1000 avis

**Option B : Importer un fichier existant**
- Formats acceptes : `.csv`, `.xlsx`, `.xls`
- Colonnes requises (le nom exact est configurable via un mapping) :
  - Texte de l'avis (obligatoire)
  - Nom de l'etablissement
  - Localisation/adresse
  - Auteur
  - Note numerique
  - Date de l'avis
- L'UI propose un mapping de colonnes si les noms ne correspondent pas

### 4.5 Estimation de cout — Affichage en temps reel

Le formulaire affiche une estimation de cout **en temps reel** quand l'utilisateur modifie le nombre d'avis ou la source.

**Formules :**

```typescript
function estimateCost(config: ResearchConfig): CostBreakdown {
  const n = config.brands.length * config.maxReviewsPerBrand;

  // Scraping (si applicable)
  const scrapingCost = config.dataSource === "scrape"
    ? (n / 1000) * 1.50
    : 0;

  // Claude API (avec prompt caching)
  const avgInputTokens = 1800;
  const avgOutputTokens = 600;
  const cachedTokens = 1661;    // Taille du system prompt (stable)
  const dynamicTokens = avgInputTokens - cachedTokens;  // ~139
  const cacheHitRate = 0.98;

  // Premier avis : cache write (1.25x)
  const firstReviewCost = (avgInputTokens * 3.75 + avgOutputTokens * 15) / 1_000_000;

  // Avis suivants : cache read (0.10x sur cached, 1.0x sur dynamic)
  const cachedReviewCost = (
    (cachedTokens * 0.30 + dynamicTokens * 3.0) + avgOutputTokens * 15
  ) / 1_000_000;

  const missReviewCost = (avgInputTokens * 3.75 + avgOutputTokens * 15) / 1_000_000;

  const subsequent = n - 1;
  const hits = subsequent * cacheHitRate;
  const misses = subsequent * (1 - cacheHitRate);

  const analysisCost = firstReviewCost + (hits * cachedReviewCost) + (misses * missReviewCost);

  return {
    scraping: scrapingCost,
    analysis: analysisCost,
    total: scrapingCost + analysisCost
  };
}
```

**Exemples de couts (criteres standard, ~600 tokens output) :**
| Avis | Analyse seule | Avec scraping |
|------|--------------|---------------|
| 100 | ~$0.95 | ~$1.10 |
| 500 | ~$4.70 | ~$5.45 |
| 1,000 | ~$9.40 | ~$10.90 |
| 5,000 | ~$47.00 | ~$54.50 |

**Limites de securite :**
- Alerte a $100
- Blocage a $500 (configurable)

---

## 5. API Endpoints (backend Python)

Le frontend Next.js appelle ces endpoints :

### `POST /api/review-research/estimate`
```json
// Request
{ "config": { ...ResearchConfig } }

// Response
{ "scraping": 1.50, "analysis": 9.40, "total": 10.90, "reviewCount": 1000 }
```

### `POST /api/review-research/start`
```json
// Request
{ "config": { ...ResearchConfig } }

// Response
{ "jobId": "uuid-xxx", "status": "started", "estimatedCost": 10.90 }
```

### `GET /api/review-research/status/:jobId`
```json
// Response
{
  "status": "running",         // "running" | "completed" | "error"
  "progress": 0.45,            // 0-1
  "analyzed": 450,
  "total": 1000,
  "cacheHits": 12,
  "errors": 2,
  "eta": "3m 20s"
}
```

### `GET /api/review-research/results/:jobId`
```json
// Response
{
  "excelUrl": "/downloads/analysis_2026-03-06.xlsx",
  "jsonUrl": "/downloads/analysis_2026-03-06.json",
  "summary": {
    "totalReviews": 1000,
    "analyzedReviews": 985,
    "skipped": 15,
    "avgScores": { "qualite_nourriture": 72, "rapidite_service": 58, ... },
    "cost": { "scraping": 1.50, "analysis": 9.38, "total": 10.88 }
  }
}
```

---

## 6. Patterns techniques cles

### Prompt caching (reduction de 90% des couts)
1. Le prompt (system message) est marque `cache_control: {"type": "ephemeral"}`
2. Le 1er avis est analyse **seul** pour creer le cache cote Anthropic
3. Attente de 5 secondes pour propagation du cache
4. Tous les avis suivants reutilisent le cache (98% hit rate)
5. Seul le user message (texte de l'avis, metadonnees) est facture plein tarif

### Analyse en 2 phases
- **Phase 1 :** 1 avis sequentiel (initialisation du cache)
- **Phase 2 :** N-1 avis en parallele (ThreadPoolExecutor, 10 workers par defaut)

### Cache local pour reprise
- Chaque resultat est sauvegarde dans un fichier JSON local
- Si le process est interrompu, relancer reprend ou il s'est arrete
- Ecriture atomique (fichier temp + rename)
- Thread-safe (threading.Lock)

### Gestion d'erreurs
- Retry avec backoff exponentiel (3 tentatives, 2-30s) pour rate limits
- Un avis en erreur ne bloque pas le batch
- Avis echoues marques "N/A" / "ERROR"

---

## 7. Dependances backend

```
anthropic          # Client API Claude (avec support cache_control)
outscraper         # Scraping Google Maps (optionnel)
pandas             # Manipulation donnees
openpyxl           # Export Excel
fastapi            # API endpoints
uvicorn            # Serveur ASGI
python-dotenv      # Variables d'environnement
```

Python 3.9+. Pas de syntaxe `X | Y` — utiliser `Optional[X]` / `Union[X, Y]`.

---

## 8. Variables d'environnement requises

```env
ANTHROPIC_API_KEY=sk-ant-...     # Obligatoire
OUTSCRAPER_API_KEY=...           # Seulement si scraping Google Maps
```

---

## 9. Checklist d'integration

- [ ] Creer le formulaire React de configuration (scope, criteres, echelle, source)
- [ ] Implementer le flow conversationnel Claude pour guider la config
- [ ] Generer la `ResearchConfig` JSON a partir de la conversation
- [ ] Pre-remplir le formulaire avec la config generee
- [ ] Afficher l'estimation de cout en temps reel dans le formulaire
- [ ] Creer les endpoints API backend (estimate, start, status, results)
- [ ] Integrer le generateur de prompt dynamique (`build_analysis_prompt`)
- [ ] Integrer le module d'analyse (scrapers, analyzers, orchestrator, exporters)
- [ ] Afficher la progression en temps reel (polling ou websocket)
- [ ] Proposer le telechargement des resultats (Excel + JSON)
- [ ] Ajouter les presets de criteres par industrie
- [ ] Gerer l'upload de fichiers existants (CSV/Excel) avec mapping de colonnes
