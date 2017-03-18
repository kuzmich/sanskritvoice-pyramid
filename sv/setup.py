import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    'pyramid',
    # 'pyramid_jinja2',
    'pyramid_mako',
    'SQLAlchemy',
    'psycopg2',
    'alembic',
    'deform',
    'pyramid_redis_sessions',
    'waitress',
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',
    'pytest-cov',
]

dev_require = [
    'ipython',
    'pyramid_ipython',
    'pyramid_debugtoolbar',
    'logging_tree',
    # 'watchdog'
]

setup(
    name='sv',
    version='0.1',
    description='sanskritvoice.ru website',
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Pyramid',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    author='Alexey Kuzminich',
    author_email='akuzminich@gmail.com',
    url='http://sanskritvoice.ru',
    keywords='web pyramid pylons',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={
        'testing': tests_require,
        'dev': dev_require,
    },
    install_requires=requires,
    entry_points={
        'paste.app_factory': [
            'main = sv:main',
        ],
        'console_scripts': [
            'initialize_sv_db = sv.scripts.initializedb:main',
        ],
    },
)
