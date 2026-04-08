#!/bin/bash

echo "Uruchamianie testów..."

for i in {1..32}; do
    # Wysłanie danych do serwera i zapisanie wyniku
    python3 mini-udpcat.py 127.0.0.1 2020 < "tests/test${i}-dane.txt" > "tests/wynik-test${i}.txt"
    
    # Porównanie wyniku (wymgamy dokładnej zgodności zawartości, beż żadnych odstępstw)
    if cmp -s "tests/wynik-test${i}.txt" "tests/test${i}-wynik.txt"; then
        echo "✅ Test $i: SUKCES"
    else
        echo "❌ Test $i: BŁĄD"
        echo "  Oczekiwano: '$(cat tests/test${i}-wynik.txt)'"
        echo "  Otrzymano : '$(cat tests/wynik-test${i}.txt)'"
    fi
done

echo "-----------------------------------"

