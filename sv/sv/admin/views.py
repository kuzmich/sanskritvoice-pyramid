import deform
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config

from sv.models import Bhajan
from . import forms


@view_config(route_name='admin-index', renderer='admin/bhajans.mako')
@view_config(route_name='admin-bhajans', renderer='admin/bhajans.mako')
def bhajans(request):
    db = request.dbsession

    bhajans = db.query(Bhajan)
    return {'bhajans': bhajans}


@view_config(route_name='admin-add_bhajan', renderer='admin/add_bhajan.mako')
def add_bhajan(request):
    db = request.dbsession
    form = deform.Form(forms.BhajanWithRecords(), buttons=(u'добавить',))

    if request.method == 'POST':
        try:
            data = form.validate(request.POST.items())
        except deform.ValidationFailure as e:
            return dict(form=e.render(), resources=form.get_widget_resources())

        bhajan = Bhajan(
            title=data['title'],
            category=data['category'],
            text=data['text'],
            accords=data['accords']
        )

        db.add(bhajan)
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
