"""
CS50P Final Project - Global Energy Explorer

Analyses how countries' energy sources have changed over time using real data from Our World in Data (energy consumption, energy mix, and renewable
share by country and year). Lets the user look up a country's energy transition, compare two countries, or find which countries lead on a given
metric (e.g. highest renewable share).

Data source: https://github.com/owid/energy-data
"""

import csv
import os
import requests
from difflib import get_close_matches
from tabulate import tabulate

DATA_URL = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"
DATA_FILE = "owid-energy-data.csv"

def main():

    # Load the dataset once at the start
    data = load_data(DATA_FILE)

    print("\n=== GLOBAL ENERGY EXPLORER ===\n")

    # Keep showing the menu until the user chooses to quit
    while True:
        # The options
        print("What would you like to do?")
        print("1. Look up a country's energy profile")
        print("2. Compare two countries")
        print("3. Find the world leader on a metric")
        print("4. Quit")

        # Get the user's choice
        choice = input("Choose (1-4): ").strip()

        # Option 1: single country lookup
        if choice == "1":
            country = input("Enter a country: ").strip()
            summary = country_summary(data, country)

            # If not found, try suggesting a close match first
            if summary is None:
                suggestion = suggest_country(data, country)
                if suggestion:
                    answer = input(f"Did you mean '{suggestion}'? (y/n): ").lower().strip()
                    if answer in ["y", "yes"]:
                        summary = country_summary(data, suggestion)
                    else:
                        print("Okay, no results shown.\n")
                        continue
                else:
                    print("Country not found.\n")
                    continue

            # Display the summary
            print(f"\n{summary['country']} ({summary['latest_year']})")
            print(f"  Renewable share: {summary['renewables_share']:.1f}%")
            print(f"  Fossil share:    {summary['fossil_share']:.1f}%")
            print(f"  Renewables change since {summary['change_since']}: {summary['renewables_change']:+.1f}%\n")



        # Option 2: compare two countries
        elif choice == "2":
            c1 = input("First country: ").strip()
            c2 = input("Second country: ").strip()

            # Check each country individually so we can tell the user exactly
            # which one wasn't found, and offer a suggestion for it
            s1 = country_summary(data, c1)
            if s1 is None:
                suggestion = suggest_country(data, c1)
                if suggestion:
                    answer = input(f"'{c1}' not found. Did you mean '{suggestion}'? (y/n): ").lower().strip()
                    if answer in ["y", "yes"]:
                        s1 = country_summary(data, suggestion)
                if s1 is None:
                    print(f"Couldn't find '{c1}'. Try again.\n")
                    continue

            s2 = country_summary(data, c2)
            if s2 is None:
                suggestion = suggest_country(data, c2)
                if suggestion:
                    answer = input(f"'{c2}' not found. Did you mean '{suggestion}'? (y/n): ").lower().strip()
                    if answer in ["y", "yes"]:
                        s2 = country_summary(data, suggestion)
                if s2 is None:
                    print(f"Couldn't find '{c2}'. Try again.\n")
                    continue

            # Both found — build a table comparing them side by side
            table = [
                ["Renewable share (%)", f"{s1['renewables_share']:.1f}", f"{s2['renewables_share']:.1f}"],
                ["Fossil share (%)", f"{s1['fossil_share']:.1f}", f"{s2['fossil_share']:.1f}"],
                ["Renewables change (%)", f"{s1['renewables_change']:+.1f}", f"{s2['renewables_change']:+.1f}"],
            ]
            headers = ["Metric", s1["country"], s2["country"]]
            print("\n" + tabulate(table, headers=headers, tablefmt="grid", disable_numparse=True))

            higher = s1['country'] if s1['renewables_share'] > s2['renewables_share'] else s2['country']
            print(f"\nHigher renewable share: {higher}\n")



        # Option 3: find the world leader on a metric
        elif choice == "3":
            print("Which metric?")
            print("  1. Renewable share")
            print("  2. Fossil fuel share")
            print("  3. Solar share")
            metric_choice = input("Choose (1-3): ").strip()

            # Turn the user's choice into the matching column name
            if metric_choice == "1":
                metric = "renewables_share_energy"
            elif metric_choice == "2":
                metric = "fossil_share_energy"
            elif metric_choice == "3":
                metric = "solar_share_energy"
            else:
                print("Invalid choice.\n")
                continue

            result = find_extreme(data, metric)
            if result is None:
                print("No data available for that metric.\n")
                continue

            # Display result
            country, value, year = result
            print(f"\nWorld leader: {country} ({value:.1f}%, {year} data)\n")

        # Option 4: quit
        elif choice == "4":
            print("Goodbye!")
            break

        # Anything else: invalid input
        else:
            print("Please choose 1, 2, 3, or 4.\n")



def load_data(filename):
    """
    Loads the OWID energy dataset. If the CSV isn't already present locally, downloads it first from Our World in Data's GitHub repository.
    Returns the data as a list of dictionaries, one per country-year row.
    """

    # If the file isn't already saved locally, download it first
    if not os.path.exists(filename):
        print("Dataset not found locally, downloading...")
        response = requests.get(DATA_URL)
        with open(filename, "w") as file:
            file.write(response.text)

    # Open the local file and read it as CSV
    with open(filename) as file:
        reader = csv.DictReader(file)
        data = list(reader)
    # Sanity check: the real dataset has tens of thousands of rows.
    if len(data) < 100:
        raise ValueError("Data file looks incomplete or corrupted")
    return data



def country_summary(data, country):
    """
    Returns a summary of one country's energy profile: its most recent renewable share, fossil share,
    and how its renewable share has changed since the earliest year with data.
    Returns None if the country isn't found.
    """

    # Collect every row for this country that actually has a renewable-share figure.
    # Many rows are blank for some countries/years, so we skip those
    rows = []
    for row in data:
        if row["country"].lower() == country.lower() and row["renewables_share_energy"]:
            rows.append(row)

    # If nothing matched, the country isn't in the data (or has no figures).
    # Return None so the caller can handle it (e.g. suggest a correction).
    if not rows:
        return None

    # The file is in year order per country, so the last usable row is the most recent year with data, and the first is the earliest.
    latest = rows[-1]
    earliest = rows[0]

    # Build a tidy dictionary of the figures we care about.
    summary = {
        "country": latest["country"],
        "latest_year": latest["year"],
        "renewables_share": float(latest["renewables_share_energy"]),
        "fossil_share": float(latest["fossil_share_energy"]),
        "change_since": earliest["year"],
        "renewables_change": float(latest["renewables_share_energy"]) - float(earliest["renewables_share_energy"]),
    }

    return summary



def suggest_country(data, country):
    """
    If a country name isn't found exactly, finds the closest matching country name in the dataset.
    Returns the closest match as a string, or None if nothing is close enough.
    """
    # Build a set of every unique country name in the dataset.
    all_countries = {row["country"] for row in data}

    # get_close_matches compares the user's input against all real names and returns the closest.
    # accept it if it's at least ~60% similar (stops it suggesting nonsense).
    matches = get_close_matches(country, all_countries, n=1, cutoff=0.6)

    return matches[0] if matches else None



def compare_countries(data, country1, country2):
    """
    Compares two countries' latest energy figures side by side.
    Returns a dictionary with each country's summary plus which one has the higher renewable share.
    Returns None if either country isn't found.
    """
    # Reuse country_summary to get each country's figures.
    summary1 = country_summary(data, country1)
    summary2 = country_summary(data, country2)

    # If either country wasn't found, signal back with None
    if summary1 is None or summary2 is None:
        return None

    # Work out which country has the higher renewable share
    if summary1["renewables_share"] > summary2["renewables_share"]:
        leader = summary1["country"]
    else:
        leader = summary2["country"]

    # Bundle both summaries and the verdict into one result
    comparison = {
        "country1": summary1,
        "country2": summary2,
        "higher_renewables": leader,
    }

    return comparison



def find_extreme(data, metric):
    """
    Scans every country and finds the one with the highest value for a given metric,
    using the most recent year that actually has data for that metric.
    Returns a tuple of (country_name, value, year), or None if no data was found.
    """

    # Find the most recent year that has data FOR THIS METRIC specifically.
    years_with_data = [
        row["year"]
        for row in data
        if row[metric] and row["iso_code"]
    ]

    # If no year has data for this metric at all, we can't do anything
    if not years_with_data:
        return None
    latest_year = max(years_with_data)

    best_country = None
    best_value = 0

    for row in data:
        # Only the chosen year, non-blank metric, and real countries (have iso_code)
        if row["year"] == latest_year and row[metric] and row["iso_code"]:
            value = float(row[metric])
            if value > best_value:
                best_value = value
                best_country = row["country"]

    if best_country is None:
        return None

    return (best_country, best_value, latest_year)


if __name__ == "__main__":
    main()
