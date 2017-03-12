import deform
from pkg_resources import resource_filename
from pyramid.config import Configurator
from pyramid.i18n import get_localizer
from pyramid.threadlocal import get_current_request


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    # config.include('pyramid_jinja2')
    config.include('.models.session')
    config.include('.routes')
    config.include('.routes.admin', route_prefix='/dj')
    config.scan()

    config.add_translation_dirs(
        'colander:locale',
        'deform:locale',
    )

    def translator(term):
        return get_localizer(get_current_request()).translate(term)

    deform_template_dir = resource_filename('deform', 'templates/')
    zpt_renderer = deform.ZPTRendererFactory(
        [deform_template_dir],
        translator=translator,
    )
    deform.Form.set_default_renderer(zpt_renderer)

    return config.make_wsgi_app()
