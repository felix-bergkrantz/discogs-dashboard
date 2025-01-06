import streamlit as st
import pandas as pd
import ast
import requests
import altair as alt

# Load the CSV file
@st.cache_data  # Cache the data for faster loading
def load_data():
    try:
        df = pd.read_csv('salsoul_releases_updated_5.csv')
        
        # Extract stats from the 'Stats' column
        def extract_stats(stats_str):
            try:
                stats = ast.literal_eval(stats_str)  # Safely parse the string
                community = stats.get('community', {})
                return community.get('in_wantlist', 0), community.get('in_collection', 0)
            except (ValueError, SyntaxError, AttributeError):
                return 0, 0

        df['in_wantlist'], df['in_collection'] = zip(*df['Stats'].apply(extract_stats))
        return df
    except FileNotFoundError:
        st.error("The file 'salsoul_releases_updated_5.csv' was not found.")
        return pd.DataFrame()  # Return an empty DataFrame if the file is missing

df = load_data()

def fetch_release_data(release_id):
    base_url = f"https://api.discogs.com/releases/{release_id}"
    headers = {'User-Agent': 'SalsoulApp/1.0 +https://mywebsite.com'}
    response = requests.get(base_url, headers=headers)
    if response.status_code == 200:
        release_data = response.json()
        return {
            "youtube_links": [
                video['uri'] for video in release_data.get('videos', []) if "youtube.com" in video.get('uri', "")
            ],
            "uri": release_data.get('uri', None)  # Extract the Discogs release URL
        }
    else:
        return {"youtube_links": [], "uri": None}


# Stop execution if the DataFrame is empty
if df.empty:
    st.stop()

# Header image
st.image(
    "https://images.squarespace-cdn.com/content/v1/62fe9c18730c7512708cb412/09b5243b-3ba2-41b7-af86-a43b898dcac6/salsoul-records.png?format=1500w",  # Replace with your image path or URL
    caption="Welcome to the Salsoul Records interactive Dashboard",
    use_container_width=True
)

# Check for the necessary columns
cover_column = 'Thumb'  # Replace with the correct column name for album covers
if cover_column not in df.columns:
    st.error(f"The column '{cover_column}' is missing from the dataset.")
    st.stop()

# Inject custom CSS for image height
st.markdown(
    """
    <style>
    .album-cover {
        max-height: 150px;
        object-fit: contain;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Title and Description
st.title("Salsoul Records Dashboard")
st.write("""
Iconic US 1970s and early 1980s disco label based in New York City and one of the first to release a commercial 
(as opposed to promo-only) 12-inch single. It was founded by brothers Joe Cayre, Ken Cayre, and Stan Cayre, 
who appeared as executive producers on many productions.

The Cayre trio continued their business in computer games and video with Good Times Home Videos. 
In 1978, Salsoul's manufacturing & distribution was taken on by RCA Records. This agreement remained 
until Salsoul folded around 1985.

At the same time as the RCA deal, a solid red bar appears under the main Salsoul logo 
(e.g., Disco Boogie Vol. 2). In some cases, the red bar is not present. However, if you look closely 
at the design, you can see the red bar has been 'patched over' with the cloud illustration not aligned correctly 
(e.g., Inner Life - I Like It Like That).

Explore the releases from the Salsoul Records label using this interactive dashboard!
""")

# Releases by Year (All Data)
st.subheader("Releases Per Year throughout the Salsoul history")

if not df.empty:
    # Prepare the data
    releases_per_year = df['Year'].value_counts().reset_index()
    releases_per_year.columns = ['Year', 'Count']  # Rename columns to match Altair usage

    # Create an interactive heatmap-style bar chart with Altair
    chart = alt.Chart(releases_per_year).mark_bar().encode(
        x=alt.X('Year:O', title='Year', sort='ascending'),
        y=alt.Y('Count:Q', title='Number of Releases'),
        color=alt.Color('Count:Q', scale=alt.Scale(scheme='viridis'), title='Count'),
        tooltip=['Year', 'Count']
    ).properties(
        title="Releases Per Year",
        width=600,
        height=400
    )
    
    # Display the chart in Streamlit
    st.altair_chart(chart, use_container_width=True)
else:
    st.write("No data available.")


# Top 5 Most Collected Releases
st.subheader("Top 5 Most Collected Releases by Discogs users")

unique_df = df.drop_duplicates(subset=['Release Title', 'Year'])
top_collected = unique_df.sort_values(by='in_collection', ascending=False).head(5)

if not top_collected.empty:
    num_columns = 5
    columns = st.columns(num_columns)

    for idx, row in enumerate(top_collected.iterrows()):
        row_data = row[1]
        col = columns[idx % num_columns]
        with col:
            release_id = row_data['ID']
            release_data = fetch_release_data(release_id)
            release_url = release_data["uri"]

            if pd.notnull(row_data[cover_column]):
                # Clickable image
                if release_url:
                    st.markdown(
                        f"""
                        <a href="{release_url}" target="_blank" style="text-decoration:none;">
                            <img src="{row_data[cover_column]}" alt="Album Cover" class="album-cover">
                        </a>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <img src="{row_data[cover_column]}" alt="Album Cover" class="album-cover">
                        """,
                        unsafe_allow_html=True
                    )

            # Title and collection count
            st.caption(f"{row_data['Artist']} - {row_data['Release Title']} - {row_data['Year']}")
            st.write(f"**In Collection**: {row_data['in_collection']}")
else:
    st.write("No data available for the top collected releases.")


# Sidebar filters
st.sidebar.header("Filter Options")

# Artist dropdown menu
artist_filter = st.sidebar.selectbox(
    "Select Artist:",
    options=["All Artist"] + sorted(df['Artist'].dropna().unique()),  # Dropdown menu for unique artists
    help="Select an artist to view their releases."
)

# Filter data by selected artist
filtered_df = df[df['Artist'] == artist_filter]  # Filter the DataFrame by selected artist

# Year filter for the selected artist
year_filter = st.sidebar.multiselect(
    "Select Year(s):",
    options=sorted(filtered_df['Year'].dropna().unique()),  # Unique years for the selected artist
    default=sorted(filtered_df['Year'].dropna().unique()),  # Pre-select all years by default
    help="Select one or more years to filter releases."
)

# Apply year filter
filtered_df = filtered_df[filtered_df['Year'].isin(year_filter)]

# Display filtered data with album covers, stats, and Discogs links
st.subheader(f"Releases by {artist_filter}")

if not filtered_df.empty:
    num_columns = 3  # Display 3 releases per row
    columns = st.columns(num_columns)  # Create columns for the grid

    for idx, row in enumerate(filtered_df.iterrows()):
        row_data = row[1]
        col = columns[idx % num_columns]
        with col:
            # Check if release_id exists
            release_id = row_data.get('ID', None)
            if release_id:
                release_data = fetch_release_data(release_id)
                release_url = release_data.get("uri", None)
                youtube_links = release_data.get("youtube_links", [])
            else:
                release_data = {"youtube_links": [], "uri": None}
                release_url = None
                youtube_links = []

            # Display clickable album cover or plain image
            if pd.notnull(row_data[cover_column]):
                if release_url:
                    st.markdown(
                        f"""
                        <a href="{release_url}" target="_blank" style="text-decoration:none;">
                            <img src="{row_data[cover_column]}" alt="Album Cover" class="album-cover">
                        </a>
                        """,
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"""
                        <img src="{row_data[cover_column]}" alt="Album Cover" class="album-cover">
                        """,
                        unsafe_allow_html=True
                    )

            # Title and collection count
            st.caption(f"{row_data['Year']} - {row_data['Release Title']}")
            st.write(f"**In Collection**: {row_data['in_collection']}")

            # Display the first YouTube link if available
            if youtube_links:
                first_link = youtube_links[0]
                st.markdown(f"**[Watch on YouTube]({first_link})**")
            else:
                st.write("No YouTube link available.")
else:
    st.write(f"No data available for {artist_filter} in the selected years.")


# Releases by Format for the Selected Artist
st.subheader(f"Releases by Format for {artist_filter}")

if not filtered_df.empty:
    format_counts = filtered_df['Format'].value_counts().reset_index()
    format_counts.columns = ['Format', 'Count']

    # Create a bar chart
    chart = alt.Chart(format_counts).mark_bar().encode(
        x=alt.X('Format:O', title='Format', sort='ascending'),
        y=alt.Y('Count:Q', title='Number of Releases'),
        color=alt.Color('Count:Q', scale=alt.Scale(scheme='plasma')),
        tooltip=['Format', 'Count']
    ).properties(
        title=f"Releases by Format for {artist_filter}",
        width=600,
        height=400
    )

    st.altair_chart(chart, use_container_width=True)
else:
    st.write(f"No data available for {artist_filter} in the selected years.")


# Releases Timeline for the Selected Artist
st.subheader(f"Releases Timeline for {artist_filter}")

if not filtered_df.empty:
    releases_per_year = filtered_df['Year'].value_counts().reset_index()
    releases_per_year.columns = ['Year', 'Count']

    # Line chart showing the number of releases over time
    chart = alt.Chart(releases_per_year).mark_line(point=True).encode(
        x=alt.X('Year:O', title='Year', sort='ascending'),
        y=alt.Y('Count:Q', title='Number of Releases'),
        tooltip=['Year', 'Count']
    ).properties(
        title=f"Releases Timeline for {artist_filter}",
        width=600,
        height=400
    )

    st.altair_chart(chart, use_container_width=True)
else:
    st.write(f"No data available for {artist_filter} in the selected years.")
