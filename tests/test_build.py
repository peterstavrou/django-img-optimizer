import pytest
from django.conf import settings
from django_img_optimizer.utils import get_settings, optimize_images, delete_optimized_images
import os

@pytest.fixture
def settings_config(settings):
    settings.OPTIMIZE_IMAGE_ROOT = os.path.join(settings.PROJECT_DIR, 'static', 'images')
    settings.OPTIMIZE_IMAGE_EXCLUDED_FOLDERS = ['excluded_folder']

def test_get_settings_returns_dictionary_with_expected_keys():
    expected_keys = [
        'OPTIMIZE_IMAGE_ROOT',
        'OPTIMIZE_IMAGE_QUALITY',
        'OPTIMIZE_IMAGE_TYPES',
        'OPTIMIZE_IMAGE_EXCLUDED_FOLDERS'
        ]

    result = get_settings()

    # Assert that the result is a dictionary
    assert isinstance(result, dict)

    # Assert that the dictionary contains the expected keys
    for key in expected_keys:
        assert key in result.keys(), f"Expected key '{key}' not found in settings dictionary"

def test_raise_exception_no_OPTIMIZE_IMAGE_root_set_in_settings():
    settings.OPTIMIZE_IMAGE_ROOT = None

    with pytest.raises(Exception, match="Set OPTIMIZE_IMAGE_ROOT in settings.py"):
        optimize_images()

def test_optimize_all_images(settings_config):
        optimize_images()

        # Assert webp image optimization
        assert os.path.exists(f'{settings.OPTIMIZE_IMAGE_ROOT}/logo.webp')

        # Assert that subdirectories are traversed
        assert os.path.exists(f'{settings.OPTIMIZE_IMAGE_ROOT}/subdirectory/subdirectory-logo.webp')

        # Assert that the OPTIMIZE_IMAGE_EXCLUDED_FOLDERS setting works
        assert not os.path.exists(f'{settings.OPTIMIZE_IMAGE_ROOT}/excluded_folder/exclude.webp')

        # Assert that the delete_if_optimized_image_is_smaller_or_equal function works
        assert not os.path.exists(f'{settings.OPTIMIZE_IMAGE_ROOT}/small.webp')

def test_optimized_image_template_tag(client):
    response = client.get('/')

    # Assert that the the template tag created a html picture tag containing the optimized webp image
    optimized_image = '''
    <picture>
        <source srcset="/static/images/logo.webp" type="image/webp">
        <img loading="lazy" decoding="async" src="/static/images/logo.jpg" alt="Logo" class="img-fluid">
    </picture>
    '''
    assert optimized_image in response.content.decode()

    # Assert that the the template tag created an alt and title attribute from the image name
    optimized_image_with_auto_alt_and_title_attributes = '''
    <picture>
        <source srcset="/static/images/logo-auto-attributes.webp" type="image/webp">
        <img loading="lazy" decoding="async" src="/static/images/logo-auto-attributes.jpg" alt="Logo Auto Attributes" title="Logo Auto Attributes">
    </picture>
    '''
    assert optimized_image_with_auto_alt_and_title_attributes in response.content.decode()

    # Assert that the template tag created an html picture tag that does not contain a webp image as the optimized size is larger than the original
    not_optimized_image = '''
    <picture>
        <source srcset="/static/images/small.webp" type="image/webp">
        <img loading="lazy" decoding="async" src="/static/images/small.jpg" alt="Logo Small">
    </picture>
    '''
    assert not_optimized_image not in response.content.decode()

def test_delete_all_optimized_images(settings_config):
    delete_optimized_images()

    assert not os.path.exists(f'{settings.OPTIMIZE_IMAGE_ROOT}/logo.webp')
    assert not os.path.exists(f'{settings.OPTIMIZE_IMAGE_ROOT}/subdirectory/subdirectory-logo.webp')