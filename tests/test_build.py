from io import StringIO

import pytest
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.template import Context, Template
from PIL import Image

from django_img_optimizer.utils import (
    ImageOptimizationError,
    delete_optimized_images,
    get_settings,
    optimize_images,
)


@pytest.fixture
def settings_config(settings):
    settings.OPTIMIZE_IMAGE_ROOT = settings.PROJECT_DIR / 'static' / 'images'
    settings.OPTIMIZE_IMAGE_EXCLUDED_FOLDERS = ['excluded_folder']
    yield
    delete_optimized_images()


@pytest.fixture
def setup_optimized_images(settings_config):
    optimize_images()


def save_large_jpeg(file_path):
    image = Image.effect_noise((800, 600), 100).convert('RGB')
    image.save(file_path, 'JPEG', quality=100)


def configure_temporary_root(settings, root):
    settings.OPTIMIZE_IMAGE_ROOT = root
    settings.OPTIMIZE_IMAGE_EXCLUDED_FOLDERS = []


def test_get_settings_returns_validated_settings(settings_config):
    result = get_settings()

    assert result['OPTIMIZE_IMAGE_ROOT'] == settings.OPTIMIZE_IMAGE_ROOT
    assert result['OPTIMIZE_IMAGE_TYPES'] == {'jpeg', 'jpg', 'png'}
    assert result['OPTIMIZE_IMAGE_EXCLUDED_FOLDERS'] == {'excluded_folder'}
    assert result['OPTIMIZE_IMAGE_AVIF_QUALITY'] == 61
    assert result['OPTIMIZE_IMAGE_WEBP_QUALITY'] == 80


def test_settings_accept_none_for_excluded_folders(settings_config, settings):
    settings.OPTIMIZE_IMAGE_EXCLUDED_FOLDERS = None

    assert get_settings()['OPTIMIZE_IMAGE_EXCLUDED_FOLDERS'] == set()


def test_missing_image_root_raises_a_configuration_error(settings):
    settings.OPTIMIZE_IMAGE_ROOT = None

    with pytest.raises(ImproperlyConfigured, match='Set OPTIMIZE_IMAGE_ROOT'):
        optimize_images()


def test_optimize_all_images(settings_config):
    optimize_images()

    for output_format in ['avif', 'webp']:
        assert (settings.OPTIMIZE_IMAGE_ROOT / f'logo.{output_format}').exists()
        assert (
            settings.OPTIMIZE_IMAGE_ROOT
            / 'subdirectory'
            / f'subdirectory-logo.{output_format}'
        ).exists()
        assert not (
            settings.OPTIMIZE_IMAGE_ROOT
            / 'excluded_folder'
            / f'exclude.{output_format}'
        ).exists()


def test_optimized_files_keep_the_original_dimensions(settings, tmp_path):
    save_large_jpeg(tmp_path / 'image.jpg')
    configure_temporary_root(settings, tmp_path)

    optimize_images()

    for output_format in ['avif', 'webp']:
        with Image.open(tmp_path / f'image.{output_format}') as optimized_image:
            assert optimized_image.size == (800, 600)


@pytest.mark.parametrize('extra_bytes', [0, 1])
def test_discards_renditions_that_are_not_smaller(settings, tmp_path, monkeypatch, extra_bytes):
    source_file = tmp_path / 'image.jpg'
    Image.new('RGB', (1, 1), 'blue').save(source_file)
    configure_temporary_root(settings, tmp_path)

    def save_rendition(image, output_file, pillow_format, quality):
        output_file.write_bytes(b'x' * (source_file.stat().st_size + extra_bytes))

    monkeypatch.setattr('django_img_optimizer.utils._save_rendition', save_rendition)
    optimize_images()

    assert not (tmp_path / 'image.avif').exists()
    assert not (tmp_path / 'image.webp').exists()


def test_renditions_preserve_png_transparency(settings, tmp_path):
    image = Image.effect_noise((800, 600), 100).convert('RGBA')
    image.putalpha(Image.effect_noise((800, 600), 100))
    image.save(tmp_path / 'transparent.png')
    configure_temporary_root(settings, tmp_path)

    optimize_images()

    for output_format in ['avif', 'webp']:
        with Image.open(tmp_path / f'transparent.{output_format}') as rendition:
            assert 'A' in rendition.getbands()


def test_excluded_folder_excludes_all_descendants(settings, tmp_path):
    nested_excluded_folder = tmp_path / 'excluded' / 'nested'
    nested_excluded_folder.mkdir(parents=True)
    save_large_jpeg(nested_excluded_folder / 'excluded.jpg')
    save_large_jpeg(tmp_path / 'included.jpg')
    configure_temporary_root(settings, tmp_path)
    settings.OPTIMIZE_IMAGE_EXCLUDED_FOLDERS = ['excluded']

    optimize_images()

    assert (tmp_path / 'included.avif').exists()
    assert (tmp_path / 'included.webp').exists()
    assert not (nested_excluded_folder / 'excluded.avif').exists()
    assert not (nested_excluded_folder / 'excluded.webp').exists()


def test_rejects_conflicting_output_names(settings, tmp_path):
    save_large_jpeg(tmp_path / 'logo.jpg')
    Image.new('RGB', (800, 600), 'blue').save(tmp_path / 'logo.png')
    configure_temporary_root(settings, tmp_path)

    with pytest.raises(ImageOptimizationError, match='Multiple source images'):
        optimize_images()


def test_does_not_overwrite_or_delete_unmanaged_optimized_files(settings, tmp_path):
    save_large_jpeg(tmp_path / 'image.jpg')
    manual_webp = tmp_path / 'image.webp'
    Image.new('RGB', (10, 10), 'red').save(manual_webp, 'WEBP')
    original_manual_file = manual_webp.read_bytes()
    configure_temporary_root(settings, tmp_path)

    summary = optimize_images()
    deleted_count = delete_optimized_images()

    assert summary['skipped'] == 1
    assert deleted_count == 1
    assert manual_webp.read_bytes() == original_manual_file


def test_delete_removes_only_manifest_tracked_files(settings, tmp_path):
    save_large_jpeg(tmp_path / 'image.jpg')
    manual_webp = tmp_path / 'manual.webp'
    Image.new('RGB', (10, 10), 'red').save(manual_webp, 'WEBP')
    configure_temporary_root(settings, tmp_path)

    optimize_images()
    deleted_count = delete_optimized_images()

    assert deleted_count == 2
    assert not (tmp_path / 'image.avif').exists()
    assert not (tmp_path / 'image.webp').exists()
    assert manual_webp.exists()
    assert not (tmp_path / '.django-img-optimizer.json').exists()


def test_failed_optimization_keeps_generated_files_tracked(settings, tmp_path):
    save_large_jpeg(tmp_path / 'a.jpg')
    (tmp_path / 'b.jpg').write_bytes(b'not an image')
    configure_temporary_root(settings, tmp_path)

    with pytest.raises(ImageOptimizationError, match='Could not optimize b.jpg'):
        optimize_images()

    assert delete_optimized_images() == 2
    assert not (tmp_path / 'a.avif').exists()
    assert not (tmp_path / 'a.webp').exists()


def test_command_reports_the_optimization_summary(settings, tmp_path):
    save_large_jpeg(tmp_path / 'image.jpg')
    configure_temporary_root(settings, tmp_path)
    output = StringIO()

    call_command('optimize_images', stdout=output)

    assert 'Image optimization complete. Generated: 2.' in output.getvalue()


def test_optimized_image_template_tag(client, setup_optimized_images):
    response = client.get('/')
    content = response.content.decode()

    assert response.status_code == 200
    assert '<picture>' in content
    assert '<source srcset="/static/images/logo.avif" type="image/avif">' in content
    assert '<source srcset="/static/images/logo.webp" type="image/webp">' in content
    assert '<img loading="lazy" decoding="async" src="/static/images/logo.jpg" alt="Logo" class="img-fluid">' in content
    assert '<img loading="lazy" decoding="async" src="/static/images/logo-auto-attributes.jpg" alt="Logo Auto Attributes" title="Logo Auto Attributes">' in content
    assert content.index('type="image/avif"') < content.index('type="image/webp"')
    assert 'data-bs-toggle="modal"' in content
    assert 'data-bs-target="#exampleModal"' in content
    assert 'data_bs_toggle' not in content
    assert 'data_bs_target' not in content


def test_template_tag_escapes_attribute_values():
    content = Template(
        '{% load image_optimizer %}'
        '{% optimized_image src="images/logo.jpg" alt=unsafe_alt %}'
    ).render(Context({'unsafe_alt': 'One" onerror="alert(1)'}))

    assert 'alt="One&quot; onerror=&quot;alert(1)"' in content
    assert '<img src="/static/images/logo.jpg" alt="One&quot; onerror=&quot;alert(1)">' in content
