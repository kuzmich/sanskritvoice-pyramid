def includeme(config):
    config.add_static_view('static/deform', 'deform:static')
    config.add_static_view('static', 'static', cache_max_age=3600)

    config.add_static_view(name='uploads', path='sv:uploads')
    config.override_asset(to_override='sv:uploads/',
                          override_with=config.registry.settings['sv.upload_dir'])

    config.add_route('home', '/')
    config.add_route('bhajan', '/b/{bid}')
    config.add_route('category', '/c/{category}')

    config.add_route('logout', '/logout')


def admin(config):
    config.add_route('admin-index', '/')
    config.add_route('admin-bhajans', '/bhajans')
    config.add_route('admin-records', '/records')
    config.add_route('admin-add_bhajan', '/add_bhajan')
    config.add_route('admin-edit_bhajan', '/bhajans/{bid:\d+}')
