import unittest
from unittest.mock import Mock

from golem.ethereum.web3.middleware import RemoteRPCErrorMiddlewareBuilder


class TestMiddleware(unittest.TestCase):

    def test_successful_calls(self):
        listener = Mock()
        builder = RemoteRPCErrorMiddlewareBuilder(listener, max_errors=2)
        make_request = Mock()
        middleware = builder.build(make_request, _web3=None)

        middleware(Mock(), None)
        assert not listener.called

        middleware(Mock(), None)
        assert not listener.called

    def test_recoverable_errors(self):
        listener = Mock()
        builder = RemoteRPCErrorMiddlewareBuilder(listener, max_errors=2)
        make_request = Mock(side_effect=Exception)
        middleware = builder.build(make_request, _web3=None)

        with self.assertRaises(Exception):
            middleware(Mock(), None)
        assert not listener.called

        with self.assertRaises(Exception):
            middleware(Mock(), None)
        assert not listener.called

    def test_unrecoverable_errors(self):
        listener = Mock()
        builder = RemoteRPCErrorMiddlewareBuilder(
            listener,
            max_errors=5,
            retries=2,
        )
        make_request = Mock(side_effect=ConnectionError)
        middleware = builder.build(make_request, _web3=None)

        middleware(Mock(), None)
        assert listener.call_count == 1

        middleware(Mock(), None)
        assert listener.call_count == 2

        with self.assertRaises(ConnectionError):
            middleware(Mock(), None)
