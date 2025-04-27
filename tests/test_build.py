import pytest
from django.conf import settings
from django_img_optimizer.utils import get_settings, optimize_images, delete_optimized_images

# === Fixtures ===

@pytest.fixture
def settings_config(settings):
    """Configure custom settings for image optimization tests."""
    settings.OPTIMIZE_IMAGE_ROOT = settings.PROJECT_DIR / 'static' / 'images'
    settings.OPTIMIZE_IMAGE_EXCLUDED_FOLDERS = ['excluded_folder']

@pytest.fixture
def setup_optimized_images(settings_config):
    """Optimize images before tests that depend on generated .webp files."""
    optimize_images()


# === Tests for Settings ===

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


# === Tests for Image Optimization ===

def test_raise_exception_no_OPTIMIZE_IMAGE_root_set_in_settings():
    settings.OPTIMIZE_IMAGE_ROOT = None

    with pytest.raises(Exception, match="Set OPTIMIZE_IMAGE_ROOT in settings.py"):
        optimize_images()

def test_optimize_all_images(settings_config):
        optimize_images()

        # Assert that webp image optimization occurred
        assert (settings.OPTIMIZE_IMAGE_ROOT / 'logo.webp').exists()

        # Assert that subdirectories are traversed
        assert (settings.OPTIMIZE_IMAGE_ROOT / 'subdirectory' / 'subdirectory-logo.webp').exists()

        # Assert that excluded folders are respected
        assert not (settings.OPTIMIZE_IMAGE_ROOT / 'excluded_folder' / 'exclude.webp').exists()

        # Assert that small images are not optimized if larger or equal
        assert not (settings.OPTIMIZE_IMAGE_ROOT / 'small.webp').exists()


# === Tests for Template Tag Rendering ===

import pytest
from django.conf import settings
from django_img_optimizer.utils import get_settings, optimize_images, delete_optimized_images

# === Fixtures ===

@pytest.fixture
def settings_config(settings):
    """Configure custom settings for image optimization tests."""
    settings.OPTIMIZE_IMAGE_ROOT = settings.PROJECT_DIR / 'static' / 'images'
    settings.OPTIMIZE_IMAGE_EXCLUDED_FOLDERS = ['excluded_folder']

@pytest.fixture
def setup_optimized_images(settings_config):
    """Optimize images before tests that depend on generated .webp files."""
    optimize_images()


# === Tests for Settings ===

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


# === Tests for Image Optimization ===

def test_raise_exception_no_OPTIMIZE_IMAGE_root_set_in_settings():
    settings.OPTIMIZE_IMAGE_ROOT = None

    with pytest.raises(Exception, match="Set OPTIMIZE_IMAGE_ROOT in settings.py"):
        optimize_images()

def test_optimize_all_images(settings_config):
        optimize_images()

        # Assert that webp image optimization occurred
        assert (settings.OPTIMIZE_IMAGE_ROOT / 'logo.webp').exists()

        # Assert that subdirectories are traversed
        assert (settings.OPTIMIZE_IMAGE_ROOT / 'subdirectory' / 'subdirectory-logo.webp').exists()

        # Assert that excluded folders are respected
        assert not (settings.OPTIMIZE_IMAGE_ROOT / 'excluded_folder' / 'exclude.webp').exists()

        # Assert that small images are not optimized if larger or equal
        assert not (settings.OPTIMIZE_IMAGE_ROOT / 'small.webp').exists()


# === Tests for Template Tag Rendering ===

def test_optimized_image_template_tag(client, setup_optimized_images):
    response = client.get('/')
    content = response.content.decode()

    # Assert that the response returned successfully
    assert response.status_code == 200

    # === Tests for logo.jpg ===

    # Assert <picture> and fallback <img> are created
    assert '<picture>' in content
    assert '<img loading="lazy" decoding="async" src="/static/images/logo.jpg" alt="Logo" class="img-fluid">' in content
    assert '</picture>' in content

    # Assert <source> for optimized logo.webp is created
    assert '<source srcset="/static/images/logo.webp" type="image/webp">' in content

    # === Tests for logo-auto-attributes.jpg ===

    # Assert <source> for optimized logo-auto-attributes.webp is created
    assert '<source srcset="/static/images/logo-auto-attributes.webp" type="image/webp">' in content

    # Assert <img> fallback with auto alt/title is created
    assert '<img loading="lazy" decoding="async" src="/static/images/logo-auto-attributes.jpg" alt="Logo Auto Attributes" title="Logo Auto Attributes">' in content

    # === Tests for small.jpg ===

    # Assert no <source> for small.webp (not optimized)
    assert '<source srcset="/static/images/small.webp" type="image/webp">' not in content

    # Assert <img> fallback exists for small.jpg
    assert '<img loading="lazy" decoding="async" src="/static/images/small.jpg" alt="Logo Small">' in content


# === Tests for Deleting Optimized Images ===

def test_delete_all_optimized_images(settings_config):
    delete_optimized_images()

    # Assert that optimized images are deleted
    assert not (settings.OPTIMIZE_IMAGE_ROOT / 'logo.webp').exists()
    assert not (settings.OPTIMIZE_IMAGE_ROOT / 'subdirectory' / 'subdirectory-logo.webp').exists()
