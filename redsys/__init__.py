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
import ast
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

    def encode_parameters(self, merchant_parameters):
        """
        Create a json object, codify it in base64 and delete their carrier returns

        :param merchant_parameters: Dict with all merchant parameters
        :return Ds_MerchantParameters: Encoded json structure with all parameters
        """
        parameters = (json.dumps(merchant_parameters)).encode()
        return ''.join(unicode(base64.encodestring(parameters), 'utf-8').splitlines())

    def decode_parameters(self, Ds_MerchantParameters):
        """
        Given the Ds_MerchantParameters from Redsys, decode it and eval the json file

        :param Ds_MerchantParameters: Encoded json structure returned from Redsys
        :return merchant_parameters: Json structure with all parameters 
        """

        Ds_MerchantParameters_decoded = base64.standard_b64decode(Ds_MerchantParameters)
        return ast.literal_eval(Ds_MerchantParameters_decoded)

    def encrypt_order_with_3DES(self, Ds_Merchant_Order):
        """
        This method creates a unique key for every request, based on the Ds_Merchant_Order
        and in the shared secret (SERMEPA_SECRET_KEY).
        This unique key is Triple DES ciphered.

        :param Ds_Merchant_Order: Dict with all merchant parameters
        :return  order_encrypted: The encrypted order
        """
        pycrypto = DES3.new(base64.standard_b64decode(self.secret_key), DES3.MODE_CBC, IV=b'\0\0\0\0\0\0\0\0')
        order_padded = Ds_Merchant_Order.ljust(16, b'\0')
        return pycrypto.encrypt(order_padded)

    def sign_hmac256(self, order_encrypted, Ds_MerchantParameters):
        """
        Use the order_encrypted we have to sign the merchant data using
        a HMAC SHA256 algorithm  and encode the result using Base64

        :param order_encrypted: Encrypted Ds_Merchant_Order
        :param Ds_MerchantParameters: Redsys aleready encoded parameters
        :return Ds_Signature: Generated signature encoded in base64
        """
        hmac_value = hmac.new(order_encrypted, Ds_MerchantParameters, hashlib.sha256).digest()
        return base64.b64encode(hmac_value)

    def redsys_generate_request(self, transaction_params):
        """
        Method to generate Redsys Ds_MerchantParameters and Ds_Signature

        :param transaction_params: Dict with all transaction parameters
        :return dict url, signature, parameters and type signature
        """
        for param in transaction_params:
            if param not in DATA:
                raise ValueError(u"The received parameter %s is not allowed."
                                 % param)
            setattr(self, param, transaction_params[param])
        if not transaction_params.get('DS_MERCHANT_MERCHANTDATA'):
            self.DS_MERCHANT_MERCHANTDATA = None
        if not transaction_params.get('DS_MERCHANT_DATEFRECUENCY'):
            self.DS_MERCHANT_DATEFRECUENCY = None
        if not transaction_params.get('DS_MERCHANT_CHARGEEXPIRYDATE'):
            self.DS_MERCHANT_CHARGEEXPIRYDATE = None
        if not transaction_params.get('DS_MERCHANT_AUTHORISATIONCODE'):
            self.DS_MERCHANT_AUTHORISATIONCODE = None
        if not transaction_params.get('DS_MERCHANT_TRANSACTIONDATE'):
            self.DS_MERCHANT_TRANSACTIONDATE = None

        merchant_parameters = {
            'DS_MERCHANT_AMOUNT': int(self.DS_MERCHANT_AMOUNT * 100),
            'DS_MERCHANT_ORDER': self.DS_MERCHANT_ORDER.zfill(10),
            'DS_MERCHANT_MERCHANTCODE': self.DS_MERCHANT_MERCHANTCODE[:9],
            'DS_MERCHANT_CURRENCY': self.DS_MERCHANT_CURRENCY or 978, # EUR
            'DS_MERCHANT_TRANSACTIONTYPE': self.DS_MERCHANT_TRANSACTIONTYPE \
                    or '0',
            'DS_MERCHANT_TERMINAL': self.DS_MERCHANT_TERMINAL or '1',
            'DS_MERCHANT_URLOK': self.DS_MERCHANT_URLOK[:250],
            'DS_MERCHANT_URLKO': self.DS_MERCHANT_URLKO[:250],
            'DS_MERCHANT_MERCHANTURL': self.DS_MERCHANT_MERCHANTURL[:250],
            'DS_MERCHANT_PRODUCTDESCRIPTION':
                    self.DS_MERCHANT_PRODUCTDESCRIPTION[:125],
            'DS_MERCHANT_TITULAR': self.DS_MERCHANT_TITULAR[:60],
            'DS_MERCHANT_MERCHANTNAME': self.DS_MERCHANT_MERCHANTNAME[:25],
            'DS_MERCHANT_CONSUMERLANGUAGE': LANG_MAP.get(self.DS_MERCHANT_CONSUMERLANGUAGE, '001'),
            }

        Ds_MerchantParameters = self.encode_parameters(merchant_parameters)
        order_encrypted = self.encrypt_order_with_3DES(merchant_parameters['DS_MERCHANT_ORDER'])
        Ds_Signature = self.sign_hmac256(order_encrypted, Ds_MerchantParameters)

        return {
            'Ds_Redsys_Url': self.redsys_url,
            'Ds_SignatureVersion': 'HMAC_SHA256_V1',
            'Ds_MerchantParameters': Ds_MerchantParameters,
            'Ds_Signature': Ds_Signature,
            }

    def redsys_check_response(self, Ds_Signature, Ds_MerchantParameters):
        """
        Method to check received Ds_Signature with the one we extract from Ds_MerchantParameters data.
        We remove non alphanumeric characters before doing the comparison

        :param Ds_Signature: Received signature
        :param Ds_MerchantParameters: Received parameters
        :return: True if signature is confirmed, False if not 
        """
        merchant_parameters = self.decode_parameters(Ds_MerchantParameters)
        order = merchant_parameters['Ds_Order']
        order_encrypted = self.encrypt_order_with_3DES(order)
        Ds_Signature_calculated = self.sign_hmac256(order_encrypted, Ds_MerchantParameters)

        alphanumeric_characters = re.compile('[^a-zA-Z0-9]')
        Ds_Signature_safe = re.sub(alphanumeric_characters, '', Ds_Signature)
        Ds_Signature_calculated_safe = re.sub(alphanumeric_characters, '', Ds_Signature_calculated)
        if Ds_Signature_safe  == Ds_Signature_calculated_safe:
            return True
        else:
            return False
