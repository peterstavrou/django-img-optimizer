from django.conf import settings
from glob import iglob
import os
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
    OPTIMIZE_IMAGE_ROOT = image_optimizer_settings.get('OPTIMIZE_IMAGE_ROOT')

    for file in iglob(f'{OPTIMIZE_IMAGE_ROOT}/**', recursive=True):
        if os.path.isfile(file):
            file_extension = file.rsplit('.', 1)[-1]
            if file_extension in ['webp']:
                os.remove(file)

    print('Optimized images have been deleted.')

def delete_if_optimized_image_is_larger(original_file: str, output_file: str):
    """ Compares the original image to the optimized image and deletes it they it is larger in size. """
    file_size = os.path.getsize(original_file)
    output_file_size = os.path.getsize(output_file)

    if output_file_size >= file_size:
        os.remove(output_file)

def optimize_images():
    """
    Optimize images by converting them to WebP format with a specified quality (100 by default).
    Deletes the optimized image if it is larger than the original.
    """
    image_optimizer_settings = get_settings()
    OPTIMIZE_IMAGE_ROOT = image_optimizer_settings.get('OPTIMIZE_IMAGE_ROOT')
    OPTIMIZE_IMAGE_TYPES = image_optimizer_settings.get('OPTIMIZE_IMAGE_TYPES')
    OPTIMIZE_IMAGE_QUALITY = image_optimizer_settings.get('OPTIMIZE_IMAGE_QUALITY')
    OPTIMIZE_IMAGE_EXCLUDED_FOLDERS = image_optimizer_settings.get('OPTIMIZE_IMAGE_EXCLUDED_FOLDERS')

    for file in iglob(f'{OPTIMIZE_IMAGE_ROOT}/**', recursive=True):
        folder_name = os.path.basename(os.path.dirname(file))

        if os.path.isfile(file) and (folder_name not in OPTIMIZE_IMAGE_EXCLUDED_FOLDERS):
            split_file_name = file.rsplit('.', 1)
            file_path_and_name = split_file_name[0]
            file_extension = split_file_name[-1]

            if file_extension in OPTIMIZE_IMAGE_TYPES:
                image = Image.open(file)
                output_file = f'{file_path_and_name}.webp'
                image.save(output_file, 'webp', quality=OPTIMIZE_IMAGE_QUALITY)
                delete_if_optimized_image_is_larger(file, output_file)

    print('Image optimization complete.')