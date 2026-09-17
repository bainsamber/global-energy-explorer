
from project import load_data, country_summary, suggest_country, find_extreme

# Load the data once, so all tests can use it
data = load_data("owid-energy-data.csv")


def test_country_summary_valid():
    # A real country should return a dictionary with the expected keys
    result = country_summary(data, "United Kingdom")
    assert result is not None
    assert result["country"] == "United Kingdom"
    assert "renewables_share" in result


def test_country_summary_invalid():
    # A country that doesn't exist should return None
    assert country_summary(data, "Wakanda") is None


def test_suggest_country():
    # A typo of a real country should be corrected to the right name
    assert suggest_country(data, "Untied Kingdom") == "United Kingdom"
    # Total nonsense should return None
    assert suggest_country(data, "zzzzzzz") is None


def test_find_extreme():
    # find_extreme should return a 3-part tuple (country, value, year)
    result = find_extreme(data, "renewables_share_energy")
    assert result is not None
    country, value, year = result
    assert isinstance(country, str)
    assert isinstance(value, float)
