# Salsoul Records Dashboard

## Overview
The **Salsoul Records Dashboard** is a web-based interactive application built using **Streamlit** that allows users to explore the iconic releases from the legendary Salsoul Records label. It provides visual insights, filterable data, and detailed information about the label's releases, including clickable links to Discogs and YouTube videos.

## Features

### 1. Releases Per Year
 An interactive bar chart displaying the number of releases per year throughout Salsoul's history
 Highlights trends and peaks in the label's production over time

### 2. Top 5 Most Collected Releases
 Displays the top 5 releases with the highest collection counts by Discogs users
 Includes clickable album covers linked directly to Discogs pages

### 3. Filterable Artist and Year Data
 A sidebar allows users to filter releases by artist and year
 Displays detailed information about each filtered release, including:
  Album cover (clickable link to Discogs)
  Title, year, and "In Collection" stats
  First available YouTube link (if any)

### 4. Releases by Format
 A bar chart summarizing the distribution of releases by format (e.g., vinyl, CD, etc.)

### 5. Releases Timeline
 A line chart showing the number of releases over time for the selected artist

### 6. Data Download
 Allows users to download filtered data as a CSV file for offline analysis

## How It Works
 The app reads data from a pre-processed CSV file (`salsoul_releases_updated_5_final_version.csv`)
 Data is dynamically fetched from the **Discogs API** to enhance information, such as:
  Links to Discogs release pages
  YouTube video links associated with releases
 Streamlit's layout and interactivity provide a clean and user-friendly interface

## Installation and Setup

### Prerequisites
 Python 3.8 or higher
 Required Python packages:
  `streamlit`
  `pandas`
  `altair`
  `requests`
