from pprint import pprint
from py._path.local import LocalPath
from pyramid import testing
from pyramid.request import Request
from pyramid.threadlocal import get_current_registry
import pytest
from webob.multidict import MultiDict

from sv.models import Bhajan, Record


@pytest.fixture
def bhajan_factory(mixer):
    def factory(**kwargs):
        bhajan = mixer.blend(
            Bhajan,
            # title='Ом Нама Шивая',
            category=mixer.RANDOM('shiva', 'ganesh', 'guru', 'devi', 'other'),
            # text='Ом Нама Шивая'
        )
        print(bhajan)
        return bhajan
    return factory

@pytest.fixture
def records_factory(session, mixer, tmpdir):
    from mixer._faker import faker

    def factory(num, bhajan, **kwargs):
        records = []
        for i in range(num):
            records.append(mixer.blend(Record,
                                       artist=faker.name(),
                                       bhajan=bhajan))

        for rec in records:
            rec.path = '{bid}/{rid}'.format(bid=bhajan.id, rid=rec.id)
        session.commit()

        print(records)

        bhajan_upload_dir = tmpdir.join(str(bhajan.id))
        bhajan_upload_dir.mkdir()

        record_files = [bhajan_upload_dir.join('%s.mp3' % rec.id) for rec in records]
        for rf, rec in zip(record_files, records):
            rf.write_binary('record {} audio'.format(rec.id).encode())

        return records, record_files

    return factory


@pytest.fixture
def request_factory(session):
    def factory(url, bhajan, records):
        post_data = [
            ('_charset_', 'UTF-8'),
            ('__formid__', 'deform'),

            # ('title', bhajan.title),
            # ('category', bhajan.category),
            # ('text', bhajan.text),
            # ('accords', bhajan.accords),

            # ('__start__', 'records:sequence'),
            # ('__start__', 'record:mapping'),
            # ('artist', 'Вася'),
            # ('__start__', 'audio:mapping'),
            # ('upload', b''),
            # ('uid', str(rec2.id)),
            # ('__end__', 'audio:mapping'),
            # ('__end__', 'record:mapping'),
            # ('__end__', 'records:sequence'),
            # ('сохранить', 'сохранить')
        ]

        if isinstance(bhajan, dict):
            post_data.extend([
                ('title', bhajan['title']),
                ('category', bhajan['category']),
                ('text', bhajan['text']),
                ('accords', bhajan.get('accords', '')),
            ])
        else:
            post_data.extend([
                ('title', bhajan.title),
                ('category', bhajan.category),
                ('text', bhajan.text),
                ('accords', bhajan.accords),
            ])

        if records:
            post_data.append(
                ('__start__', 'records:sequence')
            )
            for r in records:
                post_data.extend([
                    ('__start__', 'record:mapping'),
                    ('artist', r['artist']),
                    ('__start__', 'audio:mapping'),
                    ('upload', r['upload']),
                    # ('uid', r['uid']),
                    ('__end__', 'audio:mapping'),
                    ('__end__', 'record:mapping'),
                ])
                if 'uid' in r:
                    post_data.insert(-3, ('uid', r['uid']))
            post_data.append(
                ('__end__', 'records:sequence')
            )

        pprint(post_data)

        request = Request.blank(
            url,
            POST=MultiDict(post_data),
        )

        request.dbsession = session
        request.session = testing.DummySession()

        request.matchdict = {}
        if not isinstance(bhajan, dict):
            request.matchdict['bid'] = str(bhajan.id)

        registry = get_current_registry()
        request.registry = registry

        return request
    return factory


def test_add_bhajan(config, session, tmpdir: LocalPath, request_factory):
    from sv.admin.forms import DeformUploadTmpStore
    from sv.admin.views import add_bhajan

    config.add_route('admin-bhajans', '/bhajans')

    request = request_factory(
        '/dj/add_bhajan',
        {
            'title': 'Ом Нама Шивая',
            'category': 'shiva',
            'text': 'Ом Нама Шивая',
            'accords': ''
        },
        [
            {'artist': 'Виктор', 'upload': ('some_audio.mp3', b'record 1 audio')},
            {'artist': 'Вася', 'upload': ('some_audio.mp3', b'record 2 audio')}
        ]
    )

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


def test_edit_bhajan(config, session,
                     bhajan_factory, records_factory, request_factory,
                     tmpdir: LocalPath):
    from sv.admin.forms import DeformUploadTmpStore
    from sv.admin.views import edit_bhajan

    config.add_route('admin-bhajans', '/bhajans')

    bhajan = bhajan_factory()
    records, files = records_factory(2, bhajan)

    request = request_factory(
        '/dj/bhajans/%s' % bhajan.id,
        bhajan,
        [{'artist': r.artist, 'upload': b'', 'uid': str(r.id)}
         for r in records]
    )

    resp = edit_bhajan(request)
    # print(resp)

    # у нас по-прежнему 1 баджана и 2 записи
    assert session.query(Bhajan).count() == 1
    assert session.query(Record).count() == 2

    # файлов записей так же 2
    bhajan_upload_dir = tmpdir.join(str(bhajan.id))
    assert bhajan_upload_dir.listdir(sort=True) == files

    # и их содержимое не изменилось
    for f, rec in zip(files, records):
        assert f.read_binary() == 'record {} audio'.format(rec.id).encode()

    # tmpstore пустое
    tmpstore = DeformUploadTmpStore(request)
    assert list(tmpstore.keys()) == []


