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
```

Finished PDFs are copied to `experiment_guides/`. The stand-alone `.tex` guides keep their PDF next to the source. Files shared by every guide (`header.tex`, `pchem_bib.bib`) are in `guide_src/shared/`, which each guide's `Tectonic.toml` adds to its search path with `extra_paths`. Run `uv run build.py --help` for more options.
