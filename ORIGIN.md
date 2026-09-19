# Origin

This repository vendors a snapshot of [tt-a1i/archify](https://github.com/tt-a1i/archify) into [manik2050/chief-of-staff](https://github.com/manik2050/chief-of-staff).

| Field | Value |
|---|---|
| Upstream | https://github.com/tt-a1i/archify |
| Snapshot commit | [`72c750bb070d95171dbb2244e5b62b1b7da69c12`](https://github.com/tt-a1i/archify/commit/72c750bb070d95171dbb2244e5b62b1b7da69c12) |
| Upstream version | `v2.17.0-dev.1` |
| License | MIT (see [LICENSE](LICENSE)) |

The snapshot is a file copy of the upstream working tree. Git history from Archify is not imported.

Project pages, Proof Lab, and scenario guide links in the original README still point at the upstream GitHub Pages site.

Local adaptations:

- `.github/CODEOWNERS` points at `@manik2050`
- CI skips the upstream `published-update-manifest` gate, which requires Archify GitHub Releases that this repository does not publish
