# rebelelitefc.com

Static site for Rebel Elite FC (girls' program of Ignite FC, St. George, Utah), hosted on GitHub Pages from `docs/`.

- `src/build.py` — generator (content + pages). `src/site.css`, `src/img/` — styles and source images.
- Build: `cd src && python3 build.py site` (production, writes CNAME) or `python3 build.py site preview` (noindex, no CNAME), then copy `src/out/site/` to `docs/`.
