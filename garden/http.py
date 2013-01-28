from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from twisted.internet import defer
from zope.interface import implements

import json

from garden.data import Input
from garden.interface import IInputSource, IDataReceiver



class WebInputSource(Resource):
    
    implements(IInputSource)
    
    input_receiver = None
    
    
    def setInputReceiver(self, receiver):
        self.input_receiver = receiver


    def render_GET(self, request):
        return '''
        <html>
        <body>
            <form method="post">
                entity: <input type="text" name="entity">
                name: <input type="text" name="name">
                version: <input type="text" name="version">
                value: <input type="text" name="value">
                <input type="submit" value="submit">
            </form>
        </body>
        '''

    def render_POST(self, request):
        entity = request.args['entity'][0]
        name = request.args['name'][0]
        version = request.args['version'][0]
        value = request.args['value'][0]
        
        res = self.input_receiver.inputReceived(Input(entity, name, version,
                                                      value))
        def received(result):
            request.write('success')
            request.finish()
        def error(err):
            request.setResponseCode(500)
            request.write('error')
            request.finish()
        res.addCallbacks(received, error)
        return NOT_DONE_YET


def sseMsg(name, data):
    return 'event: %s\ndata: %s\n\n' % (name, data)


class WebDataFeed(Resource):

    implements(IDataReceiver)


    def __init__(self):
        Resource.__init__(self)
        self.spectators = set()


    def render_GET(self, request):
        if request.args.get('event'):
            return self.renderFeed(request)
        return '''
        <html>
            <head>
                <style>
                    th {
                        text-align: left;
                    }
                    .thing {
                        font-family: monospace;
                        white-space: nowrap;
                    }
                    .entity {
                        
                    }
                    .name {
                    }
                    .version {
                        color: #006;
                    }
                    .lineage {
                        font-family: monospace;
                        color: #999;
                    }
                    .value {
                        font-family: monospace;
                        color: #090;
                    }
                </style>
            </head>
            <body>
                <table width="500">
                    <tr>
                        <th>entity</th>
                        <th>name</th>
                        <th>version</th>
                        <th>lineage</th>
                        <th>value</th>
                    </tr>
                    <tbody id="place"></tbody>
                </table>
                <script>
                    things = ['entity', 'name', 'version', 'lineage', 'value'];
                    function dataReceived(ev) {
                        var data = JSON.parse(ev.data);
                        var row = document.createElement('tr');
                        for (var i = 0; i < things.length; i++) {
                            var d = document.createElement('td');
                            d.setAttribute('class', 'thing ' +things[i]);
                            d.innerHTML = data[i];
                            row.appendChild(d);
                        }
                        document.getElementById('place').appendChild(row);
                    }
                    var source = new EventSource(window.location.href + '?event=true');
                    source.addEventListener('data', dataReceived);
                </script>
            </body>
        </html>'''


    def renderFeed(self, request):
        request.setHeader('Content-type', 'text/event-stream')
        request.write(sseMsg('keepalive', 'hello'))
        self.spectators.add(request)
        return NOT_DONE_YET


    def dataReceived(self, data):
        entity, name, version, lineage, value = data
        for s in list(self.spectators):
            if s.transport.disconnected:
                self.spectators.remove(s)
                continue
            s.write(sseMsg('data', json.dumps([entity, name, version, lineage, value])))
        return defer.succeed('received')
