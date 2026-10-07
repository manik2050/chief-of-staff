# Security

Learning evidence for Day 10 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Security is the set of controls that keep a request from becoming an
execution path or a data leak. The primer's basics: encrypt on the wire and
on disk; treat every user-supplied value as hostile; bind SQL parameters
instead of concatenating them; give each account only the privileges the
job needs. Authentication is proving identity; authorization (OAuth scopes
on the API checklist) is what that identity may do. Rate limits blunt
brute force. Secrets stay out of URLs and out of source.

```
  client
     |
     | TLS (in transit)
     v
+-----------+   bind params,        +-----------+
|    app    |   least-privilege     |    db     |  encrypted
|  encode   | --------------------> |  tables   |  at rest
|  output   |   never concat SQL    |           |
+-----------+                       +-----------+
```

```python
# stdlib only. Paste into python3, or: python3 - <<'PY' ... PY
import html, sqlite3

print(html.escape("<script>alert(1)</script>"))
# &lt;script&gt;alert(1)&lt;/script&gt;   HTML context, not a script tag

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE users (name TEXT)")
db.execute("INSERT INTO users VALUES ('alice')")
payload = "' OR '1'='1"
print("concat", list(db.execute(
    "SELECT name FROM users WHERE name = '" + payload + "'")))
# concat [('alice',)]   payload became SQL: WHERE name = '' OR '1'='1'
print("bound ", list(db.execute(
    "SELECT name FROM users WHERE name = ?", (payload,))))
# bound  []             payload stayed data: no user named "' OR '1'='1"
```

TLS encrypts the hop; disk encryption encrypts the files. One does not
replace the other. Filesystem or hardware encryption protects against
physical theft of the box, not a remote compromise of the app. Concatenated
SQL is easy and injectable; a `?` placeholder keeps code and data apart so
the payload cannot change the statement. Escaping every SQL string is
fragile; parameterization is the primary defense. For XSS, encode on
output when you must echo user text into HTML; input filtering is a
secondary check. Least privilege costs setup: a SELECT-only account is
slower to wire than DBA, and a successful injection then owns only what
that account could already do. Rate limiting rejects traffic past a
threshold so abuse does not starve the API.

Encrypt in transit with TLS (1.2 or newer; prefer 1.3). Encrypt stored
secrets and PII at rest — a key vault if you have one, never the repo.
Parameterize every untrusted value in SQL. HTML-encode (or use the
framework's auto-escape) when echoing text into a page. Give the app's
database user the minimum rights the endpoint needs. Keep tokens in the
Authorization header. Rate-limit login and public APIs (HTTP 429).

Sources: [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer)
(Security: encrypt in transit and at rest, sanitize inputs against XSS and
SQL injection, parameterized queries, least privilege);
[systemdesign42/system-design-academy](https://github.com/systemdesign42/system-design-academy)
([This Is How Stripe Does Rate Limiting to Build Scalable APIs](https://newsletter.systemdesign.one/p/rate-limiter));
[OWASP: SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
(parameterized queries; escaping discouraged; least privilege);
[OWASP: XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
(HTML entity encoding on output);
[OWASP: Transport Layer Security](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html)
(TLS 1.3 default, TLS 1.2 for compatibility);
[OWASP: Cryptographic Storage](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
(at rest; hardware encryption vs remote compromise; no keys in source);
[Wikipedia: Principle of least privilege](https://en.wikipedia.org/wiki/Principle_of_least_privilege);
[API Security Checklist](https://github.com/shieldfy/API-Security-Checklist)
(TLS 1.2+, authn vs OAuth authz, secrets not in URLs, rate limiting);
[Python sqlite3 placeholders](https://docs.python.org/3/library/sqlite3.html#how-to-use-placeholders-to-bind-values-in-sql-queries);
[Python html.escape](https://docs.python.org/3/library/html.html#html.escape).
