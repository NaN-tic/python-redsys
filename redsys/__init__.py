# -*- coding: utf-8 -*-

"""
    Redsys client classes
    ~~~~~~~~~~~~~~~~~~~~~~

    Basic client for the Redsys credit card paying services.

"""

import re
import hashlib
import json
import base64
import hmac
from Crypto.Cipher import DES3

DATA = [
    'DS_MERCHANT_AMOUNT',
    'DS_MERCHANT_CURRENCY',
    'DS_MERCHANT_ORDER',
    'DS_MERCHANT_PRODUCTDESCRIPTION',
    'DS_MERCHANT_TITULAR',
    'DS_MERCHANT_MERCHANTCODE',
    'DS_MERCHANT_MERCHANTURL',
    'DS_MERCHANT_URLOK',
    'DS_MERCHANT_URLKO',
    'DS_MERCHANT_MERCHANTNAME',
    'DS_MERCHANT_CONSUMERLANGUAGE',
    'DS_MERCHANT_MERCHANTSIGNATURE',
    'DS_MERCHANT_TERMINAL',
    'DS_MERCHANT_TRANSACTIONTYPE',
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
    'eu': '013',
    'da': '208',
    }

ALPHANUMERIC_CHARACTERS = re.compile(b'[^a-zA-Z0-9]')

class Client(object):
    """Client"""

    def __init__(self, business_code, secret_key, sandbox=False):
        # init params
        for param in DATA:
            setattr(self, param, None)
        self.Ds_Merchant_MerchantCode = business_code
        self.secret_key = secret_key
        if sandbox:
            self.redsys_url = 'https://sis-t.redsys.es:25443/sis/realizarPago'
        else:
            self.redsys_url = 'https://sis.redsys.es/sis/realizarPago'

    @staticmethod
    def decode_parameters(merchant_parameters):
        """
        Given the Ds_MerchantParameters from Redsys, decode it and eval the
        json file

        :param merchant_parameters: Base 64 encoded json structure returned by
               Redsys
        :return merchant_parameters: Json structure with all parameters
        """
        assert isinstance(merchant_parameters, str)
        return json.loads(base64.b64decode(merchant_parameters).decode())

    def encrypt_order_with_3DES(self, order):
        """
        This method creates a unique key for every request, based on the
        Ds_Merchant_Order and in the shared secret (SERMEPA_SECRET_KEY).
        This unique key is Triple DES ciphered.

        :param Ds_Merchant_Order: Dict with all merchant parameters
        :return  order_encrypted: The encrypted order
        """
        assert isinstance(order, str)
        cipher = DES3.new(base64.b64decode(self.secret_key),
            DES3.MODE_CBC, IV=b'\0\0\0\0\0\0\0\0')
        return cipher.encrypt(order.encode().ljust(16, b'\0'))

    @staticmethod
    def sign_hmac256(encrypted_order, merchant_parameters):
        """
        Use the encrypted_order we have to sign the merchant data using
        a HMAC SHA256 algorithm and encode the result using Base64.

        :param encrypted_order: Encrypted Ds_Merchant_Order
        :param merchant_parameters: Redsys already encoded parameters
        :return Generated signature as a base64 encoded string
        """
        assert isinstance(encrypted_order, bytes)
        assert isinstance(merchant_parameters, bytes)
        digest = hmac.new(encrypted_order, merchant_parameters,
            hashlib.sha256).digest()
        return base64.b64encode(digest)

    def redsys_generate_request(self, params):
        """
        Method to generate Redsys Ds_MerchantParameters and Ds_Signature

        :param params: Dict with all transaction parameters
        :return dict url, signature, parameters and type signature
        """
        merchant_parameters = {
            'DS_MERCHANT_AMOUNT': int(params['DS_MERCHANT_AMOUNT'] * 100),
            'DS_MERCHANT_ORDER': params['DS_MERCHANT_ORDER'].zfill(10),
            'DS_MERCHANT_MERCHANTCODE': params['DS_MERCHANT_MERCHANTCODE'][:9],
            'DS_MERCHANT_CURRENCY': params['DS_MERCHANT_CURRENCY'] or 978, # EUR
            'DS_MERCHANT_TRANSACTIONTYPE': (
                params['DS_MERCHANT_TRANSACTIONTYPE'] or '0'),
            'DS_MERCHANT_TERMINAL': params['DS_MERCHANT_TERMINAL'] or '1',
            'DS_MERCHANT_URLOK': params['DS_MERCHANT_URLOK'][:250],
            'DS_MERCHANT_URLKO': params['DS_MERCHANT_URLKO'][:250],
            'DS_MERCHANT_MERCHANTURL': params['DS_MERCHANT_MERCHANTURL'][:250],
            'DS_MERCHANT_PRODUCTDESCRIPTION': (
                    params['DS_MERCHANT_PRODUCTDESCRIPTION'][:125]),
            'DS_MERCHANT_TITULAR': params['DS_MERCHANT_TITULAR'][:60],
            'DS_MERCHANT_MERCHANTNAME': params['DS_MERCHANT_MERCHANTNAME'][:25],
            'DS_MERCHANT_CONSUMERLANGUAGE': LANG_MAP.get(
                params.get('DS_MERCHANT_CONSUMERLANGUAGE'), '001'),
            }

        # Encode merchant_parameters in json + base64
        b64_params = base64.b64encode(json.dumps(merchant_parameters).encode())
        # Encrypt order
        encrypted_order = self.encrypt_order_with_3DES(
            merchant_parameters['DS_MERCHANT_ORDER'])
        # Sign parameters
        signature = self.sign_hmac256(encrypted_order, b64_params).decode()
        return {
            'Ds_Redsys_Url': self.redsys_url,
            'Ds_SignatureVersion': 'HMAC_SHA256_V1',
            'Ds_MerchantParameters': b64_params.decode(),
            'Ds_Signature': signature,
            }

    def redsys_check_response(self, signature, b64_merchant_parameters):
        """
        Method to check received Ds_Signature with the one we extract from
        Ds_MerchantParameters data.
        We remove non alphanumeric characters before doing the comparison

        :param signature: Received signature
        :param b64_merchant_parameters: Received parameters
        :return: True if signature is confirmed, False if not
        """
        merchant_parameters = json.loads(base64.b64decode(
                b64_merchant_parameters).decode())

        order = merchant_parameters['Ds_Order']
        encrypted_order = self.encrypt_order_with_3DES(order)
        computed_signature = self.sign_hmac256(encrypted_order,
            merchant_parameters)

        safe_signature = re.sub(ALPHANUMERIC_CHARACTERS, b'', signature)
        safe_computed_signature = re.sub(ALPHANUMERIC_CHARACTERS, b'',
            computed_signature)
        return safe_signature == safe_computed_signature
