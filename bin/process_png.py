import os
import shutil
from PIL import Image
import subprocess
import click
import glob


@click.command()
@click.argument('image_directory', type=click.Path(exists=True))
def process_images(image_directory):
    # Create subdirectories
    original_dir = os.path.join(image_directory, 'original')
    resized_dir = os.path.join(image_directory, '50x50')

    os.makedirs(original_dir, exist_ok=True)
    os.makedirs(resized_dir, exist_ok=True)

    # Copy files to subdirectories
    for filename in glob.glob(os.path.join(image_directory, '*.png')):
        shutil.copy(filename, original_dir)
        shutil.copy(filename, resized_dir)

    # Run mogrify commands
    subprocess.run(['mogrify', '-resize', '50x50', os.path.join(resized_dir, '*.png')])
    subprocess.run(['mogrify', '-format', 'png', '-alpha', 'on', os.path.join(resized_dir, '*.png')])
    subprocess.run(['mogrify', '-fill', 'black', '-colorize', '100', os.path.join(resized_dir, '*.png')])

    # Process images with PIL
    for image_path in glob.glob(os.path.join(resized_dir, '*.png')):
        with Image.open(image_path).convert("RGBA").resize((50, 50), Image.Resampling.LANCZOS) as image:
            image.save(image_path)


if __name__ == '__main__':
    process_images()
