# -*- coding: utf-8 -*-

"""
    Redsys client classes
    ~~~~~~~~~~~~~~~~~~~~~~

    Basic client for the Redsys credit card paying services.

"""

import hashlib

DATA = [
    'Ds_Merchant_Amount',
    'Ds_Merchant_Currency',
    'Ds_Merchant_Order',
    'Ds_Merchant_ProductDescription',
    'Ds_Merchant_Titular',
    'Ds_Merchant_MerchantCode',
    'Ds_Merchant_MerchantURL',
    'Ds_Merchant_UrlOK',
    'Ds_Merchant_UrlKO',
    'Ds_Merchant_MerchantName',
    'Ds_Merchant_ConsumerLanguage',
    'Ds_Merchant_MerchantSignature',
    'Ds_Merchant_Terminal',
    'Ds_Merchant_SumTotal',
    'Ds_Merchant_TransactionType',
]

LANG_MAP = {
    'es': '001',
    'en': '002',
    'ca': '003',
    'fr': '004',
    'de': '005',
    'nl': '006',
    'it': '007',
    'sv': '008',
    'pt': '009',
    'pl': '011',
    'gl': '012',
    'eu' : '013',
    'da': '208',
}

class Client(object):
    """Client"""

    def __init__(self, business_code, priv_key, sandbox=False):
        # init params
        for param in DATA:
            setattr(self, param, None)
        self.Ds_Merchant_MerchantCode = business_code
        self.priv_key = priv_key
        if sandbox:
            self.redsys_url = 'https://sis-t.redsys.es:25443/sis/realizarPago'
        else:
            self.redsys_url = 'https://sis.redsys.es/sis/realizarPago'

    def get_pay_form_data(self, transaction_params):
        """Pay call"""
        for param in transaction_params:
            if param not in DATA:
                raise ValueError(u"The received parameter %s is not allowed."
                                 % param)
            setattr(self, param, transaction_params[param])
        if not transaction_params.get('Ds_Merchant_MerchantData'):
            self.Ds_Merchant_MerchantData = None
        if not transaction_params.get('Ds_Merchant_DateFrecuency'):
            self.Ds_Merchant_DateFrecuency = None
        if not transaction_params.get('Ds_Merchant_ChargeExpiryDate'):
            self.Ds_Merchant_ChargeExpiryDate = None
        if not transaction_params.get('Ds_Merchant_AuthorisationCode'):
            self.Ds_Merchant_AuthorisationCode = None
        if not transaction_params.get('Ds_Merchant_TransactionDate'):
            self.Ds_Merchant_TransactionDate = None

        signature = (str(int(self.Ds_Merchant_Amount * 100)) +
                     str(self.Ds_Merchant_Order) +
                     str(self.Ds_Merchant_MerchantCode) +
                     str(self.Ds_Merchant_Currency or '978') +
                     str(self.Ds_Merchant_TransactionType) +
                     str(self.Ds_Merchant_MerchantURL) +
                     str(self.priv_key))
        self.Ds_Merchant_MerchantSignature = \
            hashlib.sha1(signature).hexdigest().upper()

        data = {
            'Ds_Redsys_Url': self.redsys_url,
            'Ds_Merchant_Amount': int(self.Ds_Merchant_Amount * 100),
            'Ds_Merchant_Currency': self.Ds_Merchant_Currency or 978, # EUR
            'Ds_Merchant_Order': self.Ds_Merchant_Order[:12],
            'Ds_Merchant_ProductDescription':
                self.Ds_Merchant_ProductDescription[:125],
            'Ds_Merchant_Titular': self.Ds_Merchant_Titular[:60],
            'Ds_Merchant_MerchantCode': self.Ds_Merchant_MerchantCode[:9],
            'Ds_Merchant_MerchantURL': self.Ds_Merchant_MerchantURL[:250],
            'Ds_Merchant_UrlOK': self.Ds_Merchant_UrlOK[:250],
            'Ds_Merchant_UrlKO': self.Ds_Merchant_UrlKO[:250],
            'Ds_Merchant_MerchantName': self.Ds_Merchant_MerchantName[:25],
            'Ds_Merchant_ConsumerLanguage': LANG_MAP.get(self.Ds_Merchant_ConsumerLanguage, '001'),
            'Ds_Merchant_MerchantSignature': self.Ds_Merchant_MerchantSignature,
            'Ds_Merchant_Terminal': self.Ds_Merchant_Terminal or '1',
            'Ds_Merchant_SumTotal': int(self.Ds_Merchant_SumTotal * 100),
            'Ds_Merchant_TransactionType': self.Ds_Merchant_TransactionType \
                or '0',
            'Ds_Merchant_MerchantData': self.Ds_Merchant_MerchantData,
            'Ds_Merchant_DateFrecuency': self.Ds_Merchant_DateFrecuency,
            'Ds_Merchant_ChargeExpiryDate':
                (self.Ds_Merchant_ChargeExpiryDate and
                 self.Ds_Merchant_ChargeExpiryDate[:10] or None),
            'Ds_Merchant_AuthorisationCode': self.Ds_Merchant_AuthorisationCode,
            'Ds_Merchant_TransactionDate': self.Ds_Merchant_TransactionDate,
        }
        return data
