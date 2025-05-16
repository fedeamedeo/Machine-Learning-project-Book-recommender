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
    </style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "favorites" not in st.session_state:
    st.session_state.favorites = []

# ---------- LOAD DATA ----------
@st.cache_data
def load_data():
    recs = pd.read_csv("tf_idf.csv")
    merged = pd.read_csv("books_complete.csv")
    return recs, merged

recs_df, merged_df = load_data()

# ---------- SIDEBAR ----------
st.sidebar.title("Book Recommendations")
st.sidebar.image("https://media.istockphoto.com/id/1210557301/photo/magic-book-open.jpg?s=612x612&w=0&k=20&c=2T9x_Z_by3QEeo2DdPOapMUi545Zi10V-eDwg6ToUoI=", width=300)
st.sidebar.markdown("Welcome to the Book Recommender! Explore personalized book recommendations based on your preferences.")
st.sidebar.markdown("Select your Personal Library User ID to see book recommendations just for you.")
user_id = st.sidebar.selectbox("User ID", recs_df['user_id'].unique())
