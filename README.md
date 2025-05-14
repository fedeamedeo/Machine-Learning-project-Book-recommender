# Book Recommendation System using Machine Learning

This project aims to develop a personalized book recommendation system using machine learning techniques. Leveraging collaborative filtering methods, the system analyzes user interactions and book metadata to generate accurate and tailored suggestions.


## Libraries and Models Used:

- Pandas:  Data manipulation and analysis.

- NumPy:  Numerical computing.

- Matplotlib and seaborn:  Data visualization.

- ipywidgets:  Interactive widgets.

- Scikit-learn (sklearn):  Machine learning library.

- KNN (K-Nearest Neighbors):  Algorithm for generating recommendations.


## Project Workflow:

- Data Exploration: The project begins with loading the dataset containing book information using Pandas. Various attributes such as book title, authors, average rating, language, and publication date are examined to gain insights into the data structure and distribution.

- Data Cleaning and Preprocessing: This stage involves handling missing values, duplicate entries, and ensuring consistency in column names and data types. Preprocessing steps include feature extraction (e.g., publication year) and dropping unnecessary columns like bookID and ISBN.

- Exploratory Data Analysis (EDA): EDA techniques such as visualization and aggregation are employed to understand the distribution and relationships within the dataset. Analysis includes exploring book ratings, language distribution, top publishers, and authors based on various metrics.

- Interactive Recommendations: The project offers an interactive interface using Streamlit and ipywidgets, allowing users to explore recommendations based on publishers, authors, languages, and specific book titles. Recommendations are generated using the K-Nearest Neighbors algorithm, providing users with similar books based on their selections.

- By combining machine learning algorithms with interactive visualization, the Book Recommendation System provides a user-friendly platform for discovering new books tailored to individual preferences. Whether users are searching for popular titles from favorite publishers or exploring books by preferred authors, this system offers personalized recommendations to enhance their reading experience.
