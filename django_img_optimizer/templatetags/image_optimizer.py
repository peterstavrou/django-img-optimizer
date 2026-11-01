from pathlib import Path

from django import template
from django.contrib.staticfiles.finders import find
from django.templatetags.static import static
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

from django_img_optimizer.utils import OUTPUT_FORMATS


register = template.Library()


@register.simple_tag()
def optimized_image(**attrs):
    """Return a picture element with AVIF, WebP, and original fallbacks."""

    # Ensure src is provided.
    relative_image_path = attrs.get('src')
    if not relative_image_path:
        return mark_safe('<!-- optimized_image tag missing "src" attribute -->')

    # Build the relative source and static URL paths.
    relative_path = Path(str(relative_image_path))
    attrs['src'] = static(relative_path.as_posix())

    # Create alt and/or title attributes from the filename.
    if attrs.get('alt') == 'auto' or attrs.get('title') == 'auto':
        image_name = relative_path.stem.replace('-', ' ').replace('_', ' ').title()
        for key in ['alt', 'title']:
            if attrs.get(key) == 'auto':
                attrs[key] = image_name

    # Build safe HTML attributes and convert underscores to hyphens.
    attributes_output = format_html_join(
        ' ',
        '{}="{}"',
        ((key.replace('_', '-'), value) for key, value in attrs.items()),
    )

    source_tags = []
    for output_format, output_settings in OUTPUT_FORMATS.items():
        optimized_image_path = relative_path.with_suffix(f'.{output_format}').as_posix()
        if find(optimized_image_path):
            source_tags.append(
                format_html(
                    '<source srcset="{}" type="{}">',
                    static(optimized_image_path),
                    output_settings['mime_type'],
                )
            )

    picture_content = format_html_join(
        '\n',
        '{}',
        ((tag,) for tag in [*source_tags, format_html('<img {}>', attributes_output)]),
    )
    return format_html('<picture>\n{}\n</picture>', picture_content)
