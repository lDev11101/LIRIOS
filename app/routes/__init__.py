from flask import Flask


def register_blueprints(app: Flask):
    from . import auth
    from . import main
    from . import admin
    from . import user

    app.register_blueprint(auth.bp_auth)
    app.register_blueprint(main.bp_main)
    app.register_blueprint(admin.bp_admin)
    app.register_blueprint(user.bp_user)