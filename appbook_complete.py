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

# ---------- MAIN AREA ----------
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
                    st.markdown(f"**{row['Title']}**")
                    st.caption(row.get('Author', 'Unknown'))

                    subjects = row.get('Subjects')
                    if isinstance(subjects, str):
                        st.caption(subjects.split(',')[0])

                    count = interactions_df[interactions_df['i'] == row['i']].shape[0]
                    st.caption(f"👥 {count} visualizations")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("❤️", key=f"fav_{row['i']}"):
                            if row['i'] not in st.session_state.favorites:
                                st.session_state.favorites.append(row['i'])
                    with col2:
                        if st.button("More Info", key=f"info_{row['i']}"):
                            st.session_state.expanded_book_id = row['i']

                # ---------- Expandable Book Details ----------
                if st.session_state.expanded_book_id == row['i']:
                    with st.expander("📖 Book Details", expanded=True):
                        st.image(row['image'], width=160)
                        st.markdown("### Details")
                        st.write(row.get("Description", "No description available."))
                        st.markdown(f"**Author:** {row.get('Author', 'N/A')}")
                        st.markdown(f"**Pages:** {row.get('Pages', 'N/A')}")
                        st.markdown(f"**Published:** {row.get('Year', row.get('Published', 'N/A'))}")
                        st.markdown(f"**Language:** {row.get('Language', 'N/A')}")
                        st.markdown(f"**Publisher:** {row.get('Publisher', 'N/A')}")
                        st.markdown(f"**Subjects:** {row.get('Subjects', 'N/A')}")

                        if row.get('link'):
                            st.markdown(f"""<a href="{row['link']}" target="_blank">
                                            <button class="grey-button">🔗 Visit Link</button></a>""",
                                        unsafe_allow_html=True)

                        if st.button("❤️ Add to Favorites", key=f"modal_fav_{row['i']}"):
                            if row['i'] not in st.session_state.favorites:
                                st.session_state.favorites.append(row['i'])

                        if st.button("❌ Close", key=f"close_{row['i']}"):
                            st.session_state.expanded_book_id = None

# ---------- BOOK PICKER ----------
book_titles = merged_df['title_long'].dropna().unique()
selected_book = st.sidebar.selectbox("📖 Pick a Book Title", sorted(book_titles))
if st.sidebar.button("View Book Details"):
    book_info = merged_df[merged_df['title_long'] == selected_book].iloc[0]

    st.subheader("📘 Book Details")
    st.image(book_info['image'], width=150)
    st.markdown(f"**{book_info['title_long']}**")
    st.caption(book_info['Author'])

    subject = book_info.get('Subjects')
    if isinstance(subject, str):
        st.caption(subject.split(',')[0])

    st.caption(f"👥 {interactions_df[interactions_df['i'] == book_info['i']].shape[0]} visualizations")

    if st.button("❤️ Save to Favorites"):
        if book_info['i'] not in st.session_state.favorites:
            st.session_state.favorites.append(book_info['i'])

# ---------- SEARCH ----------
st.title("🔍 Search the Book Database")
search_query = st.text_input("Search for a book by title, author, or subject:")
if search_query:
    results = merged_df[
        merged_df['Title'].str.contains(search_query, case=False, na=False) |
        merged_df['Author'].str.contains(search_query, case=False, na=False) |
        merged_df['Subjects'].str.contains(search_query, case=False, na=False)
    ]
    st.subheader(f"Found {len(results)} result(s):")
    cols = st.columns(5)
    for i, (_, row) in enumerate(results.head(15).iterrows()):
        with cols[i % 5]:
            with st.container(border=True):
                st.image(row['image'], width=120)
                st.markdown(f"**{row['Title']}**")
                st.caption(row['Author'])

                if isinstance(row.get('Subjects'), str):
                    st.caption(row['Subjects'].split(',')[0])

                st.caption(f"👥 {interactions_df[interactions_df['i'] == row['i']].shape[0]} visualizations")

                col1, col2 = st.columns(2)
                with col2:
                    if st.button("❤️", key=f"search_{row['i']}"):
                        if row['i'] not in st.session_state.favorites:
                            st.session_state.favorites.append(row['i'])
# ---------- FAVORITES ----------
if st.session_state.favorites:
    st.subheader("⭐ Your Favorite Books")
    fav_books = merged_df[merged_df['i'].isin(st.session_state.favorites)]
    if st.button("🗑️ Clear Favorites"):
        st.session_state.favorites = []

    cols = st.columns(5)
    for i, (_, row) in enumerate(fav_books.iterrows()):
        with cols[i % 5]:
            with st.container(border=True):
                st.image(row['image'], width=120)
                st.markdown(f"**{row['Title']}**")
                st.caption(row['Author'])
                if isinstance(row.get('Subjects'), str):
                    st.caption(row['Subjects'].split(',')[0])
                st.caption(f"👥 {interactions_df[interactions_df['i'] == row['i']].shape[0]} visualizations")
                col1, col2 = st.columns(2)
                with col1:
                    if row.get('link'):
                        st.markdown(f"""<a href="{row['link']}" target="_blank"><button class="grey-button" style="width: 100%">🔗</button></a>""", unsafe_allow_html=True)
                with col2:
                    if st.button("❤️", key=f"fav_{row['i']}"):
                        if row['i'] not in st.session_state.favorites:
                            st.session_state.favorites.append(row['i'])