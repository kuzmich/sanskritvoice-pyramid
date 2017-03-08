from pyramid.view import view_config


@view_config(route_name='admin-index', renderer='../templates/admin/bhajans.mako')
@view_config(route_name='admin-bhajans', renderer='../templates/admin/bhajans.mako')
def bhajans(request):
    # bhajans = m.Bhajan.query().fetch()
    # return {'bhajans': bhajans}
    return {'bhajans': []}
