import logging
import os
from pathlib import Path
import shutil

import deform
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config
import sqlalchemy as sa

from sv.models import Bhajan, Record
from . import forms


logger = logging.getLogger(__name__)


def manage_records(records_data, bhajan, db, upload_dir, tmpstore):
    # data['records'] = [{'artist': '...', 'audio': {}}, {...}]
    # 'artist': 'Витя'
    # 'audio': {
    #     'filename': 'Vitamins_Vim_Colorscheme_by_hcalves.vim',
    #     'mimetype': 'application/octet-stream',
    #     'size': -1,
    #     'uid': 'BSLAIPECML',
    #     'fp': None,
    #     'path': '/home/alexey/dev/sv-new/uploads/tmp/r7fyw49w'
    # }
    def get_new_record_path(record_id, audio_data):
        return records_dir / '{name}{ext}'.format(
            name=record_id,
            ext=os.path.splitext(audio_data['filename'])[1] or '.audio'
        )

    def add(data):
        record_id = db.execute(seq)

        record_path = get_new_record_path(record_id, data['audio'])
        shutil.move(data['audio']['path'], str(record_path))

        record = Record(
            id=record_id,
            artist=data['artist'],
            bhajan=bhajan,
            path=str(record_path.relative_to(upload_dir))
        )
        db.add(record)

    def edit(record, data):
        record.artist = data['artist']

        # новый файл
        if 'path' in data['audio']:
            upload_dir.joinpath(record.path).unlink()

            record_path = get_new_record_path(record.id, data['audio'])
            shutil.move(data['audio']['path'], str(record_path))
            record.path = str(record_path.relative_to(upload_dir))

        db.commit()

    def delete():
        pass

    upload_dir = Path(upload_dir)
    records_dir = upload_dir / str(bhajan.id)
    records_dir.mkdir(exist_ok=True)

    seq = sa.Sequence('records_id_seq')

    records_map = {str(r.id): r for r in bhajan.records}
    records_data_map = {data['audio']['uid']: data for data in records_data}

    for data in records_data:
        uid = data['audio']['uid']
        # uid не цифра, значит это новая запись
        if not uid.isdigit():
            add(data)
        else:
            edit(records_map[uid], data)

        # удалить информацию об upload в DeformUploadTmpStore
        del tmpstore[uid]


@view_config(route_name='admin-index', renderer='admin/bhajans.mako')
@view_config(route_name='admin-bhajans', renderer='admin/bhajans.mako')
def bhajans(request):
    db = request.dbsession

    bhajans = db.query(Bhajan)
    return {'bhajans': bhajans}


@view_config(route_name='admin-add_bhajan', renderer='admin/add_bhajan.mako')
def add_bhajan(request):
    db = request.dbsession
    settings = request.registry.settings
    upload_tmp_store = forms.DeformUploadTmpStore(request)

    schema = forms.BhajanWithRecords().bind(request=request)
    form = deform.Form(schema, buttons=(u'добавить',))

    if request.method == 'POST':
        logger.debug('POST: %s', request.POST)
        controls = request.POST.items()
        try:
            data = form.validate(controls)
            logger.debug('Validated data: %s', data)
        except deform.ValidationFailure as e:
            return dict(form=e.render(), resources=form.get_widget_resources())

        # TODO использовать транзакцию для добавления бажданы и ее записей

        bhajan = Bhajan(
            title=data['title'],
            category=data['category'],
            text=data['text'],
            accords=data['accords']
        )
        db.add(bhajan)
        db.flush()

        manage_records(data['records'], bhajan, db, settings['sv.upload_dir'], upload_tmp_store)

        db.commit()

        return HTTPFound(request.route_path('admin-bhajans'))

    return dict(form=form.render(), resources=form.get_widget_resources())


@view_config(route_name='admin-edit_bhajan', renderer='admin/edit_bhajan.mako')
def edit_bhajan(request):
    db = request.dbsession
    settings = request.registry.settings
    upload_tmp_store = forms.DeformUploadTmpStore(request)
    bid = int(request.matchdict['bid'])

    bhajan = db.query(Bhajan).get(bid)
    schema = forms.BhajanWithRecords().bind(request=request)
    form = deform.Form(schema, buttons=(u'сохранить',))

    if request.method == 'POST':
        logger.debug('POST: %s', request.POST)
        try:
            data = form.validate(request.POST.items())
            logger.debug('Validated data: %s', data)
        except deform.ValidationFailure as e:
            return dict(bhajan=bhajan, form=e.render(), resources=form.get_widget_resources())

        # db.query(Bhajan).filter_by(id=bhajan.id).update(data)

        bhajan.title = data['title']
        bhajan.category = data['category']
        bhajan.text = data['text']
        bhajan.accords = data['accords']

        manage_records(data['records'], bhajan, db, settings['sv.upload_dir'], upload_tmp_store)

        db.commit()

        return HTTPFound(request.route_path('admin-bhajans'))

    appstruct = bhajan.to_dict()
    appstruct['records'] = []
    for record in bhajan.records:
        record_data = {
            'artist': record.artist,
            'audio': {
                'uid': '{}'.format(record.id),
                'filename': os.path.basename(record.path),
            }
        }
        appstruct['records'].append(record_data)

    return dict(bhajan=bhajan, form=form.render(appstruct), resources=form.get_widget_resources())
