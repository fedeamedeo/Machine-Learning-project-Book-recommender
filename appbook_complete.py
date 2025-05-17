import streamlit as st
import pandas as pd

# ---------- CONFIG ----------
st.set_page_config(page_title="📚 Book Recommender", layout="wide", initial_sidebar_state="expanded")

# ---------- SESSION STATE ----------
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "page" not in st.session_state:
    st.session_state.page = "home"
if "selected_book_id" not in st.session_state:
    st.session_state.selected_book_id = None

# ---------- LOAD DATA ----------
@st.cache_data
def load_data():
    recs = pd.read_csv("tf_idf.csv")
    items = pd.read_csv("items_improved_image2.csv")
    interactions = pd.read_csv("interactions_train1.csv")
    merged = pd.read_csv("books_complete.csv")
    return recs, items, interactions, merged

recs_df, items_df, interactions_df, merged_df = load_data()

# ---------- CALLBACKS ----------
def go_to_details(book_id):
    st.session_state.selected_book_id = book_id
    st.session_state.page = "details"

def go_to_home():
    st.session_state.page = "home"

# ---------- HOME PAGE ----------
if st.session_state.page == "home":
    st.sidebar.title("Book Recommendations")
    st.sidebar.image(
        "https://media.istockphoto.com/id/1210557301/photo/magic-book-open.jpg?s=612x612&w=0&k=20&c=2T9x_Z_by3QEeo2DdPOapMUi545Zi10V-eDwg6ToUoI=",
        width=300
    )
    st.sidebar.markdown("Welcome to the Book Recommender!")
    user_id = st.sidebar.selectbox("Select a user", recs_df['user_id'].unique())

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

                        if row.get('Subjects'):
                            st.caption(row['Subjects'].split(',')[0])

                        st.caption(f"👥 {interactions_df[interactions_df['i'] == row['i']].shape[0]} visualizations")

                        col1, col2 = st.columns(2)

                        with col1:
                            if st.button("❤️", key=f"fav_{row['i']}"):
                                if row['i'] not in st.session_state.favorites:
                                    st.session_state.favorites.append(row['i'])

                        with col2:
                            st.button("More Info", key=f"info_{row['i']}",
                                      on_click=go_to_details, args=(row['i'],))

# ---------- DETAILS PAGE ----------
elif st.session_state.page == "details":
    book_id = st.session_state.selected_book_id

    if book_id is not None:
        book = merged_df[merged_df['i'] == book_id].iloc[0]

        st.subheader(f"📘 {book['Title']}")
        col1, col2 = st.columns([1, 3])

        with col1:
            st.image(book['image'], width=160)

        with col2:
            st.markdown("### Synopsis")
            st.write(book.get("Description", "No description available."))

            st.markdown(f"**Authors:** {book.get('Author', 'N/A')}")
            st.markdown(f"**Pages:** {book.get('Pages', 'N/A')}")
            st.markdown(f"**Published:** {book.get('Year', book.get('Published', 'N/A'))}")
            st.markdown(f"**Language:** {book.get('Language', 'N/A')}")
            st.markdown(f"**Publisher:** {book.get('Publisher', 'N/A')}")
            st.markdown(f"**Subjects:** {book.get('Subjects', 'N/A')}")

            if book.get('link'):
                st.markdown(f"""<a href="{book['link']}" target="_blank">
                                <button class="grey-button">🔗 Visit Link</button></a>""", unsafe_allow_html=True)

        if st.button("❤️ Add to Favorites", key=f"fav_detail_{book['i']}"):
            if book['i'] not in st.session_state.favorites:
                st.session_state.favorites.append(book['i'])

    st.markdown("---")
    st.button("⬅️ Back to Recommendations", on_click=go_to_home)
