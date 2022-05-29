from __main__ import app

from flask import session, url_for, redirect, render_template, request, abort, Response, jsonify

from gcp_tts_calls import list_languages, list_voices, list_genders, text_to_wav
from main_tts_calls import *

# from flask_oidc import OpenIDConnect
# from okta import UsersClient

app.config.from_object('config')


# app.config["OIDC_CLIENT_SECRETS"] = "client_secrets.json"
# app.config["OIDC_COOKIE_SECURE"] = False
# app.config["OIDC_CALLBACK_ROUTE"] = "/oidc/callback"
# app.config["OIDC_SCOPES"] = ["openid", "email", "profile"]
# app.config["SECRET_KEY"] = "RGVlcCBDYWRlbmNlIC0gTmFtZSBQcm9udW5jaWF0aW9uIFRvb2w="
# oidc = OpenIDConnect(app)
# okta_client = UsersClient("dev-00396574.okta.com", "00rMlCM2_bu8ypbWn0hu0OYFrLCenIXI4ej0_wOI1J")
#
#
# @app.before_request
# def before_request():
#     if oidc.user_loggedin:
#         g.user = okta_client.get_user(oidc.user_getfield("sub"))
#     else:
#         g.user = None


@app.route("/")
# @oidc.require_login
def func_root():
    return render_template("home.html")


@app.route("/login", methods=["POST"])
# @oidc.require_login
def func_login():
    id_submitted = request.form.get("id")
    is_success, returned_name = authenticate(id_submitted, request.form.get("pw"))
    if is_success:
        session['current_user'] = returned_name
        session['current_user_email'] = id_submitted
    return redirect(url_for("func_root"))


@app.route("/profile")
def func_user():
    # Get the current user's profile only
    if session.get("current_user_email", None) is not None:
        # language_options = {code: {gender: list_voices(language_code=code, ssml_gender=gender)
        #                            for gender in list_genders(language_code=code)}
        #                     for code in list_languages()}
        user_profile = get_recording(session.get("current_user_email"))[0]
        lang_code_lists = list_languages()
        file = 'json/lang_code_name.json'
        with open(file, 'r') as f:
            name_dict = json.load(f)
        lang_lists = {code: name_dict.get(code, f'Unknown ({code})') for code in lang_code_lists}
        return render_template("profile.html",
                               profile=user_profile,
                               lang_codes=dict(sorted(lang_lists.items(), key=lambda item: item[1])))


@app.route("/logout/")
def func_logout():
    session.pop("current_user", None)
    session.pop("current_user_email", None)
    return redirect(url_for("func_root"))


@app.route('/cascade_dropdown')
def func_cascade_dropdown():
    selected_locale = request.args.get('selected_locale', type=str)
    selected_gender = request.args.get('selected_gender', type=str)
    if not selected_gender:
        optionshtml = '<option selected="selected" value="">--select a gender--</option>'
        genders = list_genders(selected_locale)
        for entry in genders:
            optionshtml += '<option value="{}">{}</option>'.format(entry, entry)
        return jsonify(options_html=optionshtml)
    else:
        optionshtml = '<option selected="selected" value="">--select a voice--</option>'
        voices = list_voices(selected_locale, selected_gender)
        for entry in voices:
            optionshtml += '<option value="{}">{}</option>'.format(entry, entry)
        return jsonify(options_html=optionshtml)


@app.route("/user_lookup", methods=["POST", "GET"])
def func_user_lookup():
    _id = request.form.get('id') or request.args.get('id')
    if _id:
        user_list = get_recording(_id)
        if user_list:
            user_tbl = zip(range(1, len(user_list) + 1),
                           user_list,
                           [x.format(y['name'], y['email_id']) for x, y in
                            zip(["/api/pronounce?name={}&email={}"] * len(user_list), user_list)],
                           [x.format(y['email_id'], _id) if y['is_saved'] else None
                            for x, y in zip(["/delete_saved_recording/{}/{}"] * len(user_list), user_list)])
            return render_template("home.html", users=user_tbl, is_emp=True)
        else:
            return render_template("home.html", users=request.form.get('id'))


@app.route("/save_pref/", methods=['POST'])
def func_save_preference():
    name = session.get("current_user")
    email = session.get("current_user_email")
    voice = request.form.get("search_voice")
    speed = request.form.get("ss")
    pitch = request.form.get("ps")
    pref_name = request.form.get('preferredName')
    save_preferences(name, email, voice, float(speed), float(pitch), preferred_name=pref_name)
    return redirect(url_for("func_user"))


@app.route("/save_rec/", methods=["POST"])
@app.route("/save_rec/<alias>", methods=["POST"])
def func_save_recording(alias=None):
    if request.data:
        audio_sample = text_to_wav(request.data.decode("utf-8")) if request.content_type.startswith(
            "text") else request.data
        save_recordings(session.get("current_user"), session.get("current_user_email"), audio_sample, alias)
    else:
        return Response(status=400)
    return jsonify({"redirect": "/profile"})


@app.route("/delete_saved_recording", methods=["POST", "GET"])
@app.route("/delete_saved_recording/<email>/<name>", methods=["POST", "GET"])
def func_delete_saved_recording(email=None, name=None):
    email_id = session.get("current_user_email")
    route = "func_user_lookup"
    if not email:
        email = email_id
        route = "func_user"
    delete_recording(email)
    return redirect(url_for(route, id=name))


@app.route("/admin/")
def func_admin():
    if session.get("current_user", None).lower() == "admin":
        user_list = get_all_user()
        user_table = zip(range(1, len(user_list) + 1),
                         user_list,
                         [x + y.get('email_id', "")
                          for x, y in zip(["/delete_user/"] * len(user_list), user_list)])
        return render_template("console.html",
                               users=user_table,
                               is_success=request.args.get('is_success'),
                               id_to_add_is_duplicated=request.args.get('id_to_add_is_duplicated'),
                               id_to_add_is_invalid=request.args.get('id_to_add_is_invalid'))
    else:
        return abort(401)


@app.route("/delete_user/<email>/", methods=['GET'])
def func_delete_user(email):
    if session.get("current_user").lower() == "admin":
        if email == session.get("current_user_email"):  # ADMIN account can't be deleted.
            return abort(403)
        delete_user(email)
        return redirect(url_for("func_admin"))
    else:
        return abort(401)


@app.route("/add_user", methods=["POST"])
def func_add_user():
    if session.get("current_user", None).lower() == "admin":  # only Admin should be able to add user.
        # before we add the user, we need to ensure this is doesn't exist in database.
        if request.form.get('email').lower() in [user['email_id'].lower() for user in get_all_user()]:
            user_list = get_all_user()
            user_table = zip(range(1, len(user_list) + 1),
                             user_list,
                             [x + y.get('email_id') for x, y in zip(["/delete_user/"] * len(user_list), user_list)])
            return render_template("console.html", id_to_add_is_duplicated=True, users=user_table)
        else:
            personadd(request.form.get('id'), request.form.get('email'), request.form.get('pw'))
            return redirect(url_for("func_admin", is_success=True))
    else:
        return abort(401)


@app.errorhandler(401)
def func_401(error):
    return render_template("page_401.html"), 401


@app.errorhandler(403)
def func_403(error):
    return render_template("page_403.html"), 403


@app.errorhandler(404)
def func_404(error):
    return render_template("page_404.html"), 404


@app.errorhandler(405)
def func_405(error):
    return render_template("page_405.html"), 405
