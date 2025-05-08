# GCERC Award Timeline Visualization

## Overview
This interactive visualization displays the timeline of GCERC (Gulf Coast Ecosystem Restoration Council) awards, including their status, amendments, and associated funding amounts. The visualization allows users to explore award data through time, filter by grant leads and program staff, and track amendments to awards.

## Features

### Interactive Timeline
- **Date Slider**: Move through time to see how awards and their statuses change
- **Award Bars**: Each horizontal bar represents an award
  - Blue bars: Active awards
  - Grey bars: Closed awards
- **Amendment Markers**: Black vertical lines indicate amendment dates
- **Today's Date**: Red dashed line shows the current date

### Filtering Options
- **Grant Lead**: Filter awards by specific grant leads
- **Program Staff**: Filter awards by program staff members

### Legend Information
- Total award amounts
- Breakdown of active vs. closed awards
- Amendment count
- Data source date

## How to Use

1. **Date Navigation**
   - Use the timeline slider at the top to move through different dates
   - The visualization updates in real-time to show:
     - Award statuses (Active/Closed)
     - Total award amounts
     - Amendment counts
     - Amendment markers

2. **Filtering**
   - Use the dropdown menus to filter by:
     - Grant Lead
     - Program Staff
   - Filters can be used in combination
   - Select "All" to clear a filter

3. **Hover Information**
   - Hover over any award bar to see:
     - Award title
     - FAIN (Federal Award Identification Number)
     - Duration
     - Award amount
     - Grant lead
     - Program staff
   - Hover over amendment markers to see:
     - Amendment date
     - Amendment type

## Data Sources

### Award Data
- Source: Master Tracker CSV file
- Last Updated: April 16, 2025
- Contains:
  - Award details
  - Project timelines
  - Funding amounts
  - Grant leads
  - Program staff

### Amendment Data
- Source: Award Details Excel file
- Last Updated: May 5, 2025
- Contains:
  - Amendment dates
  - Amendment types
  - Associated FAINs

## Technical Details

### Files
- `project_timeline_d3_filtered.html`: Main visualization file
- `timeline_visualization.py`: Python script for generating the visualization
- `process_amendments.py`: Python script for processing amendment data
- `Master Tracker 04162025.csv`: Source data for awards
- `Award_Details_20250505.xlsx`: Source data for amendments

### Dependencies
- Python 3.x
- Required Python packages:
  - pandas
  - openpyxl (for Excel file processing)

## Viewing the Visualization
1. Open `project_timeline_d3_filtered.html` in a web browser
2. No additional setup required - all data is embedded in the HTML file

## Data Processing
The visualization is generated through the following steps:
1. Python scripts process the raw data files
2. Data is converted to JSON format
3. D3.js visualization is generated with embedded data
4. Interactive features are added for filtering and time navigation

## Notes
- All monetary values are in USD
- Dates are in YYYY-MM-DD format
- Amendment markers only appear for amendments that occurred during the award's active period 