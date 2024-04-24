from django import template
from django.templatetags.static import static
from django.utils.safestring  import mark_safe
from django.contrib.staticfiles.finders import find
import re

register = template.Library()

@register.simple_tag()
def optimized_image(*args):
    """
    Returns:
        str: A html picture tag with an optimized webp image if it exists, or just the original image if no optimized image is found.

    Args:
        *args: Variable number of arguments representing the attributes for the image tag.
    """
    attributes = ' '.join(args)

    # Get src attribute value
    match_src = re.search(r'src="([^"]+)"', attributes)
    # print(match_src)
    # print('************')
    relative_image_path = match_src.group(1) if match_src.group(1) is not None else "src could not be found"

    # Get django static path
    image_static_src = static(relative_image_path)

    # Replace src in attributes with django static src
    attributes_output = re.sub(r'(src=")([^"]+)(")(?=\s|>)', fr'\g<1>{image_static_src}\g<3>', attributes)

    # Check if optimized image exists
    relative_image_path_without_extension = relative_image_path.rsplit('.', 1)[0]
    optimized_image_webp_absolute_path = find(f'{relative_image_path_without_extension}.webp')

    if optimized_image_webp_absolute_path:
        optimized_image_static_src = static(f'{relative_image_path_without_extension}.webp')
        optimized_image_webp = f'<source srcset="{optimized_image_static_src}" type="image/webp">'
    else:
        optimized_image_webp = ''

    # Create alt and/or title attribute using image name
    if 'alt="auto"' in attributes_output or 'title="auto"' in attributes_output:
        image_name = relative_image_path_without_extension.split('/')[-1].replace('-', ' ').title()
        attributes_output = attributes_output.replace('="auto"', f'="{image_name}"')

    # Create html picture tag
    picture_tag = f'''
    <picture>
        {optimized_image_webp}
        <img {attributes_output}>
    </picture>
    '''
    return mark_safe(picture_tag)