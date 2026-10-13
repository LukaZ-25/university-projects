from entsoe import EntsoePandasClient
import pandas as pd

def dohvati_imbalance_vols():
    client = EntsoePandasClient(api_key="ENTSOE-TRANSPARENCY-API-KEY")

    start = pd.Timestamp('20250101', tz='Europe/Brussels')
    end = pd.Timestamp('20251101', tz='Europe/Brussels')
    country_code = 'HR'  # Belgium
    country_code_from = 'HR'  # France
    country_code_to = 'HR' # Germany-Luxembourg
    type_marketagreement_type = 'A01'
    contract_marketagreement_type = "A01"
    process_type = 'A51'

    # znaci, meni treba:
    # -imbalance volume (brojke)
    # -imbalance situation (deficit/surplus)
    # ovo vrati odmah u jednom: x>0 za surplus, x<0 za deficit

    df_training = client.query_imbalance_volumes(country_code, start=start, end=end, psr_type=None)
    start = pd.Timestamp('20251101', tz='Europe/Brussels')
    # end = pd.Timestamp('202511021200', tz='Europe/Brussels')
    end = pd.Timestamp('20251102', tz='Europe/Brussels')
    df_real = client.query_imbalance_volumes(country_code, start=start, end=end, psr_type=None)
    return df_training, df_real
