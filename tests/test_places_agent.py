import unittest
from unittest.mock import Mock, patch

from places_agent import PlacesAgent


class PlacesAgentTests(unittest.TestCase):
    def test_geocoding_result_is_cached_case_insensitively(self):
        response = Mock()
        response.json.return_value = [{"lat": "12.9716", "lon": "77.5946"}]
        response.raise_for_status.return_value = None

        agent = PlacesAgent()
        with patch("places_agent.requests.get", return_value=response) as mocked_get:
            first = agent.get_coordinates("Bengaluru")
            second = agent.get_coordinates("  bengaluru  ")

        self.assertEqual(first, (12.9716, 77.5946))
        self.assertEqual(second, first)
        mocked_get.assert_called_once()

    def test_empty_place_name_and_invalid_queries_do_not_call_apis(self):
        agent = PlacesAgent()
        with patch("places_agent.requests.get") as mocked_get, patch(
            "places_agent.requests.post"
        ) as mocked_post:
            self.assertIsNone(agent.get_coordinates("   "))
            self.assertIsNone(agent.get_tourist_attractions(12.0, 77.0, limit=0))
            self.assertIsNone(agent.get_tourist_attractions(91.0, 77.0))
            self.assertIsNone(agent.get_tourist_attractions(float("nan"), 77.0))

        mocked_get.assert_not_called()
        mocked_post.assert_not_called()


if __name__ == "__main__":
    unittest.main()
