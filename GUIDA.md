# Podcast privato su GitHub Pages — guida passo a passo

Obiettivo: i tuoi dieci episodi audio online, ascoltabili dal telefono in streaming o offline,
con la **posizione salvata per episodio** e la velocità di riproduzione regolabile.

Come funziona in tre righe: GitHub ospita gli MP3, un file XML (`feed.xml`) fa da indice,
l'app di podcast legge quell'indice e gestisce ascolto, download e segnalibro.

---

## Prima: genera gli audio

Su [NotebookLM](https://notebooklm.google.com): un notebook per capitolo, carica il `.txt`
corrispondente come fonte, genera l'**Audio Overview** e scaricalo.

Rinomina i file mantenendo la numerazione — è quella che determina l'ordine:

```
01_Nautische_Ausbildung.mp3
02_Seeschifffahrtsrecht.mp3
03_Schiffskunde.mp3
04_Navigationshilfen.mp3
05_Klassische_Navigation.mp3
06_Elektronische_Navigation.mp3
07_Gezeitenkunde.mp3
08_Meteorologie.mp3
09_Sicherheit_an_Bord.mp3
10_Schiffsfuehrung.mp3
```

> Se NotebookLM esporta in `.wav` o `.m4a`, converti in MP3 (più leggero e compatibile).
> Con ffmpeg: `ffmpeg -i input.wav -codec:a libmp3lame -b:a 96k -ac 1 output.mp3`
> A 96 kbps mono un episodio di 15 minuti pesa circa 10 MB.

---

## Passo 1 — Crea il repository

1. Su GitHub: **New repository**
2. Nome: `hochsee-podcast`
3. Visibilità: **Public**

> ⚠️ GitHub Pages sui piani gratuiti funziona solo con repo pubblici. Significa che chi
> conosce l'URL può accedere ai file: non sono indicizzati né trovabili, ma non sono
> segreti. Per materiale di studio in tedesco non è un problema. Se vuoi vera
> riservatezza servono GitHub Pro (repo privati) o un'alternativa tipo Cloudflare R2.

---

## Passo 2 — Carica i file

Struttura finale del repo:

```
hochsee-podcast/
├── audio/
│   ├── 01_Nautische_Ausbildung.mp3
│   ├── 02_Seeschifffahrtsrecht.mp3
│   └── ... (tutti e dieci)
├── cover.png
├── feed.xml
└── make_feed.py
```

Via interfaccia web: **Add file → Upload files**, trascina tutto.
Da riga di comando:

```bash
git clone https://github.com/TUOUSERNAME/hochsee-podcast.git
cd hochsee-podcast
mkdir audio
# copia gli MP3 in audio/, poi:
git add .
git commit -m "Aggiunge episodi Hochseeausweis"
git push
```

> Limiti GitHub: 100 MB per singolo file, ~1 GB per repo consigliato.
> Dieci episodi da 10 MB fanno 100 MB in totale: nessun problema.

---

## Passo 3 — Attiva GitHub Pages

Nel repo: **Settings → Pages**

- Source: **Deploy from a branch**
- Branch: `main`, cartella `/ (root)`
- **Save**

Dopo un minuto il sito è online su:

```
https://TUOUSERNAME.github.io/hochsee-podcast/
```

Verifica che un audio sia raggiungibile aprendo nel browser:

```
https://TUOUSERNAME.github.io/hochsee-podcast/audio/01_Nautische_Ausbildung.mp3
```

Se parte la riproduzione, sei a metà strada.

---

## Passo 4 — Genera il feed

Apri `make_feed.py` e modifica la riga:

```python
SITE_BASE = "https://TUOUSERNAME.github.io/hochsee-podcast"
```

mettendo il tuo username reale. Poi, nella cartella del repo:

```bash
python make_feed.py
```

Lo script legge la cartella `audio/`, calcola le dimensioni dei file, ricava i titoli dai
nomi e scrive `feed.xml`. Ti stampa anche l'elenco degli episodi e l'URL finale del feed.

Poi committa:

```bash
git add feed.xml
git commit -m "Aggiorna feed"
git push
```

---

## Passo 5 — Aggiungi il feed nell'app

L'URL del tuo feed è:

```
https://TUOUSERNAME.github.io/hochsee-podcast/feed.xml
```

**AntennaPod** (Android, gratis, open source)
→ Aggiungi podcast → *Aggiungi tramite URL RSS* → incolla → Sottoscrivi

**Pocket Casts** (piano gratuito basta)
→ Cerca → incolla l'URL del feed nella barra di ricerca → Sottoscrivi

**Apple Podcasts** (iOS)
→ Libreria → *Aggiungi programma via URL* → incolla

Fatto. Da questo momento hai posizione salvata per episodio, download offline,
velocità regolabile e ripresa esatta da dove hai lasciato.

---

## Aggiungere episodi in seguito

1. Metti il nuovo MP3 in `audio/`
2. Esegui di nuovo `python make_feed.py`
3. `git add . && git commit -m "nuovo episodio" && git push`
4. Nell'app: aggiorna il podcast (pull-to-refresh)

---

## Se qualcosa non funziona

**L'app dice che il feed non è valido**
→ Apri l'URL del feed nel browser: devi vedere XML. Se vedi 404, Pages non è ancora
attivo (attendi qualche minuto) o il branch/cartella in Settings → Pages è sbagliato.

**Il feed si carica ma gli episodi non partono**
→ Verifica che `SITE_BASE` nello script sia esatto, senza slash finale, e che l'URL
diretto di un MP3 funzioni nel browser. Gli URL sono sensibili a maiuscole/minuscole.

**Gli episodi sono in ordine sbagliato**
→ Nell'app cerca l'opzione di ordinamento e scegli *dal più vecchio*. Il feed usa già
`itunes:type = serial` con numeri di episodio, che la maggior parte delle app rispetta.

**Caratteri tedeschi strani nei titoli (ä, ö, ü)**
→ Evita umlaut nei *nomi dei file* (usa `Schiffsfuehrung`, non `Schiffsführung`).
Nei titoli visualizzati non ci sono problemi.

---

## Consigli d'uso per lo studio

- Ascolta a **1.2x–1.5x**: per il ripasso è comodissimo e le app lo ricordano.
- **Scarica tutto** prima di partire in treno — il WiFi di bordo non è affidabile.
- Metti in coda i due capitoli tosti (**05 Klassische Navigation** e **07 Gezeitenkunde**)
  con più frequenza degli altri: sono quelli che vogliono ripetizione.
- L'ascolto non sostituisce l'esercizio: per astronomia e maree servono calcoli su carta.
  Il podcast serve a tenere i concetti caldi tra una sessione e l'altra.
