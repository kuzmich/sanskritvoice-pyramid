from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker


def get_engine(settings, prefix='sqlalchemy.'):
    return engine_from_config(settings, prefix)


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    return factory


def includeme(config):
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('sv.models')``.

    """
    settings = config.get_settings()

    session_factory = get_session_factory(get_engine(settings))
    config.registry['dbsession_factory'] = session_factory

    # make request.dbsession available for use in Pyramid
    config.add_request_method(
        lambda r: session_factory(),
        'dbsession',
        reify=True
    )
