from urllib.request import urlopen, HTTPError, URLError
from urllib.parse import urlparse, urljoin, urlsplit
from bs4 import BeautifulSoup
from io import BytesIO
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from PIL import Image, ImageOps
from django.core.files.base import ContentFile
import mimetypes
from django.conf import settings


def url_validate(url):
    """
    Validate given URL by regexp, then try to check if it exists
    """
    validate = URLValidator()
    if not url.startswith('http'):
        url = 'http://' + url
    try:
        validate(url)
        urlopen(url)
    except (ValidationError, HTTPError, URLError):
        return False
    else:
        return url

def mimetype_validate(url):
    """
    validate if url link to image
    """
    mimetype, encoding = mimetypes.guess_type(url)
    if mimetype:
        return mimetype.startswith('image')
    else:
        return False

def image_parser(url):
    """
    Image generator. Parse html finds all img tag and
    return absolute image URL like http://example.com/image.jpg
    """
    domain = urljoin(url, '/')
    soup = BeautifulSoup(urlopen(url), "html.parser")
    images = soup.findAll('img', src=True)
    for image in images:
        image_url = urljoin(domain, image["src"])
        if mimetype_validate(image_url):
            yield image_url
        else:
            continue

def read_image(image_url):
    """
    read image from url
    """
    try:
        image = Image.open(BytesIO(urlopen(image_url).read()))
        return image
    except (IOError, OSError):
        print('bad image')
        return False

def get_image(image):
    """
    create image file from image
    """
    image = image
    image_ext = image.format
    temp_image = BytesIO()
    image.save(temp_image, image_ext, optimize=True, quality=95)
    temp_image.seek(0)
    return ContentFile(temp_image.getvalue())

def get_thumb(image):
    """
    create thumbnail from image
    """
    THUMBNAIL_SIZE = getattr(
                settings,
                "GALLERY_THUMBNAIL_SIZE",
                (260, 146)
            )
    width, height = image.size
    image_ext = image.format
    if width > THUMBNAIL_SIZE[0] or height > THUMBNAIL_SIZE[1]:
        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
    temp_thumb = BytesIO()
    image.save(temp_thumb, image_ext, optimize=True, quality=95)
    temp_thumb.seek(0)
    return ContentFile(temp_thumb.getvalue())

def get_name(url):
    """
    return url without http:// and query. Used to name Site instance
    """
    return urlsplit(url).netloc + urlsplit(url).path

def get_filename(image_url):
    """
    return name of image file with extension
    """
    return image_url.split('/')[-1] 