import sys
import os
import pytest

# Add workspace root to Python path for package imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from python_news_dashboard.analyze import extract_news_data, analyze_tags_and_region_ids, EXCLUDE_TAGS


def test_extract_news_data_from_api():
    data = {
        "news": [
            {"title": "News A", "date": "2026-03-18", "tags": [{"tag": "Politik"}], "regionId": 1, "ressort": "Inland"},
            {"title": "News B", "date": "2026-03-18", "tags": [{"tag": "Wirtschaft"}], "regionId": 2, "ressort": "Wirtschaft"}
        ]
    }

    extracted, total = extract_news_data(data, from_api=True)
    assert total == 2
    assert len(extracted) == 2
    assert extracted[0]["title"] == "News A"
    assert extracted[1]["regionId"] == 2


def test_extract_news_data_invalid():
    extracted, total = extract_news_data({"invalid": []}, from_api=True)
    assert extracted == []
    assert total == 0


def test_analyze_tags_and_region_ids_filters_and_counts():
    # Use sample data with tags and regionId for mapping tests
    data = {
        "news": [
            {
                "title": "Test 1",
                "tags": [{"tag": "Politik"}, {"tag": "Test"}, {"tag": "Test"}, {"tag": "Test"}],
                "regionId": 1
            },
            {
                "title": "Test 2",
                "tags": [{"tag": "Politik"}, {"tag": "ignore"}],
                "regionId": 2
            },
            {
                "title": "Test 3",
                "tags": [{"tag": "Test"}],
                "regionId": 100
            }
        ]
    }

    filtered_tags, state_counter = analyze_tags_and_region_ids(data, from_api=True)

    # "Test" appears 4 times -> included and above threshold
    assert filtered_tags.get("Test") == 4
    # "Politik" appears 2 times -> filtered out due to threshold
    assert "Politik" not in filtered_tags
    # Region counts: 1 -> Schleswig-Holstein, 2 -> Hamburg
    assert state_counter["Schleswig-Holstein"] == 1
    assert state_counter["Hamburg"] == 1


def test_exclude_tags_not_counted():
    # Create data with one excluded tag from default EXCLUDE_TAGS
    if not EXCLUDE_TAGS:
        pytest.skip("No exclude tags configured")

    excluded = EXCLUDE_TAGS[0]
    data = {"news": [{"tags": [{"tag": excluded}], "regionId": 1}]}
    filtered_tags, _ = analyze_tags_and_region_ids(data, from_api=True)
    assert excluded not in filtered_tags
