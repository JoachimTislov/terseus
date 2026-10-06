# Research site

Static, client-side visualization of the research registry: `index.html`,
`style.css`, and `app.js`. There is no build step and no dependencies.

`app.js` loads its data with `fetch` calls using paths relative to the page:
the registry files under `research/` and the agent network samples under
`experiments/008-agent-domain-languages/samples/anl/`. Two consequences:

- the page cannot be opened from the filesystem (browsers block `fetch`
  on `file://` URLs);
- it cannot be served from inside `site/` either, because the registry lives
  outside it (`research/projects.json` would 404).

The page has to be served from a directory assembled the same way the Pages
workflow does it.

## Previewing locally

From the repo root:

```
mkdir -p _site
cp site/* _site/
cp -r research _site/research
mkdir -p _site/experiments/008-agent-domain-languages/samples
cp -r experiments/008-agent-domain-languages/samples/anl _site/experiments/008-agent-domain-languages/samples/
python3 -m http.server --directory _site 8000
```

Open http://localhost:8000, stop the server with Ctrl-C. `_site/` is a
throwaway directory and git-ignored; delete it after use, and re-run the
copy commands to pick up registry changes. Any static file server works in
place of `python3 -m http.server`; what matters is serving the assembled
directory, not `site/` itself.

## Deployment

`.github/workflows/pages.yml` deploys on every push to `main`: it assembles
`_site/` from `site/*` plus `research/` and publishes that to GitHub Pages.
Note the deployed copy does not include the experiment 008 ANL samples, so
a local preview as above is currently the only place the agent network
section renders. Without all fetched files present, `app.js` renders no
data at all: the first failed `fetch` rejects and aborts the whole page.
