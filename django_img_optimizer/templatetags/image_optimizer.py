from django import template
from django.templatetags.static import static
from django.utils.safestring  import mark_safe
from django.contrib.staticfiles.finders import find
from pathlib import Path


register = template.Library()

@register.simple_tag()
def optimized_image(**attrs):
    """
    Returns:
        str: An HTML <picture> tag with an optimized WebP image if available, or just the original image if not.

    Args:
        **attrs: Keyword arguments representing the attributes for the image tag.
    """

    # Ensure src is provided
    relative_image_path = attrs.get('src')
    if not relative_image_path:
        return '<!-- optimized_image tag missing "src" attribute -->'

    # Build Path object from src
    relative_path = Path(relative_image_path)

    # Prepare paths
    relative_image_path_without_extension = str(relative_path.with_suffix(''))  # Remove file extension
    image_static_src = static(relative_image_path)  # Get full static URL for original image

    # Replace src attribute with Django static URL
    attrs['src'] = image_static_src

    # Check if optimized WebP image exists
    optimized_image_webp_absolute_path = find(f'{relative_image_path_without_extension}.webp')

    if optimized_image_webp_absolute_path:
        optimized_image_static_src = static(f'{relative_image_path_without_extension}.webp').replace('%5C', '/') # Replace to fix Windows backslashes (%5C) in static URLs for proper web formatting.
        optimized_image_webp = f'<source srcset="{optimized_image_static_src}" type="image/webp">'
    else:
        optimized_image_webp = ''

    # Create alt and/or title attribute using image name
    if attrs.get('alt') == 'auto' or attrs.get('title') == 'auto':
        image_name = relative_path.stem.replace('-', ' ').title()  # Get filename without extension
        for key in ['alt', 'title']:
            if attrs.get(key) == 'auto':
                attrs[key] = image_name

    # Build HTML attributes for the <img> tag
    attributes_output = ' '.join(f'{key}="{value}"' for key, value in attrs.items())

    # Build full <picture> tag
    picture_tag = f'''
    <picture>
        {optimized_image_webp}
        <img {attributes_output}>
    </picture>
    '''
    return mark_safe(picture_tag)