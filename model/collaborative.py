import pandas as pd 
import pickle

movies=pd.read_csv("../dataset/movies.csv")
ratings=pd.read_csv("../dataset/ratings.csv")

print(movies.head())
print(ratings.head())

print("movie shape:",movies.shape)
print("ratings shape:",ratings.shape)

# print(movies.columns)
# print(ratings.columns)

#combine both movie and ratings dataset
movies_with_ratings = movies.merge(ratings, on="movieId")

print(movies_with_ratings.head())
print(movies_with_ratings.shape)

#finding popular  movie
movie_ratings = movies_with_ratings.groupby('title').count()['rating']

print(movie_ratings.sort_values(ascending=False).head())

#rating statistics
ratings_count = movies_with_ratings.groupby('title')['rating'].count().reset_index()

ratings_count.rename(columns={'rating':'num_of_ratings'}, inplace=True)
print(ratings_count.head())

#merge rating count
final_df = movies_with_ratings.merge(ratings_count, on='title')
print(final_df.head())

#filter   popular movie
final_df = final_df[final_df['num_of_ratings'] >= 50]

print(final_df.shape)

#user movie matrix
pivot_table = final_df.pivot_table(
    index='title',
    columns='userId',
    values='rating'
)

print(pivot_table.shape)

pivot_table.fillna(0, inplace=True)

print(pivot_table.head())

#calculating movie similarity
from sklearn.metrics.pairwise import cosine_similarity

similarity_scores = cosine_similarity(pivot_table)

print(similarity_scores.shape)

#recommendation fucntion for collaborative flitering
def recommend_movie(movie_name):
    if movie_name not in pivot_table.index:
        print("Movie not found!")
        return

    index = pivot_table.index.get_loc(movie_name)

    distances = similarity_scores[index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:11]

    print("\nRecommended Movies:\n")

    for i in movies_list:
        print(pivot_table.index[i[0]])


# for movie in pivot_table.index:
#     if "Matrix" in movie:
#         print(movie)
# recommend_movie("Matrix, The (1999)")

#save model
pickle.dump(pivot_table,open('saved_models/user_movie_matrix.pkl','wb'))

pickle.dump(similarity_scores,open('saved_models/collaborative_similarity.pkl','wb'))

print("collaborative model saved successfully ")