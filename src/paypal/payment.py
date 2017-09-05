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

class PaymentAPI(object):

    def create_payment(
        self,
        intent = "sale",
        payer = None,
        transactions = [],
        redirect_urls = []
    ):
        url = self.base_url + "payments/payment"
        payload = dict(
            intent = intent,
            payer = payer,
            transactions = transactions,
            redirect_urls = redirect_urls
        )
        contents = self.post(url, data_j = payload)
        return contents

    def get_payment(self, payment):
        url = self.base_url + "payments/payment/%s" % payment
        contents = self.get(url)
        return contents

    def execute_payment(self, payment, payer_id):
        url = self.base_url + "payments/payment/%s/execute" % payment
        contents = self.post(url, data_j = dict(payer_id = payer_id))
        return contents
