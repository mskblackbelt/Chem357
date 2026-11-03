# Chem357
Course materials for Chem357 - P. Chem II lab

For information on setting up a JupyterHub server to accompany the code in these labs, see the instructions [in the Jupyter Server setup repo](https://github.com/mskblackbelt/tljh_server_setup).


## Building the experiment guides

The guides in `experiment_guides/guide_src/` are built with [Tectonic](https://tectonic-typesetting.github.io); no TeX Live installation is needed. With [uv](https://docs.astral.sh/uv/) and Tectonic installed (`brew install uv tectonic`), run from `experiment_guides/`:

```sh
uv run build.py              # build every guide that has changed
uv run build.py hcl          # build one guide (any part of its folder or PDF name)
uv run build.py hcl --watch  # rebuild that guide whenever one of its files changes
uv run build.py --list       # list the guides and whether each PDF is current
uv run build.py hcl --figures  # recompute the guide's figure data, then build
```

Finished PDFs are copied to `experiment_guides/`. The stand-alone `.tex` guides keep their PDF next to the source. Files shared by every guide (`header.tex`, `pchem_bib.bib`) are in `guide_src/shared/`, which each guide's `Tectonic.toml` adds to its search path with `extra_paths`. Run `uv run build.py --help` for more options.

Builds are reproducible: a guide is dated by the day of its last commit (or today, if it has uncommitted changes), so rebuilding an unchanged guide produces an identical PDF and git only shows PDFs whose content changed. Build and commit a guide on the same day to keep its PDF in sync with the commit.

On every push that touches `experiment_guides/`, GitHub Actions (`.github/workflows/build-guides.yml`) builds all the guides on Linux, attaches the PDFs to the run, and warns if any committed PDF is out of date.
