import pickle

# Content-Based Models
movies = pickle.load(
    open('model/saved_models/movies.pkl', 'rb')
)

content_similarity = pickle.load(
    open('model/saved_models/cosine_similarity.pkl', 'rb')
)

# Collaborative Models
pivot_table = pickle.load(
    open('model/saved_models/user_movie_matrix.pkl', 'rb')
)

collaborative_similarity = pickle.load(
    open('model/saved_models/collaborative_similarity.pkl', 'rb')
)

# print("All Models Loaded Successfully!")

#content-Based function
def content_recommend(movie):

    try:
        movie_index = movies[movies['title'].str.lower() == movie.lower()].index[0]

        distances = content_similarity[movie_index]

        movie_list = sorted(
            list(enumerate(distances)),
            reverse=True,
            key=lambda x: x[1]
        )[1:11]

        recommendations = []

        for i in movie_list:
            recommendations.append(
                movies.iloc[i[0]].title
            )

        return recommendations
    except:
        return []

# print(content_recommend("Avatar"))   just for testing

#collaborative function
def collaborative_recommend(movie):

    try:
        movie_titles = pivot_table.index.str.lower()

        movie = movie.lower()

        index = movie_titles.get_loc(movie)

        distances = collaborative_similarity[index]

        movie_list = sorted(
            list(enumerate(distances)),
            reverse=True,
            key=lambda x: x[1]
        )[1:11]

        recommendations = []

        for i in movie_list:
            recommendations.append(
                pivot_table.index[i[0]]
            )

        return recommendations
    except:
        return []

# print(collaborative_recommend("Matrix, The (1999)"))  just for testing

#hybrid recommendation system
def hybrid_recommend(movie):

    content_movies = content_recommend(movie)

    collaborative_movies = collaborative_recommend(movie)

    final_movies = []

    final_movies.extend(content_movies)
    final_movies.extend(collaborative_movies)

    final_movies = list(dict.fromkeys(final_movies))

    return final_movies[:10]


# print("Avatar" in pivot_table.index)  just for testing

#for testing we implement later it in flask
# movie_name = input("Enter Movie Name: ")

# recommendations = hybrid_recommend(movie_name)

# if len(recommendations) == 0:
#     print("movie not found!")

# else:
#     print("\nRecommended Movies:\n")

#     for movie in recommendations:
#         print(movie)