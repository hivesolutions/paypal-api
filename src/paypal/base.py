#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive PayPal API
# Copyright (c) 2008-2017 Hive Solutions Lda.
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

__version__ = "1.0.0"
""" The version of the module """

__revision__ = "$LastChangedRevision$"
""" The revision number of the module """

__date__ = "$LastChangedDate$"
""" The last change date of the module """

__copyright__ = "Copyright (c) 2008-2017 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import appier

from . import payment
from . import webhook

BASE_URL = "https://api.paypal.com/v1/"
""" The default base url to be used when no other
base url value is provided to the constructor """

SANDBOX_URL = "https://api.sandbox.paypal.com/v1/"
""" The base url that should be used whenever using
the api under a sandbox environment """

CLIENT_ID = None
""" The default value to be used for the client id
in case no client id is provided to the api client """

CLIENT_SECRET = None
""" The secret value to be used for situations where
no client secret has been provided to the client """

class API(
    appier.OAuth2API,
    payment.PaymentAPI,
    webhook.WebhookAPI
):

    def __init__(self, *args, **kwargs):
        appier.OAuth2API.__init__(self, *args, **kwargs)
        self.sandbox = appier.conf("PAYPAL_SANDBOX", True, cast = bool)
        self.client_id = appier.conf("PAYPAL_ID", CLIENT_ID)
        self.client_secret = appier.conf("PAYPAL_SECRET", CLIENT_SECRET)
        self.base_url = kwargs.get("base_url", SANDBOX_URL if self.sandbox else BASE_URL)
        self.client_id = kwargs.get("client_id", self.client_id)
        self.client_secret = kwargs.get("client_secret", self.client_secret)
        self.access_token = kwargs.get("access_token", None)

    def get_access_token(self):
        if self.access_token: return self.access_token
        return self.oauth_token()

    def auth_callback(self, params, headers):
        self.oauth_token()
        headers["Authorization"] = "Bearer %s" % self.get_access_token()

    def oauth_token(self, grant_type = "client_credentials"):
        url = self.base_url + "oauth2/token"
        if not self.client_id: raise appier.OAuthAccessError(
            message = "No client id provided"
        )
        if not self.client_secret: raise appier.OAuthAccessError(
            message = "No client secret provided"
        )
        token = appier.http._authorization(self.client_id, self.client_secret)
        authorization = "Basic %s" % token
        params = dict(
            grant_type = grant_type
        )
        headers = {
            "Accept" : "application/json",
            "Accept-Language" : "en_US",
            "Authorization" : authorization
        }
        contents = self.post(
            url,
            params = params,
            headers = headers,
            auth = False,
            token = False
        )
        self.access_token = contents["access_token"]
        return self.access_token

    def get_url(self, links, target):
        for link in links:
            rel = link.get("rel", None)
            href = link.get("href", None)
            if not rel == target: continue
            return href
        return None
