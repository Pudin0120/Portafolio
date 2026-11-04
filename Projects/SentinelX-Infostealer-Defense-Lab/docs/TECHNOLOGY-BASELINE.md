# Technology Baseline (2026-11-03)

This is a candidate version baseline for the SentinelX academic implementation. It records upstream releases visible on 2026-11-03; it is not a claim that the full stack has been integrated or compatibility-tested.

| Component | Candidate version | Upstream evidence | Integration note |
|---|---:|---|---|
| Python | 3.15.2 | https://www.python.org/downloads/release/python-3152/ | Confirm that all selected scientific and ML dependencies publish compatible wheels before pinning. Python 3.14 is the conservative fallback. |
| FastAPI | 0.162.0 | https://fastapi.tiangolo.com/release-notes/ | Validate against the chosen Python and Pydantic versions; review recent behavior changes before adoption. |
| Next.js | 16.4 | https://nextjs.org/blog | Use an Active LTS release, not a canary build. |
| React | 19.3 | https://react.dev/blog/2026/09/09/react-19-3 | Verify compatibility with the selected Next.js release and component libraries. |
| PostgreSQL | 18.6 | https://www.postgresql.org/docs/18/release.html | Prefer the latest supported minor release in the selected major line. |
| ClickHouse | 26.8 LTS | https://clickhouse.com/blog/clickHouse-release-26-08 | LTS candidate for analytical event storage. |
| Rust | 1.98.1 | https://doc.rust-lang.org/stable/releases.html | Pin the toolchain and dependency graph; use the producer only for synthetic fixture generation. |

## Selection policy

1. Prefer supported stable or LTS releases over prerelease/canary versions.
2. Confirm compatibility across the complete dependency graph in CI before pinning.
3. Commit lockfiles and exact container image tags; do not use floating production tags.
4. Run unit, integration, security, and reproducibility checks after every dependency upgrade.
5. If Python 3.15 support is incomplete for a required data-science dependency, use Python 3.14 rather than forcing an unsupported combination.
6. Re-check upstream security advisories immediately before the thesis demonstration and final release.

## Source observations

- Python.org lists the 3.15 bugfix series and Python 3.15.2 as released on 2026-10-25.
- FastAPI's release notes list 0.162.0 on 2026-10-23.
- The Next.js blog lists Next.js 16.4 on 2026-10-06.
- The React team announced React 19.3 on 2026-09-09.
- PostgreSQL's release notes list PostgreSQL 18.6, released on 2026-08-13.
- ClickHouse identifies 26.8 as a long-term-support release.
- The Rust stable release notes list 1.98.1 on 2026-09-03.

Always consult the upstream links again before implementation; release pages and security status can change.
