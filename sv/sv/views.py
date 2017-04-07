from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.view import view_config
from sv.models import Bhajan, Record, CATEGORIES


@view_config(route_name='home', renderer='public/home.mako')
def home(request):
    bhajans = request.dbsession.query(Bhajan).order_by(Bhajan.title)
    return dict(bhajans=bhajans,
                categories=CATEGORIES[1:])


@view_config(route_name='bhajan', renderer='public/bhajan.mako')
def bhajan(request):
    bid = request.matchdict['bid']
    bhajan = request.dbsession.query(Bhajan).get(bid)
    if not bhajan:
        return HTTPNotFound()

    return dict(bhajan=bhajan,
                categories=CATEGORIES[1:])
