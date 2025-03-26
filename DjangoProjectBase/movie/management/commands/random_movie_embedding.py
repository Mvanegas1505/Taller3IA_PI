
import numpy as np
import random
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Display the embeddings of a randomly selected movie"

    def handle(self, *args, **kwargs):
        # ✅ Fetch all movies from the database
        movies = Movie.objects.all()

        if not movies.exists():
            self.stdout.write(self.style.ERROR("❌ No movies found in the database."))
            return

        # ✅ Select a random movie
        random_movie = random.choice(movies)
        self.stdout.write(f"🎲 Randomly selected movie: {random_movie.title}")

        try:
            # ✅ Load the embedding from the database
            embedding_vector = np.frombuffer(random_movie.emb, dtype=np.float32)
            self.stdout.write(f"🔍 Embedding for '{random_movie.title}': {embedding_vector}")  # Muestra los primeros 10 valores
        except Exception as e:
            self.stderr.write(f"❌ Failed to load embedding for {random_movie.title}: {e}")