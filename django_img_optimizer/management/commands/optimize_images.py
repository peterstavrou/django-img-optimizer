# https://docs.djangoproject.com/en/5.0/howto/custom-management-commands/

from django.core.management.base import BaseCommand, CommandError
from PIL import Image
from glob import iglob
import os
from django_img_optimizer.utils import delete_optimized_images, optimize_images

class Command(BaseCommand):
    help = 'Optimizes images by converting them to WebP and AVIF'

    def add_arguments(self, parser):
        parser.add_argument(
                "--delete",
                action="store_true",
                help="Delete all optimized images from static folder",
            )

    def handle(self, *args, **options):
        if options["delete"]:
            delete_optimized_images()
        else:
            optimize_images()