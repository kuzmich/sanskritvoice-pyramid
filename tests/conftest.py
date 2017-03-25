import logging
import sys

from mixer.backend.sqlalchemy import Mixer
from pyramid import testing
import pytest
from sqlalchemy import event
from sqlalchemy.engine import engine_from_config
from sqlalchemy.orm.session import Session
from webtest import TestApp


@pytest.fixture
def settings(tmpdir):
    return {
        'sqlalchemy.url': 'postgresql://alexey@/test_sanskritvoice',
        'pyramid.debug_notfound': True,
        'pyramid.debug_routematch': True,
        'sv.upload_dir': str(tmpdir),
        'sv.upload_tmp_dir': str(tmpdir.mkdir('tmp'))
    }

@pytest.fixture
def config(settings):
    configurator = testing.setUp(settings=settings)
    yield configurator
    testing.tearDown()


@pytest.fixture
def engine(settings):
    return engine_from_config(settings)


@pytest.fixture
def db(engine):
    from sv.models.meta import Base
    Base.metadata.create_all(engine)


@pytest.fixture
def session(engine, db):
    # connect to the database
    connection = engine.connect()

    # begin a non-ORM transaction
    trans = connection.begin()

    # bind an individual Session to the connection
    session = Session(bind=connection)

    # start the session in a SAVEPOINT...
    session.begin_nested()

    # then each time that SAVEPOINT ends, reopen it
    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(session, transaction):
        if transaction.nested and not transaction._parent.nested:

            # ensure that state is expired the way
            # session.commit() at the top level normally does
            # (optional step)
            session.expire_all()

            session.begin_nested()

    yield session

    session.close()

    # rollback - everything that happened with the
    # Session above (including calls to commit())
    # is rolled back.
    trans.rollback()

    # return connection to the Engine
    connection.close()


@pytest.fixture
def client(config, session):
    config.include('pyramid_jinja2')
    config.include('sv.models.session')
    config.include('sv.routes')
    config.include('sv.routes.admin', route_prefix='/dj')
    config.scan('sv')

    config.add_request_method(
        lambda r: session,
        'dbsession',
        reify=True
    )

    config.add_request_method(
        lambda r: testing.DummySession(),
        'session',
        reify=True
    )

    return TestApp(config.make_wsgi_app())


@pytest.fixture
def mixer(session):
    return Mixer(session=session, commit=True, locale='ru_RU')


@pytest.fixture
def events(config):
    return config.testing_add_subscriber()


@pytest.fixture
def log():
    handler = logging.StreamHandler(stream=sys.stdout)

    l = logging.getLogger('sv')
    l.setLevel(logging.DEBUG)
    l.addHandler(handler)

    return l

