import pandas as pd
import ast

#load dataset
movies=pd.read_csv("../dataset/tmdb_5000_movies.csv")
credits=pd.read_csv("../dataset/tmdb_5000_credits.csv")

# print(movies.head())

print("movie shape:")
print(movies.shape)

print("credits shape:")
print(credits.shape)

print("\nmovie colmuns:")
print(movies.columns)

print("\ncredits colmuns:")
print(credits.columns)

#merge both dataset using title
print("after merging movie and credit dataset:")
movies=movies.merge(credits , on="title")

movies= movies[
    ['movie_id',
    'title',
    'overview',
    'genres',
    'keywords',
    'cast',
    'crew'
    ]
]

print(movies.head())

print("after movie shape:")
print(movies.shape)

print("col after merge:")
print(movies.columns)

#preprocess the dataset

print("missing value before cleaning:")
print(movies.isnull().sum())

movies.dropna(inplace=True)

print(" movie shape after clesning:")
print(movies.shape)

print("missing value after cleaning:")
print(movies.isnull().sum())

#function for genres and keywords
def convert(text):
    L = []

    for i in ast.literal_eval(text):
        L.append(i['name'])

    return L

#applying function
movies['genres'] = movies['genres'].apply(convert)
#remove space
movies['genres'] = movies['genres'].apply(
    lambda x: [i.replace(" ", "") for i in x]
)

movies['keywords'] = movies['keywords'].apply(convert)
#remove space
movies['keywords'] = movies['keywords'].apply(
    lambda x: [i.replace(" ", "") for i in x]
)

print(movies[['title', 'genres', 'keywords']].head())

#cast function
def convert3(text):
    L = []

    counter = 0

    for i in ast.literal_eval(text):

        if counter != 3:
            L.append(i['name'])
            counter += 1
        else:
            break

    return L

#apply cast function
movies['cast'] = movies['cast'].apply(convert3)
#remove space
movies['cast'] = movies['cast'].apply(
    lambda x: [i.replace(" ", "") for i in x]
)

print(movies[['title', 'cast']].head())

#director function
def fetch_director(text):
    L = []

    for i in ast.literal_eval(text):
        if i['job'] == 'Director':
            L.append(i['name'])
            break

    return L

#applying  director function
movies['crew'] = movies['crew'].apply(fetch_director)
#remove space
movies['crew'] = movies['crew'].apply(
    lambda x: [i.replace(" ", "") for i in x]
)

print(movies[['title', 'crew']].head())

#overview
movies['overview'] = movies['overview'].apply(lambda x: x.split())

movies['tags'] = (
    movies['overview'] +
    movies['genres'] +
    movies['keywords'] +
    movies['cast'] +
    movies['crew']
)

print(movies[['title', 'tags']].head())

#final dataset
new_df = movies[['movie_id', 'title', 'tags']]

print(new_df.head())


new_df['tags'] = new_df['tags'].apply(lambda x: " ".join(x))

new_df['tags'] = new_df['tags'].apply(lambda x: x.lower())

if __name__ == "__main__":
    print(new_df.head())
    print(new_df.shape)
 

