# Optimalno ulaganje u baterije

Desktop GUI aplikacija koja procjenjuje isplativost ulaganja u baterijski sustav za poduzeće, na temelju stvarne godišnje potrošnje električne energije dotičnog poduzeća. Aplikacija simulira optimalan rad baterije (punjenje/pražnjenje) kroz svaki sat u godini te izračunava ostvarenu novčanu uštedu u odnosu na rad bez baterije.

Grafički prikaz rada aplikacije [image.png](image.png)

## Kako radi

1. Korisnik učitava Excel datoteku sa satnom potrošnjom energije kroz 
   godinu (8760 vrijednosti) te unosi parametre: veličinu baterije, 
   dnevnu i noćnu tarifu, i cijenu za vršno mjesečno opterećenje (Peak 
   Monthly Load).
2. Podaci se šalju matematičkom modelu baterije izgrađenom u **Pyomo** 
   okviru, koji se rješava pomoću **HiGHS** solvera.
3. Model optimizira raspored punjenja/pražnjenja baterije za svaki sat 
   u godini tako da minimizira ukupni trošak energije (uključujući i 
   trošak vršnog opterećenja), uz poštivanje fizikalnih ograničenja 
   baterije (kapacitet, SOC granice, učinkovitost punjenja/pražnjenja).
4. Rezultati (nova cijena, originalna cijena, ušteda) prikazuju se u 
   aplikaciji, a profil punjenja/pražnjenja baterije prikazan je grafički 
   po satima za dan koji korisnik odabire.

## Matematički model

Model minimizira zbroj:
- troška energije po satu (umnožak satne tarife i potrošnje, uz korekciju za 
  punjenje/pražnjenje baterije i njihove gubitke pri konverziji),
- troška vršnog mjesečnog opterećenja,

uz ograničenja na:
- stanje napunjenosti baterije (State of Charge) unutar dopuštenih 
  granica (15%–95% kapaciteta),
- maksimalnu snagu punjenja/pražnjenja ograničenu veličinom baterije,
- kontinuitet stanja napunjenosti između uzastopnih sati.

**Potrebne biblioteke:** PyQt5, pandas, matplotlib, pyomo

Zasebno je instaliran HiGHS optimizator koji se koristi putem pyomo biblioteke.

## Format ulazne Excel datoteke

Datoteka treba sadržavati satnu potrošnju energije (kWh) kroz jednu 
godinu, u drugom stupcu, počevši od drugog retka (prvi red zaglavlje).

## Struktura projekta


- main.py -> PyQt5 sučelje i glavna logika aplikacije
- calculations_highs.py -> Pyomo model i optimizacija (HiGHS)


## Napomene

- Projekt je izrađen u sklopu kolegija Projekt R, prijediplomski 
  studij računarstva, FER, 2025/2026.
