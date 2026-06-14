# Klub Polarny — statyczna kopia strony

Statyczna (offline) kopia serwisu **klubpolarny.pl** — wszystkie podstrony, artykuły,
grafika i pliki PDF zapisane jako pliki HTML jeden do jednego z oryginału. Wersja
nie wymaga WordPressa, PHP ani bazy danych — to czysty HTML/CSS/JS gotowy do
hostowania na GitHub Pages lub dowolnym serwerze plików statycznych.

## Jak to uruchomić

**Lokalnie:** otwórz `index.html` w przeglądarce.

**GitHub Pages:** w ustawieniach repozytorium → *Settings → Pages* wybierz
publikację z gałęzi `main`, katalog `/ (root)`. Plik `.nojekyll` wyłącza
przetwarzanie Jekyll, dzięki czemu pliki o nazwach zawierających znaki `@`/`%`
(pozostałość po adresach WordPressa) serwowane są bez zmian.

## Struktura

- `index.html` — strona główna
- `aktualnosci/` — archiwum aktualności i wiadomości
- `galeria-zdjec/` — galerie zdjęć
- `biuletyn-polarny/`, `edukacja-i-popularyzacja/`, `mapy-polarne/`,
  `muzyka-polarna/`, `statut-ptg/`, `zarzad-klubu/`, `kontakt/` itd. — pozostałe działy
- `wp-content/uploads/` — wszystkie pliki graficzne i PDF
- `wp-includes/`, `wp-content/` — style i skrypty potrzebne do wyglądu strony

## Uwagi

- Treści dynamiczne (kamery na żywo, osadzone mapy/wideo z serwisów zewnętrznych)
  z natury nie działają offline — zapisana jest tylko ich strona-kontener.
- Część odnośników kierujących do zasobów nieobecnych w kopii może prowadzić do
  oryginalnej domeny `klubpolarny.pl`.
- Prawa do treści, zdjęć i materiałów należą do **Polskiego Klubu Polarnego**.
  Kopia przeznaczona do archiwizacji / migracji za zgodą właściciela.
