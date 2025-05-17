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
st.sidebar.image("https://media.istockphoto.com/id/1210557301/photo/magic-book-open.jpg", width=300)
st.sidebar.markdown("Welcome to the Book Recommender! Explore personalized book recommendations based on your preferences.")
st.sidebar.markdown("Select your Personal Library User ID to see book recommendations just for you.")
user_id = st.sidebar.selectbox("User ID", recs_df['user_id'].unique())
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
                st.caption(description[:120] + "..." if isinstance(description, str) and len(description) > 120 else description)
                if allow_expansion:
                    st.markdown('<div class="book-buttons">', unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("❤️", key=f"{prefix}_fav_{row['i']}"):
                            if row['i'] not in st.session_state.favorites:
                                st.session_state.favorites.append(row['i'])
                    with col2:
                        if st.button("More Info", key=f"{prefix}_info_{row['i']}"):
                            st.session_state.expanded_book_id = None if st.session_state.expanded_book_id == row['i'] else row['i']
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('</div></div>', unsafe_allow_html=True)
                if allow_expansion and st.session_state.expanded_book_id == row['i']:
                    with st.expander("📓 Book Details", expanded=True):
                        st.image(image_url if isinstance(image_url, str) and image_url.startswith("http")
                                 else "https://via.placeholder.com/180x270?text=No+Cover", width=180)
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

# ---------- VIEW RECOMMENDATIONS ----------
if st.sidebar.button("Show Recommendations", key="show_recs_button"):
    user_row = recs_df[recs_df['user_id'] == user_id]
    if not user_row.empty:
        book_ids = list(map(int, user_row.iloc[0]['recommendation'].split()))[:10]
        recommended_books = merged_df[merged_df['i'].isin(book_ids)]
        st.subheader("📖 Top Book Picks for You")
        render_books_vertical(recommended_books, "rec", allow_expansion=True)

# ---------- VIEW SELECTED BOOK ----------
if st.sidebar.button("View Book Details", key="view_details_button"):
    book_info = merged_df[merged_df['title_long'] == selected_book].iloc[0]
    render_books_vertical(pd.DataFrame([book_info]), "picker", allow_expansion=True)

# ---------- SEARCH ----------
st.title("🔍 Search the Book Database")
search_query = st.text_input("Search for a book by title, author, or subject:")
if search_query:
    results = merged_df[
        merged_df['title'].str.contains(search_query, case=False, na=False) |
        merged_df['Author'].str.contains(search_query, case=False, na=False) |
        merged_df['Subjects'].str.contains(search_query, case=False, na=False)
    ]
    st.subheader(f"Found {len(results)} result(s):")
    render_books_vertical(results.head(15), "search", allow_expansion=True)

# ---------- FAVORITES ----------
if st.session_state.favorites:
    st.subheader("⭐ Your Favorite Books")
    fav_books = merged_df[merged_df['i'].isin(st.session_state.favorites)]
    if st.button("🗑️ Clear Favorites"):
        st.session_state.favorites = []
    render_books_vertical(fav_books, "fav")

# ---------- MOST POPULAR ----------
st.header("🔥 Most Popular Books")
popular_ids = interactions_df['i'].value_counts().head(10).index.tolist()
popular_books = merged_df[merged_df['i'].isin(popular_ids)]
render_books_vertical(popular_books, "pop", allow_expansion=True)

# ---------- BOOKS BY GENRE ----------
st.header("🎨 Books by Genre")
genres = ["Mangas", "Roman", "Bande dessinées", "Science-fiction", "Thriller", "Fantasy"]
for genre in genres:
    genre_books = merged_df[merged_df['Subjects'].fillna("").str.contains(genre, case=False, na=False)]
    if not genre_books.empty:
        st.subheader(f"📚 {genre.title()}")
        render_books_vertical(genre_books.head(6), prefix=genre.lower().replace(" ", "_"), allow_expansion=True)
