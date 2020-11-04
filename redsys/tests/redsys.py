import unittest
from .redsys import Client


class TestRedsysClient(unittest.TestCase):

    def test_sample(self):
        SANDBOX = True
        REDSYS_MERCHANT_URL = 'http://www.zikzakmedia.com'
        REDSYS_MERCHANT_NAME = "Zikzakmedia SL"
        REDSYS_MERCHANT_CODE = '000000000'
        REDSYS_SECRET_KEY = 'sq7HjrUOBfKmC576ILgskD5srU870gJ7'
        REDSYS_TERMINAL = '1'
        REDSYS_CURRENCY = 978
        REDSYS_TRANS_TYPE = '0'

        values = {
            'DS_MERCHANT_AMOUNT': 10.0,
            'DS_MERCHANT_CURRENCY': REDSYS_CURRENCY,
            'DS_MERCHANT_ORDER': 'SO001',
            'DS_MERCHANT_PRODUCTDESCRIPTION': 'ZZSaas services',
            'DS_MERCHANT_TITULAR': REDSYS_MERCHANT_NAME,
            'DS_MERCHANT_MERCHANTCODE': REDSYS_MERCHANT_CODE,
            'DS_MERCHANT_MERCHANTURL': REDSYS_MERCHANT_URL,
            'DS_MERCHANT_URLOK': 'http://localhost:5000/redsys/confirm',
            'DS_MERCHANT_URLKO': 'http://localhost:5000/redsys/cancel',
            'DS_MERCHANT_MERCHANTNAME': REDSYS_MERCHANT_NAME,
            'DS_MERCHANT_TERMINAL': REDSYS_TERMINAL,
            'DS_MERCHANT_TRANSACTIONTYPE': REDSYS_TRANS_TYPE,
            }

        redsyspayment = Client(business_code=REDSYS_MERCHANT_CODE, secret_key=REDSYS_SECRET_KEY, sandbox=SANDBOX)
        redsys_data = redsyspayment.redsys_generate_request(values)

        signature = 'XiMqO66ytDZ8PeoGoiGjm57igv0I4Dr1PD7wXyJLSKE='
        self.assertEqual(redsys_data['Ds_Signature'], signature)

if __name__ == '__main__':
    unittest.main()
