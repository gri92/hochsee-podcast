#!/usr/bin/env python3
"""
Generatore di feed RSS per podcast privato su GitHub Pages.

USO:
  1. Metti i file MP3 nella cartella ./audio/
     Nomina i file cosi':  01_Nautische_Ausbildung.mp3, 02_Seeschifffahrtsrecht.mp3, ...
  2. Modifica le 5 righe di CONFIG qui sotto (soprattutto SITE_BASE)
  3. Esegui:  python make_feed.py
  4. Il file feed.xml viene creato/aggiornato. Commit + push su GitHub.

Nessuna dipendenza esterna: funziona con qualsiasi Python 3 su Windows, Mac o Linux.
"""

import os
import re
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

# ============================================================
# CONFIG — modifica queste righe
# ============================================================

# L'indirizzo base del tuo GitHub Pages, SENZA slash finale.
# Formato: https://<tuo-username>.github.io/<nome-repo>
SITE_BASE = "https://TUOUSERNAME.github.io/hochsee-podcast"

TITLE       = "Hochseeausweis — Lernpodcast"
AUTHOR      = "Giona Rinaldi"
DESCRIPTION = ("Vertiefte Einfuehrung in die zehn Kapitel der SYA-Ausbildung "
               "fuer den Schweizerischen Hochseeausweis. Persoenlicher Lernpodcast.")
LANGUAGE    = "de-CH"

AUDIO_DIR   = "audio"          # cartella con gli MP3
OUTPUT      = "feed.xml"       # file da generare
COVER       = "cover.png"      # copertina (opzionale, lascia "" se non ce l'hai)

# Data del primo episodio. Gli episodi successivi ricevono date crescenti,
# cosi' l'app li ordina correttamente dal capitolo 1 al 10.
START_DATE  = datetime(2026, 7, 28, 8, 0, tzinfo=timezone.utc)

# ============================================================
# Da qui in giu' non serve modificare nulla
# ============================================================

MIME = {
    ".mp3":  "audio/mpeg",
    ".m4a":  "audio/mp4",
    ".mp4":  "audio/mp4",
    ".wav":  "audio/wav",
    ".ogg":  "audio/ogg",
}


def pretty_title(filename: str) -> tuple[int, str]:
    """Da '05_Klassische_Navigation.mp3' ricava (5, 'Kapitel 5 — Klassische Navigation')."""
    stem = os.path.splitext(filename)[0]
    match = re.match(r"^(\d+)[_\-\s]*(.*)$", stem)
    if match:
        number = int(match.group(1))
        rest = match.group(2).replace("_", " ").replace("-", " ").strip()
        if rest:
            return number, f"Kapitel {number} \u2014 {rest}"
        return number, f"Kapitel {number}"
    return 0, stem.replace("_", " ")


def collect_episodes() -> list[dict]:
    if not os.path.isdir(AUDIO_DIR):
        raise SystemExit(f"ERRORE: la cartella '{AUDIO_DIR}' non esiste. Creala e mettici gli MP3.")

    files = [f for f in os.listdir(AUDIO_DIR)
             if os.path.splitext(f)[1].lower() in MIME]
    if not files:
        raise SystemExit(f"ERRORE: nessun file audio trovato in '{AUDIO_DIR}'.")

    files.sort()  # ordine alfabetico = ordine numerico grazie ai prefissi 01, 02, ...

    episodes = []
    for index, filename in enumerate(files):
        path = os.path.join(AUDIO_DIR, filename)
        number, title = pretty_title(filename)
        episodes.append({
            "number":   number if number else index + 1,
            "title":    title,
            "filename": filename,
            "size":     os.path.getsize(path),
            "mime":     MIME[os.path.splitext(filename)[1].lower()],
            "pubdate":  START_DATE + timedelta(days=index),
        })
    return episodes


def build_feed(episodes: list[dict]) -> str:
    now = format_datetime(datetime.now(timezone.utc))
    cover_url = f"{SITE_BASE}/{COVER}" if COVER else ""

    lines = []
    add = lines.append

    add('<?xml version="1.0" encoding="UTF-8"?>')
    add('<rss version="2.0"')
    add('     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"')
    add('     xmlns:content="http://purl.org/rss/1.0/modules/content/">')
    add('  <channel>')
    add(f'    <title>{escape(TITLE)}</title>')
    add(f'    <link>{escape(SITE_BASE)}</link>')
    add(f'    <language>{escape(LANGUAGE)}</language>')
    add(f'    <description>{escape(DESCRIPTION)}</description>')
    add(f'    <itunes:author>{escape(AUTHOR)}</itunes:author>')
    add(f'    <itunes:summary>{escape(DESCRIPTION)}</itunes:summary>')
    add('    <itunes:explicit>false</itunes:explicit>')
    # "serial" dice alle app che e' un corso: mostrano gli episodi dal numero 1 in avanti
    add('    <itunes:type>serial</itunes:type>')
    add('    <itunes:category text="Education"/>')
    add(f'    <lastBuildDate>{now}</lastBuildDate>')
    if cover_url:
        add(f'    <itunes:image href="{escape(cover_url)}"/>')
        add('    <image>')
        add(f'      <url>{escape(cover_url)}</url>')
        add(f'      <title>{escape(TITLE)}</title>')
        add(f'      <link>{escape(SITE_BASE)}</link>')
        add('    </image>')

    for ep in episodes:
        url = f"{SITE_BASE}/{AUDIO_DIR}/{ep['filename']}"
        add('    <item>')
        add(f'      <title>{escape(ep["title"])}</title>')
        add(f'      <itunes:episode>{ep["number"]}</itunes:episode>')
        add(f'      <guid isPermaLink="false">{escape(url)}</guid>')
        add(f'      <pubDate>{format_datetime(ep["pubdate"])}</pubDate>')
        add(f'      <enclosure url="{escape(url)}" length="{ep["size"]}" type="{ep["mime"]}"/>')
        add(f'      <description>{escape(ep["title"])}</description>')
        add(f'      <itunes:author>{escape(AUTHOR)}</itunes:author>')
        add('    </item>')

    add('  </channel>')
    add('</rss>')
    return "\n".join(lines) + "\n"


def main() -> None:
    if "TUOUSERNAME" in SITE_BASE:
        print("!! ATTENZIONE: devi ancora sostituire TUOUSERNAME in SITE_BASE.\n")

    episodes = collect_episodes()
    feed = build_feed(episodes)

    with open(OUTPUT, "w", encoding="utf-8") as handle:
        handle.write(feed)

    print(f"Creato '{OUTPUT}' con {len(episodes)} episodi:\n")
    for ep in episodes:
        mb = ep["size"] / (1024 * 1024)
        print(f"  {ep['number']:>2}. {ep['title']:<45} {mb:>6.1f} MB")
    print(f"\nURL del feed da incollare nell'app:\n  {SITE_BASE}/{OUTPUT}")


if __name__ == "__main__":
    main()
