import colander
import deform.widget


CATEGORIES = [('', 'Выберите категорию'),
              ('ganesh', 'Ганеша'),
              ('shiva', 'Шива'),
              ('guru', 'Гуру'),
              ('devi', 'Деви'),
              ('other', 'Другие')]


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


class MemoryTmpStore(dict):
    def preview_url(self, name):
        return None


class Record(colander.MappingSchema):
    # bhajan = colander.SchemaNode(colander.String(),
    #                              widget=deform.widget.SelectWidget(values=Choices(bhajan_ch)),
    #                              title=u'Баджана')
    artist = colander.SchemaNode(colander.String(),
                                 validator=colander.Length(1, 100),
                                 title='Исполнитель')
    audio = colander.SchemaNode(deform.FileData(),
                                widget=deform.widget.FileUploadWidget(MemoryTmpStore()),
                                title='Аудио файл')


class Records(colander.SequenceSchema):
    record = Record(title='Запись')


class BhajanWithRecords(Bhajan):
    records = Records(title='Записи')
