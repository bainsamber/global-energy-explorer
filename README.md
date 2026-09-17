# Global Energy Explorer
#### Video Demo: (https://youtu.be/Fc4aveG3E4o)
#### Description:

Global Energy Explorer is a Python data-analysis program built around the global energy dataset published by Our World in Data. It gives the user several ways to explore and interpret that data through a simple command-line menu. Three modes of analysis are available: viewing a **single country's energy profile**, including its renewable and fossil fuel shares; **comparing two countries** side by side; and identifying the **world-leading country** for a metric of the user's choosing. In this last case, the program automatically selects the most recent year for which sufficient data exists for the chosen metric, ensuring the result is both current and reliable. To make the tool more versatile, it detects minor spelling mistakes in country names and offers the user a suggested correction. Once finished, the user can choose to exit through the menu's quit option.

---

## Files in this project

- **`project.py`** – the main program, containing all the analysis logic and user interaction. It holds the `main` function, which runs the menu loop, along with the functions that do the actual work: `load_data`, `country_summary`, `suggest_country`, `compare_countries`, and `find_extreme`.
- **`requirements.txt`** – the pip-installable libraries the project uses: `requests` (to download the dataset) and `tabulate` (to format the comparison table), plus `pytest` for running the tests.
- **`test_project.py`** – the unit tests I wrote to check that the core functions behave correctly, ran with `pytest`.

---

## Design Choices

- **Auto-downloading the data:** I gave the program the ability to download the CSV automatically if it isn't already present, rather than asking the user to download it manually. This makes the program simpler and more user-friendly, since it works straight away with no setup.
- **Suggesting corrections for misspelled countries:** I used close-matching to catch minor spelling mistakes in country names, because typing errors are bound to be common and silently failing would make the program frustrating to use. Instead of correcting the input automatically, the program suggests the closest match and asks the user to confirm, so it never guesses wrong on the user's behalf.
- **Choosing the latest year with sufficient data:** For the "world leader" option, `find_extreme` uses the most recent year that has enough data for the chosen metric, rather than simply using the newest year in the dataset. The newest year is often incomplete, so this approach gives the most up-to-date result that is still accurate and well-rounded.
- **Testing structure rather than exact values:** My tests check the *shape* of what each function returns — the correct type, the expected keys, `None` for invalid input, instead of asserting exact numbers. This is deliberate as the underlying dataset is updated over time, so a test like `assert value == 21.3` would break the moment the data changed. Testing structure and behaviour keeps the tests valid regardless of data updates.
- **Presenting comparisons as a table:** For the two-country comparison, I used the `tabulate` library to display the results in a bordered table rather than plain lines of text. This makes the figures far easier to read and lets the user compare the two countries at a glance.

---

## What I Learned

- **Formatting output with `tabulate`:** When I first built the comparison table, I wanted positive and negative changes to show clearly with a `+` or `-` sign. The signs kept vanishing, and it took some digging to work out why: `tabulate` was reparsing my formatted values back into plain numbers. I fixed it by passing `disable_numparse=True`, which tells `tabulate` to leave the strings exactly as I formatted them. This taught me that a library can quietly override your own formatting, and that understanding *why* something breaks matters more than guessing at fixes.
- **Returning the right values from a function:** I wanted `find_extreme` to return the year the data came from, alongside the country and the value. I hit a bug where the function returned only two values while `main` expected three, which caused the program to crash. Tracking it down taught me to make sure a function's return value always matches what the code calling it expects.
- **Working with messy real-world data:** The dataset was far from clean as many countries had blank cells for certain years and metrics, and there were rows like "World" and "Europe" mixed in with actual countries. I had to filter these out and handle the gaps so the program only worked with valid data. This showed me that real datasets rarely come ready to use, and that a good chunk of data analysis is just cleaning and filtering before any real work can happen.
- **Testing data that changes over time:** Because the dataset is updated periodically, I learned that I couldn't test my functions against exact values, a test checking for a specific number would fail as soon as the data was refreshed, even though the code was still correct. This pushed me to think differently about testing. Instead of checking exact answers, I tested the structure and behaviour of my functions, which stays valid no matter how the data numbers change. It was a useful lesson in writing tests that are robust rather than brittle.
