from __future__ import absolute_import
import json

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPOk, HTTPNotImplemented
from socketio import socketio_manage
from socketio.namespace import BaseNamespace

from .. import log, models, Session


@view_config(route_name='socket.io')
def socketio(request):  # pragma: nocover: don't need to unittest socketio.io
    """
    Main socket.io handler for the application
    Pretty much registers socket.io namespaces
    """

    # Check if the transport requested is not supported
    if 'socketio' not in request.environ:
        return HTTPNotImplemented()

    # TODO: Do not use SQLAlchemy in websockets, it is not stable
    #       We'll have to figure out a way to broadcast events to the
    #       WSGI-side
    Session.remove()

    socketio_manage(
        request.environ,
        request=request,
        namespaces={
            '/export': ExportNamespace
        }
    )

    return HTTPOk()


class ExportNamespace(BaseNamespace):
    """
    This service will emit the progress of the current user's exports

    Note that this service is just a pass-through for export broadcasts,
    it simply takes what is published in the export channel and emits
    progress data with the message that was broadcast. The only key
    in the message that this service depends on is the ``owner_user``
    key (to ensure the broadcast goes to the appropriate user).
    """

    def get_initial_acl(self):
        """
        Everything is locked at first
        """
        return []

    def initialize(self):
        """
        Determines from the request if this socket can accept events
        """
        log.debug('Initializing socket.io service')
        exports = models.ExportFactory(self.request)
        if self.request.has_permission('view', exports):
            self.lift_acl_restrictions()
            self.session['user'] = self.request.authenticated_userid
            self.session['redis'] = self.request.redis
            log.debug('socket.io for %s' % self.session['user'])
            self.spawn(self.listener)

    def listener(self):
        """
        Main process that listens for export progress broadcasts.
        All progress relating to the current user will be sent back.
        """
        userid = self.session['user']
        redis = self.session['redis']

        pubsub = redis.pubsub()
        pubsub.subscribe('export')

        # emit subsequent progress
        for message in pubsub.listen():
            if message['type'] == 'message':
                data = json.loads(message['data'])
                if data['owner_user'] == userid:
                    log.debug(data)
                    self.emit('export', data)
