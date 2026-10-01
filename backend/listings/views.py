import json
import math
from datetime import date, datetime
from pathlib import Path

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


DATA_FILE = Path(__file__).resolve().parent.parent / "sample_listings.json"


def load_listings():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def calculate_relevance(listing, target_budget):
    """
    Relevance is based on:
    70% price proximity to the target budget
    30% listing recency
    """

    # Price score: closer to target budget = higher score.
    if target_budget:
        difference = abs(listing["price"] - target_budget)
        budget_score = 1 / (1 + (difference / target_budget))
    else:
        budget_score = 1.0

    # Recency score: newer listings receive a higher score.
    listed_date = datetime.strptime(
        listing["listedDate"], "%Y-%m-%d"
    ).date()

    age_days = max((date.today() - listed_date).days, 0)
    recency_score = 1 / (1 + (age_days / 30))

    relevance = (0.70 * budget_score) + (0.30 * recency_score)

    return round(relevance, 4)


@api_view(["GET"])
def search_listings(request):
    try:
        min_price = request.query_params.get("minPrice")
        max_price = request.query_params.get("maxPrice")
        min_bedrooms = request.query_params.get("minBedrooms")
        city = request.query_params.get("city")
        keyword = request.query_params.get("keyword")
        target_budget = request.query_params.get("targetBudget")

        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("pageSize", 5))

        min_price = float(min_price) if min_price else None
        max_price = float(max_price) if max_price else None
        min_bedrooms = int(min_bedrooms) if min_bedrooms else None
        target_budget = float(target_budget) if target_budget else None

    except ValueError:
        return Response(
            {"error": "Numeric query parameters must contain valid numbers."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Input validation
    if min_price is not None and min_price < 0:
        return Response(
            {"error": "minPrice cannot be negative."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if max_price is not None and max_price < 0:
        return Response(
            {"error": "maxPrice cannot be negative."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        return Response(
            {"error": "minPrice cannot be greater than maxPrice."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if min_bedrooms is not None and min_bedrooms < 0:
        return Response(
            {"error": "minBedrooms cannot be negative."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if target_budget is not None and target_budget <= 0:
        return Response(
            {"error": "targetBudget must be greater than zero."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if page <= 0:
        return Response(
            {"error": "page must be greater than zero."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if page_size <= 0:
        return Response(
            {"error": "pageSize must be greater than zero."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    listings = load_listings()

    # Filtering
    if min_price is not None:
        listings = [
            item for item in listings
            if item["price"] >= min_price
        ]

    if max_price is not None:
        listings = [
            item for item in listings
            if item["price"] <= max_price
        ]

    if min_bedrooms is not None:
        listings = [
            item for item in listings
            if item["bedrooms"] >= min_bedrooms
        ]

    if city:
        city_normalized = city.strip().lower()
        listings = [
            item for item in listings
            if item["city"].strip().lower() == city_normalized
        ]

    if keyword:
        keyword_normalized = keyword.strip().lower()
        listings = [
            item for item in listings
            if keyword_normalized in item["description"].lower()
        ]

    # Calculate relevance.
    for listing in listings:
        listing["relevanceScore"] = calculate_relevance(
            listing,
            target_budget,
        )

    # Deterministic ordering is useful when relevance scores tie.
    listings.sort(
        key=lambda item: (
            -item["relevanceScore"],
            -datetime.strptime(
                item["listedDate"], "%Y-%m-%d"
            ).timestamp(),
            item["source"],
            item["id"],
        )
    )

    # Pagination
    total_results = len(listings)
    total_pages = (
        math.ceil(total_results / page_size)
        if total_results
        else 0
    )

    start = (page - 1) * page_size
    end = start + page_size
    paginated_results = listings[start:end]

    return Response({
        "results": paginated_results,
        "pagination": {
            "page": page,
            "pageSize": page_size,
            "totalResults": total_results,
            "totalPages": total_pages,
        },
    })