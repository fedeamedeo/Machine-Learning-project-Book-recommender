import streamlit as st
import pandas as pd

# ---------- CONFIG ----------
st.set_page_config(page_title="📚 Book Recommender", layout="wide", initial_sidebar_state="expanded")

# ---------- GLOBAL STYLES ----------
st.markdown("""
    <style>
        .grey-button {
            background-color: #e0e0e0 !important;
            color: black !important;
            border: none;
            padding: 0.4rem 0.8rem;
            border-radius: 5px;
            cursor: pointer;
        }
        .grey-button:hover {
            background-color: #d5d5d5 !important;
        }
        .book-card {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            padding: 1rem;
            border-radius: 12px;
            box-shadow: 0 4px 14px rgba(0,0,0,0.06);
            background-color: #ffffff;
            min-width: 200px;
            max-width: 220px;
            flex: 0 0 auto;
        }
        .book-row-scroll {
            display: flex;
            overflow-x: auto;
            gap: 1rem;
            padding-bottom: 1rem;
        }
        .book-content {
            display: flex;
            gap: 2rem;
            width: 100%;
            align-items: flex-start;
        }
        .book-info {
            flex-grow: 1;
        }
        .book-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "expanded_book_id" not in st.session_state:
    st.session_state.expanded_book_id = None

# ---------- DATA LOADING ----------
@st.cache_data
def load_data():
    recs = pd.read_csv("tf_idf.csv")
    items = pd.read_csv("items_improved_image2.csv")
    interactions = pd.read_csv("interactions_train1.csv")
    merged = pd.read_csv("books_complete.csv")
    return recs, items, interactions, merged

recs_df, items_df, interactions_df, merged_df = load_data()

# ---------- SIDEBAR ----------
st.sidebar.title("Book Recommendations")
st.sidebar.image("https://media.istockphoto.com/id/1210557301/photo/magic-book-open.jpg?s=612x612&w=0&k=20&c=2T9x_Z_by3QEeo2DdPOapMUi545Zi10V-eDwg6ToUoI=", width=300)
st.sidebar.markdown("Welcome to the Book Recommender! Explore personalized book recommendations based on your preferences.")
st.sidebar.markdown("Select your Personal Library User ID to see book recommendations just for you.")
user_id = st.sidebar.selectbox("User ID", recs_df['user_id'].unique())

# ---------- RENDER BOOK SCROLLABLE ----------
def render_books_scrollable(df, prefix):
    st.markdown('<div class="book-row-scroll">', unsafe_allow_html=True)
    for _, row in df.iterrows():
        st.markdown('<div class="book-card">', unsafe_allow_html=True)
        image_url = row.get('image')
        if isinstance(image_url, str) and image_url.startswith("http"):
            st.image(image_url, width=120)
        else:
            st.image("https://via.placeholder.com/120x180?text=No+Cover", width=120)
        st.markdown(f"**{row['title']}**")
        description = row.get("Description") or row.get("synopsis", "No description available.")
        if isinstance(description, str) and len(description) > 100:
            st.caption(description[:100] + "...")
        else:
            st.caption(description)
        if st.button("More Info", key=f"{prefix}_info_{row['i']}"):
            st.session_state.expanded_book_id = row['i']
        if st.session_state.expanded_book_id == row['i']:
            st.markdown("### Details")
            st.markdown(f"**Author:** {row.get('Author', 'Unknown')}")
            st.markdown(f"**Published:** {row.get('Year', row.get('date_published', 'N/A'))}")
            st.markdown(f"**Language:** {row.get('language', row.get('Language', 'N/A'))}")
            st.markdown(f"**Publisher:** {row.get('publisher', row.get('Publisher', 'N/A'))}")
            st.markdown(f"**Subjects:** {row.get('Subjects', 'N/A')}")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- BOOKS BY GENRE ----------
st.header("🎨 Books by Genre")
genres = ["Mangas", "Roman", "Bande dessinées", "Science-fiction", "Thriller", "Fantasy"]
for genre in genres:
    genre_books = merged_df[merged_df['Subjects'].fillna("").str.contains(genre, case=False, na=False)]
    if not genre_books.empty:
        st.subheader(f"📚 {genre.title()}")
        render_books_scrollable(genre_books.head(10), f"genre_{genre}")
