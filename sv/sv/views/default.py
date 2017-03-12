import logging
from pyramid.view import view_config

logger = logging.getLogger(__name__)


@view_config(route_name='home', renderer='../templates/mytemplate.jinja2')
def my_view(request):
    db = request.dbsession

    try:
        # db.add(MyModel(name='two', value=2))
        m = MyModel(name='two', value=2)
        db.add(m)
        db.commit()
    except Exception as e:
        logger.exception('Shit!')
        db.rollback()
        logger.warning('Rolled back')

    try:
        with db.begin_nested():
            m = MyModel(name='two', value=2)
            db.add(m)
    except Exception as e:
        logger.exception('Shit!')
        db.rollback()
        logger.warning('Rolled back')

    query = db.query(MyModel)
    one = query.filter(MyModel.name == 'one').first()
    return {'one': one, 'project': 'sv'}
