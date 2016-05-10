# -*- coding: utf-8 -*-
from __future__ import (unicode_literals, absolute_import)

import logging

import requests
import ssl
import xmltodict
from money import Money

from briefdruckzentrum.adapters import SSLAdapter

logger = logging.getLogger(__name__)


class Error(object):
    def __init__(self, raw_string):
        code, self.message = raw_string.split(':', 1)
        self.code = int(code)

    def __unicode__(self):
        return '<Error {code}: "{message}">'.format(code=self.code, message=self.message)


class Costs(dict):
    def __init__(self, raw_dict, **kwargs):
        super(Costs, self).__init__(**kwargs)
        self.update(raw_dict)
        self.production = Money(amount=float(raw_dict['Betrag']) / 100,
                                currency='EUR')
        self.shipping = Money(amount=float(raw_dict['Porto']) / 100,
                              currency='EUR')
        self.shipping_tax_free = Money(amount=float(raw_dict['Porto_MwSt_Frei']) / 100,
                                       currency='EUR')


class OrderException(Exception):
    def __init__(self, errors):
        super(OrderException, self).__init__(
            ' - '.join(e.message for e in errors)
        )

        self.errors = errors


class Order(object):
    BLACK_AND_WHITE = 1
    COLOUR = 2
    COLOR_MODES = [BLACK_AND_WHITE, COLOUR]

    GERMANY = 1
    EU = 2
    WORLD_WIDE = 3
    REGIONS = [GERMANY, EU, WORLD_WIDE]

    SIMPLEX = 1
    DUPLEX = 2

    ENVELOPE_DL = 1
    ENVELOPE_C4 = 2
    ENVELOPE_AUTO = 3

    ENVELOPE_FORMATS = [ENVELOPE_DL, ENVELOPE_C4, ENVELOPE_AUTO]

    URL = 'https://www.briefdruckzentrum.de/rest/bdz/auftrag'

    # ignore error: 900 TESTAUFTRAG
    IGNORE_ERROR_CODES = (900, )

    errors = None

    @classmethod
    def get_request(cls, file, color_mode, region,
                    duplex=DUPLEX, paper=0, envelopeDL=0, envelopeC4=0,
                    envelope_format=ENVELOPE_DL, name=None, test=True):

        if color_mode not in cls.COLOR_MODES:
            raise ValueError('"%s"  is not a valid color_mode option.' % color_mode)

        if region not in cls.REGIONS:
            raise ValueError('"%s"  is not a valid region.' % region)

        if envelope_format not in cls.ENVELOPE_FORMATS:
            raise ValueError('"%s" is not a valid envelope format.' % envelope_format)

        if not isinstance(test, bool):
            raise ValueError('"test" must be a boolean, got "%s"' % test)

        return cls.URL, {
            'Druckart': color_mode,
            'Region': region,
            'Druckmodus': duplex,
            'Papier': paper,
            'KuvertDL': envelopeDL,
            'KuvertC4': envelopeC4,
            'Briefformat': envelope_format,
            'Name': name,
            'Test': test,
        }, {'file': file}

    def __init__(self, response):
        self.response = response
        r_dict = xmltodict.parse(response)['Auftrag']
        if 'Error' in r_dict:
            if isinstance(r_dict['Error']['Error'], list):
                self.errors = [Error(e) for e in r_dict['Error']['Error']]
            else:
                self.errors = [Error(r_dict['Error']['Error'])]

        if 'Files' in r_dict:
            self.files = r_dict['Files']
        if "Auftragskosten" in r_dict:
            self.costs = Costs(r_dict['Auftragskosten'])


class Client(object):
    def __init__(self, user, password):
        self.session = requests.Session()
        self.session.mount('https://', SSLAdapter(ssl_version=ssl.PROTOCOL_TLSv1))
        self.session.auth = (user, password)
        self.session.verify = True

    def create_order(self, file, color_mode, region,
                     duplex=Order.DUPLEX, paper=0, envelopeDL=0, envelopeC4=0,
                     envelope_format=Order.ENVELOPE_DL, name=None, test=True):

        url, data, files = Order.get_request(file, color_mode, region, duplex,
                                             paper, envelopeDL, envelopeC4,
                                             envelope_format, name, test)

        logger.debug("url %s, data %s", url, data)

        response = self.session.post(url, data=data, files=files)
        logger.debug("response %s %s", response.status_code, response.text)

        response.raise_for_status()

        order = Order(response.text)
        if order.errors:
            real_errors = [
                error
                for error in order.errors
                if error.code not in Order.IGNORE_ERROR_CODES
            ]

            if real_errors:
                raise OrderException(real_errors)

        order.request = response.request
        return order
