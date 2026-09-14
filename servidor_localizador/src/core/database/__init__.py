from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_app(app):
    """
    Initializes the database with the app.
    """
    db.init_app(app)
    config(app)
    return app


def config(app):
    """
    Configures the database with the app.
    """

    @app.teardown_appcontext
    def close_session(exception=None):
        db.session.close()

    return app


# Commands


def reset_db():
    """
    Resets the database.
    """
    print("Resetting the database⚰️")
    db.drop_all()
    print("Creating the database🏗")
    db.create_all()
    print("Database reseted🎉")


def commit_db(object):
    """
    Commits the object to the database.
    """
    db.session.add(object)
    db.session.commit()
    return object


def delete_from_db(object):
    """
    Deletes the object from the database.
    """
    db.session.delete(object)
    db.session.commit()
    return object