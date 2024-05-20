import os
import platform
import shutil
import tarfile
import tempfile
import urllib.request
import zipfile

def download_and_extract_imagemagick():
    system = platform.system().lower()
    download_url = None

    # Determine the ImageMagick download URL based on the operating system
    if system == 'linux':
        download_url = 'https://download.imagemagick.org/ImageMagick/download/binaries/ImageMagick.tar.gz'
    elif system == 'darwin':
        download_url = 'https://imagemagick.org/archive/binaries/ImageMagick-x86_64-apple-darwin20.1.0.tar.gz'
    elif system == 'windows':
        download_url = 'https://imagemagick.org/archive/binaries/ImageMagick-7.1.1-32-portable-Q16-x64.zip'
    else:
        print("Unsupported operating system")
        return

    # Create a temporary directory to store the downloaded file
    temp_dir = tempfile.mkdtemp()
    download_path = os.path.join(temp_dir, 'magick.tar.gz' if system != 'windows' else 'magick.zip')

    # Download the ImageMagick archive
    print("Downloading ImageMagick...")
    urllib.request.urlretrieve(download_url, download_path)

    # Extract the ImageMagick archive
    print("Extracting ImageMagick...")
    if system != 'windows':
        with tarfile.open(download_path, 'r:gz') as tar:
            tar.extractall(temp_dir)
    else:
        with zipfile.ZipFile(download_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

    # Find the extracted ImageMagick directory
    imagemagick_dir = None
    for name in os.listdir(temp_dir):
        if name.startswith('ImageMagick'):
            imagemagick_dir = os.path.join(temp_dir, name)
            break

    if not imagemagick_dir:
        print("Failed to find ImageMagick directory")
        return

    return imagemagick_dir

if __name__ == "__main__":
    imagemagick_dir = download_and_extract_imagemagick()
    if imagemagick_dir:
        print("ImageMagick downloaded and extracted to:", imagemagick_dir)
    else:
        print("Failed to download and extract ImageMagick")
