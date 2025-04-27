from django.conf import settings
from glob import iglob
from pathlib import Path
from PIL import Image


def get_settings():
    """ Retrieves the optimization settings from the Django settings """
    OPTIMIZE_IMAGE_ROOT = getattr(settings, 'OPTIMIZE_IMAGE_ROOT', None)
    if not OPTIMIZE_IMAGE_ROOT:
        raise Exception("Set OPTIMIZE_IMAGE_ROOT in settings.py")

    OPTIMIZE_IMAGE_QUALITY = getattr(settings, 'OPTIMIZE_IMAGE_QUALITY', 100)
    if OPTIMIZE_IMAGE_QUALITY < 0 or OPTIMIZE_IMAGE_QUALITY > 100:
        raise Exception("Image Quality needs to be between 0 and 100")

    OPTIMIZE_IMAGE_TYPES = getattr(settings, 'OPTIMIZE_IMAGE_TYPES', ['jpg', 'jpeg', 'png'])

    OPTIMIZE_IMAGE_EXCLUDED_FOLDERS = getattr(settings, 'OPTIMIZE_IMAGE_EXCLUDED_FOLDERS', [])

    return {
        'OPTIMIZE_IMAGE_ROOT': OPTIMIZE_IMAGE_ROOT,
        'OPTIMIZE_IMAGE_TYPES': OPTIMIZE_IMAGE_TYPES,
        'OPTIMIZE_IMAGE_QUALITY': OPTIMIZE_IMAGE_QUALITY,
        'OPTIMIZE_IMAGE_EXCLUDED_FOLDERS': OPTIMIZE_IMAGE_EXCLUDED_FOLDERS
    }

def delete_optimized_images():
    """ Delete all optimized images. """
    image_optimizer_settings = get_settings()
    OPTIMIZE_IMAGE_ROOT = Path(image_optimizer_settings.get('OPTIMIZE_IMAGE_ROOT'))

    for file in iglob(f'{OPTIMIZE_IMAGE_ROOT}/**', recursive=True):
        file_path = Path(file)
        if file_path.is_file() and file_path.suffix in ['.webp']:
            file_path.unlink()

    print('Optimized images have been deleted.')

def delete_if_optimized_image_is_larger(original_file: Path, output_file: Path):
    """ Compares the original image to the optimized image and deletes it if it is larger in size. """
    if output_file.stat().st_size >= original_file.stat().st_size:
        output_file.unlink()

def optimize_images():
    """
    Optimize images by converting them to WebP format with a specified quality (100 by default).
    Deletes the optimized image if it is larger than the original.
    """
    image_optimizer_settings = get_settings()
    OPTIMIZE_IMAGE_ROOT = Path(image_optimizer_settings.get('OPTIMIZE_IMAGE_ROOT'))
    OPTIMIZE_IMAGE_TYPES = image_optimizer_settings.get('OPTIMIZE_IMAGE_TYPES')
    OPTIMIZE_IMAGE_QUALITY = image_optimizer_settings.get('OPTIMIZE_IMAGE_QUALITY')
    OPTIMIZE_IMAGE_EXCLUDED_FOLDERS = image_optimizer_settings.get('OPTIMIZE_IMAGE_EXCLUDED_FOLDERS')

    for file in iglob(f'{OPTIMIZE_IMAGE_ROOT}/**', recursive=True):
        file_path = Path(file)
        folder_name = file_path.parent.name

        if file_path.is_file() and folder_name not in OPTIMIZE_IMAGE_EXCLUDED_FOLDERS:
            file_extension = file_path.suffix.lstrip('.')

            if file_extension in OPTIMIZE_IMAGE_TYPES:
                image = Image.open(file_path)

                # Create and save WebP
                webp_output_file = file_path.with_suffix('.webp')
                image.save(webp_output_file, 'webp', quality=OPTIMIZE_IMAGE_QUALITY)
                delete_if_optimized_image_is_larger(file_path, webp_output_file)

    print('Image optimization complete.')