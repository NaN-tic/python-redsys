import unittest
from redsys import Client


class TestRedsysClient(unittest.TestCase):

    def test_sample(self):
        SANDBOX = True
        REDSYS_MERCHANT_URL = 'http://www.zikzakmedia.com'
        REDSYS_MERCHANT_NAME = "Zikzakmedia SL"
        REDSYS_MERCHANT_CODE = '000000000'
        REDSYS_SECRET_KEY = '123456'
        REDSYS_TERMINAL = 1
        REDSYS_CURRENCY = 978
        REDSYS_TRANS_TYPE = 0

        values = {
            'Ds_Merchant_Amount': 10.0,
            'Ds_Merchant_Currency': 978,
            'Ds_Merchant_Order': 'SO001',
            'Ds_Merchant_ProductDescription': 'ZZSaas services',
            'Ds_Merchant_Titular': REDSYS_MERCHANT_NAME,
            'Ds_Merchant_MerchantCode': REDSYS_MERCHANT_CODE,
            'Ds_Merchant_MerchantURL': REDSYS_MERCHANT_URL,
            'Ds_Merchant_UrlOK': 'http://www.zzsaas.com/redsys/confirm',
            'Ds_Merchant_UrlKO': 'http://www.zzsaas.com/redsys/cancel',
            'Ds_Merchant_MerchantName': REDSYS_MERCHANT_NAME,
            'Ds_Merchant_Terminal': REDSYS_TERMINAL,
            'Ds_Merchant_SumTotal': 10.0,
            'Ds_Merchant_TransactionType': REDSYS_TRANS_TYPE,
        }

        redsyspayment = Client(business_code=REDSYS_MERCHANT_CODE, priv_key=REDSYS_SECRET_KEY, sandbox=SANDBOX)
        redsys_data = redsyspayment.get_pay_form_data(values)

        signature = '8A20806C19A5C1D4E25CF26A24F19265CD32F9DE'
        self.assertEqual(redsys_data['Ds_Merchant_MerchantSignature'], signature)

if __name__ == '__main__':
    unittest.main()
