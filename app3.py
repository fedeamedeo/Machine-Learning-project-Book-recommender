import streamlit as st
import pandas as pd
import os
import webbrowser

# ---------- CONFIG ----------
st.set_page_config(page_title="📚 Book Recommender", layout="wide", initial_sidebar_state="expanded")

# ---------- SESSION STATE ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "selected_user" not in st.session_state:
    st.session_state.selected_user = None

# ------------------ LOAD DATA ------------------
@st.cache_data
def load_data():
    recs = pd.read_csv("tf_idf.csv")
    items = pd.read_csv("items_improved_image2.csv")
    interactions = pd.read_csv("interactions_train1.csv")
    return recs, items, interactions

recs_df, items_df, interactions_df = load_data()

# ---------- SIDEBAR ----------
st.sidebar.title("Book Recommendations")
st.sidebar.image("https://media.istockphoto.com/id/1210557301/photo/magic-book-open.jpg?s=612x612&w=0&k=20&c=2T9x_Z_by3QEeo2DdPOapMUi545Zi10V-eDwg6ToUoI=", width=300)
st.sidebar.markdown("Welcome to the Book Recommender! Explore personalized book recommendations based on your preferences.")


st.sidebar.markdown("Select your Personal Library User Id user to see book recommendations just for you.")
st.session_state.selected_user = st.sidebar.selectbox("User ID", recs_df['user_id'].unique(), index=0, key="user_select")

if st.sidebar.button("Show Recommendations", key="sidebar_show_recs"):
    user_row = recs_df[recs_df['user_id'] == st.session_state.selected_user]

    if not user_row.empty:
        book_ids = list(map(int, user_row.iloc[0]['recommendation'].split()))[:10]
        recommended_books = items_df[items_df['i'].isin(book_ids)]

        st.subheader("📖 Top Book Picks for You")
        cols = st.columns(5)
        for i, (_, row) in enumerate(recommended_books.iterrows()):
            interactions_count = interactions_df[interactions_df['i'] == row['i']].shape[0]
            with cols[i % 5]:
                st.image(row['cover_url'], width=100)
                st.markdown(f"**{row['Title']}**")
                st.caption(row['Author'])
                st.caption(f"👥 {interactions_count} interactions")
                if row.get('link'):
                    st.link_button("🔗 Open Link", row['link'], use_container_width=True)
                if st.button("❤️ Save", key=f"rec_{row['i']}"):
                    if row['i'] not in st.session_state.favorites:
                        st.session_state.favorites.append(row['i'])
    else:
        st.warning("No recommendations found for this user.")
st.sidebar.markdown("---")
st.sidebar.markdown("You can search for books by title, author, or subject. Browse by genre to discover new books and save your favorite books to revisit later")


st.sidebar.subheader("📖 Pick a Book Title")
book_titles = items_df['Title'].dropna().unique()
selected_book = st.sidebar.selectbox(
    "Type or select a book from the dropdown", 
    sorted(book_titles), 
    key="book_select"
)

if st.sidebar.button("View Book Details", key="view_book_details"):
    book_info = items_df[items_df['Title'] == selected_book].iloc[0]
    interactions_count = interactions_df[interactions_df['i'] == book_info['i']].shape[0]

    st.image(book_info['cover_url'], width=150)
    st.markdown(f"**{book_info['Title']}**")
    st.caption(book_info['Author'])
    st.caption(f"👥 {interactions_count} interactions")

    if book_info.get('link'):
        st.markdown(f"[🔗 Open Link]({book_info['link']})", unsafe_allow_html=True)

    if st.button("❤️ Save to Favorites", key=f"select_{book_info['i']}"):
        if book_info['i'] not in st.session_state.favorites:
            st.session_state.favorites.append(book_info['i'])



# ---------- SEARCH BAR ----------
st.title("🔍 Search the Book Database")
search_query = st.text_input("Search for a book by title, author, or subject:")
if search_query:
    results = items_df[
        items_df['Title'].str.lower().str.contains(search_query.lower(), na=False) |
        items_df['Author'].str.lower().str.contains(search_query.lower(), na=False) |
        items_df['Subjects'].str.lower().str.contains(search_query.lower(), na=False)
    ]
    st.subheader(f"Found {len(results)} result(s):")
    cols = st.columns(5)
    for i, (_, row) in enumerate(results.head(15).iterrows()):
        interactions_count = interactions_df[interactions_df['i'] == row['i']].shape[0]
        with cols[i % 5]:
            st.image(row.get('cover_url', "https://via.placeholder.com/128x195.png?text=No+Image"), width=100)
            st.markdown(f"**{row['Title']}**")
            st.caption(row['Author'])
            st.caption(f"👥 {interactions_count} interactions")
            if row.get('link'):
                st.link_button("🔗 Open Link", row['link'], use_container_width=True)

# ------------------ FAVORITES SECTION ------------------
if st.session_state.favorites:
    st.subheader("⭐ Your Favorite Books")
    fav_books = items_df[items_df['i'].isin(st.session_state.favorites)]
    clear = st.button("🗑️ Clear Favorites")
    if clear:
        st.session_state.favorites = []

    cols = st.columns(5)
    for i, (_, row) in enumerate(fav_books.iterrows()):
        interactions_count = interactions_df[interactions_df['i'] == row['i']].shape[0]
        with cols[i % 5]:
            st.image(row['cover_url'], width=100)
            st.markdown(f"**{row['Title']}**")
            st.caption(row['Author'])
            st.caption(f"👥 {interactions_count} interactions")
            if row.get('link'):
                st.link_button("🔗 Open Link", row['link'], use_container_width=True)

# ------------------ MOST POPULAR ------------------
# ------------------ MOST POPULAR ------------------
st.title("📚 Book Recommendation System")
st.header("🔥 Most Popular Books")

# Add custom CSS to style buttons
st.markdown("""
    <style>
        .grey-button {
            background-color: #e0e0e0 !important;
            color: #000000 !important;
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

popular_ids = interactions_df['i'].value_counts().head(10).index.tolist()
popular_books = items_df[items_df['i'].isin(popular_ids)]

num_columns = 5
cols = st.columns(num_columns)

for idx, (_, row) in enumerate(popular_books.iterrows()):
    interactions_count = interactions_df[interactions_df['i'] == row['i']].shape[0]

    with cols[idx % num_columns]:
        with st.container(border=True):
            st.image(row['cover_url'], width=120)
            st.markdown(f"**{row['Title']}**")
            st.caption(row['Author'])

            if pd.notna(row.get('Subjects')) and isinstance(row['Subjects'], str):
                main_subject = row['Subjects'].split(',')[0]
                st.markdown(f"`{main_subject.strip()}`")

            st.caption(f"👥 {interactions_count} interactions")

            # Buttons styled with HTML links as workaround for custom styling
            col1, col2 = st.columns([1, 1])
            with col1:
                if row.get('link'):
                    st.markdown(f"""
                        <a href="{row['link']}" target="_blank">
                            <button class="grey-button" style="width: 100%">🔗</button>
                        </a>
                    """, unsafe_allow_html=True)

            with col2:
                if st.button("❤️", key=f"pop_{row['i']}"):
                    if row['i'] not in st.session_state.favorites:
                        st.session_state.favorites.append(row['i'])

# ------------------ BROWSE BY GENRE ------------------
st.header("📚 Browse by Genre")

top_subjects = ["Mangas", "Roman", "Sciences", "Fantasy", "Histoire"]

for subject in top_subjects:
    st.subheader(f"📖 {subject}")
    subject_books = items_df[
        items_df['Subjects'].str.contains(subject, case=False, na=False)
    ].head(5)

    cols = st.columns(5)
    for i, (_, row) in enumerate(subject_books.iterrows()):
        interactions_count = interactions_df[interactions_df['i'] == row['i']].shape[0]
        with cols[i % 5]:
            st.image(row['cover_url'], width=100)
            st.markdown(f"**{row['Title']}**")
            st.caption(row['Author'])
            st.caption(f"👥 {interactions_count} interactions")
            if row.get('link'):
                st.link_button("🔗 Open Link", row['link'], use_container_width=True)
            if st.button("❤️ Save", key=f"genre_{row['i']}"):
                if row['i'] not in st.session_state.favorites:
                    st.session_state.favorites.append(row['i'])