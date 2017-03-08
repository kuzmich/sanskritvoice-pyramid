import logging
from pyramid.events import NewRequest, subscriber

logger = logging.getLogger(__name__)


@subscriber(NewRequest)
def on_new_request(event):
    request = event.request
    request.add_finished_callback(on_request_finished)


def on_request_finished(request):
    request.dbsession.close()
