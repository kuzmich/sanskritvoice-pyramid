import logging
import os
from pathlib import Path

import deform
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config
import sqlalchemy as sa

from sv.models import Bhajan, Record
from . import forms


logger = logging.getLogger(__name__)


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

        # перенести аудио в нужное место и запомнить его
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
        record_dir = Path(settings['sv.upload_dir'], str(bhajan.id))
        record_dir.mkdir(exist_ok=True)

        seq = sa.Sequence('records_id_seq')

        for rec_data in data['records']:
            record_id = db.execute(seq)

            record_path = record_dir / '{name}{ext}'.format(
                name=record_id,
                ext=os.path.splitext(rec_data['audio']['filename'])[1] or '.audio'
            )

            os.rename(rec_data['audio']['path'], str(record_path))

            record = Record(
                id=record_id,
                artist=rec_data['artist'],
                bhajan=bhajan,
                path=str(record_path.relative_to(settings['sv.upload_dir']))
            )
            db.add(record)

            # удалить информацию об upload в DeformUploadTmpStore
            del upload_tmp_store[rec_data['audio']['uid']]

        db.commit()

        return HTTPFound(request.route_path('admin-bhajans'))

    return dict(form=form.render(), resources=form.get_widget_resources())


@view_config(route_name='admin-edit_bhajan', renderer='admin/edit_bhajan.mako')
def edit_bhajan(request):
    db = request.dbsession
    bid = int(request.matchdict['bid'])

    bhajan = db.query(Bhajan).get(bid)
    form = deform.Form(forms.BhajanWithRecords(), buttons=(u'сохранить',))

    if request.method == 'POST':
        try:
            data = form.validate(request.POST.items())
        except deform.ValidationFailure as e:
            return dict(bhajan=bhajan, form=e.render())

        # db.query(Bhajan).filter_by(id=bhajan.id).update(data)

        bhajan.title = data['title']
        bhajan.category = data['category']
        bhajan.text = data['text']
        bhajan.accords = data['accords']

        db.commit()

        return HTTPFound(request.route_path('admin-bhajans'))

    return dict(bhajan=bhajan, form=form.render(bhajan.to_dict()))
