# Models You Can Trust

% Status: first full draft. Ch. 8 per private/book-plan.md §2 (unchanged by
% this draft, per David's explicit instruction). Worked example throughout
% is the round-cell family's own can (outer cylinder minus inner cylinder,
% wall thickness as the live parameter) rather than the L-bracket the
% source lecture (private/CAx-Programmierung - 10 Optimierung.md) used -
% the same shape Ch. 12 later optimizes at h = 2r, so this chapter and
% that one share one function instead of introducing two.
%
% Every failure mode shown below was run against the installed CadQuery
% func API (not build123d, which the source lecture actually uses and
% which returns/accepts narrower types) and is quoted with its real,
% observed output:
% - wall == r_outer: inner cylinder degenerates to d=0, the cut removes
%   nothing, result is a valid Solid with volume 16540.485321150263 -
%   exactly cf.cylinder(d=18, h=65).Volume() to the last printed digit.
%   No exception, no isValid() complaint.
% - wall > r_outer: inner diameter goes negative, cf.cylinder itself
%   raises OCP.OCP.Standard.Standard_ConstructionError with an empty
%   message.
% - wall <= 0 (i.e. inner radius >= outer radius, tested at wall=0 and
%   wall=-1): cut returns an empty Compound, isValid() True, Volume()
%   0.0, Solids() == [].
% - Oversized fillet radius on the can's rim (5.0 mm against a 2.0 mm
%   wall): cf.fillet raises StdFail_NotDone ("BRep_API: command not
%   done"); min(radius, wall * 0.45) avoids it, verified at both 1.0 and
%   5.0 mm requested radius collapsing to the same valid result.
% - Analytic volume check: pi * (r_outer**2 - (r_outer-wall)**2) * h
%   against cell_can(9.0, 2.0, 65.0).Volume() agree to 9e-13 mm^3.
% - Collision check via cf.intersect(a, b).Volume(): reusing Ch. 4's own
%   pocket numbers (cell_radius=9.0, clearance=0.3, pocket_depth=3.0),
%   pitch 18.6 mm (= 2 * pocket radius) gives exactly 0.0, pitch 18.0 mm
%   gives 5.64 mm^3 of measurable overlap.
% Ch. 5 already covers isValid() returning False on a nonzero-volume
% result and the topological naming problem in full (its own worked
% examples, not repeated here) - this chapter explicitly builds on both
% rather than re-teaching them, and adds the complementary case Ch. 5
% does not: isValid() returning True on a result that is silently empty
% or silently wrong.

## Validating Parameters Before the Kernel Runs

A parametric model is a function: numbers go in, a shape comes out.
Every chapter so far has treated that function's domain as if it were
the numbers a person actually tried – a radius, a height, a wall
thickness, each one plausible because whoever wrote the script picked
a plausible value. Nothing about the function itself enforces that.
`r_outer`, `wall`, and `height` are each just a `float`; the language
accepts a negative one, a zero one, a wall wider than the part it is
supposed to belong to, exactly as readily as it accepts a good one, and
hands all of them straight to the kernel to find out what happens. A
model is **robust** to the extent that its behavior is actually known
across that whole domain – not just the corner of it a person happened
to try while developing it – and this chapter is about closing that
gap: rejecting the inputs that are simply wrong, tolerating the ones
that are merely inconvenient, and checking the result even when the
input was fine.

The round cell can this chapter builds around is deliberately the
simplest shape that has a domain worth worrying about: a cylindrical
shell, cut as an outer cylinder minus a slightly smaller inner one,
three numbers in – an outer radius, a wall thickness, a height.

```python
from cadquery import Solid
from cadquery import func as cf


def cell_can(r_outer: float, wall: float, height: float) -> Solid:
    outer = cf.cylinder(d=2 * r_outer, h=height)
    inner = cf.cylinder(d=2 * (r_outer - wall), h=height)
    return outer - inner


cell_can(9.0, 2.0, 65.0)  # an ordinary 2 mm wall
```

Nobody sits down and decides to make a wall as thick as the can's own
radius. The dangerous combinations arrive a different way: `wall`
computed from other quantities rather than typed in by hand – solved
backward from a required inner volume, say, or read from a component
table alongside a new outer radius that does not fit it – or swept
automatically across a range by an optimizer or a batch job over many
named variants, the way Chapter 9's release pipeline and Chapter 12's
optimization loop both do. Nobody looks at each combination a script
like that touches; whatever the function does with a bad one is what
actually happens, unattended.

Pushing the wall up to exactly the outer radius is one way to see what
that function actually does, without waiting for an optimizer to find
it by accident:

```python
too_thick = cell_can(9.0, 9.0, 65.0)
print(too_thick.isValid(), round(too_thick.Volume(), 1))
```

This prints `True` and `16540.5` – exactly the volume of a solid
cylinder with no cavity in it at all. At `wall == r_outer` the inner
cylinder's own diameter is `0`; the kernel is willing to construct that
degenerate cylinder, the cut removes essentially nothing from it, and
the function hands back a can that is not hollow, still reporting
itself valid. Ch. 5 already showed `isValid()` return `False` on a
shape with a perfectly ordinary-looking volume; this is the
complementary failure – `isValid()` says `True`, and the shape is wrong
in a way no validity checker is built to catch, because nothing about a
solid cylinder is actually invalid.

Push the wall past the outer radius and the failure changes character
entirely:

```python
cell_can(9.0, 10.0, 65.0)
```

```
Standard_ConstructionError
```

`r_outer - wall` is now negative, `cf.cylinder` is asked for a negative
diameter, and the kernel's own construction code raises directly – a
bare, message-less error from the layer underneath. Whichever side of
`wall == r_outer` the mistake lands on, the reader learns about it in
the least useful way available: a wrong-but-valid part, or a crash with
nothing to say why.

The fix is to state the constraint the numbers already implied and
check it before any of this runs:

```python
def cell_can(r_outer: float, wall: float, height: float) -> Solid:
    if not 0 < wall < r_outer:
        raise ValueError(f"wall must be between 0 and {r_outer}, got {wall}")
    if height <= 0:
        raise ValueError(f"height must be positive, got {height}")
    outer = cf.cylinder(d=2 * r_outer, h=height)
    inner = cf.cylinder(d=2 * (r_outer - wall), h=height)
    return outer - inner
```

`if`/`raise` belongs in front of the kernel call, not after it – an
arithmetic comparison costs nothing to evaluate, and it turns both
failures above into one clear `ValueError` naming exactly which
argument was wrong, before the kernel ever sees a negative diameter or
a degenerate one.

## Soft Limits: Capping Instead of Crashing

Not every bad value is invalid in the same sense. A wall thickness of
`-1` describes nothing; a fillet radius that happens to be a little
larger than the wall can round can still describe a can, just not the
one that number literally asked for – the geometrically sensible answer
is the largest rounding the wall actually allows, not an exception.

```python
def cell_can(r_outer: float, wall: float, height: float, rim_fillet: float = 1.0) -> Solid:
    if not 0 < wall < r_outer:
        raise ValueError(f"wall must be between 0 and {r_outer}, got {wall}")
    if height <= 0:
        raise ValueError(f"height must be positive, got {height}")
    outer = cf.cylinder(d=2 * r_outer, h=height)
    inner = cf.cylinder(d=2 * (r_outer - wall), h=height)
    can = outer - inner
    top_outer_edge = max(can.edges(">Z").Edges(), key=lambda e: e.radius())
    return cf.fillet(can, top_outer_edge, rim_fillet)
```

Called with `rim_fillet=5.0` against a 2 mm wall, this raises
`StdFail_NotDone` – the kernel's own way of saying the rounding this
asked for does not fit in the material given. Capping the radius
before the fillet call, rather than catching the exception after it,
keeps the function's result geometrically sane however the caller's
number is chosen:

```python
    rim_fillet = min(rim_fillet, wall * 0.45)
```

Requesting `1.0` mm and requesting `5.0` mm against the same 2 mm wall
now build the identical, valid result – the second one silently
capped to `0.9` mm rather than failing. The `0.45` is not a universal
constant; it is a margin under the theoretical `0.5 * wall` bound at
which the fillet becomes tangent to itself, a safety factor for exactly
this kind of geometrically motivated limit. It is not the right move
for the earlier section's `wall <= 0` – there is no sensible "capped"
wall thickness for a negative number, and hiding that behind a silent
clamp would only replace one silent failure with another, better
disguised one. Soft-capping belongs where a real geometric ceiling
exists to cap to; where a value is simply nonsensical, `if`/`raise`
stays the right tool.

## Testing Geometry, Not Just Trusting It

`isValid()` catches structural nonsense; it does not catch a can that is
the wrong size. `cell_can`'s own material – outer cylinder minus inner
cylinder – has a closed-form volume, and checking the function against
it costs nothing a validity check does not already cost:

```python
import math

r_outer, wall, height = 9.0, 2.0, 65.0
can = cell_can(r_outer, wall, height)
analytic = math.pi * (r_outer**2 - (r_outer - wall) ** 2) * height
print(can.Volume() - analytic)
```

This prints a number on the order of `1e-12` – floating-point noise, not
a real discrepancy. The same idea, applied instead of assumed, is what
would have caught the `wall == r_outer` failure two sections back
without ever inspecting the shape by eye: a can whose volume matches a
solid cylinder's, not a hollow one's, fails this check immediately.

A second property worth testing directly is one geometry alone cannot
see: whether two cans, placed where a design puts them, actually
collide. Chapter 4's own tray positions pocket cylinders on a grid at a
pitch chosen from the cell radius and a clearance; `cf.intersect` turns
"do these two overlap" into a number instead of a look in the viewer:

```python
cell_radius, clearance, pocket_depth = 9.0, 0.3, 3.0
pocket_r = cell_radius + clearance
pocket = cf.cylinder(d=2 * pocket_r, h=pocket_depth)

for pitch in (18.6, 18.0):
    other = pocket.translate((pitch, 0, 0))
    print(pitch, cf.intersect(pocket, other).Volume())
```

At `18.6` mm – twice the pocket radius, the spacing the clearance
calculation actually promises – the overlap volume is exactly `0.0`.
Tighten the pitch to `18.0` mm and it comes back `5.64` mm³: a real,
measurable interference, the kind a hex-packed grid can produce quietly
if a later change shrinks the spacing without anyone re-deriving it.
`cf.intersect(a, b).Volume() > 0` is a collision check that costs one
boolean, cheap enough to run on every neighboring pair in a pattern
rather than trusted from the formula that placed them.

## Types as Contracts

Every version of `cell_can` so far has carried a return annotation,
`-> Solid`, the same practice this book has followed on every function
signature since Chapter 2. A type hint is a checked promise only where
something actually checks it: a type checker such as mypy reads
`wall: float` and flags a call that passes a string before the code
ever runs, and an editor uses the same annotation to complete
`can.` correctly – real guarantees, but both of them live entirely at
the level of the *source code*, before any of it executes.

None of that reaches a value built from a kernel operation. This
chapter's very first `cell_can`, before any validation was added,
carried the same `-> Solid` promise:

```python
def cell_can_unvalidated(r_outer: float, wall: float, height: float) -> Solid:
    outer = cf.cylinder(d=2 * r_outer, h=height)
    inner = cf.cylinder(d=2 * (r_outer - wall), h=height)
    return outer - inner


degenerate = cell_can_unvalidated(9.0, 0.0, 65.0)
print(type(degenerate).__name__)
```

This prints `Compound`, not `Solid` – the return annotation promised a
type the function does not actually always deliver, and no type
checker caught the mismatch, because nothing about the *source code*
is wrong. `outer - inner` really can return either type depending on
values only known once the kernel runs, and a static tool has no way
to evaluate those values in advance. A type hint here is documentation
of intent, not a guarantee of what came back; telling the two apart at
the point a result is actually used is what `isinstance` is for:

```python
def cell_can(r_outer: float, wall: float, height: float, rim_fillet: float = 1.0) -> Solid:
    if not 0 < wall < r_outer:
        raise ValueError(f"wall must be between 0 and {r_outer}, got {wall}")
    if height <= 0:
        raise ValueError(f"height must be positive, got {height}")
    outer = cf.cylinder(d=2 * r_outer, h=height)
    inner = cf.cylinder(d=2 * (r_outer - wall), h=height)
    can = outer - inner
    if not isinstance(can, Solid):
        raise RuntimeError("cut did not produce a single solid")
    rim_fillet = min(rim_fillet, wall * 0.45)
    top_outer_edge = max(can.edges(">Z").Edges(), key=lambda e: e.radius())
    return cf.fillet(can, top_outer_edge, rim_fillet)
```

The input validation at the top of this function and the `isinstance`
check in the middle are answering two different questions.
`0 < wall < r_outer` states what the *caller* must guarantee;
`isinstance(can, Solid)` states what the *kernel* must have produced,
given that the caller did. Ordinary Python code narrows types this way
constantly – `assert isinstance(x, int)` before treating `x` as one –
and a `Shape` hierarchy with `Solid`, `Compound`, `Shell` and the rest
as genuinely distinct classes, not one grab-bag type, makes that
narrowing mean something concrete here: an unnarrowed `Shape` might not
have a single well-defined `Volume()` to check against the analytic
formula earlier in this chapter at all. This version's own `-> Solid`
annotation is finally true every time it runs – not because a type
checker enforces it, but because the `isinstance` check right above the
`return` refuses to let the function end any other way.

## Verification on Every Change

Every check this chapter has run so far – `isValid()`, the volume
comparison, the collision check – was typed at a prompt, read once, and
forgotten. That is fine for finding a bug in the moment, but it proves
nothing about tomorrow: nobody re-types `print(can.Volume() -
analytic)` before every future change to `cell_can`, so a change that
quietly breaks that match can sit in the repository for months before
anyone happens to run that exact line again.

A **test** turns a check like that into something that runs itself: a
small function that calls the code under test and states, with
`assert`, what must be true about the result, rather than printing a
number for a person to judge. It succeeds silently or fails loudly, the
same result whoever runs it and whenever they run it – the manual
checks earlier in this chapter, made repeatable. `pytest` is the tool
this book uses to collect and run functions like that; it needs no
special syntax to find them, only a name starting with `test_`:

```python
import pytest


def test_cell_can_matches_analytic_volume():
    r_outer, wall, height = 9.0, 2.0, 65.0
    can = cell_can(r_outer, wall, height, rim_fillet=0.5)
    analytic = math.pi * (r_outer**2 - (r_outer - wall) ** 2) * height
    assert can.isValid()
    assert abs(can.Volume() - analytic) < 1.0  # fillet removes a little material


def test_cell_can_rejects_wall_past_outer_radius():
    with pytest.raises(ValueError):
        cell_can(9.0, 10.0, 65.0)
```

Nothing about these two functions is CadQuery-specific; `assert` states
the invariant, `pytest.raises` states which input should fail and how,
the same vocabulary any Python test suite uses. Run on its own,
`pytest` reads a project's `tests/` directory, calls every function
matching that name, and reports which passed and which did not – the
same two checks this chapter already ran by hand, now able to outlive
the terminal they were first typed into.

A test that only runs when a person remembers to run it is still only
as reliable as that person's memory, though – exactly the gap between
"this code is correct" and "this code was correct the day someone last
checked it." **Continuous integration** (CI) closes that gap by moving
the trigger: instead of a person deciding to run the tests, a shared
server runs them automatically on every change pushed to the
repository, before that change gets to call itself finished. GitHub
Actions is one such server, configured with a file describing what to
run and when:

```yaml
name: geometry tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install cadquery pytest
      - run: pytest tests/
```

Every `push` or `pull_request` checks the repository out fresh,
installs CadQuery and pytest, and runs the same `tests/` directory a
developer would run locally – except automatically, on every change,
whether or not its author remembered to. A change that quietly moves
`wall` past `r_outer` somewhere upstream, or loosens the validation
this chapter just added, fails this job before it fails a person – the
same fail-fast argument as `if`/`raise`, applied now to the
repository's history instead of to one function call.

:::{note} Try It
- Add a rectangular wiring slot to Chapter 4's tray, and give its
  internal corners a fillet. A real end mill has a radius and cannot cut
  a sharp internal corner; write a check that flags any internal corner
  smaller than a stated tool radius, and confirm it actually rejects a
  slot filleted too small before rejecting one that looks fine in the
  viewer.
- Extend the collision check above from one pair of pockets to every
  neighboring pair in a hex-packed grid (Chapter 4's own Try It). At
  what pitch does the first collision appear, and does it match `2 *
  pocket_r` the way the two-pocket case above did?
- Add the same three checks this chapter ran on `cell_can` –
  `isValid()`, the analytic volume, and an `isinstance` narrowing after
  the boolean – to `make_cell` from Chapter 4, for all three of its
  named `CellSpec` variants at once.
:::
