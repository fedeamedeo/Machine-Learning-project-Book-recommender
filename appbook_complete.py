import streamlit as st
import pandas as pd

# ---------- CONFIG ----------
st.set_page_config(page_title="📚 Book Recommender", layout="wide", initial_sidebar_state="expanded")

# ---------- GLOBAL STYLES ----------
st.markdown("""
    <style>
        .book-button {
            border: 1px solid lightgray;
            padding: 0.3rem 0.7rem;
            border-radius: 8px;
            font-size: 14px;
            background-color: white;
            margin-top: 0.5rem;
        }
        .book-button:hover {
            background-color: #f0f0f0;
            border-color: gray;
        }
    </style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "open_modal" not in st.session_state:
    st.session_state.open_modal = None  # store which book to show modal for

# ---------- LOAD DATA ----------
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
st.sidebar.image(
    "https://media.istockphoto.com/id/1210557301/photo/magic-book-open.jpg?s=612x612&w=0&k=20&c=2T9x_Z_by3QEeo2DdPOapMUi545Zi10V-eDwg6ToUoI=",
    width=300
)
st.sidebar.markdown("Welcome to the Book Recommender!")
user_id = st.sidebar.selectbox("Select a user", recs_df['user_id'].unique())

# ---------- RECOMMENDATIONS ----------
if st.sidebar.button("Show Recommendations"):
    user_row = recs_df[recs_df['user_id'] == user_id]

    if not user_row.empty:
        book_ids = list(map(int, user_row.iloc[0]['recommendation'].split()))[:10]
        recommended_books = merged_df[merged_df['i'].isin(book_ids)]

        st.subheader("📖 Top Book Picks for You")
        cols = st.columns(5)

        for i, (_, row) in enumerate(recommended_books.iterrows()):
            with cols[i % 5]:
                with st.container(border=True):
                    st.image(row['image'], width=120)
                    
                    # Book title as button
                    if st.button(row['Title'], key=f"btn_{row['i']}", help="Click to see more", use_container_width=True):
                        st.session_state.open_modal = row['i']

# ---------- MODAL DISPLAY ----------
if st.session_state.open_modal is not None:
    book_row = merged_df[merged_df['i'] == st.session_state.open_modal].iloc[0]

    with st.modal(f"📖 {book_row['Title']}"):
        st.image(book_row['image'], width=160)
        
        st.markdown("### Synopsis")
        st.write(book_row.get("Description", "No description available."))

        st.markdown(f"**Authors:** {book_row.get('Author', 'N/A')}")
        st.markdown(f"**Pages:** {book_row.get('Pages', 'N/A')}")
        st.markdown(f"**Published:** {book_row.get('Year', book_row.get('Published', 'N/A'))}")
        st.markdown(f"**Language:** {book_row.get('Language', 'N/A')}")
        st.markdown(f"**Publisher:** {book_row.get('Publisher', 'N/A')}")
        st.markdown(f"**Subjects:** {book_row.get('Subjects', 'N/A')}")

        if book_row.get('link'):
            st.markdown(f"""<a href="{book_row['link']}" target="_blank"><button class="book-button">🔗 Visit Link</button></a>""", unsafe_allow_html=True)

        if st.button("❤️ Add to Favorites"):
            if book_row['i'] not in st.session_state.favorites:
                st.session_state.favorites.append(book_row['i'])
