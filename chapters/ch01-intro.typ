// ─────────────────────────────────────────────────────────────────────────────
// Chapter 1 — Template demo
// ─────────────────────────────────────────────────────────────────────────────
#import "../template.typ": note, warning, tip, code-example

= Chapter Title

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor
incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis
nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

== Section Heading

Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore
eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt
in culpa qui officia deserunt mollit anim id est laborum.

=== Subsection Heading

Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac
turpis egestas. Vestibulum tortor quam, feugiat vitae, ultricies eget.

== Code Blocks

Inline code looks like `some_function(x)` within a sentence. Display code
blocks are rendered with syntax highlighting:

```python
def greet(name: str) -> str:
    """Return a greeting string."""
    return f"Hello, {name}!"

for person in ["Alice", "Bob", "Carol"]:
    print(greet(person))
```

== Admonitions

#note[
  This is a note. Use it for supplementary information that helps the reader
  but is not essential to the main flow.
]

#tip[
  This is a tip. Use it to highlight a useful technique or shortcut.
]

#warning[
  This is a warning. Use it to flag potential pitfalls or important caveats.
]

== Formulae

Inline formulae sit within the text, for example the quadratic formula
$x = (-b plus.minus sqrt(b^2 - 4 a c)) / (2a)$, and the reader moves on.

Display formulae are centred on their own line:

$ sum_(k=1)^n k = (n(n + 1)) / 2 $
