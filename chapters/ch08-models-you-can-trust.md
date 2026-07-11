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
%
% Second pass, after auditing X2/X3 lecture messages against the draft:
% - The Types as Contracts section's original claim ("no type checker
%   caught the mismatch") was FALSE - verified directly, both mypy and
%   pyright DO flag `cell_can_unvalidated`'s `-> Solid` before it ever
%   runs (`error: Incompatible return value type (got "Shape", expected
%   "Solid")`), because CadQuery types `Solid.__sub__` as returning
%   `Shape` honestly, not imprecisely. David's correction: this is not a
%   stub-accuracy gap, it's that a boolean's true output type is
%   genuinely undecidable from source alone (depends on the specific
%   geometry at runtime) - Shape is the CORRECT annotation for such an
%   operation, and isinstance narrowing is the only place that can ever
%   resolve it, not a workaround for lazy typing. Rewrote the section
%   around this. cast()/`# type: ignore` added as the anti-pattern this
%   narrowing replaces - David: "type:ignore is evil," encourage
%   mypy/pyright/Pylance use routinely, not just when something breaks.
% - Third pass: David flagged the isinstance check on `can` (the boolean
%   result) as "silly... we know it will never fail" once wall/height are
%   validated - correct, verified directly (couldn't produce a Compound
%   from valid inputs). Rather than swap the whole chapter's worked
%   example for something riskier (considered a sweep per Ch. 7 - rejected,
%   the pinched-tube case is always a valid Solid, isValid()-catches-
%   wrongness is Ch. 7's own point, not a Solid/Compound type problem),
%   kept cell_can and fixed the honesty of the claim instead: David - "in
%   real life I'd use assert here" - correct, and exposed a real bug in
%   my own verification. My earlier "both mypy and pyright report zero
%   issues" claim was checked against a SIMPLIFIED version missing the
%   trailing `cf.fillet` call; `cf.fillet` is ALSO typed to return `Shape`
%   (a fillet can fail to stay a clean solid too), so the real function
%   needs a SECOND `assert isinstance(filleted, Solid)` after the fillet
%   call, not just one after the boolean - verified: without it mypy
%   flags the final `return` line; with it, both mypy and pyright report
%   zero issues on the actual full function. Both narrowings changed from
%   `if not isinstance(...): raise RuntimeError(...)` to bare
%   `assert isinstance(...)`, matching X3's own assert-for-internal-
%   invariants rule properly this time (my prior draft had the if/raise
%   vs assert mapping backwards). This also resolves David's "trivial"
%   complaint honestly: the boolean's own assert IS close to a formality
%   given validated inputs, stated as such in the text; the fillet's
%   assert is the less trivial one, backed by the soft-cap argument from
%   §2 rather than a simple bound, and is where the real teaching content
%   now sits.
% - pytest.approx(analytic, abs=5.0) replaces the old manual
%   `abs(diff) < 1.0` - that old tolerance was simply wrong, caught by
%   re-verifying: the actual diff for r_outer=9.0, wall=2.0, height=65.0,
%   rim_fillet=0.5 is ~2.996 mm^3, not under 1.0. Re-verified abs=5.0
%   passes.
% - Added: bounding-box + face-count checks in §3 (named in book-plan's
%   own Ch. 8 description, never actually written until now); pure-
%   function-is-testable principle opening §5; the "reimplementation"
%   antipattern (test recomputes the function's own formula) after the
%   pytest example; a refactor-keeps-tests-green Try It bullet.
% 2026-07-11 pass: intro paragraph added; §Types opening corrected (its
% "same practice since Chapter 2" claim went stale when David stripped
% return hints from Chs. 3-7 on purpose - now says return annotations
% were deliberately rare until this section supplies the machinery);
% "Ch. 5" -> "Chapter 5"; two brand mentions reworded ("the library's
% source", "specific to geometry"); ~13 "X's own" tics swept; new
% figure ch08_cell_can.py (three-quarter cutaway of the finished can,
% laid over per the ch12-buoy tall-figure lesson - the chapter never
% showed its part). Spot-re-verified: bbox prints exactly "65.0 18.0"
% (no tolerance slack), 4 faces plain / 5 filleted (TORUS rim),
% too_thick prints "True 16540.5".
% Domain-sweep test ADDED (David approved, in @pytest.mark.parametrize
% form at his direction - stacked decorators for the cross product;
% he'd reject a bare nested loop in review, and parametrize is also
% semantically right: 16 named cases vs. a loop that stops at the
% first failure). Verified: 4x4 grid of (r_outer, wall) all valid WITH
% the cap in 0.2 s; WITHOUT the cap 8 of 16 combinations raise
% StdFail_NotDone (every thin wall); worst |V - analytic|/analytic
% across the grid is 0.00155, so rel=0.005 has 3x margin.
% - Deliberately NOT added: TDD/red-green-refactor, unit-vs-integration-
%   test distinction, the other X2 antipatterns beyond reimplementation,
%   angle-unit-in-parameter-name convention (no natural landing spot yet
%   - Ch. 3's rz= is CadQuery's own kwarg, already clarified inline as
%   degrees) - scoped out as checklist bloat / no current landing point,
%   not oversights.

This chapter is about earning the word "trust": what it takes for a
parametric model to behave correctly on inputs nobody hand-picked, and
for that correctness to survive the model's next edit. The tools are
an escalation – validating inputs before the kernel sees them, capping
values where a geometric ceiling exists, checking the result's own
volume, size, and topology, making type annotations into promises a
checker verifies, and finally handing all of it to a test runner so it
happens on every change. Habits from earlier chapters – Chapter 2's
two-line `assert`, Chapter 5's `isValid()`, Chapter 7's
valid-but-wrong tube – converge here into one systematic practice.

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

Nobody sits down and decides to make a wall as thick as the can's
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
cylinder's diameter is `0`; the kernel is willing to construct that
degenerate cylinder, the cut removes essentially nothing from it, and
the function hands back a can that is not hollow, still reporting
itself valid. Chapter 5 already showed `isValid()` return `False` on a
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
diameter, and the kernel's construction code raises directly – a
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
`StdFail_NotDone` – the kernel's way of saying the rounding this
asked for does not fit in the material given. Capping the radius
before the fillet call, rather than catching the exception after it,
keeps the function's result geometrically sane however the caller's
number is chosen:

```python
    rim_fillet = min(rim_fillet, wall * 0.45)
```

Requesting `1.0` mm and requesting `5.0` mm against the same 2 mm wall
now build the identical, valid result – the second one silently
capped to `0.9` mm rather than failing.

:::{figure} ../figures/generated/ch08-cell-can.png
:width: 70%

The can this chapter builds and rebuilds, cut open for the page: a
2 mm wall and the rim fillet, requested at 1.0 mm and capped to
0.9 mm.
:::

The `0.45` is not a universal
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
the wrong size. The shape `cell_can` builds – outer cylinder minus inner
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
a real discrepancy. The same idea, applied instead of assumed, would
have caught this chapter's earlier `wall == r_outer` failure
immediately, without ever inspecting the shape by eye: `too_thick`, the
solid cylinder `isValid()` reported as a perfectly good can, has a
volume that matches a solid cylinder's formula, not a hollow one's –
exactly what this check is built to notice.

A second property worth testing directly is one geometry alone cannot
see: whether two cans, placed where a design puts them, actually
collide. Chapter 4's tray positions pocket cylinders on a grid at a
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

Two more properties are worth checking as a matter of course, because
both are cheap and because either `wall == r_outer` or `wall > r_outer`
from the first section would have looked wrong on sight, not just in a
printed number: the can's outer size, and how many faces its
boundary is built from.

```python
can = cell_can(9.0, 2.0, 65.0)
bbox = can.BoundingBox()
print(bbox.zlen, bbox.xlen)
print(len(can.Faces()))
```

```
65.0 18.0
4
```

`bbox.zlen` matches `height` and `bbox.xlen` matches `2 * r_outer` –
both read directly off the can's geometry rather than assumed from
the parameters that were supposed to produce them, catching a scale
error a volume check alone might miss, since two shapes can share a
volume without sharing a size. Four faces – both cylinders, both end
caps – is the exact topology this construction is supposed to produce;
the filleted version from the previous section has five, a `TORUS`
face added at the rim. A face count that doesn't match is a first,
cheap sign that a boolean or a fillet did something other than
intended, before looking at a single number.

## Types as Contracts

Every version of `cell_can` so far has carried a return annotation,
`-> Solid`. Parameter annotations have been routine since Chapter 2;
return annotations on geometry, after a first appearance on
`plate_with_hole`, have been deliberately rare in this book – a return
type on kernel-produced geometry is a promise, and keeping it takes
exactly the machinery this section introduces. A type hint is a
checked promise only where
something actually checks it: a type checker such as **mypy** or
**pyright** reads a function's annotations and flags a mismatch before
the code ever runs, far cheaper than a boolean or a fillet call into
the kernel. Both are worth running routinely, not just once something
has already gone wrong.

This chapter's very first `cell_can`, before any validation was added,
returned `outer - inner` directly:

```python
def cell_can_unvalidated(r_outer: float, wall: float, height: float) -> Solid:
    outer = cf.cylinder(d=2 * r_outer, h=height)
    inner = cf.cylinder(d=2 * (r_outer - wall), h=height)
    return outer - inner
```

Running `mypy` against this file, without ever calling the function:

```
error: Incompatible return value type (got "Shape", expected "Solid")
```

`Shape` is the base class Chapter 5 introduced `Solid`, `Compound`,
and the rest of the hierarchy as belonging to – the general type that
covers all of them, used whenever the exact one is not yet known. In
the library's source code, the `-` operator is declared to return
`Shape`, not `Solid` – and that is worth taking seriously rather than
reading past, because a boolean's actual result genuinely depends on
the geometry involved. Two solids that touch, overlap, or cancel out
can produce a `Solid`, a `Compound`, or an empty result, and which one
happens is not decidable by reading the code that calls `-`; it
depends on values only the kernel resolves at the moment it runs.
Declaring the result as `Shape` is the *correct*, honest type for an
operation like that – not a looser placeholder standing in for
`Solid`, but the actual guarantee `-` is able to make ahead of time.
`cell_can_unvalidated`'s `-> Solid` was the real mistake here: it
promised a narrower type than the operation it is built from can
promise.

Going from `Shape` down to `Solid` is an instance of **type
narrowing**: telling a type checker that a value's actual type is more
specific than the type it was declared with, at a point in the code
where that has become true. Here it is not optional cleanup – it is
the only place that narrowing can happen, because it is the only point
where the actual value, not just its declared type, is available:

```python
can = outer - inner
assert isinstance(can, Solid)
```

`0 < wall < r_outer` already rules out the only inputs that could make
this particular cut come back as anything other than a `Solid`, so by
the time this line runs the assertion is close to a formality – cheap
insurance against a case validation has already excluded, not a real
branch. That is exactly what `assert` is for: a statement of something
that must be true given correct code above it, not a guard against a
value that might legitimately vary. `wall`'s bounds get `if`/`raise`
instead, further up, because they check a *caller's* input – something
that can be anything a caller decides to pass, not an internal
consequence of code already checked.

The fillet call two lines later is the less obvious case. Whether it
stays a clean `Solid` does not follow from a simple bound the way the
boolean above does; it follows from the soft-capping argument two
sections back, `rim_fillet = min(rim_fillet, wall * 0.45)`, capping the
radius under the point where the fillet becomes geometrically
impossible. `cf.fillet` is typed to return `Shape` for the same reason
`-` is – a fillet can fail to produce a clean solid too – so the same
narrowing belongs here as well, backed this time by a geometric
argument rather than an arithmetic one:

```python
def cell_can(r_outer: float, wall: float, height: float, rim_fillet: float = 1.0) -> Solid:
    if not 0 < wall < r_outer:
        raise ValueError(f"wall must be between 0 and {r_outer}, got {wall}")
    if height <= 0:
        raise ValueError(f"height must be positive, got {height}")
    outer = cf.cylinder(d=2 * r_outer, h=height)
    inner = cf.cylinder(d=2 * (r_outer - wall), h=height)
    can = outer - inner
    assert isinstance(can, Solid)
    rim_fillet = min(rim_fillet, wall * 0.45)
    top_outer_edge = max(can.edges(">Z").Edges(), key=lambda e: e.radius())
    filleted = cf.fillet(can, top_outer_edge, rim_fillet)
    assert isinstance(filleted, Solid)
    return filleted
```

Both `mypy` and `pyright` report zero issues against this version –
not because either annotation is trusted on faith, but because each
`assert isinstance(...)` is itself something both tools recognize as
narrowing: after it, they know the value really is a `Solid`, the same
fact the check enforces at runtime. Static and runtime checking agree
here for the same reason: two runtime checks are what make the
promises both are making actually true.

Two shortcuts exist that look like they solve the same problem and do
not. `cast(Solid, outer - inner)` tells the type checker to stop
complaining, with zero effect at runtime – the value is exactly as
uncertain as it was before, now with the warning that would have
caught it removed. `# type: ignore` silences the same message without
resolving it either. Both make the type checker's output look clean;
neither makes either return statement any truer. Treat either one
appearing on a line like this as worth asking about directly – almost
always an `assert isinstance` was skipped, not made unnecessary.

`0 < wall < r_outer` and the two `assert isinstance` checks are
answering different questions, worth keeping straight. `if wall <= 0:
raise` states what a *caller* must guarantee – something that can
legitimately be anything, so it has to be checked explicitly, with a
clear exception naming what went wrong. The two `assert` lines state
what the *kernel* must have produced, given that the caller already
held up its end – an internal invariant, true by construction if the
reasoning above each one is correct, which is exactly the case `assert`
exists for: not a check against unpredictable input, but a statement
that the code above it already made the outcome certain.

## Verification on Every Change

None of this chapter's checks would be worth automating if `cell_can`
itself were harder to call in isolation. It has been a **pure
function** since the first line of this chapter – geometry in,
geometry out, no viewer, no file write, no global state – which is
exactly why every check so far could be three lines at a prompt rather
than a small program of its own. A function that also opens a viewer
window or exports a file can still be checked, but every check then
pays for that extra work and has to route around it; keeping
construction separate from display and export is what keeps the
geometry itself this cheap to verify.

Every check this chapter has run so far – `isValid()`, the volume
comparison, the collision check – was typed at a prompt, read once, and
forgotten. That is fine for finding a bug in the moment, but it proves
nothing about tomorrow: nobody re-types `print(can.Volume() -
analytic)` before every future change to `cell_can`, so a change that
quietly breaks that match can sit in the repository for months before
anyone happens to run that exact line again.

A **unit test** turns a check like that into something that runs itself: a
small function that calls the code under test and states, with
`assert`, what must be true about the result, rather than printing a
number for a person to judge. It succeeds silently or fails loudly, the
same result whoever runs it and whenever they run it – the manual
checks earlier in this chapter, made repeatable. `pytest` is the tool
this book uses to collect and run functions like that; it needs no
special syntax to find them, only a name starting with `test_`.

Comparing the two volumes for exact equality would fail for a reason
that has nothing to do with `cell_can` being wrong: `0.1 + 0.2 == 0.3`
is `False` in Python, and every geometry operation accumulates the same
kind of floating-point rounding on the way to a final number.
`pytest.approx` states a tolerance explicitly instead of comparing bit
for bit:

```python
import pytest


def test_cell_can_matches_analytic_volume():
    r_outer, wall, height = 9.0, 2.0, 65.0
    can = cell_can(r_outer, wall, height, rim_fillet=0.5)
    analytic = math.pi * (r_outer**2 - (r_outer - wall) ** 2) * height
    assert can.isValid()
    assert can.Volume() == pytest.approx(analytic, abs=5.0)  # fillet removes a few mm³


def test_cell_can_rejects_wall_past_outer_radius():
    with pytest.raises(ValueError):
        cell_can(9.0, 10.0, 65.0)
```

One trap is worth naming before moving on. A unit test that recomputes
the same formula the function itself uses proves nothing, because a
mistake in that formula – a stray factor, a wrong sign – would sit
inside both the function and its own test, agreeing with each other
and wrong together. `test_cell_can_matches_analytic_volume` avoids this
by construction: `analytic` is a closed-form fact about a hollow
cylinder's volume, independent of how `cell_can` happens to build one
– not a restatement of `cell_can`'s construction steps in a
different order. A unit test's real job is checking a function against
a truth it does not already assume.

Nothing about these two test functions is specific to geometry; `assert`
states the invariant, `pytest.raises` states which input should fail
and how, the same vocabulary any Python test suite uses. Run on its
own, `pytest` reads a project's `tests/` directory, calls every
function matching that name, and reports which passed and which did
not – the same checks this chapter already ran by hand, now able to
outlive the terminal they were first typed into.

Both tests probe a single point of the domain, though – the same
`(9.0, 2.0, 65.0)` every check in this chapter has used. The opening
section defined robustness as behavior known across the *whole*
domain, and `pytest` has a purpose-built tool for saying exactly that,
`@pytest.mark.parametrize`: it runs one test body once per listed
value, and two stacked decorators run the whole cross product.

```python
@pytest.mark.parametrize("r_outer", [6.0, 9.0, 12.0, 21.0])
@pytest.mark.parametrize("wall", [0.5, 1.0, 2.0, 4.0])
def test_cell_can_across_the_domain(r_outer, wall):
    can = cell_can(r_outer, wall, height=65.0)
    analytic = math.pi * (r_outer**2 - (r_outer - wall) ** 2) * 65.0
    assert can.isValid()
    assert can.Volume() == pytest.approx(analytic, rel=0.005)  # fillet trims < 0.2%
```

Sixteen test cases from one function, each reported under its own
name, so a failure names the exact combination that broke – where a
plain loop over the same grid would stop at the first bad one and hide
the rest. The whole grid builds and checks in under two seconds, and it
earns its keep: remove the `rim_fillet` cap from two sections ago and
half of these sixteen combinations – every thin-walled one – crash
with `StdFail_NotDone`. This one test is what protects that soft limit
from being simplified away by a later edit that never saw the
reasoning behind it. The checked corner has become the checked domain.

A test that only runs when a person remembers to run it is still only
as reliable as that person's memory, though – exactly the gap between
"this code is correct" and "this code was correct the day someone last
checked it." **Continuous integration** (CI) closes that gap by moving
the trigger: instead of a person deciding to run the tests, a shared
server runs them automatically on every change pushed to the
repository, before that change gets to call itself finished. GitHub
Actions is one such server: a short configuration file, committed to
the repository like any other file, names the trigger – every `push`
or `pull_request` – and the steps to run on it: check the repository
out fresh, install CadQuery and pytest, then run `pytest tests/`,
exactly the command a developer would type locally.

Nothing about that sequence depends on a person remembering to run it.
A change that quietly moves `wall` past `r_outer` somewhere upstream,
or loosens the validation this chapter just added, fails this job
before it fails a person – the same fail-fast argument as `if`/`raise`,
applied now to the repository's history instead of to one function
call.

:::{note} Try It
- Add a rectangular wiring slot to Chapter 4's tray, and give its
  internal corners a fillet. A real end mill has a radius and cannot cut
  a sharp internal corner; write a check that flags any internal corner
  smaller than a stated tool radius, and confirm it actually rejects a
  slot filleted too small before rejecting one that looks fine in the
  viewer.
- Extend the collision check above from one pair of pockets to every
  neighboring pair in a hex-packed grid (Chapter 4's exercises). At
  what pitch does the first collision appear, and does it match `2 *
  pocket_r` the way the two-pocket case above did?
- Add the same three checks this chapter ran on `cell_can` –
  `isValid()`, the analytic volume, and an `isinstance` narrowing after
  the boolean – to `make_cell` from Chapter 4, for all three of its
  named `CellSpec` variants at once.
- Rebuild `cell_can`'s outer and inner cylinders with `extrude` on a
  circular profile instead of `cf.cylinder`, and rerun this chapter's
  tests unchanged. A test suite that does not need to change when
  the implementation does is what makes a rewrite like this safe to
  attempt in the first place.
:::
