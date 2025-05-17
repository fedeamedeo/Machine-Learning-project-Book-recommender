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
            gap: 2rem;
            padding: 1.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 18px rgba(0,0,0,0.08);
            transition: box-shadow 0.3s ease-in-out;
            margin-bottom: 1rem;
            align-items: flex-start;
            background-color: #ffffff;
            flex-direction: column;
        }
        .book-card:hover {
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
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
            gap: 1.2rem;
            margin-top: 0.75rem;
        }

        .stColumn > div:empty {
            display: none !important;
        }

        .stColumns {
            margin-bottom: 0rem !important;
        }

        .block-container > div:has(.element-container:empty) {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "expanded_book_id" not in st.session_state:
    st.session_state.expanded_book_id = None
if "recommended_book_ids" not in st.session_state:
    st.session_state.recommended_book_ids = []

# ---------- DATA LOADING ----------
@st.cache_data
def load_data():
    recs = pd.read_csv("tf_idf.csv")
    interactions = pd.read_csv("interactions_train1.csv")
    merged = pd.read_csv("books_complete.csv")
    return recs, interactions, merged

recs_df, interactions_df, merged_df = load_data()

# ---------- SIDEBAR ----------
st.sidebar.title("Book Recommendations")
st.sidebar.image("https://media.istockphoto.com/id/944631208/photo/education-concept-with-book-in-library.jpg?s=612x612&w=0&k=20&c=uJF-uOU5MRR-iwXqJEPAdXeaH-VJ-nqt6TdKUpEdEkk=", width=300)
st.sidebar.markdown("Welcome to the Book Recommender! Explore personalized book recommendations based on your preferences.")
st.sidebar.markdown("Select your Personal Library User ID to see book recommendations just for you.")
user_id = st.sidebar.selectbox("User ID", recs_df['user_id'].unique())

# ---------- BOOK PICKER ----------
book_titles = merged_df['title_long'].dropna().unique()
selected_book = st.sidebar.selectbox("📋 Pick a Book Title", sorted(book_titles))

# ---------- RENDER BOOKS VERTICALLY ----------
def render_books_vertical(df, prefix, allow_expansion=True):
    rows = [df.iloc[i:i+3] for i in range(0, len(df), 3)]
    for row_group in rows:
        cols = st.columns(len(row_group))
        for col, (_, row) in zip(cols, row_group.iterrows()):
            with col:
                st.markdown('<div class="book-card">', unsafe_allow_html=True)
                st.markdown('<div class="book-content">', unsafe_allow_html=True)
                image_url = row.get('image')
                st.image(image_url if isinstance(image_url, str) and image_url.startswith("http")
                         else "https://via.placeholder.com/140x210?text=No+Cover", width=140)
                st.markdown('<div class="book-info">', unsafe_allow_html=True)
                st.markdown(f"**{row['title']}**")
                description = row.get("Description") or row.get("synopsis", "No description available.")
