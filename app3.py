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
    items = pd.read_csv("items_improved_image2.csv")
    interactions = pd.read_csv("interactions_train1.csv")
    return recs, items, interactions

recs_df, items_df, interactions_df = load_data()

# ---------- SIDEBAR ----------
t.sidebar.title("Book Recommendations")
st.sidebar.image("https://media.istockphoto.com/id/1210557301/photo/magic-book-open.jpg?s=612x612&w=0&k=20&c=2T9x_Z_by3QEeo2DdPOapMUi545Zi10V-eDwg6ToUoI=", width=300)
st.sidebar.markdown("Welcome to the Book Recommender! Explore personalized book recommendations based on your preferences.")

st.sidebar.markdown("Select your Personal Library User ID to see book recommendations just for you.")
st.session_state.selected_user = st.sidebar.selectbox("User ID", recs_df['user_id'].unique(), index=0, key="user_select")
# ---------- BOOK PICKER ----------
book_titles = items_df['Title'].dropna().unique()
selected_book = st.sidebar.selectbox("📖 Pick a Book Title", sorted(book_titles))
if st.sidebar.button("View Book Details"):
    book_info = items_df[items_df['Title'] == selected_book].iloc[0]
    st.image(book_info['cover_url'], width=150)
    st.markdown(f"**{book_info['Title']}**")
    st.caption(book_info['Author'])
    st.caption(f"👥 {interactions_df[interactions_df['i'] == book_info['i']].shape[0]} interactions")
    if book_info.get('link'):
        st.markdown(f"[🔗 Open Link]({book_info['link']})", unsafe_allow_html=True)
    if st.button("❤️ Save to Favorites"):
        if book_info['i'] not in st.session_state.favorites:
            st.session_state.favorites.append(book_info['i'])

# ---------- USER RECOMMENDATIONS ----------
if st.sidebar.button("Show Recommendations"):
    user_row = recs_df[recs_df['user_id'] == user_id]
    if not user_row.empty:
        book_ids = list(map(int, user_row.iloc[0]['recommendation'].split()))[:10]
        recommended_books = items_df[items_df['i'].isin(book_ids)]

        st.subheader("📖 Top Book Picks for You")
        cols = st.columns(5)
        for i, (_, row) in enumerate(recommended_books.iterrows()):
            with cols[i % 5]:
                with st.container(border=True):
                    st.image(row['cover_url'], width=120)
                    st.markdown(f"**{row['Title']}**")
                    st.caption(row['Author'])
                    if pd.notna(row.get('Subjects')):
                        st.markdown(f"`{row['Subjects'].split(',')[0]}`")
                    st.caption(f"👥 {interactions_df[interactions_df['i'] == row['i']].shape[0]} interactions")
                    col1, col2 = st.columns(2)
                    with col1:
                        if row.get('link'):
                            st.markdown(f"""<a href="{row['link']}" target="_blank"><button class="grey-button" style="width: 100%">🔗</button></a>""", unsafe_allow_html=True)
                    with col2:
                        if st.button("❤️", key=f"rec_{row['i']}"):
                            if row['i'] not in st.session_state.favorites:
                                st.session_state.favorites.append(row['i'])

# ---------- SEARCH ----------
st.title("🔍 Search the Book Database")
search_query = st.text_input("Search for a book by title, author, or subject:")
if search_query:
    results = items_df[
        items_df['Title'].str.contains(search_query, case=False, na=False) |
        items_df['Author'].str.contains(search_query, case=False, na=False) |
        items_df['Subjects'].str.contains(search_query, case=False, na=False)
    ]
    st.subheader(f"Found {len(results)} result(s):")
    cols = st.columns(5)
    for i, (_, row) in enumerate(results.head(15).iterrows()):
        with cols[i % 5]:
            with st.container(border=True):
                st.image(row['cover_url'], width=120)
                st.markdown(f"**{row['Title']}**")
                st.caption(row['Author'])
                if pd.notna(row.get('Subjects')):
                    st.markdown(f"`{row['Subjects'].split(',')[0]}`")
                st.caption(f"👥 {interactions_df[interactions_df['i'] == row['i']].shape[0]} interactions")
                col1, col2 = st.columns(2)
                with col1:
                    if row.get('link'):
                        st.markdown(f"""<a href="{row['link']}" target="_blank"><button class="grey-button" style="width: 100%">🔗</button></a>""", unsafe_allow_html=True)
                with col2:
                    if st.button("❤️", key=f"search_{row['i']}"):
                        if row['i'] not in st.session_state.favorites:
                            st.session_state.favorites.append(row['i'])

# ---------- FAVORITES ----------
if st.session_state.favorites:
    st.subheader("⭐ Your Favorite Books")
    fav_books = items_df[items_df['i'].isin(st.session_state.favorites)]
    if st.button("🗑️ Clear Favorites"):
        st.session_state.favorites = []

    cols = st.columns(5)
    for i, (_, row) in enumerate(fav_books.iterrows()):
        with cols[i % 5]:
            with st.container(border=True):
                st.image(row['cover_url'], width=120)
                st.markdown(f"**{row['Title']}**")
                st.caption(row['Author'])
                if pd.notna(row.get('Subjects')):
                    st.markdown(f"`{row['Subjects'].split(',')[0]}`")
                st.caption(f"👥 {interactions_df[interactions_df['i'] == row['i']].shape[0]} interactions")
                col1, col2 = st.columns(2)
                with col1:
                    if row.get('link'):
                        st.markdown(f"""<a href="{row['link']}" target="_blank"><button class="grey-button" style="width: 100%">🔗</button></a>""", unsafe_allow_html=True)
                with col2:
                    if st.button("❤️", key=f"fav_{row['i']}"):
                        if row['i'] not in st.session_state.favorites:
                            st.session_state.favorites.append(row['i'])

# ---------- MOST POPULAR ----------
st.header("🔥 Most Popular Books")
popular_ids = interactions_df['i'].value_counts().head(10).index.tolist()
popular_books = items_df[items_df['i'].isin(popular_ids)]
cols = st.columns(5)
for i, (_, row) in enumerate(popular_books.iterrows()):
    with cols[i % 5]:
        with st.container(border=True):
            st.image(row['cover_url'], width=120)
            st.markdown(f"**{row['Title']}**")
            st.caption(row['Author'])
            if pd.notna(row.get('Subjects')):
                st.markdown(f"`{row['Subjects'].split(',')[0]}`")
            st.caption(f"👥 {interactions_df[interactions_df['i'] == row['i']].shape[0]} interactions")
            col1, col2 = st.columns(2)
            with col1:
                if row.get('link'):
                    st.markdown(f"""<a href="{row['link']}" target="_blank"><button class="grey-button" style="width: 100%">🔗</button></a>""", unsafe_allow_html=True)
            with col2:
                if st.button("❤️", key=f"pop_{row['i']}"):
                    if row['i'] not in st.session_state.favorites:
                        st.session_state.favorites.append(row['i'])

# ---------- GENRE BROWSE ----------
st.header("📚 Browse by Genre")
genres = ["Mangas", "Roman", "Sciences", "Fantasy", "Histoire"]
for genre in genres:
    st.subheader(f"📘 {genre}")
    genre_books = items_df[items_df['Subjects'].str.contains(genre, case=False, na=False)].head(5)
    cols = st.columns(5)
    for i, (_, row) in enumerate(genre_books.iterrows()):
        with cols[i % 5]:
            with st.container(border=True):
                st.image(row['cover_url'], width=120)
                st.markdown(f"**{row['Title']}**")
                st.caption(row['Author'])
                st.caption(f"`{genre}`")
                st.caption(f"👥 {interactions_df[interactions_df['i'] == row['i']].shape[0]} interactions")
                col1, col2 = st.columns(2)
                with col1:
                    if row.get('link'):
                        st.markdown(f"""<a href="{row['link']}" target="_blank"><button class="grey-button" style="width: 100%">🔗</button></a>""", unsafe_allow_html=True)
                with col2:
                    if st.button("❤️", key=f"genre_{row['i']}"):
                        if row['i'] not in st.session_state.favorites:
                            st.session_state.favorites.append(row['i'])