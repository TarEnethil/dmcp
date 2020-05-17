from app import db
from app.helpers import page_title, flash_no_permission
from app.media import bp
from app.media.forms import SettingsForm, MediaItemCreateForm, MediaItemEditForm, CategoryForm
from app.media.helpers import media_admin_required, get_media, gen_media_category_choices, media_filename, generate_thumbnail
from app.media.models import MediaSetting, MediaItem, MediaCategory
from flask import render_template, flash, redirect, url_for, request, jsonify, send_from_directory, current_app
from flask_login import login_required, current_user
from sqlalchemy import not_, and_, or_
from os import path, remove, stat

no_perm_url = "media.index"

@bp.route("/index", methods=["GET"])
@bp.route("/list", methods=["GET"])
@bp.route("/", methods=["GET"])
@login_required
def index():
    media = get_media()

    return render_template("media/index.html", media=media, title=page_title("Media"))

@bp.route("/view/<int:id>/<string:name>", methods=["GET"])
@bp.route("/view/<int:id>", methods=["GET"])
@login_required
def view(id, name=None):
    item = MediaItem.query.filter_by(id=id).first_or_404()

    if not item.is_visible_for_user():
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    if not item.is_visible:
        flash("This item is only visible to you.", "warning")

    return render_template("media/view.html", item=item, title=page_title("View File"))

@bp.route("/list/category-<int:c_id>/<string:c_name>", methods=["GET"])
@login_required
def list_by_cat(c_id, c_name=None):
    m = MediaCategory.query.filter_by(id=c_id).first_or_404()
    files = get_media(c_id)

    return render_template("media/list.html", media=files, cat=m, title=page_title("View Files in Category '{}'".format(m.name)))

@bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    form = MediaItemCreateForm()
    form.category.choices = gen_media_category_choices()

    # check if ajax-GET param was set, which means we must return json
    ajax = request.args.get("ajax") != None

    if form.validate_on_submit():
        filename = media_filename(form.file.data.filename)

        filepath = path.join(current_app.config["MEDIA_DIR"], filename)
        form.file.data.save(filepath)

        size = stat(filepath).st_size

        new_media = MediaItem(name=form.name.data, filename=filename, filesize=size, is_visible=form.is_visible.data, category_id=form.category.data)

        msg = "Upload successful."
        level = "success"

        if new_media.is_image():
            if generate_thumbnail(filename) == False:
                msg = "Upload successful, but there were errors."
                level = "warning"

        db.session.add(new_media)
        db.session.commit()

        flash(msg, level)

        # uploaded succeeded, send back info about new media
        if ajax:
            return jsonify(data={'success' : True,
                                'html' : render_template("media/upload_success.html", item=new_media),
                                'media_info' : new_media.sidebar_info()
                                })
        else:
            return redirect(new_media.view_url())

    elif ajax and request.method == "POST":
        # the form validation failed, send back the form with displayed errors
        flash("There was an error processing the upload.", "danger")
        return jsonify(data={'success' : False, 'html': render_template("media/upload_raw.html", form=form, max_filesize=current_app.config["MAX_CONTENT_LENGTH"]) })
    elif request.method == "GET":
        # pre-select category if get-param was passed
        category_id = request.args.get("category")

        # will do nothing if var is not an int or not in choices
        if category_id:
            try:
                form.category.data = int(category_id)
            except:
                pass

    # non-ajax: return the full page
    template = "media/upload.html"

    # ajax: return only the form
    if ajax:
        template = "media/upload_raw.html"

    return render_template(template, form=form, max_filesize=current_app.config["MAX_CONTENT_LENGTH"], title=page_title("Upload File"))

@bp.route("/edit/<int:id>/<string:name>", methods=["GET", "POST"])
@login_required
def edit(id, name=None):
    item = MediaItem.query.filter_by(id=id).first_or_404()

    form = MediaItemEditForm()
    form.category.choices = gen_media_category_choices()

    if not item.is_editable_by_user():
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    if not item.is_owned_by_user():
        del form.is_visible

    form.file.label.text = "Replace with file"

    if form.validate_on_submit():
        item.name = form.name.data
        item.category_id = form.category.data

        if item.is_owned_by_user():
            item.is_visible = form.is_visible.data

        msg = "File was edited."
        level = "success"

        if form.file.data:
            filepath = path.join(current_app.config["MEDIA_DIR"], item.filename)

            # see github issue #47
            if item.get_file_ext() != form.file.data.filename.split(".", 1)[-1]:
                flash("Due to current technical limitations, the old and new file need to have the same file type. As a workaround, you can upload a new file instead.", "danger")
                return render_template("media/edit.html", form=form, title=page_title("Edit File '{}'".format(item.name)))

            # overrides former file
            form.file.data.save(filepath)

            item.filesize = stat(filepath).st_size

            if item.is_image():
                # overrides former thumbnail
                if generate_thumbnail(item.filename) == False:
                    msg = "File was edited, but there were errors."
                    level = "warning"

        db.session.commit()

        flash(msg, level)

        return redirect(item.view_url())
    elif request.method == "GET":
        form.name.data = item.name
        form.category.data = item.category_id

        if item.is_owned_by_user():
            form.is_visible.data = item.is_visible

    return render_template("media/edit.html", form=form, title=page_title("Edit File '{}'".format(item.name)))

@bp.route("/delete/<int:id>/<string:name>", methods=["GET"])
@login_required
def delete(id, name=None):
    item = MediaItem.query.filter_by(id=id).first_or_404()

    if not item.is_deletable_by_user():
        flash_no_permission()
        return redirect(url_for(no_perm_url))

    fname = path.join(current_app.config["MEDIA_DIR"], item.filename)
    if path.isfile(fname):
        remove(fname)

    tname = path.join(current_app.config["MEDIA_DIR"], "thumbnails", item.filename)
    if item.is_image() and path.isfile(tname):
        remove(tname)

    db.session.delete(item)
    db.session.commit()

    flash("Media item was deleted.", "success")
    return redirect(url_for('media.index'))

@bp.route("/category/create", methods=["GET", "POST"])
@login_required
@media_admin_required
def category_create():
    heading = "Add Media Category"
    form = CategoryForm()
    form.submit.label.text = "Create Category"

    if form.validate_on_submit():
        new_category = MediaCategory(name=form.name.data)

        db.session.add(new_category)
        db.session.commit()

        flash("Category created.", "success")
        return redirect(url_for("media.settings"))

    return render_template("media/category.html", form=form, heading=heading, title=page_title(heading))

@bp.route("/category/edit/<int:id>/<string:name>", methods=["GET", "POST"])
@login_required
@media_admin_required
def category_edit(id, name=None):
    form = CategoryForm()
    form.submit.label.text = "Save Category"

    category = MediaCategory.query.filter_by(id=id).first_or_404()
    heading = "Edit Media Category '%s'" % category.name

    if form.validate_on_submit():
        category.name = form.name.data

        db.session.commit()

        flash("Media category edited.", "success")
        return redirect(url_for("media.settings"))
    elif request.method == "GET":
        form.name.data = category.name

    return render_template("media/category.html", category=category, form=form, heading=heading, title=page_title(heading))

@bp.route("/settings", methods=["GET", "POST"])
@login_required
@media_admin_required
def settings():
    settings = MediaSetting.query.get(1)
    # form = SettingsForm()

    # if form.validate_on_submit():
    #     settings.default_visible = form.default_visible.data

    #     db.session.commit()

    #     flash("Event settings have been changed.", "success")
    # elif request.method == "GET":
    #     form.default_visible.data = settings.default_visible

    categories = MediaCategory.query.all()

    return render_template("media/settings.html", settings=settings, categories=categories, title=page_title("Media Settings"))

@bp.route("/sidebar/", methods=["POST"])
@login_required
def sidebar():
    tbsend = {}

    files = get_media()

    for mfile in files:
        k = mfile.category_id
        if not k in tbsend.keys():
            tbsend[k] = mfile.category.sidebar_info()
            tbsend[k]["data"] = []

        tbsend[k]["data"].append(mfile.sidebar_info())

    return jsonify({"categories" : list(tbsend.values()) })

@bp.route("/serve/<filename>")
def serve_file(filename):
    return send_from_directory(current_app.config["MEDIA_DIR"], filename)

@bp.route("/serve-thumb/<filename>")
def serve_thumbnail(filename):
    return send_from_directory(path.join(current_app.config["MEDIA_DIR"], "thumbnails"), filename)
