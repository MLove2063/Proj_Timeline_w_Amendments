import pandas as pd
import json
from datetime import datetime

# Read and prepare the data
df = pd.read_csv('Master Tracker 04162025.csv', encoding='windows-1252')
df.columns = df.columns.str.strip()

# Convert dates and clean data
df['Project Start Date'] = pd.to_datetime(df['Project Start Date'], errors='coerce')
df['Project End Date'] = pd.to_datetime(df['Project End Date'], errors='coerce')

# Clean and convert Award Amount - remove any currency symbols and commas, then convert to float
df['Award Amount'] = df['Award Amount'].astype(str).str.replace('$', '').str.replace(',', '').str.replace('(', '-').str.replace(')', '')
df['Award Amount'] = pd.to_numeric(df['Award Amount'], errors='coerce')

# Remove rows with invalid dates
df = df.dropna(subset=['Project Start Date', 'Project End Date'])

# Sort by end date
df = df.sort_values('Project End Date', ascending=True)

# Create color coding
today = datetime.now()
df['Status'] = df['Project End Date'].apply(lambda x: 'Closed' if x < today else 'Active')
df['Color'] = df['Status'].map({'Closed': 'grey', 'Active': 'rgb(30, 144, 255)'})

# Convert DataFrame to list of dictionaries for JSON, converting dates to strings
json_data = []
for _, row in df.iterrows():
    data_dict = row.to_dict()
    # Convert datetime objects to strings
    if isinstance(data_dict['Project Start Date'], pd.Timestamp):
        data_dict['Project Start Date'] = data_dict['Project Start Date'].strftime('%Y-%m-%d')
    if isinstance(data_dict['Project End Date'], pd.Timestamp):
        data_dict['Project End Date'] = data_dict['Project End Date'].strftime('%Y-%m-%d')
    # Ensure Award Amount is a number
    if pd.isna(data_dict['Award Amount']):
        data_dict['Award Amount'] = 0
    else:
        data_dict['Award Amount'] = float(data_dict['Award Amount'])
    json_data.append(data_dict)

# Print some debug information
print(f"Total number of awards: {len(df)}")
print(f"Total award amount: ${df['Award Amount'].sum():,.2f}")
print(f"Number of awards with non-zero amount: {(df['Award Amount'] > 0).sum()}")

# Read amendment data
amendment_data = {}
try:
    amendment_df = pd.read_excel('Award_Details_20250505.xlsx', sheet_name='Award Details')
    print(f"\nReading amendment data from Award_Details_20250505.xlsx")
    print(f"Number of records: {len(amendment_df)}")
    
    # Group amendments by FAIN
    for _, row in amendment_df.iterrows():
        fain = row['FAIN']
        amendment_type = row['Amendment Type']
        
        # Only process rows that have a FAIN and a non-empty Amendment Type
        if pd.isna(fain) or pd.isna(amendment_type) or str(amendment_type).strip() == '':
            continue
            
        if fain not in amendment_data:
            amendment_data[fain] = []
        
        # Get the amendment date from Day of Award Issue Date
        amendment_date = row['Day of Award Issue Date']
        if pd.notna(amendment_date):
            if isinstance(amendment_date, pd.Timestamp):
                amendment_date = amendment_date.strftime('%Y-%m-%d')
            
            amendment_data[fain].append({
                'date': amendment_date,
                'type': str(amendment_type).strip()
            })
    
    print(f"Number of awards with amendments: {len(amendment_data)}")
    total_amendments = sum(len(amendments) for amendments in amendment_data.values())
    print(f"Total number of amendments: {total_amendments}")
    
    # Print some sample amendment data
    print("\nSample amendment data:")
    sample_fains = list(amendment_data.keys())[:3]
    for fain in sample_fains:
        print(f"\nFAIN: {fain}")
        for amendment in amendment_data[fain]:
            print(f"  - Date: {amendment['date']}, Type: {amendment['type']}")
    
except Exception as e:
    print(f"Warning: Could not read amendment data: {e}")
    print("Exception details:", str(e.__class__.__name__))
    import traceback
    traceback.print_exc()
    amendment_data = {}

# Create the HTML file with embedded data
html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>GCERC Award Timeline with Filtering</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f8f9fa;
        }}
        .bar {{
            fill-opacity: 0.8;
        }}
        .bar:hover {{
            fill-opacity: 1;
        }}
        .axis text {{
            font-size: 16px;
        }}
        .axis path,
        .axis line {{
            fill: none;
            stroke: #000;
            shape-rendering: crispEdges;
        }}
        .grid line {{
            stroke: lightgrey;
            stroke-opacity: 0.7;
            shape-rendering: crispEdges;
        }}
        .grid path {{
            stroke-width: 0;
        }}
        .legend-box {{
            fill: white;
            stroke: #ccc;
            stroke-width: 1px;
            rx: 5;
            ry: 5;
        }}
        .legend-title {{
            font-size: 18px;
            font-weight: bold;
        }}
        .legend-subtitle {{
            font-size: 16px;
            font-weight: bold;
            fill: #666;
        }}
        .legend-text {{
            font-size: 14px;
        }}
        .legend-total {{
            font-size: 14px;
            font-weight: bold;
            fill: #444;
        }}
        .tooltip {{
            position: absolute;
            padding: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            border-radius: 4px;
            font-size: 14px;
            pointer-events: none;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}
        .today-line {{
            stroke: red;
            stroke-width: 2;
            stroke-dasharray: 5,5;
        }}
        .today-date {{
            fill: red;
            font-size: 14px;
            font-weight: bold;
        }}
        .filter-controls {{
            margin-bottom: 20px;
            padding: 15px;
            background: white;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .filter-select {{
            margin-right: 20px;
            font-size: 14px;
            padding: 8px;
            min-width: 200px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }}
        #timeline {{
            background: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .graph-title {{
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        .date-slider-container {{
            margin: 20px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .date-label {{
            font-size: 18px;
            font-weight: bold;
            color: #444;
            margin-bottom: 15px;
            text-align: center;
        }}
        .date-slider {{
            -webkit-appearance: none;
            width: 100%;
            height: 8px;
            border-radius: 4px;
            background: #e0e0e0;
            outline: none;
            margin: 20px 0;
            box-shadow: inset 0 1px 3px rgba(0,0,0,0.2);
        }}
        .date-slider::-webkit-slider-thumb {{
            -webkit-appearance: none;
            appearance: none;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #2196F3;
            cursor: pointer;
            border: 2px solid white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            transition: all 0.2s ease;
        }}
        .date-slider::-webkit-slider-thumb:hover {{
            background: #1976D2;
            transform: scale(1.1);
        }}
        .date-slider::-moz-range-thumb {{
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #2196F3;
            cursor: pointer;
            border: 2px solid white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            transition: all 0.2s ease;
        }}
        .date-slider::-moz-range-thumb:hover {{
            background: #1976D2;
            transform: scale(1.1);
        }}
        .date-slider::-webkit-slider-runnable-track {{
            height: 8px;
            border-radius: 4px;
            background: linear-gradient(to right, #e0e0e0, #2196F3);
        }}
        .date-slider::-moz-range-track {{
            height: 8px;
            border-radius: 4px;
            background: linear-gradient(to right, #e0e0e0, #2196F3);
        }}
        .date-slider:focus {{
            outline: none;
        }}
        .date-slider:focus::-webkit-slider-thumb {{
            box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.3);
        }}
        .date-slider:focus::-moz-range-thumb {{
            box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.3);
        }}
    </style>
</head>
<body>
    <div class="filter-controls">
        <select id="grantLeadFilter" class="filter-select">
            <option value="">All Grant Leads</option>
        </select>
        <select id="programStaffFilter" class="filter-select">
            <option value="">All Program Staff</option>
        </select>
    </div>
    <div class="date-slider-container">
        <div class="date-label">Timeline Position: <span id="selectedDate"></span></div>
        <input type="range" id="dateSlider" class="date-slider" step="1">
    </div>
    <div class="graph-title">GCERC Award Timeline</div>
    <div id="timeline"></div>
    <script>
        // Process data first
        const today = new Date();

        // Embed the project data directly
        const jsonData = {json.dumps(json_data)};

        // Embed the amendment data directly
        const amendmentData = {json.dumps(amendment_data)};

        // Process the embedded data
        const data = jsonData.map(d => {{
            const startDate = new Date(d['Project Start Date']);
            const endDate = new Date(d['Project End Date']);
            return {{
                ...d,
                startDate: startDate,
                endDate: endDate,
                status: endDate < today ? 'Closed' : 'Active',
                color: endDate < today ? 'grey' : 'rgb(30, 144, 255)'
            }};
        }})
        .filter(d => !isNaN(d.startDate) && !isNaN(d.endDate))
        .sort((a, b) => b.endDate - a.endDate);  // Sort by end date descending

        // Set up date slider
        const minDate = d3.min(data, d => d.startDate);
        const maxDate = d3.max(data, d => d.endDate);
        const dateSlider = document.getElementById('dateSlider');
        dateSlider.min = minDate.getTime();
        dateSlider.max = maxDate.getTime();
        dateSlider.value = today.getTime();

        // Format date for display
        const formatDate = d3.timeFormat("%B %d, %Y");
        document.getElementById('selectedDate').textContent = formatDate(today);

        // Update date label when slider moves
        dateSlider.addEventListener('input', function() {{
            const selectedDate = new Date(parseInt(this.value));
            document.getElementById('selectedDate').textContent = formatDate(selectedDate);
            updateVisualization(getFilteredData(), selectedDate);
        }});

        console.log("Number of valid projects:", data.length);

        // Populate dropdown menus
        const grantLeads = [...new Set(data.map(d => d['Grant Lead']).filter(Boolean))].sort();
        const programStaff = [...new Set(data.map(d => d['Programs Staff Lead']).filter(Boolean))].sort();

        const grantLeadSelect = d3.select("#grantLeadFilter");
        const programStaffSelect = d3.select("#programStaffFilter");

        grantLeads.forEach(lead => {{
            grantLeadSelect.append("option")
                .attr("value", lead)
                .text(lead);
        }});

        programStaff.forEach(staff => {{
            programStaffSelect.append("option")
                .attr("value", staff)
                .text(staff);
        }});

        // Set up dimensions
        const margin = {{top: 200, right: 100, bottom: 50, left: 250}};
        const width = 1920 - margin.left - margin.right;
        const barHeight = 15;
        const height = Math.max(400, data.length * barHeight);

        // Create SVG
        const svg = d3.select("#timeline")
            .append("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${{margin.left}},${{margin.top}})`);

        // Set up scales
        const x = d3.scaleTime()
            .domain([minDate, maxDate])
            .range([0, width]);

        const y = d3.scaleBand()
            .domain(data.map(d => d.FAIN))
            .range([0, height])
            .padding(0.2);

        function getFilteredData() {{
            const selectedGrantLead = d3.select("#grantLeadFilter").property("value");
            const selectedProgramStaff = d3.select("#programStaffFilter").property("value");

            let filteredData = data;

            if (selectedGrantLead) {{
                filteredData = filteredData.filter(d => d['Grant Lead'] === selectedGrantLead);
            }}
            if (selectedProgramStaff) {{
                filteredData = filteredData.filter(d => d['Programs Staff Lead'] === selectedProgramStaff);
            }}

            return filteredData;
        }}

        // Function to update the visualization
        function updateVisualization(filteredData, selectedDate) {{
            // Update status and colors based on selected date
            filteredData.forEach(d => {{
                d.status = d.endDate < selectedDate ? 'Closed' : 'Active';
                d.color = d.endDate < selectedDate ? 'grey' : 'rgb(30, 144, 255)';
            }});

            // Update y-scale domain with filtered data
            y.domain(filteredData.map(d => d.FAIN));

            // Update height
            const newHeight = Math.max(400, filteredData.length * barHeight);
            d3.select("#timeline svg")
                .attr("height", newHeight + margin.top + margin.bottom);

            // Update y-scale range
            y.range([0, newHeight]);

            // Update bars
            const bars = svg.selectAll(".bar")
                .data(filteredData, d => d.FAIN);

            // Remove old bars
            bars.exit().remove();

            // Add new bars and update existing ones
            bars.enter()
                .append("rect")
                .attr("class", "bar")
                .merge(bars)
                .attr("x", d => x(d.startDate))
                .attr("y", d => y(d.FAIN))
                .attr("width", d => Math.max(1, x(d.endDate) - x(d.startDate)))
                .attr("height", y.bandwidth())
                .attr("fill", d => d.color);

            // Update axes
            svg.selectAll(".axis").remove();

            // Add x-axis
            svg.append("g")
                .attr("class", "axis")
                .attr("transform", `translate(0,${{newHeight}})`)
                .call(d3.axisBottom(x)
                    .ticks(d3.timeYear.every(1))
                    .tickFormat(d3.timeFormat("%Y")));

            // Add y-axis
            svg.append("g")
                .attr("class", "axis")
                .call(d3.axisLeft(y));

            // Add grid lines
            svg.append("g")
                .attr("class", "grid")
                .attr("transform", `translate(0,${{newHeight}})`)
                .call(d3.axisBottom(x)
                    .ticks(d3.timeYear.every(1))
                    .tickSize(-newHeight)
                    .tickFormat(""));

            // Update date line
            svg.selectAll(".today-line, .today-date").remove();
            svg.append("line")
                .attr("class", "today-line")
                .attr("x1", x(selectedDate))
                .attr("x2", x(selectedDate))
                .attr("y1", 0)
                .attr("y2", newHeight);
            
            svg.append("text")
                .attr("class", "today-date")
                .attr("x", x(selectedDate))
                .attr("y", -5)
                .attr("text-anchor", "middle")
                .text(formatDate(selectedDate));

            // Calculate award totals based on selected date
            const closedTotal = filteredData
                .filter(d => d.status === 'Closed')
                .reduce((sum, d) => sum + (typeof d['Award Amount'] === 'number' ? d['Award Amount'] : 0), 0);
            
            const activeTotal = filteredData
                .filter(d => d.status === 'Active')
                .reduce((sum, d) => sum + (typeof d['Award Amount'] === 'number' ? d['Award Amount'] : 0), 0);

            // Calculate amendments up to selected date
            const amendmentsUpToDate = Object.entries(amendmentData).reduce((count, [fain, amendments]) => {{
                const validAmendments = amendments.filter(a => {{
                    const amendDate = new Date(a.date);
                    return amendDate <= selectedDate;
                }});
                return count + validAmendments.length;
            }}, 0);

            // Update legend
            svg.selectAll(".legend").remove();
            
            const legend = svg.append("g")
                .attr("class", "legend")
                .attr("transform", "translate(" + (-margin.left + 20) + ", " + (-margin.top + 20) + ")");

            // Add legend background
            const legendPadding = 15;
            const legendWidth = 480;
            const legendHeight = 150;
            
            legend.append("rect")
                .attr("class", "legend-box")
                .attr("x", 0)
                .attr("y", 0)
                .attr("width", legendWidth)
                .attr("height", legendHeight);

            // Calculate grand total based on selected date
            const grandTotal = filteredData
                .filter(d => d.startDate <= selectedDate)  // Only include awards that have started by the selected date
                .reduce((sum, d) => sum + (typeof d['Award Amount'] === 'number' ? d['Award Amount'] : 0), 0);

            // Format currency
            const formatCurrency = new Intl.NumberFormat('en-US', {{
                style: 'currency',
                currency: 'USD',
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            }});

            // Add main title with grand total
            legend.append("text")
                .attr("class", "legend-title")
                .attr("x", legendPadding)
                .attr("y", legendPadding + 15)
                .text("All Awards: ");

            legend.append("text")
                .attr("class", "legend-subtitle")
                .attr("x", legendPadding + 120)
                .attr("y", legendPadding + 15)
                .style("font-size", "18px")
                .text(formatCurrency.format(grandTotal));

            const statuses = ['Closed', 'Active'];
            const colors = ['grey', 'rgb(30, 144, 255)'];
            const totals = [closedTotal, activeTotal];

            statuses.forEach((status, i) => {{
                const legendRow = legend.append("g")
                    .attr("transform", "translate(" + legendPadding + ", " + (legendPadding + 35 + (i * 30)) + ")");

                // Add color box
                legendRow.append("rect")
                    .attr("width", 16)
                    .attr("height", 16)
                    .attr("fill", colors[i]);

                // Add status label
                legendRow.append("text")
                    .attr("class", "legend-text")
                    .attr("x", 24)
                    .attr("y", 12)
                    .text(status + " Awards:");

                // Add total amount
                legendRow.append("text")
                    .attr("class", "legend-total")
                    .attr("x", 24)
                    .attr("y", 12)
                    .attr("dx", "120")
                    .text(formatCurrency.format(totals[i]));
            }});

            // Add amendment marker to legend
            const amendmentRow = legend.append("g")
                .attr("transform", "translate(" + legendPadding + ", " + (legendPadding + 95) + ")");

            // Add amendment line
            amendmentRow.append("line")
                .attr("x1", 0)
                .attr("x2", 0)
                .attr("y1", 0)
                .attr("y2", 16)
                .attr("stroke", "black")
                .attr("stroke-width", 2);

            // Add amendment label with count up to selected date
            amendmentRow.append("text")
                .attr("class", "legend-text")
                .attr("x", 24)
                .attr("y", 12)
                .text("Amendment Date (n = " + amendmentsUpToDate + ")");

            // Add date of data text at bottom right of legend
            legend.append("text")
                .attr("class", "data-date")
                .attr("x", legendWidth - legendPadding)
                .attr("y", legendHeight - legendPadding)
                .attr("text-anchor", "end")
                .style("font-size", "14px")
                .style("fill", "#666")
                .text("Date of Source Data = April 19, 2025");

            // Update tooltips
            svg.selectAll(".bar")
                .on("mouseover", function(event, d) {{
                    const tooltip = d3.select("body")
                        .append("div")
                        .attr("class", "tooltip")
                        .style("opacity", 0);

                    tooltip.transition()
                        .duration(200)
                        .style("opacity", .9);
                    tooltip.html(`<b>${{d.Title}}</b><br>
                                FAIN: ${{d.FAIN}}<br>
                                Duration: ${{d3.timeFormat("%Y-%m-%d")(d.startDate)}} to ${{d3.timeFormat("%Y-%m-%d")(d.endDate)}}<br>
                                Award Amount: $${{d['Award Amount']?.toLocaleString() || 'N/A'}}<br>
                                Grant Lead: ${{d['Grant Lead'] || 'N/A'}}<br>
                                Program Staff: ${{d['Programs Staff Lead'] || 'N/A'}}`)
                        .style("left", (event.pageX + 10) + "px")
                        .style("top", (event.pageY - 28) + "px");
                }})
                .on("mouseout", function() {{
                    d3.selectAll(".tooltip").remove();
                }});

            // Add amendment lines up to selected date
            svg.selectAll(".amendment-line").remove();
            filteredData.forEach(d => {{
                const amendments = amendmentData[d.FAIN] || [];
                amendments.forEach(amendment => {{
                    if (amendment.date) {{
                        const amendmentDate = new Date(amendment.date);
                        if (amendmentDate <= selectedDate && amendmentDate >= d.startDate && amendmentDate <= d.endDate) {{
                            svg.append("line")
                                .attr("class", "amendment-line")
                                .attr("x1", x(amendmentDate))
                                .attr("x2", x(amendmentDate))
                                .attr("y1", y(d.FAIN))
                                .attr("y2", y(d.FAIN) + y.bandwidth())
                                .attr("stroke", "black")
                                .attr("stroke-width", 2)
                                .style("pointer-events", "all")
                                .on("mouseover", function(event) {{
                                    const tooltip = d3.select("body")
                                        .append("div")
                                        .attr("class", "tooltip")
                                        .style("opacity", 0);

                                    tooltip.transition()
                                        .duration(200)
                                        .style("opacity", .9);
                                    tooltip.html(`Amendment Date: ${{amendment.date}}<br>
                                                Type: ${{amendment.type || 'N/A'}}`)
                                        .style("left", (event.pageX + 10) + "px")
                                        .style("top", (event.pageY - 28) + "px");
                                }})
                                .on("mouseout", function() {{
                                    d3.selectAll(".tooltip").remove();
                                }});
                        }}
                    }}
                }});
            }});
        }}

        // Initial visualization with all data
        updateVisualization(data, today);

        // Add filter event listeners
        d3.select("#grantLeadFilter").on("change", function() {{
            updateVisualization(getFilteredData(), new Date(dateSlider.value));
        }});
        d3.select("#programStaffFilter").on("change", function() {{
            updateVisualization(getFilteredData(), new Date(dateSlider.value));
        }});

        console.log(`Loaded ${{data.length}} projects`);
    </script>
</body>
</html>
'''

# Write the HTML file
with open('project_timeline_d3_filtered.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("D3.js timeline visualization has been saved to 'project_timeline_d3_filtered.html'") 