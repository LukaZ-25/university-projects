# Analiza smjera i troškova odstupanja hrvatskog elektroenergetskog sustava

Završni rad na prijediplomskom studiju računarstva (FER). Cilj je predviđanje 
odstupanja (imbalance) u hrvatskom elektroenergetskom sustavu primjenom 
statističkog modeliranja vremenskih nizova, s usporedbom naspram naivnih 
osnovnih (baseline) modela.

## Podaci

Podaci o volumenu odstupanja (imbalance volume) za Hrvatsku dohvaćeni su 
putem **ENTSO-E Transparency Platform API**-ja (paket `entsoe-py`), za 
razdoblje siječanj–studeni 2025. Skup je podijeljen na trening (do 
31.10.2025, 7h) i test skup (1.11.2025, cijeli dan, u 15-minutnim 
intervalima).

## Metodologija

1. **Odabir značajnih lagova** — ACF i PACF analiza vremenskog niza (do 192 
   laga, odnosno 48h unatrag) radi identifikacije statistički značajnih 
   kašnjenja koja utječu na trenutnu vrijednost.
2. **VIF analiza** (Variance Inflation Factor) — uklanjanje kolinearnih 
   lag-varijabli (VIF ≥ 5) radi izbjegavanja multikolinearnosti u modelu.
3. **Linearna regresija** na filtriranim lag-značajkama, s rekurzivnim 
   predviđanjem unaprijed za cijeli sljedeći dan (96 intervala od 15 min).
4. **Usporedba s baseline modelima:**
   - naivna linearna regresija (samo prethodna vrijednost, $lag_1$)
   - naivno predviđanje "jučer u isto vrijeme" ($lag_{96}$)
   - naivno predviđanje "zadnja poznata vrijednost" ($lag_1$)

## Metrike evaluacije

Model je evaluiran pomoću: $R^2$, prilagođenog $R^2$ ($R_{adj}^2$) MAPE, 
sMAPE, te MASE (u odnosu na prethodnu vrijednost i na vrijednost od prije 
24h) — uz dodatnu metriku točnosti predviđanja **smjera** odstupanja 
(deficit/surplus), budući da je za procjenu troška odstupanja smjer često 
jednako bitan kao i točan iznos.  

## Napomene

Potrebne biblioteke: pandas, numpy, matplotlib, entsoe, sklearn, statsmodels

Potreban je vlastiti ENTSO-E API ključ (https://github.com/EnergieID/entsoe-py)  

## Struktura projekta

- [ml_model_imbalance](ml_model_imbalance) -> ACF/PACF, VIF, regresija, baseline modeli, evaluacija, grafički prikaz
- [entsoe_noviji.py](entsoe_noviji.py) -> dohvat podataka s ENTSO-E API-ja


## Dokumentacija

Cijeli završni rad, s detaljnim obrazložejem teorije, korištenih metoda i rezultata dostupan je u PDF obliku [zavrsni-rad.pdf](./zavrsni-rad.pdf).
