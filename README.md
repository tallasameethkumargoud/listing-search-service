# Listing Search Service

A small full-stack property listing search application built for the Software Engineer coding assessment.

## Tech Stack

- Backend: Python, Django, Django REST Framework
- Frontend: React, TypeScript, Vite
- Data: JSON
- Testing: Django test framework / DRF APIClient

## Features

The application supports:

- Minimum price filtering
- Maximum price filtering
- Minimum bedroom filtering
- Case-insensitive city filtering
- Case-insensitive description keyword search
- Target-budget relevance ranking
- Recency-based relevance ranking
- Pagination
- Loading state
- No-results state
- API and UI error handling
- Validation for invalid search parameters

## Relevance Scoring

Results are ranked using a weighted combination of budget proximity and listing recency.

Budget score:

    1 / (1 + abs(price - targetBudget) / targetBudget)

Recency score:

    1 / (1 + ageInDays / 30)

Final relevance score:

    0.70 * budgetScore + 0.30 * recencyScore

Budget proximity receives 70% of the weight because the user's target budget is treated as the primary relevance signal. Recency receives 30% so newer listings rank higher when properties have similar budget relevance.

When no target budget is supplied, the budget component is neutral and results are effectively ordered primarily by recency.

Ties are resolved deterministically using listing date, source, and listing ID.

## Trade-offs

The assessment dataset is small, so listings are loaded directly from the provided JSON file and filtered in memory. This keeps the implementation simple and makes the search logic easy to understand and test.

For a production system with large MLS feeds, I would persist normalized listings in a database or search index and perform filtering, ranking, and pagination at the data layer.

The application does not attempt to deduplicate similar properties across MLS sources because IDs are only guaranteed to be unique within a source and deduplication was not part of the requested functionality.

## Backend Setup

From the project root:

    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py runserver

The API will run at:

    http://127.0.0.1:8000/api/listings/

## Frontend Setup

In another terminal:

    cd frontend
    npm install
    npm run dev

The frontend will run at:

    http://localhost:5173/

## API Parameters

GET /api/listings/

Supported query parameters:

- minPrice
- maxPrice
- minBedrooms
- city
- keyword
- targetBudget
- page
- pageSize

Example:

    /api/listings/?city=Springfield&minBedrooms=2&targetBudget=500000&page=1&pageSize=5

## Tests

Run:

    cd backend
    source venv/bin/activate
    python manage.py test

The test suite covers:

- Normal listing retrieval
- City filtering
- No matches
- Invalid price ranges
- Invalid page sizes
- Pagination
- Pagination boundaries
- Tied relevance scores