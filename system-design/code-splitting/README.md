# Code splitting

Learning evidence for Day 36 system design. Not part of the Chief of Staff
install. The installer does not copy this folder.

Code splitting is loading code only when it is needed: ship a smaller
initial bundle, then load the rest on demand. Software bloat is code that
makes the app slower, uses extra memory, or needs more CPU cycles. In a
diverse marketplace most users need only a subset of features, so unused
ones count as bloat. Essential complexity is unavoidable; splitting keeps
those features without shipping them all at start.

Discord is a voice and text chat app with 10 million+ daily active users.
It code-splits to keep performance while adding features. On start the app
gets only the necessary JavaScript, CSS, fonts, and images; the server
sends remaining assets as the user navigates. It also receives only the
relevant translation file, which let it add many translation files without
a performance impact. The article's suggested start is the route level:
bundle routes into chunks with a tool like Webpack and lazy-load them.

Unclear: the article does not say Discord uses Webpack or HTTP streaming,
and it gives no bundle-size or latency numbers.

```
  start
     |
     v
+-----------+  necessary JS, CSS, fonts, images
|   shell   |
+-----------+
     | navigate
     v
+-----------+  remaining assets on demand
|  chunks   |  route bundles, translations, ...
+-----------+  lazy-loaded
```

```python
# python3 - <<'PY' ... PY
# Toy route chunks; sizes invented, not article numbers.
START = {"shell.js": 4, "shell.css": 1, "font": 1, "img": 1}
ROUTES = {
    "/": {},
    "/voice": {"voice.js": 5},
    "/settings": {"settings.js": 2, "en.json": 2},
}

sent = dict(START)
print("startup", list(sent), "units", sum(sent.values()))

def hit(path):
    extra = ROUTES[path]
    sent.update(extra)
    print("hit", path, "extra", list(extra) or "none",
          "units-now", sum(sent.values()))

hit("/")
hit("/voice")
hit("/settings")
# startup ['shell.js', 'shell.css', 'font', 'img'] units 7
# hit / extra none units-now 7
# hit /voice extra ['voice.js'] units-now 12
# hit /settings extra ['settings.js', 'en.json'] units-now 16
```

Sources: Neo Kim,
[How Discord Boosts Performance With Code-Splitting](https://newsletter.systemdesign.one/p/what-is-code-splitting-in-react)
(The System Design Newsletter #20, 8 Nov 2023; Discord 10 million+ DAU;
code split = load code only when needed; start: necessary JS, CSS, fonts,
images; remaining assets on navigate; relevant translation file; route-level
chunks / Webpack as an example tool; lazy-load; stylesheets, translations,
fonts; mobile / CDN / SEO; more requests and latency; HTTP streaming as a
potential fix).
