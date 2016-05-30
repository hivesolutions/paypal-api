#!/usr/bin/python
# -*- coding: utf-8 -*-

# Hive PayPal API
# Copyright (c) 2008-2016 Hive Solutions Lda.
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

__copyright__ = "Copyright (c) 2008-2016 Hive Solutions Lda."
""" The copyright for the module """

__license__ = "Apache License, Version 2.0"
""" The license for the module """

import appier

from . import payment
from . import webhook

BASE_URL = "https://api.paypal.com/v1/"
""" The default base url to be used when no other
base url value is provided to the constructor """

CLIENT_ID = None
""" The default value to be used for the client id
in case no client id is provided to the api client """

CLIENT_SECRET = None
""" The secret value to be used for situations where
no client secret has been provided to the client """

class Api(
    appier.OAuth2Api,
    payment.PaymentApi,
    webhook.WebhookApi
):

    def __init__(self, *args, **kwargs):
        appier.OAuth2Api.__init__(self, *args, **kwargs)
        self.client_id = appier.conf("PAYPAL_ID", CLIENT_ID)
        self.client_secret = appier.conf("PAYPAL_SECRET", CLIENT_SECRET)
        self.base_url = kwargs.get("base_url", BASE_URL)
        self.client_id = kwargs.get("client_id", self.client_id)
        self.client_secret = kwargs.get("client_secret", self.client_secret)
        self.access_token = kwargs.get("access_token", None)

    def oauth_token(self, grant_type = "client_credentials"):
        url = self.base_url + "oauth2/token"
        params = dict(grant_type = grant_type)
        headers = {
            "Accept" : "application/json",
            "Authorization" : "%s:%s" % (self.client_id, self.client_secret)
        }
        contents = self.get(
            url,
            params = params,
            headers = headers,
            token = False
        )
        self.access_token = contents["access_token"]
        return self.access_token
