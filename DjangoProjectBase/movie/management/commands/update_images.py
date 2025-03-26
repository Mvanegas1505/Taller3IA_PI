import os
import requests
from openai import OpenAI
from django.core.management.base import BaseCommand
from movie.models import Movie
from dotenv import load_dotenv

class Command(BaseCommand):
    help = "Generate images with OpenAI and update movie image field"

    def handle(self, *args, **kwargs):
        # ✅ Load environment variables from the .env file
        load_dotenv('../openAI.env')

        # ✅ Initialize the OpenAI client with the API key
        client = OpenAI(
            api_key=os.environ.get('openai_apikey'),
        )
        # ✅ Folder to save images
        images_folder = 'media/movie/images/'
        os.makedirs(images_folder, exist_ok=True)

        # ✅ Fetch all movies
        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies")

        for movie in movies:
            try:
                # ✅ Call the helper function
                image_relative_path = self.generate_and_download_image(client, movie.title, images_folder)

                # ✅ Update database
                movie.image = image_relative_path
                movie.save()
                self.stdout.write(self.style.SUCCESS(f"Saved and updated image for: {movie.title}"))

            except Exception as e:
                self.stderr.write(f"Failed for {movie.title}: {e}")

            # 🔎 Process just the first movie for demonstration
            break

        self.stdout.write(self.style.SUCCESS("Process finished (only first movie updated)."))

    def generate_and_download_image(self, client, movie_title, save_folder):
        """
        Generates an image using OpenAI's DALL·E model and downloads it.
        Returns the relative image path or raises an exception.
        """
        prompt = f"Movie poster of {movie_title}"

        # ✅ Generate image with OpenAI
        response = client.images.generate(
            model="dall-e-2",
            prompt=prompt,
            size="256x256",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url

        # ✅ Prepare the filename and full save path
        image_filename = f"m_{movie_title}.png"
        image_path_full = os.path.join(save_folder, image_filename)

        # ✅ Download the image
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        with open(image_path_full, 'wb') as f:
            f.write(image_response.content)

        # ✅ Return relative path to be saved in the DB
        return os.path.join('movie/images', image_filename)
import os
import csv
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Update movie descriptions in the database from a CSV file"

    def handle(self, *args, **kwargs):
        # 📥 Ruta del archivo CSV con las descripciones actualizadas
        csv_file = 'updated_movie_descriptions.csv'  # ← Puedes cambiar el nombre si es necesario

        # ✅ Verifica si el archivo existe
        if not os.path.exists(csv_file):
            self.stderr.write(f"CSV file '{csv_file}' not found.")
            return

        updated_count = 0

        # 📖 Abrimos el CSV y leemos cada fila
        with open(csv_file, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                title = row['Title']
                new_description = row['Updated Description']

                try:
                    # ❗ Aquí debes completar el código para buscar la película por título
                    movie = Movie.objects.get(title = title)

                    # ❗ Aquí debes actualizar la descripción de la película
                    movie.description = new_description
                    movie.save()
                    updated_count += 1

                    self.stdout.write(self.style.SUCCESS(f"Updated: {title}"))

                except Movie.DoesNotExist:
                    self.stderr.write(f"Movie not found: {title}")
                except Exception as e:
                    self.stderr.write(f"Failed to update {title}: {str(e)}")

        # ✅ Al finalizar, muestra cuántas películas se actualizaron
        self.stdout.write(self.style.SUCCESS(f"Finished updating {updated_count} movies from CSV."))
