#!/bin/sh

# Skrypt uruchamiający i demonstrujący działanie aplikacji z pliku
# rest_webapp.py. Skrypt przetestowano pod Debianem 7, czyli dystrybucją
# zainstalowaną w pracowniach studenckich.
#
# Przy ręcznym testowaniu  webaplikacji możesz chcieć użyć "curl -v" aby
# zobaczyć nagłówki zapytań i odpowiedzi HTTP.


# Zainicjuj bazę z danymi osób.

rm -f osoby.sqlite

sqlite3 osoby.sqlite "
CREATE TABLE osoby (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    imie VARCHAR,
    nazwisko TEXT,
    telefon TEXT,
    adres TEXT
);
INSERT INTO osoby VALUES (1, 'Anna', 'Nowak', '+48124569988',
    'Rynek Główny 2, 30-001 Kraków');
INSERT INTO osoby VALUES (2, 'Jan', 'Kowalski', '+48127770022',
    'ul. Podzamcze 1, 31-001 Kraków');

CREATE TABLE psy (
id INTEGER PRIMARY KEY AUTOINCREMENT,
imie VARCHAR,
rasa TEXT,
wlasciciel_id INTEGER REFERENCES osoby(id)
);
INSERT INTO psy VALUES (1, 'Azor', 'owczarek', 1);
INSERT INTO psy VALUES (2, 'Reksio', 'kundel', 2);
INSERT INTO psy VALUES (3, 'Puszek', 'bullterier', NULL);
"

# Dla pewności wypisz na ekran jej zawartość.

echo "Początkowa zawartość bazy:"
echo "Tabela osoby:"
sqlite3 --header osoby.sqlite "SELECT * FROM osoby"
echo "Tabela psy:"
sqlite3 --header osoby.sqlite "SELECT * FROM psy"

# Uruchom w tle serwer z webaplikacją.

env -i python3 -u rest_webapp.py > stdout.txt 2> stderr.txt &
server_pid=$!
sleep 1

# Testy aplikacji:

echo
echo "Test 1: pobieranie rekordu"
curl http://127.0.0.1:8000/osoby/1

echo
echo "Test 2: uaktualnianie rekordu"
printf "nazwisko\tadres\n" > dane.tsv
printf "Kowalska\tul. Podzamcze 1, 31-001 Kraków\n" >> dane.tsv
curl --upload-file dane.tsv \
        --header "Content-Type: text/tab-separated-values; charset=UTF-8" \
        http://127.0.0.1:8000/osoby/1
# użycie opcji --upload-file zmienia domyślną metodę na PUT

echo
echo "Test 3: usuwanie rekordu (status 409)"
curl --request DELETE http://127.0.0.1:8000/osoby/2

echo
echo "Test 4: dodawanie nowego rekordu"
printf "imie\tnazwisko\ttelefon\tadres\n" > dane.tsv
printf "Adam\tWiśniewski\t+48120124433\tul. Reymonta 4\n" >> dane.tsv
curl --request POST --upload-file dane.tsv \
        --header "Content-Type: text/tab-separated-values; charset=UTF-8" \
        http://127.0.0.1:8000/osoby

echo
echo "Test 5: pobieranie całej bazy"
curl http://127.0.0.1:8000/osoby

echo
echo "Test 6: wyszukiwanie po imieniu"
curl "http://127.0.0.1:8000/osoby/search?imie=Jan"

echo
echo "Test 7: wyszukiwanie po imieniu i nazwisku"
curl "http://127.0.0.1:8000/osoby/search?imie=Jan&nazwisko=Kowalski"

echo
echo "Test 8: wyszukiwanie po nazwisku"
curl "http://127.0.0.1:8000/osoby/search?nazwisko=Kowalski"

echo
echo "Test 9: wyszukiwanie bez parametrow (status 400)"
curl "http://127.0.0.1:8000/osoby/search"

echo
echo "Test 10: usuwanie osoby bedacej wlascicielem psa (status 409)"
curl --request DELETE http://127.0.0.1:8000/osoby/1

echo
echo "Test 11: pobieranie rekordu z tabeli psy"
curl http://127.0.0.1:8000/psy/1

echo
echo "Test 12: pobieranie całej tabeli psy"
curl http://127.0.0.1:8000/psy

echo
echo "Test 13: uaktualnianie rekordu w tabeli psy"
printf "imie\trasa\twlasciciel_id\n" > dane.tsv
printf "Azor\tboxer\t1\n" >> dane.tsv
curl --upload-file dane.tsv \
    --header "Content-Type: text/tab-separated-values; charset=UTF-8" \
    http://127.0.0.1:8000/psy/1

echo
echo "Test 14: usuwanie rekordu z tabeli psy"
curl --request DELETE http://127.0.0.1:8000/psy/2

echo
echo "Test 15: dodawanie psa bez wlasciciel_id (tylko imie i rasa)"
printf "imie\trasa\n" > dane.tsv
printf "Reks\tkundel\n" >> dane.tsv
curl --request POST --upload-file dane.tsv \
    --header "Content-Type: text/tab-separated-values; charset=UTF-8" \
    http://127.0.0.1:8000/psy

echo
echo "Test 16: dodawanie psa z nieistniejacym wlascicielem (status 409)"
printf "imie\trasa\twlasciciel_id\n" > dane.tsv
printf "Max\tkundel\t999\n" >> dane.tsv
curl --request POST --upload-file dane.tsv \
    --header "Content-Type: text/tab-separated-values; charset=UTF-8" \
    http://127.0.0.1:8000/psy

echo
echo "Test 17: dodawanie osoby z blednym telefonem (status 400)"
printf "imie\tnazwisko\ttelefon\tadres\n" > dane.tsv
printf "Ewa\tTest\tabc\tul. Testowa 1\n" >> dane.tsv
curl --request POST --upload-file dane.tsv \
    --header "Content-Type: text/tab-separated-values; charset=UTF-8" \
    http://127.0.0.1:8000/osoby

echo
echo "Test 18: dodawanie osoby bez nazwiska (status 400)"
printf "imie\tnazwisko\ttelefon\tadres\n" > dane.tsv
printf "Ewa\t\t+48123456789\tul. Testowa 1\n" >> dane.tsv
curl --request POST --upload-file dane.tsv \
    --header "Content-Type: text/tab-separated-values; charset=UTF-8" \
    http://127.0.0.1:8000/osoby

# I jeszcze upewnienie się co do zawartości pliku z bazą.

echo
echo "Zawartość bazy po zmianach:"
echo "Tabela osoby:"
sqlite3 --header osoby.sqlite "SELECT * FROM osoby"
echo "Tabela psy:"
sqlite3 --header osoby.sqlite "SELECT * FROM psy"

# Koniec testów, można wyłączyć serwer aplikacyjny.

kill $server_pid