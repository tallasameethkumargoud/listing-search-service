from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from rest_framework.test import APIClient

from .views import calculate_relevance


class ListingSearchTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/listings/"

    def test_returns_all_listings(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["pagination"]["totalResults"],
            12
        )

    def test_city_filter(self):
        response = self.client.get(
            self.url,
            {"city": "Springfield"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["pagination"]["totalResults"],
            4
        )

        for listing in response.data["results"]:
            self.assertEqual(
                listing["city"].lower(),
                "springfield"
            )

    def test_no_matches(self):
        response = self.client.get(
            self.url,
            {"city": "Boston"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], [])
        self.assertEqual(
            response.data["pagination"]["totalResults"],
            0
        )

    def test_invalid_price_range(self):
        response = self.client.get(
            self.url,
            {
                "minPrice": 600000,
                "maxPrice": 400000,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["error"],
            "minPrice cannot be greater than maxPrice."
        )

    def test_invalid_page_size(self):
        response = self.client.get(
            self.url,
            {"pageSize": 0}
        )

        self.assertEqual(response.status_code, 400)

    def test_pagination(self):
        response = self.client.get(
            self.url,
            {
                "page": 1,
                "pageSize": 3,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 3)
        self.assertEqual(
            response.data["pagination"]["totalResults"],
            12
        )
        self.assertEqual(
            response.data["pagination"]["totalPages"],
            4
        )

    def test_pagination_boundary(self):
        response = self.client.get(
            self.url,
            {
                "page": 5,
                "pageSize": 3,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["results"], [])

    def test_tied_scores_are_deterministic(self):
        listing_one = {
            "price": 500000,
            "listedDate": "2026-09-01",
        }

        listing_two = {
            "price": 500000,
            "listedDate": "2026-09-01",
        }

        score_one = calculate_relevance(
            listing_one,
            500000
        )
        score_two = calculate_relevance(
            listing_two,
            500000
        )

        self.assertEqual(score_one, score_two)
