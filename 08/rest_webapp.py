#!/usr/bin/python3
# -*- coding: UTF-8 -*-

'''
Aplikacja WSGI implementująca najważniejsze części opisywanej na wykładzie
usługi REST dającej dostęp do bazy z danymi osób.

Uwaga: kod dydaktyczny bez pełnej obsługi błędów i sytuacji nadzwyczajnych.

Aplikacja nie potrafi sama stworzyć swojej bazy danych, trzeba to zrobić
przed jej uruchomieniem. Skrypt rest_webapp.sh pokazuje jak.
'''

plik_bazy = './osoby.sqlite'

import re, sqlite3
from urllib.parse import parse_qs

class OsobyApp:
    def __init__(self, environment, start_response):
        '''
Konstruktor wywoływany przez serwer WSGI. Jak każdy konstruktor tworzy nowy
obiekt, następnie zapamiętuje w jego polach przekazane przez serwer argumenty
i inicjuje pola na odpowiedź.
'''
        self.env = environment
        self.start_response = start_response
        self.status = '200 OK'
        self.headers = [ ('Content-Type', 'text/html; charset=UTF-8') ]
        self.content = b''

    def __iter__(self):
        '''
Metoda obsługująca proces iterowania po stworzonym obiekcie. Serwer WSGI
wymaga aby w środku była co najmniej jedna instrukcja "yield" zwracająca
ciąg bajtów do odesłania klientowi HTTP.
'''
        try:
            self.route()
        except sqlite3.Error as e:
            s = 'SQLite error: ' + str(e)
            self.failure('500 Internal Server Error', s)
        n = len(self.content)
        self.headers.append( ('Content-Length', str(n)) )
        self.start_response(self.status, self.headers)
        yield self.content

    def failure(self, status, detail = None):
        '''
Metoda wstawiająca do pól obiektu status błędu oraz dokument HTML
z komunikatem o jego wystąpieniu.
'''
        self.status = status
        s = '<html>\n<head>\n<title>' + status + '</title>\n</head>\n'
        s += '<body>\n<h1>' + status + '</h1>\n'
        if detail is not None:
            s += '<p>' + detail + '</p>\n'
        s += '</body>\n</html>\n'
        self.content = s.encode('UTF-8')

    def route(self):
        path_info = self.env.get('PATH_INFO', '')
        if path_info == '' or path_info == '/':
            self.failure('404 Not Found')
            return
        if '//' in path_info:
            self.failure('404 Not Found')
            return
        raw_segments = path_info.split('/')
        path = [segment for segment in raw_segments if segment != '']
        query_params = parse_qs(self.env['QUERY_STRING'])
        if len(path) > 0:
            domain = path[0]
            if (domain == 'osoby' or domain == 'psy'):
                if len(path) == 1:
                    self.handle_table(domain)
                    return

                if len(path) == 2:
                    resource = path[1]
                    
                    if resource == 'search':
                        if domain != 'osoby':
                            self.failure('404 Not Found')
                            return
                        self.handle_search(domain, query_params)
                        return
                    elif re.match('^[0-9]+$', resource):
                        self.handle_item(domain, resource)
                        return
            
            self.failure('404 Not Found')

    def handle_table(self, domain):

        if self.env['REQUEST_METHOD'] == 'GET':
            colnames, rows = self.sql_select(domain)
            self.send_rows(colnames, rows)
        elif self.env['REQUEST_METHOD'] == 'POST':
            colnames, vals = self.read_tsv()
            if not self.validate_payload(domain, colnames, vals):
                return
            if domain == 'psy':
                if not self.validate_owner_id(colnames, vals):
                    return
            q = 'INSERT INTO ' + domain + ' (' + ', '.join(colnames) + ') VALUES ('
            q += ', '.join(['?' for v in vals]) + ')'
            id = self.sql_modify(q, vals)
            colnames, rows = self.sql_select(domain, ['id'], [id])
            self.send_rows(colnames, rows)
        else:
            self.failure('405 Method Not Allowed')

    def handle_item(self, domain, id):

        if self.env['REQUEST_METHOD'] == 'GET':
            colnames, rows = self.sql_select(domain, ['id'], [id])
            if len(rows) == 0:
                self.failure('404 Not Found')
            else:
                self.send_rows(colnames, rows)
        elif self.env['REQUEST_METHOD'] == 'PUT':
            colnames, vals = self.read_tsv()
            if not self.validate_payload(domain, colnames, vals, is_update=True):
                return
            if domain == 'psy':
                if not self.validate_owner_id(colnames, vals):
                    return
            q = 'UPDATE ' + domain + ' SET '
            q += ', '.join([c + ' = ?' for c in colnames])
            q += ' WHERE id = ?'
            self.sql_modify(q, vals + [id])
            colnames, rows = self.sql_select(domain, ['id'], [id])
            self.send_rows(colnames, rows)
        elif self.env['REQUEST_METHOD'] == 'DELETE':
            if domain == 'osoby':
                _, rows = self.sql_select('psy', ['wlasciciel_id'], [id])
                if len(rows) > 0:
                    self.failure('409 Conflict', 'Nie mozna usunac osoby, ktora jest wlascicielem psa')
                    return
            q = 'DELETE FROM ' + domain + ' WHERE id = ?'
            self.sql_modify(q, [id])
        else:
            self.failure('501 Not Implemented')

    def handle_search(self, domain, query_params: dict):
        if self.env['REQUEST_METHOD'] == 'GET':
            if 'imie' in query_params and 'nazwisko' in query_params:
                imie = query_params['imie'][0]
                nazwisko = query_params['nazwisko'][0]
                colnames, rows = self.sql_select(domain, ['imie', 'nazwisko'], [imie, nazwisko])
                self.send_rows(colnames, rows)
            elif 'imie' in query_params:
                imie = query_params['imie'][0]
                colnames, rows = self.sql_select(domain, ['imie'], [imie])
                self.send_rows(colnames, rows)
            elif 'nazwisko' in query_params:
                nazwisko = query_params['nazwisko'][0]
                colnames, rows = self.sql_select(domain, ['nazwisko'], [nazwisko])
                self.send_rows(colnames, rows)
            else:
                self.failure('400 Bad Request', 'Brak parametru "imie" lub "nazwisko" w zapytaniu')
        else:
            self.failure('405 Method Not Allowed')

    def validate_owner_id(self, colnames, vals):
        if 'wlasciciel_id' not in colnames:
            return True
        owner_index = colnames.index('wlasciciel_id')
        owner_id = vals[owner_index].strip()
        if owner_id == '':
            return True
        _, rows = self.sql_select('osoby', ['id'], [owner_id])
        if len(rows) == 0:
            self.failure('409 Conflict', 'Nie istnieje osoba o podanym "wlasciciel_id"')
            return False
        return True

    def validate_payload(self, domain, colnames, vals, is_update=False):
        if len(colnames) == 0 or len(vals) == 0 or len(colnames) != len(vals):
            self.failure('400 Bad Request', 'Niepoprawny format danych TSV')
            return False

        allowed_columns = {
            'osoby': ['imie', 'nazwisko', 'telefon', 'adres'],
            'psy': ['imie', 'rasa', 'wlasciciel_id'],
        }
        required_columns = {
            'osoby': ['imie', 'nazwisko'],
            'psy': ['imie', 'rasa'],
        }
        if domain not in allowed_columns:
            self.failure('400 Bad Request', 'Nieznana tabela')
            return False

        for col in colnames:
            if col not in allowed_columns[domain]:
                self.failure('400 Bad Request', 'Nieznana kolumna: ' + col)
                return False

        if not is_update:
            for col in required_columns[domain]:
                if col not in colnames:
                    self.failure('400 Bad Request', 'Brak wymaganej kolumny: ' + col)
                    return False

        field_map = dict(zip(colnames, vals))

        for col in required_columns[domain]:
            if col in field_map and field_map[col].strip() == '':
                self.failure('400 Bad Request', 'Pole "' + col + '" nie moze byc puste')
                return False

        if 'telefon' in field_map:
            telefon = field_map['telefon'].strip()
            if telefon != '' and not re.match(r'^\+?[0-9]{7,15}$', telefon):
                self.failure('400 Bad Request', 'Niepoprawny format telefonu')
                return False

        if 'wlasciciel_id' in field_map:
            owner_raw = field_map['wlasciciel_id'].strip()
            if owner_raw != '' and not re.match('^[0-9]+$', owner_raw):
                self.failure('400 Bad Request', 'Niepoprawny "wlasciciel_id"')
                return False

        return True

    def read_tsv(self):
        f = self.env['wsgi.input']
        n = int(self.env['CONTENT_LENGTH'])
        raw_bytes = f.read(n)
        lines = raw_bytes.decode('UTF-8').splitlines()
        colnames = lines[0].split('\t')
        vals = lines[1].split('\t')
        return colnames, vals

    def send_rows(self, colnames, rows):
        s = '\t'.join(colnames) + '\n'
        for row in rows:
            s += '\t'.join([str(val) for val in row]) + '\n'
        self.content = s.encode('UTF-8')
        self.headers = [ ('Content-Type',
                'text/tab-separated-values; charset=UTF-8') ]

    def sql_select(self, domain, col: list = None, val: list = None):
        conn = sqlite3.connect(plik_bazy)
        crsr = conn.cursor()
        query = 'SELECT * FROM ' + domain
        params = []
        if col is not None and val is not None:
            for i in range(len(col)):
                if i == 0:
                    query += ' WHERE '
                else:
                    query += ' AND '
                query += col[i] + ' = ?'
                params.append(val[i])
        if params:
            crsr.execute(query, params)
        else:
            crsr.execute(query)
        colnames = [ d[0] for d in crsr.description ]
        rows = crsr.fetchall()
        crsr.close()
        conn.close()
        return colnames, rows

    def sql_modify(self, query, params = None):
        conn = sqlite3.connect(plik_bazy)
        crsr = conn.cursor()
        if params is None:
            crsr.execute(query)
        else:
            crsr.execute(query, params)
        rowid = crsr.lastrowid   # id wiersza wstawionego przez INSERT
        crsr.close()
        conn.commit()
        conn.close()
        return rowid

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    port = 8000
    httpd = make_server('', port, OsobyApp)
    print('Listening on port %i, press ^C to stop.' % port)
    httpd.serve_forever()