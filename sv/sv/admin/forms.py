import logging
import shutil
import tempfile

import colander
import deform.widget


logger = logging.getLogger(__name__)


CATEGORIES = [('', 'Выберите категорию'),
              ('ganesh', 'Ганеша'),
              ('shiva', 'Шива'),
              ('guru', 'Гуру'),
              ('devi', 'Деви'),
              ('other', 'Другие')]


class DeformUploadTmpStore(dict):
    """
    A temporary storage for deform file uploads

    File uploads are stored in the session so that you don't need
    to upload your file again if validation of another schema node
    fails.
    """

    def __init__(self, request):
        super().__init__()

        self.session = request.session
        self.session.setdefault('uploads', {})

        self.uploads = self.session['uploads']

        self.upload_dir = request.registry.settings['sv.upload_dir']
        self.upload_tmp_dir = request.registry.settings['sv.upload_tmp_dir']

    def __contains__(self, name):
        return name in self.uploads

    def __delitem__(self, name):
        del self.uploads[name]
        self.session.changed()

    def __getitem__(self, name):
        value = self.uploads[name].copy()
        logger.debug('Get: %s', value)
        return value

    def __setitem__(self, name, value):
        value = value.copy()
        logger.debug('Set: %s', value)

        src_file = value.pop('fp')
        value['fp'] = None

        if src_file:
            fd, tmp_file = tempfile.mkstemp(dir=self.upload_tmp_dir)
            logger.debug('Created tmp file %s', tmp_file)
            with open(fd, 'wb') as dest_file:
                shutil.copyfileobj(src_file, dest_file)

            value['path'] = tmp_file

        self.uploads[name] = value
        self.session.changed()

    def get(self, name, default=None):
        try:
            return self[name]
        except KeyError:
            return default

    def keys(self):
        return self.uploads.keys()

    def preview_url(self, name):
        return None


class Bhajan(colander.MappingSchema):
    title = colander.SchemaNode(
        colander.String(),
        # validator=colander.Length(3, 150),
        title='Название'
    )
    category = colander.SchemaNode(
        colander.String(),
        # validator=colander.OneOf([x[0] for x in CATEGORIES]),
        widget=deform.widget.SelectWidget(values=CATEGORIES),
        title='Категория'
    )
    text = colander.SchemaNode(
        colander.String(),
        # validator=colander.Length(min=10),
        widget=deform.widget.TextAreaWidget(rows=7),
        title='Текст'
    )
    accords = colander.SchemaNode(
        colander.String(),
        # validator=colander.Length(min=10),
        widget=deform.widget.TextAreaWidget(rows=7),
        title='Аккорды',
        missing='',
    )


class Record(colander.MappingSchema):
    artist = colander.SchemaNode(colander.String(),
                                 validator=colander.Length(1, 100),
                                 title='Исполнитель')
    audio = colander.SchemaNode(deform.FileData(),
                                title='Аудио файл')

    def after_bind(self, node, kw):
        self['audio'].widget = deform.widget.FileUploadWidget(
            DeformUploadTmpStore(kw['request']),
            # accept='audio/*'
        )


class Records(colander.SequenceSchema):
    record = Record(title='Запись')


class BhajanWithRecords(Bhajan):
    records = Records(title='Записи')
