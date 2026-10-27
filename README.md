# Animated contribution graph

My last year of GitHub contributions, animated six ways on plain canvas.

**Live:** https://erkankolakan.github.io/contribution-graph/

- `scripts/fetch-github.sh` pulls the contribution calendar from the GitHub GraphQL API into `data/github.json`
- `build.sh` inlines that data into `template.html` → `index.html`, and renders `skyline-light.svg` / `skyline-dark.svg` for the profile README
- `.github/workflows/deploy.yml` rebuilds and deploys to GitHub Pages every day

Run locally: `./build.sh` (needs the `gh` CLI, logged in).
