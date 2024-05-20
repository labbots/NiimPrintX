import os
import pickle
from pathlib import Path
import appdirs
import time

class CacheManager:
    def __init__(self, app_name):
        """
        Initializes the cache manager with the application name to determine
        the cache directory.

        :param app_name: Name of the application for creating a dedicated cache directory.
        """
        self.cache_dir = Path(appdirs.user_cache_dir(app_name))
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get_cache_path(self, filename):
        """
        Constructs a full path for the given cache filename within the cache directory.

        :param filename: Filename to be used in the cache directory.
        :return: Path object representing the file path.
        """
        return self.cache_dir / filename

    def save_to_cache(self, data, filename):
        """
        Saves data to a file in the cache directory, including the current timestamp.

        :param data: Data to be serialized and saved.
        :param filename: Cache filename under which to save the data.
        """
        cache_path = self.get_cache_path(filename)
        # Data is stored as a tuple (timestamp, actual_data)
        with open(cache_path, 'wb') as f:
            pickle.dump((time.time(), data), f)

    def load_from_cache(self, filename, expiration_sec=None):
        """
        Loads data from a cache file if it exists and is not expired.

        :param filename: Cache filename from which to load the data.
        :param expiration_sec: Time in seconds after which the cache should be considered expired.
        :return: Deserialized data if file exists and is fresh, None otherwise.
        """
        cache_path = self.get_cache_path(filename)
        if cache_path.exists():
            with open(cache_path, 'rb') as f:
                stored_time, data = pickle.load(f)
                # Check if the data is still fresh
                if expiration_sec is None or (time.time() - stored_time) < expiration_sec:
                    return data
        return None

    def get_data(self, filename, compute_data_func, expiration_sec=None):
        """
        Retrieves data from cache or computes it if not available or expired.

        :param filename: Filename for the cache file.
        :param compute_data_func: Function to generate data if not in cache or data is expired.
        :param expiration_sec: Expiration time in seconds for cache validity.
        :return: The loaded or computed data.
        """
        data = self.load_from_cache(filename, expiration_sec)
        if data is None:
            data = compute_data_func()
            self.save_to_cache(data, filename)
        return data

# Example usage
def compute_expensive_data():
    # Placeholder function that simulates an expensive computation
    return {"key": "value", "important": "data"}

# Create a cache manager instance for your application
cache_manager = CacheManager('MyApp')

# Using the cache manager to get data, with cache expiring after 60 seconds (1 minute)
data = cache_manager.get_data('my_cache.pkl', compute_expensive_data, expiration_sec=60)
print(data)
