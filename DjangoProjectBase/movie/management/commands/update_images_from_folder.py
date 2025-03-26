import os
from django.core.management.base import BaseCommand
from movie.models import Movie
from django.core.files import File

class Command(BaseCommand):
    help = "Update movie images in the database from a folder in media/movie/images"

    def handle(self, *args, **kwargs):
        # 📂 Ruta de la carpeta de imágenes
        image_folder = 'media/movie/images'  # Cambia esta ruta si es necesario

        # ✅ Verifica si la carpeta existe
        if not os.path.exists(image_folder):
            self.stderr.write(f"Image folder '{image_folder}' not found.")
            return

        updated_count = 0

        # 🔄 Itera sobre los archivos en la carpeta
        for image_file in os.listdir(image_folder):
            # Asegúrate de que sea un archivo de imagen
            if not image_file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                continue

            # Obtén el título de la película eliminando el prefijo 'm_' y la extensión
            if image_file.startswith('m_'):
                title = os.path.splitext(image_file)[0][2:]  # Elimina 'm_' del inicio
            else:
                self.stderr.write(f"Skipping file with unexpected format: {image_file}")
                continue

            try:
                # Busca la película por título
                movie = Movie.objects.get(title=title)

                # Actualiza la imagen de la película
                image_path = os.path.join(image_folder, image_file)
                with open(image_path, 'rb') as img_file:
                    movie.image.save(image_file, File(img_file), save=True)

                updated_count += 1
                self.stdout.write(self.style.SUCCESS(f"Updated image for: {title}"))

            except Movie.DoesNotExist:
                self.stderr.write(f"Movie not found: {title}")
            except Exception as e:
                self.stderr.write(f"Failed to update image for {title}: {str(e)}")

        # ✅ Al finalizar, muestra cuántas imágenes se actualizaron
        self.stdout.write(self.style.SUCCESS(f"Finished updating images for {updated_count} movies."))
