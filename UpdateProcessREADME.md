# Project Timeline Visualization - Weekly Update Process

This document explains how to update the project timeline visualization on a weekly basis using the provided automation scripts.

## Required Files

### Input Files
Place these files in the root directory (`C:\Users\Matt.Love\Projects\Project Management`):

1. `Awards.xlsx`
   - Source: Download from the current Master Tracker.xlsx
   - Required columns:
     - Award Number (FAIN)
     - Project Title
     - Award Date
     - End Date
     - Award Amount
     - Status
     - Award Type
     - Grant Staff Lead
     - Programs Staff Lead

2. `amendments.xlsx`
   - Source: Award Details tab from the "Award_Details_Active Applications and Amendments" Excel file (weekly report)
   - Required columns:
     - FAIN (Award Number)
     - Day of Award Issue Date
     - Amendment Type
     - Amount

### Script Files
These files should already be in place:

1. `update_visualization.py`
   - Python script that processes the Excel files and generates the visualization
   - Requires Python packages: pandas, openpyxl

2. `update_graph.bat`
   - Batch file that runs the update process
   - Handles virtual environment activation and script execution

3. Required directories:
   - `css/` - Contains styles.css
   - `js/` - Contains timeline.js

## Weekly Update Process

1. **Prepare Files**
   a. Create Awards.xlsx:
      - Open the current Master Tracker.xlsx
      - Save a copy as "Awards.xlsx" in the root directory
      - Ensure all required columns are present
      - Note: Projects without a Programs Staff Lead will show as "Unassigned" in the visualization

   b. Create amendments.xlsx:
      - Open the "Award_Details_Active Applications and Amendments" Excel file from the weekly report
      - Go to the "Award Details" tab
      - Save a copy as "amendments.xlsx" in the root directory
      - Ensure the required columns are present and properly formatted

2. **Run Update**
   - Double-click `update_graph.bat`
   - The script will:
     - Check for required files
     - Process the Excel data
     - Generate a new visualization
     - Save it in the `output` folder with today's date

3. **Output**
   - The new visualization will be saved as:
     `output/project_timeline_YYYYMMDD.html`
   - Each week's update creates a new file, preserving historical versions

## Troubleshooting

If you encounter any issues:

1. **File Not Found Errors**
   - Ensure both Excel files are in the root directory
   - Verify file names are exactly: `Awards.xlsx` and `amendments.xlsx`
   - Check that files are not open in Excel

2. **Python Package Errors**
   - Ensure the virtual environment is properly set up
   - Required packages: pandas, openpyxl
   - Run: `pip install pandas openpyxl` if needed

3. **Visualization Issues**
   - Check that the `css` and `js` directories contain required files
   - Verify Excel file column names match the required format
   - Ensure dates are in a valid format
   - If you see "NaN" in dropdowns, check for missing data in the source files

## Support

If you need assistance:
1. Check that all files are in the correct locations
2. Verify Excel file formats match the requirements
3. Contact the development team if issues persist 