#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pygments"]
# ///
"""Build the Chem 357 experiment guides with Tectonic.

Every folder under guide_src/ with a Tectonic.toml is a guide; it is built
with `tectonic -X build` and its PDF is copied to this folder.  The
stand-alone guides listed in STANDALONE are built with `tectonic -X compile`
and keep their PDF next to the .tex file.  Shared files (header.tex,
pchem_bib.bib) live in guide_src/shared/.

Builds are reproducible: each PDF is dated (SOURCE_DATE_EPOCH, which also
sets the date printed under the title) by the day of the last git commit
touching that guide, or today if it has uncommitted changes.  Rebuilding an
unchanged guide therefore gives an identical file.

Requires uv and tectonic.  Pygments (used by minted) is installed by uv.

Examples:
    uv run build.py                 # build every guide that has changed
    uv run build.py hcl             # build one guide (matches names loosely)
    uv run build.py hcl --watch     # rebuild it whenever a source file changes
    uv run build.py --force         # rebuild everything
    uv run build.py hcl --figures   # regenerate the guide's figure data first
    uv run build.py --list          # show the guides and whether they're current
    uv run build.py --clean         # delete the build/ folders
"""

import argparse
import datetime
import os
import re
import shutil
import subprocess
import sys
import sysconfig
import tempfile
import time
import tomllib
import zlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "guide_src"
SHARED = SRC / "shared"
SKIP_DIRS = {"build", "Old materials", "Reference materials"}

# Single-file guides built with `tectonic -X compile` (paths relative to SRC)
STANDALONE = [
    "python_intro/Python_Intro.tex",
    "error_analysis/Error_Analysis.tex",
    "error_analysis/Error_Analysis_HW.tex",
]
STANDALONE_BUNDLE = "https://data1b.fullyjustified.net/tlextras-2022.0r0.tar"
# Their .tex and PDF files, which aren't sources of a project guide sharing the folder
STANDALONE_FILES = {SRC / rel for rel in STANDALONE} | {(SRC / rel).with_suffix(".pdf")
                                                         for rel in STANDALONE}

# Notebooks that compute figure data for a guide; run by --figures (paths relative to SRC)
FIGURE_SCRIPTS = [
    "HCl_DCl/src/images/vibrot_energy_diagram.py",
    "NMR/src/figures/lineshape.py",
]

# Log warnings worth reporting (the rest are routine)
WARNING_PATTERNS = [
    re.compile(r"LaTeX Warning: (Reference|Citation) `[^']+' .*undefined"),
    re.compile(r"LaTeX Warning: Float too large.*"),
    re.compile(r"^! .*"),
]


@dataclass
class Guide:
    name: str  # folder relative to SRC, e.g. "HCl_DCl" or "python_intro/Python_Intro.tex"
    kind: str  # "project" or "standalone"
    path: Path  # project folder, or the .tex file
    output: str  # PDF file name
    pdf: Path  # where Tectonic writes the PDF
    dest: Path  # where the finished PDF ends up

    def sources(self):
        """Files whose changes should trigger a rebuild."""
        if self.kind == "project":
            files = [p for p in self.path.rglob("*")
                     if p.is_file() and "build" not in p.relative_to(self.path).parts
                     and p not in STANDALONE_FILES]
        else:
            files = [self.path]
        return files + [p for p in SHARED.rglob("*") if p.is_file()]

    def newest_source(self):
        return max(p.stat().st_mtime for p in self.sources())

    def stale_reason(self):
        """Why the PDF needs rebuilding, or None if it is current.  Besides
        edited sources, this catches a PDF whose date no longer matches the
        guide's last commit (e.g. after committing a non-source file)."""
        if not self.dest.exists():
            return "no PDF"
        if self.dest.stat().st_mtime < self.newest_source():
            return "sources changed"
        if (dated := pdf_date(self.dest)) != (due := source_date(self)):
            return f"dated {dated}, should be {due}"
        return None

    def is_current(self):
        return self.stale_reason() is None


def discover():
    guides = []
    for toml in sorted(SRC.rglob("Tectonic.toml")):
        folder = toml.parent
        if SKIP_DIRS & set(folder.relative_to(SRC).parts):
            continue
        config = tomllib.loads(toml.read_text())
        for output in config["output"]:
            out = output["name"]
            guides.append(Guide(
                name=str(folder.relative_to(SRC)), kind="project", path=folder,
                output=f"{out}.pdf", pdf=folder / "build" / out / f"{out}.pdf",
                dest=ROOT / f"{out}.pdf"))
    for rel in STANDALONE:
        tex = SRC / rel
        pdf = tex.with_suffix(".pdf")
        guides.append(Guide(name=rel, kind="standalone", path=tex,
                            output=pdf.name, pdf=pdf, dest=pdf))
    return guides


def select(guides, patterns):
    """Match guides by path (a guide folder, a file in one, or a parent folder)
    or else by part of the name (case-insensitive)."""
    chosen = []
    for pattern in patterns:
        path = Path(pattern).expanduser().resolve()
        if path.exists():
            matches = [g for g in guides
                       if path.is_relative_to(g.path) or g.path.is_relative_to(path)]
        else:
            matches = [g for g in guides
                       if pattern.lower() in g.name.lower() or pattern.lower() in g.output.lower()]
        if not matches:
            sys.exit(f"No guide matches '{pattern}'. Try `uv run build.py --list`.")
        chosen += [g for g in matches if g not in chosen]
    return chosen


def source_date(guide):
    """The day of the last commit touching the guide or shared/ (in the
    committer's time zone), or today if either has uncommitted changes."""
    def git(*args):
        result = subprocess.run(["git", *args, "--", guide.path, SHARED],
                                cwd=ROOT, capture_output=True, text=True)
        return result.stdout.strip() if result.returncode == 0 else None

    day = datetime.date.today()
    if git("status", "--porcelain") == "":
        if committed := git("log", "-1", "--format=%cd", "--date=format:%Y-%m-%d"):
            day = datetime.date.fromisoformat(committed)
    return day


def source_date_epoch(guide):
    """Noon UTC on the guide's source_date.  Whole days keep a PDF built just
    before committing identical to one rebuilt from the commit."""
    noon = datetime.datetime.combine(source_date(guide), datetime.time(12),
                                     tzinfo=datetime.timezone.utc)
    return str(int(noon.timestamp()))


def pdf_date(pdf):
    """The CreationDate day of a PDF built by Tectonic, or None.  Tectonic
    keeps the document info in a compressed object stream."""
    data = pdf.read_bytes()
    for m in re.finditer(rb"/Type\s*/ObjStm.*?stream\r?\n", data, re.S):
        try:
            text = zlib.decompressobj().decompress(data[m.end():])
        except zlib.error:
            continue
        if found := re.search(rb"/CreationDate\s*\(D:(\d{4})(\d\d)(\d\d)", text):
            return datetime.date(*map(int, found.groups()))
    return None


def tool_env(guide):
    """PATH with this environment's scripts (pygmentize) first, plus a fixed
    SOURCE_DATE_EPOCH so the PDF only changes when its content does."""
    env = dict(os.environ)
    env["PATH"] = sysconfig.get_path("scripts") + os.pathsep + env.get("PATH", "")
    env.setdefault("SOURCE_DATE_EPOCH", source_date_epoch(guide))
    return env


def run_figure_scripts(guides):
    """Run the figure-data notebooks belonging to the given guides."""
    scripts = [SRC / s for s in FIGURE_SCRIPTS
               if any((SRC / s).is_relative_to(g.path) for g in guides if g.kind == "project")]
    for script in scripts:
        print(f"  figures: {script.relative_to(SRC)}")
        result = subprocess.run(["uv", "run", "--quiet", script], cwd=script.parent,
                                capture_output=True, text=True)
        if result.returncode != 0:
            print(result.stdout + result.stderr)
            sys.exit(f"Figure script failed: {script.relative_to(SRC)}")


def warnings_in(log):
    if not log.exists():
        return []
    found = []
    for line in log.read_text(errors="replace").splitlines():
        for pattern in WARNING_PATTERNS:
            if pattern.search(line) and line.strip() not in found:
                found.append(line.strip())
    return found


def build(guide):
    """Build one guide; return (ok, seconds, warnings, output text)."""
    start = time.monotonic()
    env = tool_env(guide)
    if guide.kind == "project":
        result = subprocess.run(["tectonic", "-X", "build", "--keep-logs"], cwd=guide.path,
                                env=env, capture_output=True, text=True)
        ok = result.returncode == 0 and guide.pdf.exists()
        log = guide.pdf.with_suffix(".log")
        if ok:
            guide.dest.unlink(missing_ok=True)  # may be an old symlink into build/
            shutil.copy2(guide.pdf, guide.dest)
        found = warnings_in(log)
    else:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["tectonic", "-X", "compile", "--keep-logs", "--outdir", tmp,
                 "-b", STANDALONE_BUNDLE, "-Z", "shell-escape", "-Z", f"search-path={SHARED}",
                 guide.path.name],
                cwd=guide.path.parent, env=env, capture_output=True, text=True)
            built = Path(tmp) / guide.output
            ok = result.returncode == 0 and built.exists()
            if ok:
                shutil.copy2(built, guide.dest)
            found = warnings_in(Path(tmp) / guide.path.with_suffix(".log").name)
    return ok, time.monotonic() - start, found, result.stdout + result.stderr


def report(guide, ok, seconds, found, output):
    where = guide.dest.relative_to(ROOT)
    if ok:
        print(f"  ✓ {guide.name}  ({seconds:.0f} s) → {where}")
    else:
        print(f"  ✗ {guide.name}  ({seconds:.0f} s) FAILED")
        errors = [l for l in output.splitlines() if l.startswith("error")]
        for line in (errors or output.splitlines())[-15:]:
            print(f"      {line}")
    for line in found:
        print(f"      warning: {line}")


def run_builds(guides, jobs):
    failed = []
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        for guide, result in zip(guides, pool.map(build, guides)):
            report(guide, *result)
            if not result[0]:
                failed.append(guide)
    return failed


def watch(guides, jobs):
    print(f"Watching {', '.join(g.name for g in guides)} (Ctrl-C to stop)")
    attempted = {g.name: 0.0 for g in guides}
    try:
        while True:
            due = [g for g in guides if g.newest_source() > attempted[g.name]]
            if due:
                for g in due:
                    attempted[g.name] = g.newest_source()
                print(time.strftime("[%H:%M:%S] building"))
                run_builds(due, jobs)
            time.sleep(1)
    except KeyboardInterrupt:
        print()


def main():
    sys.stdout.reconfigure(line_buffering=True)  # progress shows up even when piped
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0],
        epilog="examples:" + __doc__.split("Examples:")[1],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("guides", nargs="*",
                        help="guides to build: part of a name (e.g. hcl, fret) or a path; "
                             "named guides are always rebuilt")
    parser.add_argument("-f", "--force", action="store_true",
                        help="rebuild even if the PDF is up to date")
    parser.add_argument("-w", "--watch", action="store_true",
                        help="rebuild the selected guides whenever their sources change")
    parser.add_argument("--figures", action="store_true",
                        help="regenerate figure data (FIGURE_SCRIPTS) for the selected guides first")
    parser.add_argument("-j", "--jobs", type=int, default=1,
                        help="number of guides to build at once (default 1)")
    parser.add_argument("-l", "--list", action="store_true", help="list guides and exit")
    parser.add_argument("--clean", action="store_true",
                        help="delete the build/ folders of the selected guides and exit")
    args = parser.parse_args()

    guides = discover()
    selected = select(guides, args.guides) if args.guides else guides

    if args.list:
        for g in selected:
            reason = g.stale_reason()
            state = f"needs build ({reason})" if reason else "current"
            print(f"  {g.name:<40} {g.output:<26} {state}")
        return

    if args.clean:
        for g in selected:
            if g.kind == "project" and (g.path / "build").exists():
                shutil.rmtree(g.path / "build")
                print(f"  removed {g.name}/build")
        return

    if shutil.which("tectonic") is None:
        sys.exit("tectonic not found: install it with `brew install tectonic` "
                 "(see https://tectonic-typesetting.github.io).")

    if args.figures:
        run_figure_scripts(selected)

    if args.watch:
        if not args.guides:
            sys.exit("--watch needs the guide(s) to watch, e.g. `uv run build.py hcl --watch`.")
        watch(selected, args.jobs)
        return

    if not (args.guides or args.force):
        selected = [g for g in selected if not g.is_current()]
        if not selected:
            print("All guides are up to date (use --force to rebuild).")
            return

    print(f"Building {len(selected)} guide(s) with Tectonic")
    failed = run_builds(selected, args.jobs)
    if failed:
        sys.exit(f"{len(failed)} guide(s) failed: {', '.join(g.name for g in failed)}")


if __name__ == "__main__":
    main()
