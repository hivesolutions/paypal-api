#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive PayPal API
# Copyright (c) 2008-2025 Hive Solutions Lda.
#
# This file is part of Hive PayPal API.
#
# Hive PayPal API is free software: you can redistribute it and/or modify
# it under the terms of the Apache License as published by the Apache
# Foundation, either version 2.0 of the License, or (at your option) any
# later version.
#
# Hive PayPal API is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License for more details.
#
# You should have received a copy of the Apache License along with
# Hive PayPal API. If not, see <http://www.apache.org/licenses/>.

__author__ = "João Magalhães <joamag@hive.pt>"
""" The author(s) of the module """

__copyright__ = "Copyright (c) 2008-2025 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import unittest

import appier

import paypal


class BaseTest(unittest.TestCase):

    def setUp(self):
        self.api = paypal.API(client_id="id", client_secret="secret")
        self.api.request = self._request
        self.requests = []

    def _request(self, method, url, **kwargs):
        self.requests.append((method, url, kwargs))
        if url.endswith("/oauth2/token"):
            return dict(access_token="token", token_type="Bearer")
        return dict(webhooks=[])

    def _reject(self, method, url, **kwargs):
        self.requests.append((method, url, kwargs))
        raise appier.HTTPError(None, code=401, extended=False)

    def test_basic(self):
        self.assertEqual(1 + 1, 2)

    def test_ping(self):
        result = self.api.ping()
        self.assertEqual(result, dict(webhooks=[]))
        self.assertEqual(len(self.requests), 2)
        method, url, kwargs = self.requests[0]
        self.assertEqual(method, appier.http.post)
        self.assertEqual(url, "https://api.sandbox.paypal.com/v1/oauth2/token")
        self.assertEqual(kwargs["headers"]["Authorization"], "Basic aWQ6c2VjcmV0")
        self.assertEqual(kwargs["params"]["grant_type"], "client_credentials")
        self.assertEqual(len(kwargs["params"]), 1)
        method, url, kwargs = self.requests[1]
        self.assertEqual(method, appier.http.get)
        self.assertEqual(
            url, "https://api.sandbox.paypal.com/v1/notifications/webhooks"
        )
        self.assertEqual(kwargs["headers"], dict(Authorization="Bearer token"))
        self.assertEqual(list(kwargs["params"].items()), [])
        self.assertEqual(self.api.access_token, "token")

        # the verification is made against the configured base URL
        # and using the credentials provided to the constructor
        api = paypal.API(
            base_url="https://paypal.hive.pt/v1/",
            client_id="other",
            client_secret="value",
        )
        api.request = self._request
        api.ping()
        _method, url, kwargs = self.requests[2]
        self.assertEqual(url, "https://paypal.hive.pt/v1/oauth2/token")
        self.assertEqual(kwargs["headers"]["Authorization"], "Basic b3RoZXI6dmFsdWU=")
        _method, url, kwargs = self.requests[3]
        self.assertEqual(url, "https://paypal.hive.pt/v1/notifications/webhooks")

        # an access token that is already available is used as is, so
        # no new token is requested before the webhooks listing
        api = paypal.API(client_id="id", client_secret="secret", access_token="other")
        api.request = self._request
        api.ping()
        self.assertEqual(len(self.requests), 5)
        method, url, kwargs = self.requests[4]
        self.assertEqual(method, appier.http.get)
        self.assertEqual(kwargs["headers"], dict(Authorization="Bearer other"))

        # without a client secret no token can be obtained, so the
        # verification fails before any request is made to PayPal
        api = paypal.API(client_id="id", client_secret=None)
        api.request = self._request
        self.assertRaises(appier.OAuthAccessError, api.ping)
        self.assertEqual(len(self.requests), 5)

        # invalid (or revoked) credentials are rejected by PayPal when
        # requesting the token and that error must reach the caller,
        # without listing the webhooks or keeping any access token
        api = paypal.API(client_id="id", client_secret="revoked")
        api.request = self._reject
        self.assertRaises(appier.HTTPError, api.ping)
        self.assertEqual(len(self.requests), 6)
        self.assertEqual(
            self.requests[5][1], "https://api.sandbox.paypal.com/v1/oauth2/token"
        )
        self.assertEqual(api.access_token, None)

    def test_oauth_types(self):
        self.assertEqual(self.api.oauth_types, ("header",))

        # the access token must only be sent in the authorization header
        # and never as a query string parameter, where it would end up in
        # the logs of every proxy and server that sees the request URL
        self.api.get_payment("PAYID-1")
        method, url, kwargs = self.requests[1]
        self.assertEqual(method, appier.http.get)
        self.assertEqual(
            url, "https://api.sandbox.paypal.com/v1/payments/payment/PAYID-1"
        )
        self.assertEqual(kwargs["headers"], dict(Authorization="Bearer token"))
        self.assertEqual(list(kwargs["params"].items()), [])

        self.api.execute_payment("PAYID-1", "PAYER-1")
        method, url, kwargs = self.requests[2]
        self.assertEqual(method, appier.http.post)
        self.assertEqual(
            url, "https://api.sandbox.paypal.com/v1/payments/payment/PAYID-1/execute"
        )
        self.assertEqual(kwargs["headers"], dict(Authorization="Bearer token"))
        self.assertEqual(list(kwargs["params"].items()), [])
        self.assertEqual(kwargs["data_j"], dict(payer_id="PAYER-1"))

        # the token request itself uses basic authentication only, so
        # no bearer token or token parameter is added to it
        method, url, kwargs = self.requests[0]
        self.assertEqual(url, "https://api.sandbox.paypal.com/v1/oauth2/token")
        self.assertEqual(kwargs["headers"]["Authorization"], "Basic aWQ6c2VjcmV0")
        self.assertEqual(kwargs["params"]["grant_type"], "client_credentials")
        self.assertEqual(len(kwargs["params"]), 1)
        self.assertEqual(len(self.requests), 3)
