import requests
import json
import csv
import urllib.request
import os

# Define your API key as an environment variable or use a configuration file.
api_key = '3ef01f7a6eff27b4130d190a24fc0822'

def get_movie_details(movie_id):
    """
    Get detailed information about a movie by its ID.
    """
    url = f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&append_to_response=credits'
    response = requests.get(url)
    data = json.loads(response.content)
    return data

def get_genre(genre_list):
    """
    Get the genre name from a list of genres.
    """
    return genre_list[0]['name'] if genre_list else 'Unknown'

def discover_movies(page=1):
    """
    Discover movies within a specified release date range.
    """
    url = f'https://api.themoviedb.org/3/discover/movie?api_key={api_key}&primary_release_date.gte=1900-01-01&primary_release_date.lte=2023-12-31&page={page}'
    response = requests.get(url)
    data = json.loads(response.content)
    return data.get('results', [])

# Create a directory to store images
image_dir = 'images'
os.makedirs(image_dir, exist_ok=True)

movie_list = []

# Retrieve movie data from multiple pages
for page in range(1, 101):
    movies = discover_movies(page)
    movie_list.extend(movies)
    if len(movie_list) >= 2000:
        break

# Write movie data to a CSV file
with open('movies.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['Title', 'Rating', 'Genre', 'Year', 'Director', 'Image']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
    writer.writeheader()

    for movie in movie_list:
        movie_data = get_movie_details(movie['id'])
        title = movie_data['title']
        rating = movie_data['vote_average']
        genre = get_genre(movie_data['genres'])
        year = movie_data['release_date'][:4]
        director = next((crew['name'] for crew in movie_data['credits']['crew'] if crew.get('job') == 'Director'), 'Unknown')

        poster_path = movie_data['poster_path']
        image_path = os.path.join(image_dir, f'{movie["id"]}.jpg')
        if poster_path:
            image_url = f'https://image.tmdb.org/t/p/w500{poster_path}'
            try:
                urllib.request.urlretrieve(image_url, image_path)
            except urllib.error.HTTPError:
                image_path = os.path.join(image_dir, 'noimage.jpg')

        writer.writerow({'Title': title, 'Rating': rating, 'Genre': genre, 'Year': year, 'Director': director, 'Image': image_path})