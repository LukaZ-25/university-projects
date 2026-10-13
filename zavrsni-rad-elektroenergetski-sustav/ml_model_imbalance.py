import entsoe_noviji
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.metrics import r2_score
from datetime import datetime, timedelta


df_training_og, df_real = entsoe_noviji.dohvati_imbalance_vols()
df_training = df_training_og.iloc[:-(48+4*5)]  # do 07h dana 2025-10-31


def linear_regression_1():
    """Ovdje je y=mx+b, x je prethodna vrijednost."""
    print("linear_regression_1")
    df = df_training.copy()
    df = df.to_frame(name='Imbalance Volume')

    MAX_LAG = 192
    for lag in range(1, MAX_LAG+1):
        df[f'lag{lag}'] = df['Imbalance Volume'].shift(lag)
    df = df.dropna()

    # acf, pacf actually vrijednosti
    acf_vals = acf(df['Imbalance Volume'], nlags=MAX_LAG)
    pacf_vals = pacf(df['Imbalance Volume'], nlags=MAX_LAG)
    # 0.12 i 0.5 izabrani tako da sam gledao graf i vidljiva lokalna i globalna odstupanja
    significant_acf_lags = [lag for lag, val in enumerate(acf_vals) if abs(val) > 0.12 and lag != 0]
    significant_pacf_lags = [lag for lag, val in enumerate(pacf_vals) if abs(val) > 0.05 and lag != 0]
    candidate_lags = sorted(set(significant_acf_lags + significant_pacf_lags))

    # vif - uklanja kolinearne
    X = df[[f'lag{lag}' for lag in candidate_lags]]
    vif_data = []
    for i in range(X.shape[1]):
        vif_data.append(variance_inflation_factor(X.values, i))
    filtrirani_lags = [lag for lag, vif in zip(candidate_lags, vif_data) if vif < 5]

    X = df[[f'lag{lag}' for lag in filtrirani_lags]]
    Y = df[['Imbalance Volume']]

    model = LinearRegression()
    model.fit(X, Y)

    # ovo ide priprema za treniranje samog modela
    Y_pred = model.predict(X)

    # statistika za model
    y_true = Y.values.flatten()
    y_predv = Y_pred.flatten()

    ispis_model(y_true, y_predv)

    r2 = r2_score(Y, Y_pred)
    n = len(Y)
    p = X.shape[1]
    r2_adj = 1 - (1 - r2) * (n - 1) / (n - p - 1)
    print("R2 =", r2)
    print("Radj2 =", r2_adj)

    # sad racunamo za 2025-11-01 cijeli dan imbalance, imamo data za do 2025-10-31-7:00h
    lagovi = sorted(int(col.replace("lag", "")) for col in X.columns)
    koeficijenti = model.coef_[0]
    intercept = model.intercept_[0]
    print("Model coefs: ", koeficijenti)
    print("lagovi: ", lagovi)

    # prave_vrijednosti = y_true[-192:]
    moja_predvidanja = []

    for i in range(1, 2):  # model 1
        lagi = [69, 73, 89, 92, 93, 95, 97, 100, 189, 192]
        koefci = koeficijenti[10:]
        y_racunat = intercept
        for lag, koef in zip(lagi, koefci):
            lag -= i - 1
            y_racunat += koef * y_true[-(lag - 68)]  # ide -68 kako bih uklonio prazninu dana
        moja_predvidanja.append(y_racunat)

    for i in range(2, 6):  # model 2-5
        lagi = [73, 89, 92, 93, 95, 97, 100, 189, 192]
        koefci = koeficijenti[11:]
        y_racunat = intercept
        for lag, koef in zip(lagi, koefci):
            lag -= i - 1
            y_racunat += koef * y_true[-(lag - 68)]
        moja_predvidanja.append(y_racunat)

    for i in range(6, 22):  # model 6-21
        lagi = [89, 92, 93, 95, 97, 100, 189, 192]
        koefci = koeficijenti[12:]
        y_racunat = intercept
        for lag, koef in zip(lagi, koefci):
            lag -= i - 1
            y_racunat += koef * y_true[-(lag - 68)]
        moja_predvidanja.append(y_racunat)

    for i in range(22, 25):  # model 22-24
        lagi = [92, 93, 95, 97, 100, 189, 192]
        koefci = koeficijenti[13:]
        y_racunat = intercept
        for lag, koef in zip(lagi, koefci):
            lag -= i - 1
            y_racunat += koef * y_true[-(lag - 68)]
        moja_predvidanja.append(y_racunat)

    for i in range(25, 26):  # model 25
        lagi = [93, 95, 97, 100, 189, 192]
        koefci = koeficijenti[14:]
        y_racunat = intercept
        for lag, koef in zip(lagi, koefci):
            lag -= i - 1
            y_racunat += koef * y_true[-(lag - 68)]
        moja_predvidanja.append(y_racunat)

    for i in range(26, 28):  # model 26-27
        lagi = [95, 97, 100, 189, 192]
        koefci = koeficijenti[15:]
        y_racunat = intercept
        for lag, koef in zip(lagi, koefci):
            lag -= i - 1
            y_racunat += koef * y_true[-(lag - 68)]
        moja_predvidanja.append(y_racunat)

    for i in range(28, 30):  # model 28-29
        lagi = [97, 100, 189, 192]
        koefci = koeficijenti[16:]
        y_racunat = intercept
        for lag, koef in zip(lagi, koefci):
            lag -= i - 1
            y_racunat += koef * y_true[-(lag - 68)]
        moja_predvidanja.append(y_racunat)

    for i in range(30, 33):  # model 30-32
        lagi = [100, 189, 192]
        koefci = koeficijenti[17:]
        y_racunat = intercept
        for lag, koef in zip(lagi, koefci):
            lag -= i - 1
            y_racunat += koef * y_true[-(lag - 68)]
        moja_predvidanja.append(y_racunat)

    for i in range(33, 97):  # model 33-96
        lagi = [189, 192]
        koefci = koeficijenti[18:]
        y_racunat = intercept
        for lag, koef in zip(lagi, koefci):
            lag -= i - 1
            y_racunat += koef * y_true[-(lag - 68)]
        moja_predvidanja.append(y_racunat)

    print("Moja predvidanja: ", len(moja_predvidanja))
    print(moja_predvidanja)

    # pretvaram moja predvidanja u pozitivno ili negativno odstupanje (ili uravnotezeno)
    moja_predv_plus_min = np.sign(moja_predvidanja)
    real_imbal_plus_min = np.sign(df_real.values)
    tocni = np.sum(moja_predv_plus_min == real_imbal_plus_min)
    print(f"Udio tocnih za razdoblje 2025-11-01-00-00-00 do 2025-11-01-23-45-00: {tocni / len(moja_predv_plus_min)}")

    r2 = r2_score(df_real.values, moja_predvidanja)
    n = len(Y)
    p = X.shape[1]
    r2_adj = 1 - (1 - r2) * (n - 1) / (n - p - 1)
    print("R2 =", r2)
    print("Radj2 =", r2_adj)

    ispis_model(df_real.values, moja_predvidanja)
    y_pred = np.array(moja_predvidanja)
    y_real = np.array(df_real.values)

    # x-os: brojevi od 1 do 96
    x = np.arange(1, len(y_pred) + 1)

    plt.figure(figsize=(12, 6))

    # crtanje tocaka
    plt.scatter(x, y_real, color='blue', label='Stvarne vrijednosti', s=40)
    plt.scatter(x, y_pred, color='red', label='Predviđene vrijednosti', s=40)

    plt.xlabel('Intervali: 1–96')
    plt.ylabel('Odstupanje')
    plt.title('Predviđena i stvarna odstupanja')
    plt.legend()
    plt.grid(True)

    plt.show()


def linear_regression_baseline():
    """Ovdje je y=mx+b, x je prethodna vrijednost"""
    print("linear_regression_baseline")
    df = df_training.copy()
    df = df.to_frame(name='Imbalance Volume')

    # on uci iz prosle vrijednosti
    df['lag1'] = df['Imbalance Volume'].shift(1)
    df = df.dropna()
    X = df[['lag1']]
    Y = df['Imbalance Volume']

    model = LinearRegression()
    model.fit(X, Y)

    Y_pred = model.predict(X)

    # statistika za model
    y_true = Y.values.flatten()
    y_predv = Y_pred.flatten()

    ispis_model(y_true, y_predv)

    r2 = r2_score(Y, Y_pred)
    print("R2 =", r2)

    b1 = model.coef_[0]
    b0 = model.intercept_
    print("b0 =", b0)
    print("b1 =", b1)

    return


def naivni_proslost(koliko_odstupa):
    """naivni model koji predviđa istu vrijednost za interval kao vrijednost koja se pojavila
    u istom intervalu jučer; u prethodnom intervalu;
    koliko_odstupa: 96 je jučer isto doba, 1 je prethodni interval"""
    df = df_training.copy()
    df = df.to_frame(name='Imbalance Volume')
    df["pred"] = df["Imbalance Volume"].shift(koliko_odstupa)
    df = df.dropna()

    y_true = df["Imbalance Volume"].values
    y_pred = df["pred"].values

    ispis_model(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    print("R2 =", r2)
    # Radj2 ovdje nema smisla, jedan je input
    return


def ispis_model(y_true, y_predv):
    print("Statistika za imbalance (predvidene vrijednosti)")
    print("Mean:", np.mean(y_predv))
    print("Std:", np.std(y_predv))
    print("Median:", np.median(y_predv))
    print("Min:", np.min(y_predv))
    print("Max:", np.max(y_predv))

    mae = mean_absolute_error(y_true, y_predv)
    rmse = (mean_squared_error(y_true, y_predv)) ** 0.5
    mape_values = []
    smape_values = []
    for yt, yp in zip(y_true, y_predv):
        if yt != 0:
            mape_values.append(abs((yt - yp) / yt))
        if abs(yt) + abs(yp) > 0:
            smape_values.append(abs(yt - yp) / (abs(yt) + abs(yp)))
    mape = np.mean(mape_values) * 100
    smape = np.mean(smape_values) * 2
    # racunanje mase
    mase1 = [abs(y_true[i] - y_predv[i]) for i in range(1, len(y_true))]
    mase1 = np.mean(mase1)
    mase1_denom = [abs(y_true[i] - y_true[i-1]) for i in range(1, len(y_true))]
    mase1_denom = np.mean(mase1_denom)
    mase1 = mase1 / mase1_denom

    mase96 = [abs(y_true[i] - y_predv[i-96]) for i in range(96, len(y_true))]
    mase96 = np.mean(mase96)
    mase96_denom = [abs(y_true[i] - y_true[i-96]) for i in range(96, len(y_true))]
    mase96_denom = np.mean(mase96_denom)
    mase96 = mase96 / mase96_denom

    print("MAE =", mae)
    print("RMSE =", rmse)
    print("MAPE =", mape)
    print("sMAPE =", smape)
    print("MASE_1 =", mase1)
    print("MASE_96 =", mase96)
    return


def ispis_dataset(podaci):
    vrijednosti = podaci.tolist()
    print("Mean:", np.mean(vrijednosti))
    print("Std:", np.std(vrijednosti))
    print("Median:", np.median(vrijednosti))
    print("Min:", np.min(vrijednosti))
    print("Max:", np.max(vrijednosti))
    return


# ispisivanje metrika za podatke: sve, trening, test
print("Statisticki pokazatelji za podatke: trening")
ispis_dataset(df_training)  # trening
print("Statisticki pokazatelji za podatke: test")
ispis_dataset(df_real)  # test
print("Statisticki pokazatelji za podatke: sve")
df_combined = pd.concat([df_training, df_real])
ispis_dataset(df_combined)  # sve

linear_regression_baseline()
print("naivni_jucer")
naivni_proslost(96)
print("naivni_zadnji")
naivni_proslost(1)
print("napredna_linearna_regresija")
linear_regression_1()
