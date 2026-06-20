import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(
    page_title="FIFA Player Dashboard",
    page_icon="⚽",
    layout="wide"
)

# 2. Load Data
@st.cache_data
def load_data():
    # Membaca data CSV yang diunggah
    df = pd.read_csv("fifa_player_performance_market_value.csv")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("File 'fifa_player_performance_market_value.csv' tidak ditemukan. Pastikan file berada di folder yang sama dengan app.py")
    st.stop()

# 3. Judul Dashboard
st.title("⚽ FIFA Player Performance & Market Value Dashboard")
st.markdown("Analisis interaktif performa pemain, rating, dan nilai pasar.")
st.markdown("---")

# 4. Sidebar Filter
st.sidebar.header("Filter Pemain")

# Filter Klub
all_clubs = ["Semua"] + sorted(df['club'].dropna().unique().tolist())
selected_club = st.sidebar.selectbox("Pilih Klub", all_clubs)

# Filter Posisi
all_positions = ["Semua"] + sorted(df['position'].dropna().unique().tolist())
selected_position = st.sidebar.selectbox("Pilih Posisi", all_positions)

# Filter Umur (Slider)
min_age, max_age = int(df['age'].min()), int(df['age'].max())
selected_age = st.sidebar.slider("Rentang Umur", min_age, max_age, (min_age, max_age))

# Pengaplikasian Filter ke Data
filtered_df = df.copy()
if selected_club != "Semua":
    filtered_df = filtered_df[filtered_df['club'] == selected_club]
if selected_position != "Semua":
    filtered_df = filtered_df[filtered_df['position'] == selected_position]
filtered_df = filtered_df[(filtered_df['age'] >= selected_age[0]) & (filtered_df['age'] <= selected_age[1])]

# 5. Bagian Metrik Utama (KPIs)
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Pemain (Filtered)", len(filtered_df))
with col2:
    avg_value = filtered_df['market_value_million_eur'].mean()
    st.metric("Rata-rata Market Value", f"€{avg_value:.2f} M")
with col3:
    avg_rating = filtered_df['overall_rating'].mean()
    st.metric("Rata-rata Overall Rating", f"{avg_rating:.1f}")
with col4:
    total_goals = filtered_df['goals'].sum()
    st.metric("Total Gol", f"{total_goals:,}")

st.markdown("---")

# 6. Bagian Visualisasi Grafik
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Rating vs Market Value")
    fig_scatter = px.scatter(
        filtered_df, 
        x="overall_rating", 
        y="market_value_million_eur",
        color="position",
        hover_name="player_name",
        hover_data=["club", "age"],
        labels={"overall_rating": "Overall Rating", "market_value_million_eur": "Market Value (€ Million)"},
        title="Hubungan Antara Rating dan Harga Pasar"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with chart_col2:
    st.subheader("Top 10 Pemain Termahal")
    top_10 = filtered_df.nlargest(10, 'market_value_million_eur')
    fig_bar = px.bar(
        top_10,
        x="market_value_million_eur",
        y="player_name",
        orientation='h',
        color="overall_rating",
        hover_data=["club", "position"],
        labels={"market_value_million_eur": "Market Value (€ Million)", "player_name": "Nama Pemain"},
        title="10 Pemain dengan Nilai Pasar Tertinggi (Berdasarkan Filter)"
    )
    fig_bar.update_layout(yaxis={'categoryorder':'total ascending'}) # Biar yang paling mahal di atas
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# 7. Tabel Data Mentah & Fitur Pencarian
st.subheader("🔍 Telusuri Data Pemain")
search_query = st.text_input("Cari nama pemain:", "")

if search_query:
    display_df = filtered_df[filtered_df['player_name'].str.contains(search_query, case=False, na=False)]
else:
    display_df = filtered_df

st.dataframe(
    display_df[['player_name', 'age', 'club', 'position', 'overall_rating', 'potential_rating', 'goals', 'assists', 'market_value_million_eur']], 
    use_container_width=True,
    hide_index=True
)