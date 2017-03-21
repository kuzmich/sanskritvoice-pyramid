from mixer.main import Mixer
from py._path.local import LocalPath
from pyramid import testing
from pyramid.request import Request
from pyramid.threadlocal import get_current_registry
import pytest
from webob.multidict import MultiDict

from sv.models import Bhajan, Record


def test_add_bhajan(config, session, tmpdir: LocalPath):
    from sv.admin.forms import DeformUploadTmpStore
    from sv.admin.views import add_bhajan

    config.add_route('admin-bhajans', '/bhajans')

    request = Request.blank(
        '/dj/add_bhajan',
        POST=MultiDict([
            ('_charset_', 'UTF-8'),
            ('__formid__', 'deform'),

            ('title', 'Ом Нама Шивая'),
            ('category', 'shiva'),
            ('text', 'Ом Нама Шивая'),
            ('accords', ''),

            ('__start__', 'records:sequence'),

            ('__start__', 'record:mapping'),
            ('artist', 'Виктор'),
            ('__start__', 'audio:mapping'),
            ('upload', ('some_audio.mp3', b'record 1 audio')),
            ('__end__', 'audio:mapping'),
            ('__end__', 'record:mapping'),

            ('__start__', 'record:mapping'),
            ('artist', 'Вася'),
            ('__start__', 'audio:mapping'),
            ('upload', ('some_audio.mp3', b'record 2 audio')),
            ('__end__', 'audio:mapping'),
            ('__end__', 'record:mapping'),

            ('__end__', 'records:sequence'),

            # ('сохранить', 'сохранить')
        ])
    )
    request.dbsession = session
    request.session = testing.DummySession()

    registry = get_current_registry()
    request.registry = registry

    # print(registry.settings)
    # print(request)

    resp = add_bhajan(request)
    # print(resp)

    assert session.query(Bhajan).count() == 1
    assert session.query(Record).count() == 2

    bhajan = session.query(Bhajan).one()
    records = session.query(Record).all()

    bhajan_upload_dir = tmpdir.join(str(bhajan.id))
    record_files = [
        bhajan_upload_dir.join('%s.mp3' % records[0].id),
        bhajan_upload_dir.join('%s.mp3' % records[1].id)
    ]

    assert (
        [str(lp.basename) for lp in tmpdir.listdir(sort=True)] ==
        [str(bhajan.id), 'tmp']
    )

    assert bhajan_upload_dir.listdir(sort=True) == record_files
    assert record_files[0].read_binary() == b'record 1 audio'
    assert record_files[1].read_binary() == b'record 2 audio'

    assert tmpdir.join('tmp').listdir() == []

    tmpstore = DeformUploadTmpStore(request)
    assert list(tmpstore.keys()) == []


def test_edit_bhajan(config, session, tmpdir: LocalPath, mixer: Mixer):
    from sv.admin.forms import DeformUploadTmpStore
    from sv.admin.views import edit_bhajan

    config.add_route('admin-bhajans', '/bhajans')

    bhajan = mixer.blend(
        Bhajan,
        title='Ом Нама Шивая',
        category='shiva',
        text='Ом Нама Шивая'
    )
    print(bhajan)

    rec1 = mixer.blend(Record, artist='Виктор', bhajan=bhajan)
    rec2 = mixer.blend(Record, artist='Вася', bhajan=bhajan)
    records = [rec1, rec2]
    print(records)

    for rec in records:
        rec.path = '{bid}/{rid}'.format(bid=bhajan.id, rid=rec.id)
    session.commit()

    bhajan_upload_dir = tmpdir.join(str(bhajan.id))
    bhajan_upload_dir.mkdir()

    record_files = [bhajan_upload_dir.join('%s.mp3' % rec.id) for rec in records]
    for rf, rec in zip(record_files, records):
        rf.write_binary('record {} audio'.format(rec.id).encode())

    request = Request.blank(
        '/dj/bhajans/%s' % bhajan.id,
        POST=MultiDict([
            ('_charset_', 'UTF-8'),
            ('__formid__', 'deform'),

            ('title', 'Ом Нама Шивая'),
            ('category', 'shiva'),
            ('text', 'Ом Нама Шивая'),
            ('accords', ''),

            ('__start__', 'records:sequence'),

            ('__start__', 'record:mapping'),
            ('artist', 'Виктор'),
            ('__start__', 'audio:mapping'),
            ('upload', b''),
            ('uid', str(rec1.id)),
            ('__end__', 'audio:mapping'),
            ('__end__', 'record:mapping'),

            ('__start__', 'record:mapping'),
            ('artist', 'Вася'),
            ('__start__', 'audio:mapping'),
            ('upload', b''),
            ('uid', str(rec2.id)),
            ('__end__', 'audio:mapping'),
            ('__end__', 'record:mapping'),

            ('__end__', 'records:sequence'),

            # ('сохранить', 'сохранить')
        ])
    )
    request.dbsession = session
    request.session = testing.DummySession()

    request.matchdict = {}
    request.matchdict['bid'] = str(bhajan.id)

    registry = get_current_registry()
    request.registry = registry

    resp = edit_bhajan(request)
    # print(resp)

    # у нас по-прежнему 1 баджана и 2 записи
    assert session.query(Bhajan).count() == 1
    assert session.query(Record).count() == 2

    # файлов записей так же 2
    assert bhajan_upload_dir.listdir(sort=True) == record_files

    # и их содержимое не изменилось
    for rf, rec in zip(record_files, records):
        assert rf.read_binary() == 'record {} audio'.format(rec.id).encode()

    # tmpstore пустое
    tmpstore = DeformUploadTmpStore(request)
    assert list(tmpstore.keys()) == []


def test_add_bhajan_func(session, client):
    from webtest.forms import Upload
    from webob.multidict import MultiDict

    resp = client.post(
        '/dj/add_bhajan',
        MultiDict([
            ('_charset_', 'UTF-8'),
            ('__formid__', 'deform'),
            ('title', 'ЛаЛаЛенд'),
            ('category', 'other'),
            ('text', 'ЛаЛаЛенд'),
            ('accords', ''),

            ('__start__', 'records:sequence'),

            # ('__start__', 'record:mapping'),
            # ('artist', 'АК'),
            # ('__start__', 'audio:mapping'),
            # ('upload', b''),
            # ('uid', '16'),
            # ('__end__', 'audio:mapping'),
            # ('__end__', 'record:mapping'),

            # ('__start__', 'record:mapping'),
            # ('artist', 'Витя'),
            # ('__start__', 'audio:mapping'),
            # ('upload', b''),
            # ('uid', '17'),
            # ('__end__', 'audio:mapping'),
            # ('__end__', 'record:mapping'),

            ('__start__', 'record:mapping'),
            ('artist', 'Виктор'),
            ('__start__', 'audio:mapping'),
            ('upload', Upload('some_audio.mp3', b'some_audio.mp3')),
            ('__end__', 'audio:mapping'),
            ('__end__', 'record:mapping'),

            ('__end__', 'records:sequence'),

            # ('сохранить', 'сохранить')
        ]),
        content_type='multipart/form-data'
    )
    print(resp)
    print(resp.request)
    assert resp.status_code == 302

    assert session.query(Bhajan).count() == 1
    assert session.query(Record).count() == 1

    # settings = resp.request.registry.settings
    # print(settings)
    # assert 0


