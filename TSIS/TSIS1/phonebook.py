"""phonebook.py — PhoneBook Extended (TSIS1)"""

import csv, json, os
from datetime import date

import psycopg2, psycopg2.extras
from connect import get_connection

RealDict = psycopg2.extras.RealDictCursor

CONTACT_SELECT = """
    SELECT c.id AS contact_id, c.username, c.email, c.birthday,
           g.name AS group_name,
           STRING_AGG(p.phone || '(' || COALESCE(p.type,'?') || ')', ', '
                      ORDER BY p.id) AS phones,
           c.created_at
    FROM   contacts c
    LEFT   JOIN groups g ON g.id = c.group_id
    LEFT   JOIN phones p ON p.contact_id = c.id
"""

# ── helpers ──────────────────────────────────────────────────────

def ask(prompt, default=""):
    v = input(prompt).strip()
    return v if v else default

def fetch(conn, sql, params=()):
    with conn.cursor(cursor_factory=RealDict) as cur:
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]

def execute(conn, sql, params=()):
    """Execute a single SQL statement. Returns first row or None."""
    with conn.cursor() as cur:
        cur.execute(sql, params)
        try:
            row = cur.fetchone()
        except psycopg2.ProgrammingError:
            row = None
    conn.commit()
    return row

def run_script(conn, sql):
    """Execute a .sql file that contains multiple statements."""
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()

def print_contacts(rows):
    if not rows:
        print("  (ничего не найдено)"); return
    sep = "─" * 60
    for r in rows:
        bday = r.get("birthday")
        print(sep)
        print(f"  Имя      : {r['username']}")
        print(f"  Email    : {r.get('email') or '—'}")
        print(f"  День рожд: {bday.strftime('%Y-%m-%d') if isinstance(bday, date) else bday or '—'}")
        print(f"  Группа   : {r.get('group_name') or '—'}")
        print(f"  Телефоны : {r.get('phones') or '—'}")
    print(sep)

def get_or_create_group(conn, name):
    execute(conn, "INSERT INTO groups(name) VALUES(%s) ON CONFLICT(name) DO NOTHING", (name,))
    return fetch(conn, "SELECT id FROM groups WHERE name=%s", (name,))[0]["id"]

def show_groups(conn):
    groups = fetch(conn, "SELECT id, name FROM groups ORDER BY name")
    print("  Группы:", ", ".join(f"{g['id']}={g['name']}" for g in groups))
    return groups

# ── инициализация схемы ──────────────────────────────────────────

def init_schema(conn):
    base = os.path.dirname(os.path.abspath(__file__))
    for fname in ("schema.sql", "procedures.sql"):
        path = os.path.join(base, fname)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                sql = f.read()
            run_script(conn, sql)
            print(f"  [OK] {fname}")

# ── CRUD ─────────────────────────────────────────────────────────

def add_contact(conn):
    print("\n── Добавить контакт ──")
    username = ask("  Имя пользователя: ")
    if not username:
        print("  Имя не может быть пустым."); return
    email    = ask("  Email (необязательно): ") or None
    bday     = ask("  День рождения ГГГГ-ММ-ДД (необязательно): ") or None
    show_groups(conn)
    gid      = ask("  ID группы (необязательно): ")
    group_id = int(gid) if gid.isdigit() else None

    row = execute(conn,
        "INSERT INTO contacts(username,email,birthday,group_id) "
        "VALUES(%s,%s,%s,%s) ON CONFLICT(username) DO NOTHING RETURNING id",
        (username, email, bday, group_id))
    if not row:
        print(f"  Контакт '{username}' уже существует."); return
    cid = row[0]

    while True:
        phone = ask("  Номер телефона (пусто = пропустить): ")
        if not phone: break
        ptype = ask("  Тип [mobile/home/work]: ", "mobile")
        execute(conn, "INSERT INTO phones(contact_id,phone,type) VALUES(%s,%s,%s)", (cid, phone, ptype))
        if ask("  Ещё номер? [y/N]: ").lower() != "y": break

    print(f"  ✓ Контакт '{username}' добавлен.")

def update_contact(conn):
    print("\n── Обновить контакт ──")
    username = ask("  Имя пользователя: ")
    rows = fetch(conn, "SELECT id FROM contacts WHERE username=%s", (username,))
    if not rows:
        print(f"  Не найдено: '{username}'"); return
    cid = rows[0]["id"]

    new_email = ask("  Новый email (пусто = оставить): ") or None
    new_bday  = ask("  Новый день рождения (пусто = оставить): ") or None
    show_groups(conn)
    gid = ask("  Новый ID группы (пусто = оставить): ")

    fields, vals = [], []
    if new_email:     fields.append("email=%s");    vals.append(new_email)
    if new_bday:      fields.append("birthday=%s"); vals.append(new_bday)
    if gid.isdigit(): fields.append("group_id=%s"); vals.append(int(gid))

    if fields:
        execute(conn, f"UPDATE contacts SET {','.join(fields)} WHERE id=%s", vals + [cid])
        print("  ✓ Обновлено.")
    else:
        print("  Ничего не изменено.")

def delete_contact(conn):
    print("\n── Удалить контакт ──")
    username = ask("  Имя пользователя: ")
    row = execute(conn, "DELETE FROM contacts WHERE username=%s RETURNING id", (username,))
    print("  ✓ Удалён." if row else f"  Не найдено: '{username}'")

# ── поиск и фильтры ──────────────────────────────────────────────

def search(conn):
    print("\n── Поиск ──")
    q = ask("  Запрос (имя / email / телефон): ")
    print_contacts(fetch(conn, "SELECT * FROM search_contacts(%s)", (q,)))

def filter_by_group(conn):
    print("\n── Фильтр по группе ──")
    show_groups(conn)
    gid = ask("  ID группы: ")
    if not gid.isdigit():
        print("  Неверный ID."); return
    sql = CONTACT_SELECT + "WHERE c.group_id=%s GROUP BY c.id,g.name ORDER BY c.username"
    print_contacts(fetch(conn, sql, (int(gid),)))

def search_by_email(conn):
    print("\n── Поиск по email ──")
    fragment = ask("  Фрагмент email (напр. gmail): ")
    sql = CONTACT_SELECT + "WHERE c.email ILIKE %s GROUP BY c.id,g.name ORDER BY c.username"
    print_contacts(fetch(conn, sql, (f"%{fragment}%",)))

def browse_paginated(conn):
    print("\n── Просмотр (постранично) ──")
    print("  Сортировка: username | birthday | created_at")
    sort, limit, offset = ask("  Сортировать по [username]: ", "username"), 5, 0
    while True:
        rows = fetch(conn, "SELECT * FROM get_contacts_page(%s,%s,%s)", (limit, offset, sort))
        print(f"\n  ── Стр. {offset//limit+1} ({len(rows)} записей) ──")
        print_contacts(rows)
        if len(rows) < limit: print("  (конец списка)")
        cmd = ask("  [next / prev / quit]: ").lower()
        if   cmd == "quit": break
        elif cmd == "next":
            if len(rows) == limit: offset += limit
            else: print("  Последняя страница.")
        elif cmd == "prev": offset = max(0, offset - limit)

# ── процедуры ────────────────────────────────────────────────────

def add_phone(conn):
    print("\n── Добавить телефон ──")
    name  = ask("  Имя контакта: ")
    phone = ask("  Номер: ")
    ptype = ask("  Тип [mobile/home/work]: ", "mobile")
    execute(conn, "CALL add_phone(%s,%s,%s)", (name, phone, ptype))
    print("  ✓ Готово.")

def move_to_group(conn):
    print("\n── Переместить в группу ──")
    name  = ask("  Имя контакта: ")
    group = ask("  Название группы: ")
    execute(conn, "CALL move_to_group(%s,%s)", (name, group))
    print("  ✓ Готово.")

# ── экспорт / импорт JSON ─────────────────────────────────────────

def export_json(conn):
    print("\n── Экспорт в JSON ──")
    path = ask("  Файл [contacts.json]: ", "contacts.json")
    contacts = fetch(conn,
        "SELECT c.id, c.username, c.email, c.birthday::TEXT, "
        "g.name AS group_name, c.created_at::TEXT "
        "FROM contacts c LEFT JOIN groups g ON g.id=c.group_id ORDER BY c.username")
    for c in contacts:
        c["phones"] = fetch(conn,
            "SELECT phone,type FROM phones WHERE contact_id=%s ORDER BY id", (c.pop("id"),))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)
    print(f"  ✓ {len(contacts)} контактов сохранено в '{path}'.")

def _upsert(conn, data, overwrite):
    username = data.get("username", "").strip()
    if not username: return False
    gname    = data.get("group_name") or data.get("group")
    group_id = get_or_create_group(conn, gname) if gname else None
    conflict = ("DO UPDATE SET email=EXCLUDED.email,"
                "birthday=EXCLUDED.birthday,group_id=EXCLUDED.group_id") if overwrite else "DO NOTHING"
    row = execute(conn,
        f"INSERT INTO contacts(username,email,birthday,group_id) VALUES(%s,%s,%s,%s) "
        f"ON CONFLICT(username) {conflict} RETURNING id",
        (username, data.get("email"), data.get("birthday"), group_id))
    if not row: return False
    cid = row[0]
    if overwrite:
        execute(conn, "DELETE FROM phones WHERE contact_id=%s", (cid,))
    for ph in data.get("phones", []):
        if ph.get("phone"):
            execute(conn, "INSERT INTO phones(contact_id,phone,type) VALUES(%s,%s,%s)",
                    (cid, ph["phone"], ph.get("type","mobile")))
    return True

def import_json(conn):
    print("\n── Импорт из JSON ──")
    path = ask("  Файл [contacts.json]: ", "contacts.json")
    if not os.path.isfile(path):
        print("  Файл не найден."); return
    data = json.load(open(path, encoding="utf-8"))
    added = skipped = overwritten = 0
    global_choice = None
    for item in data:
        username = item.get("username","").strip()
        if not username: continue
        exists = bool(fetch(conn, "SELECT 1 FROM contacts WHERE username=%s", (username,)))
        if exists:
            choice = global_choice
            if not choice:
                print(f"  Дубликат: '{username}'")
                choice = ask("  [s]кип / [o]верезапись / [S]кип все / [O]верезапись все: ")
                if choice == "S": global_choice = choice = "s"
                elif choice == "O": global_choice = choice = "o"
            if choice.lower() == "o":
                _upsert(conn, item, True); overwritten += 1
            else:
                skipped += 1
        else:
            _upsert(conn, item, False); added += 1
    print(f"  ✓ Добавлено={added}, перезаписано={overwritten}, пропущено={skipped}.")

# ── импорт CSV ───────────────────────────────────────────────────

def import_csv(conn):
    print("\n── Импорт из CSV ──")
    path = ask("  Файл [contacts.csv]: ", "contacts.csv")
    if not os.path.isfile(path):
        print("  Файл не найден."); return
    added = skipped = errors = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            username = (row.get("username") or "").strip()
            if not username: errors += 1; continue
            phone      = (row.get("phone") or "").strip()
            phone_type = row.get("phone_type","mobile").strip()
            if phone_type not in ("home","work","mobile"): phone_type = "mobile"
            email    = row.get("email","").strip() or None
            birthday = row.get("birthday","").strip() or None
            gname    = row.get("group","").strip() or None
            group_id = get_or_create_group(conn, gname) if gname else None

            res = execute(conn,
                "INSERT INTO contacts(username,email,birthday,group_id) VALUES(%s,%s,%s,%s) "
                "ON CONFLICT(username) DO NOTHING RETURNING id",
                (username, email, birthday, group_id))
            if res:
                cid = res[0]; added += 1
            else:
                cid = fetch(conn, "SELECT id FROM contacts WHERE username=%s", (username,))[0]["id"]
                skipped += 1
            if phone:
                execute(conn,
                    "INSERT INTO phones(contact_id,phone,type) VALUES(%s,%s,%s) ON CONFLICT DO NOTHING",
                    (cid, phone, phone_type))
    print(f"  ✓ CSV: добавлено={added}, пропущено={skipped}, ошибок={errors}.")

# ── меню ─────────────────────────────────────────────────────────

MENU = """
╔══════════════════════════════════════╗
║       PhoneBook Extended (TSIS1)     ║
╠══════════════════════════════════════╣
║  1. Добавить контакт                 ║
║  2. Обновить контакт                 ║
║  3. Удалить контакт                  ║
║  4. Поиск (имя / email / телефон)    ║
║  5. Фильтр по группе                 ║
║  6. Поиск по email                   ║
║  7. Просмотр (постранично)           ║
║  8. Добавить телефон                 ║
║  9. Переместить в группу             ║
║ 10. Экспорт в JSON                   ║
║ 11. Импорт из JSON                   ║
║ 12. Импорт из CSV                    ║
║  0. Выход                            ║
╚══════════════════════════════════════╝"""

ACTIONS = {
    "1": add_contact,     "2": update_contact,   "3": delete_contact,
    "4": search,          "5": filter_by_group,  "6": search_by_email,
    "7": browse_paginated,"8": add_phone,         "9": move_to_group,
    "10": export_json,    "11": import_json,      "12": import_csv,
}

def main():
    conn = get_connection()
    print("  Подключено к PostgreSQL.")
    init_schema(conn)
    while True:
        print(MENU)
        choice = ask("  Выбор: ")
        if choice == "0":
            print("  Пока!"); break
        fn = ACTIONS.get(choice)
        if fn:
            try:
                fn(conn)
            except psycopg2.Error as e:
                conn.rollback()
                print(f"  Ошибка БД: {e.pgerror or e}")
            except Exception as e:
                print(f"  Ошибка: {e}")
        else:
            print("  Неизвестная команда.")
    conn.close()

if __name__ == "__main__":
    main()