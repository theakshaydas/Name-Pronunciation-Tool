from __main__ import app

from flask import session, url_for, redirect, render_template, request, abort, Response

from main_tts_calls import *

app.config.from_object('config')
language_options = {'af-ZA': {'FEMALE': []}, 'ar-XA': {'MALE': ['ar-XA-Wavenet-B', 'ar-XA-Wavenet-C'],
                                                       'FEMALE': ['ar-XA-Wavenet-A', 'ar-XA-Wavenet-D']},
                    'bg-BG': {'FEMALE': []}, 'bn-IN': {'MALE': ['bn-IN-Wavenet-B'], 'FEMALE': ['bn-IN-Wavenet-A']},
                    'ca-ES': {'FEMALE': []}, 'cmn-CN': {'MALE': ['cmn-CN-Wavenet-B', 'cmn-CN-Wavenet-C'],
                                                        'FEMALE': ['cmn-CN-Wavenet-A', 'cmn-CN-Wavenet-D']},
                    'cmn-TW': {'MALE': ['cmn-TW-Wavenet-B', 'cmn-TW-Wavenet-C'], 'FEMALE': ['cmn-TW-Wavenet-A']},
                    'cs-CZ': {'FEMALE': ['cs-CZ-Wavenet-A']}, 'da-DK': {'MALE': ['da-DK-Wavenet-C'],
                                                                        'FEMALE': ['da-DK-Wavenet-A', 'da-DK-Wavenet-D',
                                                                                   'da-DK-Wavenet-E']},
                    'de-DE': {'MALE': ['de-DE-Wavenet-B', 'de-DE-Wavenet-D', 'de-DE-Wavenet-E'],
                              'FEMALE': ['de-DE-Wavenet-A', 'de-DE-Wavenet-C', 'de-DE-Wavenet-F']},
                    'el-GR': {'FEMALE': ['el-GR-Wavenet-A']}, 'en-AU': {'MALE': ['en-AU-Wavenet-B', 'en-AU-Wavenet-D'],
                                                                        'FEMALE': ['en-AU-Wavenet-A',
                                                                                   'en-AU-Wavenet-C']},
                    'en-GB': {'MALE': ['en-GB-Wavenet-B', 'en-GB-Wavenet-D'],
                              'FEMALE': ['en-GB-Wavenet-A', 'en-GB-Wavenet-C', 'en-GB-Wavenet-F']},
                    'en-IN': {'MALE': ['en-IN-Wavenet-B', 'en-IN-Wavenet-C'],
                              'FEMALE': ['en-IN-Wavenet-A', 'en-IN-Wavenet-D']}, 'en-US': {
        'MALE': ['en-US-Wavenet-A', 'en-US-Wavenet-B', 'en-US-Wavenet-D', 'en-US-Wavenet-I', 'en-US-Wavenet-J'],
        'FEMALE': ['en-US-Wavenet-C', 'en-US-Wavenet-E', 'en-US-Wavenet-F', 'en-US-Wavenet-G', 'en-US-Wavenet-H']},
                    'es-ES': {'MALE': ['es-ES-Wavenet-B'], 'FEMALE': ['es-ES-Wavenet-C', 'es-ES-Wavenet-D']},
                    'es-US': {'MALE': ['es-US-Wavenet-B', 'es-US-Wavenet-C'], 'FEMALE': ['es-US-Wavenet-A']},
                    'fi-FI': {'FEMALE': ['fi-FI-Wavenet-A']},
                    'fil-PH': {'MALE': ['fil-PH-Wavenet-C', 'fil-PH-Wavenet-D'],
                               'FEMALE': ['fil-PH-Wavenet-A', 'fil-PH-Wavenet-B']},
                    'fr-CA': {'MALE': ['fr-CA-Wavenet-B', 'fr-CA-Wavenet-D'],
                              'FEMALE': ['fr-CA-Wavenet-A', 'fr-CA-Wavenet-C']},
                    'fr-FR': {'MALE': ['fr-FR-Wavenet-B', 'fr-FR-Wavenet-D'],
                              'FEMALE': ['fr-FR-Wavenet-A', 'fr-FR-Wavenet-C', 'fr-FR-Wavenet-E']},
                    'gu-IN': {'MALE': ['gu-IN-Wavenet-B'], 'FEMALE': ['gu-IN-Wavenet-A']},
                    'hi-IN': {'MALE': ['hi-IN-Wavenet-B', 'hi-IN-Wavenet-C'],
                              'FEMALE': ['hi-IN-Wavenet-A', 'hi-IN-Wavenet-D']},
                    'hu-HU': {'FEMALE': ['hu-HU-Wavenet-A']}, 'id-ID': {'MALE': ['id-ID-Wavenet-B', 'id-ID-Wavenet-C'],
                                                                        'FEMALE': ['id-ID-Wavenet-A',
                                                                                   'id-ID-Wavenet-D']},
                    'is-IS': {'FEMALE': []}, 'it-IT': {'MALE': ['it-IT-Wavenet-C', 'it-IT-Wavenet-D'],
                                                       'FEMALE': ['it-IT-Wavenet-A', 'it-IT-Wavenet-B']},
                    'ja-JP': {'MALE': ['ja-JP-Wavenet-C', 'ja-JP-Wavenet-D'],
                              'FEMALE': ['ja-JP-Wavenet-A', 'ja-JP-Wavenet-B']},
                    'kn-IN': {'MALE': ['kn-IN-Wavenet-B'], 'FEMALE': ['kn-IN-Wavenet-A']},
                    'ko-KR': {'MALE': ['ko-KR-Wavenet-C', 'ko-KR-Wavenet-D'],
                              'FEMALE': ['ko-KR-Wavenet-A', 'ko-KR-Wavenet-B']}, 'lv-LV': {'MALE': []},
                    'ml-IN': {'MALE': ['ml-IN-Wavenet-B'], 'FEMALE': ['ml-IN-Wavenet-A']},
                    'ms-MY': {'MALE': ['ms-MY-Wavenet-B', 'ms-MY-Wavenet-D'],
                              'FEMALE': ['ms-MY-Wavenet-A', 'ms-MY-Wavenet-C']},
                    'nb-NO': {'MALE': ['nb-NO-Wavenet-B', 'nb-NO-Wavenet-D'],
                              'FEMALE': ['nb-NO-Wavenet-A', 'nb-NO-Wavenet-C', 'nb-no-Wavenet-E']},
                    'nl-BE': {'MALE': ['nl-BE-Wavenet-B'], 'FEMALE': ['nl-BE-Wavenet-A']},
                    'nl-NL': {'MALE': ['nl-NL-Wavenet-B', 'nl-NL-Wavenet-C'],
                              'FEMALE': ['nl-NL-Wavenet-A', 'nl-NL-Wavenet-D', 'nl-NL-Wavenet-E']},
                    'pa-IN': {'MALE': ['pa-IN-Wavenet-B', 'pa-IN-Wavenet-D'],
                              'FEMALE': ['pa-IN-Wavenet-A', 'pa-IN-Wavenet-C']},
                    'pl-PL': {'MALE': ['pl-PL-Wavenet-B', 'pl-PL-Wavenet-C'],
                              'FEMALE': ['pl-PL-Wavenet-A', 'pl-PL-Wavenet-D', 'pl-PL-Wavenet-E']},
                    'pt-BR': {'MALE': ['pt-BR-Wavenet-B'], 'FEMALE': ['pt-BR-Wavenet-A']},
                    'pt-PT': {'MALE': ['pt-PT-Wavenet-B', 'pt-PT-Wavenet-C'],
                              'FEMALE': ['pt-PT-Wavenet-A', 'pt-PT-Wavenet-D']},
                    'ro-RO': {'FEMALE': ['ro-RO-Wavenet-A']}, 'ru-RU': {'MALE': ['ru-RU-Wavenet-B', 'ru-RU-Wavenet-D'],
                                                                        'FEMALE': ['ru-RU-Wavenet-A', 'ru-RU-Wavenet-C',
                                                                                   'ru-RU-Wavenet-E']},
                    'sk-SK': {'FEMALE': ['sk-SK-Wavenet-A']}, 'sr-RS': {'FEMALE': []},
                    'sv-SE': {'MALE': ['sv-SE-Wavenet-C', 'sv-SE-Wavenet-E'],
                              'FEMALE': ['sv-SE-Wavenet-A', 'sv-SE-Wavenet-B', 'sv-SE-Wavenet-D']},
                    'ta-IN': {'MALE': ['ta-IN-Wavenet-B'], 'FEMALE': ['ta-IN-Wavenet-A']},
                    'te-IN': {'MALE': [], 'FEMALE': []}, 'th-TH': {'FEMALE': []},
                    'tr-TR': {'MALE': ['tr-TR-Wavenet-B', 'tr-TR-Wavenet-E'],
                              'FEMALE': ['tr-TR-Wavenet-A', 'tr-TR-Wavenet-C', 'tr-TR-Wavenet-D']},
                    'uk-UA': {'FEMALE': ['uk-UA-Wavenet-A']}, 'vi-VN': {'MALE': ['vi-VN-Wavenet-B', 'vi-VN-Wavenet-D'],
                                                                        'FEMALE': ['vi-VN-Wavenet-A',
                                                                                   'vi-VN-Wavenet-C']},
                    'yue-HK': {'MALE': [], 'FEMALE': []}}


@app.route("/")
def func_root():
    return render_template("home.html")


@app.route("/login", methods=["POST"])
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
        return render_template("profile.html", profile=user_profile, lang_options=language_options)


@app.route("/logout/")
def func_logout():
    session.pop("current_user", None)
    session.pop("current_user_email", None)
    return redirect(url_for("func_root"))


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
                           [x.format(y['email_id'], y['name']) if y['is_saved'] else None
                            for x, y in zip(["/delete_saved_recording/{}/{}"] * len(user_list), user_list)])
            return render_template("home.html", users=user_tbl, is_emp=True)
        else:
            return render_template("home.html", users=request.form.get('id'))


@app.route("/save_pref/", methods=['POST'])
def func_save_preference():
    voice = request.form.get("search_voice")
    speed = request.form.get("ss")
    pitch = request.form.get("ps")
    email = session.get("current_user_email")
    alias = request.form.get('editPreferredName')
    name = session.get("current_user")
    print(name, email, voice, float(speed), float(pitch), alias)
    save_preferences(name, email, voice, float(speed), float(pitch), preferred_name=alias)
    return redirect(url_for("func_user"))


@app.route("/save_rec/", methods=['POST'])
@app.route("/save_rec/<alias>", methods=['POST'])
def func_save_recording(alias=None):
    if request.data:
        save_recordings(session.get("current_user"), session.get("current_user_email"), request.data, alias)
        return Response(status=200)
    else:
        return Response(status=400)


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
