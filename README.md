# Netflix Engagement Report

Module to scrape engagement report data from Netflix, clean it, and create visualizations.

## Overview

This project is designed to automate the extraction, cleaning, and visualization of engagement data from Netflix reports. By leveraging Python, it streamlines the workflow from raw data acquisition to actionable insights.

## Features

- **Data Scraping:** Collects engagement report data from Netflix sources.
- **Data Cleaning:** Processes and cleans the scraped data for analysis.
- **Visualization:** Generates visuals to help understand engagement trends.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/daa2618/netflix_engagement_report.git
   cd netflix_engagement_report
   ```

2. Install the required dependencies:
   ```bash
   pip install .
   ```

## Usage

1. Run the main script to start scraping and processing data:
   ```bash
   from netflix_engagement_report import what_we_watched
   report_url = "https://about.netflix.com/en/news/what-we-watched-the-first-half-of-2025"

   what_we_watched.main(report_url)
   ```

2. Visualizations and processed data will be saved in the appropriate output folders.

## License

This project is licensed under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements.

## Author

- [daa2618](https://github.com/daa2618)



![Netflix Engagement Report Movies 2025Jan-Jun Hours Viewed](netflix_engagement_report/images/netflix_engagement_report_movies_2025Jan-Jun_hours_viewed.png)
![Netflix Engagement Report Movies 2025Jan-Jun Views](netflix_engagement_report/images/netflix_engagement_report_movies_2025Jan-Jun_views.png)
![Netflix Engagement Report Shows 2025Jan-Jun Hours Viewed](netflix_engagement_report/images/netflix_engagement_report_shows_2025Jan-Jun_hours_viewed.png)
![Netflix Engagement Report Shows 2025Jan-Jun Views](netflix_engagement_report/images/netflix_engagement_report_shows_2025Jan-Jun_views.png)
