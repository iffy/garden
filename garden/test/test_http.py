from twisted.trial.unittest import TestCase
from zope.interface.verify import verifyObject

from urllib import urlencode

from mock import Mock
from StringIO import StringIO

from twisted.internet import defer
from twisted.web import server
from twisted.web.test.test_web import DummyChannel
from twisted.web.http_headers import Headers
from twisted.web.http import parse_qs

from garden.interface import IInputSource
from garden.http import WebInputSource
from garden.test.fake import FakeInputReceiver

import cgi
from cgi import parse_header as _parseHeader


# copied from klein
def requestMock(path, method="GET", host="localhost", port=8080, isSecure=False,
                body=None, headers=None):
    if not headers:
        headers = {}

    if not body:
        body = ''

    request = server.Request(DummyChannel(), False)
    request.gotLength(len(body))
    request.content = StringIO()
    request.content.write(body)
    request.content.seek(0,0)
    request.requestHeaders = Headers(headers)
    request.setHost(host, port, isSecure)
    request.uri = path
    request.args = {}
    request.prepath = []
    request.postpath = path.split('/')
    request.method = method
    request.clientproto = 'HTTP/1.1'

    request.setResponseCode = Mock(wraps=request.setResponseCode)
    request.finish = Mock(wraps=request.finish)
    request.write = Mock(wraps=request.write)

    def registerProducer(producer, streaming):
        # This is a terrible terrible hack.
        producer.resumeProducing()
        producer.resumeProducing()

    request.registerProducer = registerProducer
    request.unregisterProducer = Mock()

    # copied from twisted.web.http.Request.requestReceived
    args = request.args
    ctype = request.requestHeaders.getRawHeaders(b'content-type')
    if ctype is not None:
        ctype = ctype[0]

    if request.method == b"POST" and ctype:
        mfd = b'multipart/form-data'
        key, pdict = _parseHeader(ctype)
        if key == b'application/x-www-form-urlencoded':
            args.update(parse_qs(request.content.read(), 1))
        elif key == mfd:
            try:
                args.update(cgi.parse_multipart(request.content, pdict))
            except KeyError as e:
                if e.args[0] == b'content-disposition':
                    # Parse_multipart can't cope with missing
                    # content-dispostion headers in multipart/form-data
                    # parts, so we catch the exception and tell the client
                    # it was a bad request.
                    request.channel.transport.write(
                            b"HTTP/1.1 400 Bad Request\r\n\r\n")
                    request.channel.transport.loseConnection()
                    return
                raise
        request.content.seek(0, 0)

    return request


def _render(resource, request):
    result = resource.render(request)
    if isinstance(result, str):
        request.write(result)
        request.finish()
        return defer.succeed(None)
    elif result is server.NOT_DONE_YET:
        if request.finished:
            return defer.succeed(None)
        else:
            return request.notifyFinish()
    else:
        raise ValueError("Unexpected return value: %r" % (result,))



class WebInputSourceTest(TestCase):


    def test_IInputSource(self):
        verifyObject(IInputSource, WebInputSource())


    def test_setInputReceiver(self):
        """
        Should have an input_receiver attribute that you can set with
        setInputReceiver
        """
        w = WebInputSource()
        self.assertEqual(w.input_receiver, None)
        w.setInputReceiver('foo')
        self.assertEqual(w.input_receiver, 'foo')


    def test_render_POST(self):
        """
        It should give input to the input_receiver that it receives over
        POST
        """
        receiver = FakeInputReceiver()
        d = defer.Deferred()
        receiver.inputReceived.mock.side_effect = lambda *a: d
        
        w = WebInputSource()
        w.setInputReceiver(receiver)
        
        data = {
            'entity': 'Joe',
            'name': 'cake',
            'version': '1',
            'value': 'abc123!@#&=_ \x00\x01\x02',
        }
        payload = urlencode(data)
        
        request = requestMock('/', 'POST', body=payload, headers={
            'Content-Type': ['application/x-www-form-urlencoded'],
        })
        result = _render(w, request)
        self.assertFalse(result.called, "Should not be done yet because the "
                         "InputReceiver hasn't acknowledged receipt yet")
        
        receiver.inputReceived.assert_called_once_with('Joe', 'cake', '1',
                'abc123!@#&=_ \x00\x01\x02')
        d.callback('foo')
        self.assertTrue(result.called, "Should have a result now")
        self.assertTrue(request.write.call_count > 0, "Should have written "
                        "something as a response")
        
        