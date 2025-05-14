import streamlit as st
import pandas as pd
import os
import webbrowser
from sklearn import neighbors
from sklearn.preprocessing import MinMaxScaler

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
    books_df = pd.read_csv("books.csv", on_bad_lines='skip')
    return recs, items, interactions, books_df

recs_df, items_df, interactions_df, books_df = load_data()

# Clean and prep books_df
books_df.drop(['bookID', 'isbn', 'isbn13'], axis=1, inplace=True)
language_df = pd.get_dummies(books_df['language_code'])
features = pd.concat([language_df, books_df[['average_rating', 'ratings_count']]], axis=1)
scaler = MinMaxScaler()
features_scaled = scaler.fit_transform(features)
model = neighbors.NearestNeighbors(n_neighbors=5, algorithm='ball_tree', metric='euclidean')
model.fit(features_scaled)
dist, idlist = model.kneighbors(features_scaled)

def recommend_books_publishers(publisher_name):
    recommended_books = books_df[books_df['publisher'] == publisher_name][['title']]
    return recommended_books.head(10)

def recommend_books_authors(authors_name):
    recommended_books = books_df[books_df['authors'] == authors_name][['title']]
    return recommended_books.head(10)

def recommend_books_lang(language):
    recommended_books = books_df[books_df['language_code'] == language][['title']]
    return recommended_books.head(10)

def BookRecommender(book_name):
    book_list_name = []
    if book_name in books_df['title'].values:
        book_id = books_df[books_df['title'] == book_name].index[0]
        for newid in idlist[book_id]:
            book_list_name.append(books_df.iloc[newid].title)
    return book_list_name

# ---------- SIDEBAR ----------
st.sidebar.title("🔧 Settings")
st.sidebar.markdown("Chat with the system to get personalized book recommendations using precomputed TF-IDF matches.")
st.session_state.selected_user = st.sidebar.selectbox("Select a User ID", recs_df['user_id'].unique(), index=0, key="user_select")

# Extra filters
st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Book Filters")
selected_publisher = st.sidebar.selectbox("Select Publisher", books_df['publisher'].dropna().unique())
selected_author = st.sidebar.selectbox("Select Author", books_df['authors'].dropna().unique())
selected_language = st.sidebar.selectbox("Select Language", books_df['language_code'].dropna().unique())

st.sidebar.subheader("🔁 Content-Based Book Recommendation")
book_to_recommend = st.sidebar.selectbox("Select Book", books_df['title'].dropna().unique())

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

# ---------- Recommendation Outputs ----------
st.header("📚 Other Recommendations")

st.subheader("🔖 Recommendations by Publisher")
st.dataframe(recommend_books_publishers(selected_publisher))

st.subheader("🖋️ Recommendations by Author")
st.dataframe(recommend_books_authors(selected_author))

st.subheader("🌐 Recommendations by Language")
st.dataframe(recommend_books_lang(selected_language))

st.subheader(f"📚 Similar Books to: '{book_to_recommend}'")
st.write(BookRecommender(book_to_recommend))


