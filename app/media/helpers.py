from app.media.models import MediaItem, MediaCategory
from flask import redirect, url_for, flash, current_app
from flask_login import current_user
from functools import wraps
from werkzeug import secure_filename
from os import path, stat
from PIL import Image

# generate choices for the media category SelectField
def gen_media_category_choices():
    choices = []

    categories = MediaCategory.query.all()

    for cat in categories:
        choices.append((cat.id, cat.name))

    return choices

# get best available file name for an uploaded media item
def media_filename(initial_filename):
    orig_filename = secure_filename(initial_filename)
    filename = orig_filename

    counter = 1
    while path.isfile(path.join(current_app.config["MEDIA_DIR"], filename)):
        # fancy duplication avoidance (tm)
        filename = "{}-{}".format(counter, orig_filename)
        counter += 1

    return filename

def generate_thumbnail(filename):
    filepath_orig = path.join(current_app.config["MEDIA_DIR"], filename)
    filepath_thumb = path.join(current_app.config["MEDIA_DIR"], "thumbnails", filename)

    image = Image.open(filepath_orig)
    image.thumbnail((200, 200))

    success = True

    try:
        image.save(filepath_thumb)
    except Exception as err:
        flash("Could not generate the thumbnail: {}".format(err), "error")
        success = False

    return success

# get all media visible to the user, can be filtered by category
def get_media(filter_category=None):
    media = MediaItem.get_query_for_visible_items()

    if filter_category:
        media = media.filter_by(category_id = filter_category)

    media = media.order_by(MediaItem.id.asc()).all()

    return media
