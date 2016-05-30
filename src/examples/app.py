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

from . import base

class PaypalApp(appier.WebApp):

    def __init__(self, *args, **kwargs):
        appier.WebApp.__init__(
            self,
            name = "paypal",
            *args, **kwargs
        )

    @appier.route("/", "GET")
    def index(self):
        return self.webhooks()

    @appier.route("/webhooks", "GET")
    def webhooks(self):
        self.ensure_api()
        api = self.get_api()
        webhooks = api.list_webhooks()
        return webhooks

    @appier.route("/payments/new", "GET")
    def new_payment(self):
        self.ensure_api()
        api = self.get_api()
        amount = self.field("amount", 100, cast = int)
        currency = self.field("currency", "EUR")
        exp_month = self.field("exp_month", 1)
        exp_year = self.field("exp_year", 2020)
        number = self.field("number", 4242424242424242)
        balance = api.create_payment(
            amount, currency, exp_month, exp_year, number
        )
        return balance

    def ensure_api(self):
        access_token = self.session.get("paypal.access_token", None)
        if access_token: return
        api = base.get_api()
        api.oauth_token()
        self.session["paypal.access_token"] = api.access_token

    def get_api(self):
        access_token = self.session and self.session.get("paypal.access_token", None)
        api = base.get_api()
        api.access_token = access_token
        return api

if __name__ == "__main__":
    app = PaypalApp()
    app.serve()
