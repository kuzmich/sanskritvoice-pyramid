

def test_my_view(request, session):
    from sv.models import MyModel
    from sv.views.default import my_view

    model = MyModel(name='one', value=1)
    session.add(model)
    session.commit()

    resp = my_view(request)
    assert resp['one'].name == 'one'
    assert resp['one'].value == 1
    assert resp['project'] == 'sv'


def test_functional(session, client):
    from sv.models import MyModel
    model = MyModel(name='one', value=1)
    session.add(model)
    session.commit()

    resp = client.get('/')
    # print(resp)
