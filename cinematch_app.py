import streamlit as st
import requests
import random

API_KEY = '5cb3d1d197734a71fc8826dbf5b2c29f'

def get_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=es-ES&append_to_response=credits"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    return None

def get_movie_recommendations(genre_id, year=None, page=1):
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={API_KEY}&with_genres={genre_id}&language=es-ES&page={page}"
    
    if year and year != "Random":
        url += f"&primary_release_year={year}"

    response = requests.get(url)
    data = response.json()
    if 'results' in data:
        filtered_results = [
            (movie['id'], movie['title'], movie['overview'], movie['poster_path'])
            for movie in data['results']
            if movie.get('original_language') in ['es', 'en']
        ][:5]
        return filtered_results
    else:
        return []

def display_movie_details(movie_id, title, overview, poster_path):
    movie_details = get_movie_details(movie_id)
    if movie_details:
        year = movie_details.get('release_date', '').split('-')[0]
        director = ', '.join([crew['name'] for crew in movie_details.get('credits', {}).get('crew', []) if crew['job'] == 'Director'])
        cast = ', '.join([cast['name'] for cast in movie_details.get('credits', {}).get('cast', [])[:3]])
        
        with st.expander(f"{title} ({year})"):
            st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", width=300)
            st.write("Descripción:", overview)
            st.write(f"Año: {year}")
            st.write(f"Director: {director}")
            st.write(f"Reparto principal: {cast}")
            rating = st.slider(f'Califica {title}:', 1, 5, 3)
            st.write(f'Has calificado {title} con {rating} estrellas.')
    else:
        st.error("Error al obtener detalles de la película.")

def main():
    st.title("CineMatch – Tu Recomendador Personalizado de Películas")
    st.write("Descubre películas adaptadas a tus gustos, disponibles en español o inglés.")

    genre_options = {
        "Acción": 28,
        "Comedia": 35,
        "Drama": 18,
        "Terror": 27,
        "Ciencia Ficción": 878,
        "Documental": 99
    }
    genre = st.selectbox("Elige tu género favorito", options=list(genre_options.keys()))
    years = ["Random"] + [str(year) for year in range(2024, 1899, -1)]
    year = st.selectbox("Año de estreno (opcional):", options=years, index=0)

    if 'page' not in st.session_state:
        st.session_state.page = 1

    if st.button('Obtener Recomendaciones'):
        st.session_state.page = random.randint(1, 10)
        st.session_state.recommendations = get_movie_recommendations(genre_options[genre], year if year != "Random" else None, st.session_state.page)

    if 'recommendations' in st.session_state and st.session_state.recommendations:
        for movie_id, movie_title, movie_details, poster_path in st.session_state.recommendations:
            display_movie_details(movie_id, movie_title, movie_details, poster_path)
        
        if st.button('Mostrar más películas'):
            st.session_state.page = random.randint(1, 10)
            st.session_state.recommendations = get_movie_recommendations(genre_options[genre], year if year != "Random" else None, st.session_state.page)
            st.rerun()

    st.write("## Cómo Funciona")
    st.write("""
    CineMatch utiliza la API de TMDB para obtener datos actualizados sobre películas y ofrecer recomendaciones basadas en tus preferencias de género y año de estreno. Las películas mostradas están garantizadas para tener información en español o inglés.
    """)

if __name__ == "__main__":
    main()
