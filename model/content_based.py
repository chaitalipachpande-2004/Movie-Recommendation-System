import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle

# Import preprocessed data
from preprocess import new_df

print(new_df.head())
print(new_df.shape)

cv = CountVectorizer(max_features=5000, stop_words='english')  #CountVectorizer converts words into numbers.

vectors = cv.fit_transform(new_df['tags']).toarray()

print(vectors.shape)

similarity = cosine_similarity(vectors)
print(similarity.shape)

#recommendation function
def recommend(movie):

    movie_index = new_df[new_df['title'] == movie].index[0]

    distances = similarity[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:11]

    for i in movies_list:
        print(new_df.iloc[i[0]].title)

# recommend("Avatar")
pickle.dump(new_df, open('saved_models/movies.pkl', 'wb'))
pickle.dump(similarity, open('saved_models/cosine_similarity.pkl', 'wb'))

print("Model Saved Successfully!")