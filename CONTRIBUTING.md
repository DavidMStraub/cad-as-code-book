# Corrections

Corrections are welcome. If something in the book is wrong, does not
reproduce, or has been overtaken by a newer CadQuery, please open an issue.

For anything version-dependent, it helps to include what you ran:

```bash
uv run python -c "import cadquery; print(cadquery.__version__)"
```

## Pull requests

Typos, broken links and formatting fixes are easiest as pull requests.

For prose, an issue is more useful than a patch.

The [README](README.md) covers building the book, if you want to see a change
rendered. Prose is hard-wrapped at roughly 72 characters and code blocks are
formatted with Black at 92, which keeps diffs small.

## Licensing

Corrections are licensed under the terms of the material they change:
CC BY 4.0 for prose and figures, MIT for code and the template. See
[`LICENSE`](LICENSE) and [`LICENSE-CODE`](LICENSE-CODE).
