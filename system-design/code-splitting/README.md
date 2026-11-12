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
a performance impact. A good place to start is the route level: bundle
routes into chunks with a tool like Webpack and lazy-load them.

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
# Toy route chunks; sizes invented, not article numbers. python3 - <<'PY' ... PY
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

The toy ships 7 units at start (invented sizes, not article numbers). The
home route adds nothing; /voice adds voice.js (12 units now); /settings
adds settings.js and the English translation file (16). Other named
candidates for a split are stylesheets, translations, and fonts. Named
benefits are improved performance on mobile clients in an unreliable
network, reduced CDN costs, and improved SEO. CDNs are charged on
bandwidth and the number of HTTP requests, so keep a balance. More
requests add overhead and can degrade latency. Code splitting via HTTP
streaming is a potential solution. The takeaway is that code splitting
allows adding new features without bloating the app.

Sources: Neo Kim,
[How Discord Boosts Performance With Code-Splitting](https://newsletter.systemdesign.one/p/what-is-code-splitting-in-react)
(The System Design Newsletter #20, 8 Nov 2023; Discord 10 million+ DAU;
code split = load code only when needed; start: necessary JS, CSS, fonts,
images; remaining assets on navigate; relevant translation file; route-level
chunks / Webpack as an example tool; lazy-load; stylesheets, translations,
fonts; mobile / CDN / SEO; CDN charged on bandwidth and request count;
more requests and latency; HTTP streaming as a potential solution; takeaway:
add features without bloating the app).
