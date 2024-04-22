# Django Image Optimizer

[![pytest](https://github.com/peterstavrou/django-img-optimizer/actions/workflows/build.yml/badge.svg)](https://github.com/peterstavrou/django-img-optimizer/actions) &nbsp; [![pypi](https://img.shields.io/badge/dynamic/toml?url=https://raw.githubusercontent.com/peterstavrou/django-img-optimizer/main/pyproject.toml&prefix=v&query=project.version&label=pypi&color=blue)](https://pypi.org/project/django-img-optimizer/1.1/)  &nbsp; [![mit-license](https://img.shields.io/badge/license-MIT-9d9d9d)](https://github.com/peterstavrou/django-img-optimizer/blob/main/LICENSE)

Django Image Optimizer converts images to WebP format while allowing you to specify the quality of the image. Optimized images that are larger than their originals are automatically deleted.

## Installation
    pip install django-img-optimizer

## Configuration

Add django_img_optimizer to `INSTALLED_APPS` in your projects `settings.py` file:

```
    INSTALLED_APPS = [
        ...
        'django_img_optimizer',
        ...
    ]
```

Set `OPTIMIZE_IMAGE_ROOT` to the top-level folder containing the images that you would like to optimize. django_img_optimizer will search through all subfolders for the specified image types.

**Example:**

If you have a folder inside static called images:

    OPTIMIZE_IMAGE_ROOT = os.path.join(PROJECT_DIR, 'static', 'images')

---
### Optional Settings

#### Image Quality

`OPTIMIZE_IMAGE_QUALITY` specifies the optimization image quality on a scale from 0 (worst) to 100 (best). The lower the quality, the smaller the size of the file.

Default is `100`.

**Example:**

    OPTIMIZE_IMAGE_QUALITY = 100

---

#### Image Types

`OPTIMIZE_IMAGE_TYPES` specifies a list of image types that you want to optimize.

Default is  `['jpg', 'jpeg', 'png']`.

**Example:**

    OPTIMIZE_IMAGE_TYPES = ['jpg', 'jpeg', 'png']

---

#### Exclude Folders

`OPTIMIZE_IMAGE_EXCLUDED_FOLDERS` is used to exclude specific folders from the optimization process.

Default is `None`.

**Example:**

    OPTIMIZE_IMAGE_EXCLUDED_FOLDERS = ['backup-larger-versions']


## Usage

###  Command line

Optimize all images:

    python manage.py optimize_images

Delete all optimized images:

    python manage.py optimize_images --delete

###  Django templates

Load the optimized images in Django templates:

    {% load image_optimizer %}

    {% optimized_image 'loading="lazy"' 'decoding="async"' 'src="images/logo.jpg"' 'alt="Logo"' 'class="img-fluid"' %}

This will render:

    <picture>
        <source srcset="/static/images/logo.webp" type="image/webp">
        <img loading="lazy" decoding="async" src="/static/images/logo.jpg" alt="Logo" class="img-fluid">
    </picture>

Pass in any `<img>` attribute by wrapping it between  single quotes `'`.

You can use variables with the `optimize_image` template tag that have been passed through `include` by using the built-in Django filter <a href="https://docs.djangoproject.com/en/5.0/ref/templates/builtins/#add" target="_blank">add</a>.

**Example:**

index.html

    {% include 'partials/include.html' with image_name='logo'  %}

include.html

    {% with src='"images/'|add:image_name|add:'.jpg"' %}
        {% optimized_image 'src='|add:src %}
    {% endwith %}

This will render:

    <picture>
        <source srcset="/static/images/logo.webp" type="image/webp">
        <img src="/static/images/logo.jpg">
    </picture>

**Code Breakdown:**

src is set to: `src='"images/'`

The single quotes `'` around `"images/` indicates that it is a string.

`|add:image_name`  adds the `image_name` variable to the string, resulting in: `src="images/logo`

`|add:'.jpg"'` adds `.jpg"` to the string, resulting in: `src="images/logo.jpg"`

## AVIF Image Support

django_img_optimizer utilizes `python-pillow` which currently lacks official support for AVIF files.
However, a <a href="https://github.com/python-pillow/Pillow/pull/5201" target="_blank">pull request</a>
 is in progress to enable this.
