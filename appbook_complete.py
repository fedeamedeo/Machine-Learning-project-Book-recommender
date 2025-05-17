import streamlit as st
import pandas as pd

# ---------- CONFIG ----------
st.set_page_config(page_title="📚 Book Recommender", layout="wide", initial_sidebar_state="expanded")

# ---------- GLOBAL STYLES ----------
st.markdown("""
    <style>
        body.dark {
            background-color: #121212;
            color: white;
        }
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
            min-width: 220px;
            max-width: 250px;
            flex: 0 0 auto;
        }
        .book-row-scroll {
            display: flex;
            overflow-x: auto;
            gap: 1.5rem;
            padding: 1rem 0;
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
        .book-row-scroll::-webkit-scrollbar {
            height: 8px;
        }
        .book-row-scroll::-webkit-scrollbar-thumb {
            background-color: #ccc;
            border-radius: 4px;
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
def render_books_vertical(df, prefix, allow_expansion=True):
    rows = [df.iloc[i:i+3] for i in range(0, len(df), 3)]
    for row_group in rows:
        cols = st.columns(len(row_group))
        for col, (_, row) in zip(cols, row_group.iterrows()):
            with col:
                st.markdown('<div class="book-card">', unsafe_allow_html=True)
                st.markdown('<div class="book-content">', unsafe_allow_html=True)
                image_url = row.get('image')
                if isinstance(image_url, str) and image_url.startswith("http"):
                    st.image(image_url, width=140)
                else:
                    st.image("https://via.placeholder.com/140x210?text=No+Cover", width=140)

                st.markdown('<div class="book-info">', unsafe_allow_html=True)
                st.markdown(f"**{row['title']}**")

                description = row.get("Description") or row.get("synopsis", "No description available.")
                if isinstance(description, str) and len(description) > 120:
                    st.caption(description[:120] + "...")
                else:
                    st.caption(description)

                if allow_expansion:
                    st.markdown('<div class="book-buttons">', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("❤️", key=f"{prefix}_fav_{row['i']}"):
                            if row['i'] not in st.session_state.favorites:
                                st.session_state.favorites.append(row['i'])
                    with col2:
                        if st.button("More Info", key=f"{prefix}_info_{row['i']}"):
                            if st.session_state.expanded_book_id == row['i']:
                                st.session_state.expanded_book_id = None
                            else:
                                st.session_state.expanded_book_id = row['i']
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('</div></div>', unsafe_allow_html=True)

                if allow_expansion and st.session_state.expanded_book_id == row['i']:
                    with st.expander("📓 Book Details", expanded=True):
                        if isinstance(image_url, str) and image_url.startswith("http"):
                            st.image(image_url, width=180)
                        else:
                            st.image("https://via.placeholder.com/180x270?text=No+Cover", width=180)

                        st.markdown("### Details")
                        st.write(description)
                        st.markdown(f"**Author:** {row.get('Author', 'Unknown')}")
                        st.markdown(f"**Pages:** {row.get('Pages', row.get('pages', 'N/A'))}")
                        st.markdown(f"**Published:** {row.get('Year', row.get('date_published', 'N/A'))}")
                        st.markdown(f"**Language:** {row.get('language', row.get('Language', 'N/A'))}")
                        st.markdown(f"**Publisher:** {row.get('publisher', row.get('Publisher', 'N/A'))}")
                        st.markdown(f"**Subjects:** {row.get('Subjects', 'N/A')}")
                        if row.get('link'):
                            st.markdown(f"""<a href=\"{row['link']}\" target=\"_blank\"><button class=\"grey-button\">🔗 Visit Link</button></a>""", unsafe_allow_html=True)
                        if st.button("❤️ Add to Favorites", key=f"{prefix}_modal_fav_{row['i']}"):
                            if row['i'] not in st.session_state.favorites:
                                st.session_state.favorites.append(row['i'])

# ---------- BOOK PICKER ----------
book_titles = merged_df['title_long'].dropna().unique()
selected_book = st.sidebar.selectbox("📋 Pick a Book Title", sorted(book_titles))
if st.sidebar.button("View Book Details"):
    book_info = merged_df[merged_df['title_long'] == selected_book].iloc[0]
    st.session_state.expanded_book_id = book_info["i"]
    render_books_scrollable(pd.DataFrame([book_info]), "picker")

# ---------- BOOKS BY GENRE ----------
st.header("🎨 Books by Genre")
genres = ["Mangas", "Roman", "Bande dessinées", "Science-fiction", "Thriller", "Fantasy"]
for genre in genres:
    genre_books = merged_df[merged_df['Subjects'].fillna("").str.contains(genre, case=False, na=False)]
    if not genre_books.empty:
        st.subheader(f"📚 {genre.title()}")
        render_books_scrollable(genre_books.head(10), f"genre_{genre}")

# ---------- DARK MODE ----------
dark_mode = st.sidebar.checkbox("🌙 Enable Dark Mode")
if dark_mode:
    st.markdown("""
        <style>
        body, .stApp {
            background-color: #121212 !important;
            color: white !important;
        }
        .stButton button {
            background-color: #444;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

# ---------- NAVIGATION ----------
st.markdown("""
<div style='margin: 20px 0;'>
    <a href="#Books-by-Genre" style="margin-right: 20px;">📚 Jump to Genres</a>
    <a href="#Top">🔝 Back to Top</a>
</div>
""", unsafe_allow_html=True)
