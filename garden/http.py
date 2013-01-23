from twisted.web.resource import Resource
from twisted.web.server import NOT_DONE_YET
from zope.interface import implements


from garden.interface import IInputSource



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
        
        res = self.input_receiver.inputReceived(entity, name, version, value)
        def received(result):
            request.write('success')
            request.finish()
        def error(err):
            request.setResponseCode(500)
            request.write('error')
            request.finish()
        res.addCallbacks(received, error)
        return NOT_DONE_YET