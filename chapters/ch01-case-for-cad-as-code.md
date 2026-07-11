# The Case for CAD as Code


## Models as Programs

This book is about an approach to mechanical design in which a part is
described by a program: the model is code, written in a general-purpose
programming language, and the geometry is computed from it. The approach is
not new – engineers have described geometry programmatically for decades –
but three developments have recently moved it from a niche into a serious
option: mature open-source geometry kernels of the same kind that power
commercial CAD systems, libraries that make them accessible from Python, and
AI assistants that have substantially lowered the cost of writing and
maintaining code.

What does such a model look like? In its simplest form it is a function. The
parameters are the dimensions and choices that define the design; the body
constructs the geometry step by step; the return value is an exact solid
that can be displayed, measured, and exported in standard formats. Larger
models are composed from smaller ones, exactly as programs are composed from
functions. The following sketch describes an electronics enclosure; the
function names are invented, but the structure is representative:

```python
def enclosure(board: Board) -> Shape:
    case = hollow_box(board.length + 8, board.width + 8, height=22, wall=2)
    case -= connector_openings(board.connectors)
    case += mounting_bosses(board.hole_positions)
    return case
```

Even without knowing the underlying operations, the model can be read: what
depends on what, which dimensions are derived, where a design decision is
encoded. The expression `board.length + 8` records more than a number – it
states an intention: the case follows the board, at a fixed margin. Change
the board, and the case follows with the margin intact. This is **design
intent** made explicit: the relationships that are meant to survive change,
written where every reader – and every future edit – can see them.
Constructing models so that intent is stated and preserved is a craft of its
own; Chapter 4 is devoted to it. How the geometric operations behind such
functions work is the subject of Part I; for this chapter, the structure is
enough.

Two families of consequences follow, one from the model being *text* and one
from it being *executable*.

Because the model is text, the standard instruments for working with text
apply. Versions can be compared line by line, so a change is visible as a
change, together with a recorded explanation of why it was made. Models can
live in the same version-control systems used for software, with history,
parallel branches, and review before changes are accepted. These are the
ordinary working conditions of every software project, and they become
available to mechanical design at the moment the design becomes text. Conventional CAD formats, being opaque binaries, do not
support these operations on their content – which is why managing them
requires dedicated infrastructure around the files rather than tools that
look inside them.
% Optional figure, Ch. 9 forward-ref: geometric diff of two revisions.

Because the model is executable, it can be run – and rerun. A parametric
family is the same function evaluated over a table of inputs; a change
propagates by regeneration instead of by editing each member. Derived
artifacts – exchange files, meshes, drawings of quantities, bills of
materials – can be produced by scripts and therefore reproduced at any time.
And a model can carry its own checks: small tests that verify dimensions,
clearances, mass, or validity of the geometry, run automatically after every
change. Chapter 8 develops this into a working practice.

The same property connects design to the rest of computational engineering.
Meshing, simulation, optimization, and data analysis are already code; a
model that is a function participates in them directly. A simulation study
can sweep its parameters, an optimizer can search them, and the results can
feed back into the model without a manual step in between. Where design work
involves simulation and iteration – an increasing share, in our experience –
this integration is the approach's largest payoff, and Part III of this book
is devoted to it.

A note on AI is warranted, because it amplifies several of the advantages
above. Language-model assistants operate on text, and a design model written
in Python is text of a tractable kind: it can be drafted, explained,
restructured, and reviewed with the same tools used for the rest of the
model. The reason this is useful rather than reckless is the checkability
described above – generated code can be diffed, tested, and reviewed before
it is trusted. This book assumes a reader who works in that mode. Some
arrive from engineering and bring code into their design work; others arrive
from software, data, or simulation and extend their work to physical parts.

The approach has costs, and they should be stated plainly. It must be
learned; constructions have to be thought through rather than adjusted by
direct manipulation; and free-form exploration of a shape remains easier in
an interactive system. The gains lie where designs are parametric, repeated,
verified, automated, or coupled to simulation. The remainder of this chapter
supplies the background for everything that follows: how CAD systems
represent geometry internally, where the code-first approach comes from,
which tools this book uses, and how to read the rest of the book.

## How CAD Systems Represent Geometry

A program like `enclosure` computes a solid. It is worth asking early what
kind of object that is, because the answer determines what can be done with
a model – measured, modified, exchanged – and it explains the file formats
that appear throughout this book.

The sketch itself suggests a natural first answer. The enclosure was built
from simple shapes combined by additions and subtractions – so why not store
exactly that? A model would then be a tree: primitive solids such as boxes,
cylinders, and spheres at the leaves, boolean operations at the branches.
This scheme exists, has a name – **constructive solid geometry**, CSG –
and is thoroughly intuitive: it is easy to assume that CAD systems store
models in just this way. The first generation of code-based CAD tools did
represent models exactly so.

Intuitive as it is, CSG cannot carry mechanical design, for two related
reasons. The first is expressiveness: many engineered surfaces are simply
not boolean combinations of primitives. The rounded transition a fillet
produces, the free-form faces of a car body or a turbine blade – no tree of
boxes and cylinders yields these shapes. The second is addressability: an
operation like "round this edge" needs an edge to refer to, and in a CSG
model there is none. The model is an expression; its faces and edges exist
only implicitly, as the outcome of evaluating it.

Professional CAD therefore represents the result directly: the *boundary*
of the solid – a set of faces, joined at edges, which meet at vertices,
where every face carries an exact mathematical surface (a plane, a
cylinder, a free-form patch) and every edge an exact curve. This is the
**boundary representation**, B-Rep. It has the expressiveness CSG lacks, its
faces and edges are there to be referred to, and it is exact: a bore is a
cylindrical face with a radius, not a bundle of facets that approximates
one. CAD systems work on boundary representations internally, and
standardized exchange formats carry them between systems, which is why a
model produced by code can be opened, measured, and machined anywhere. The price is complexity: a
boundary representation is an intricate data structure, and constructing
and maintaining it correctly is the job of a **geometry kernel** – a
substantial piece of software in its own right, which the libraries in this
book build on rather than reimplement.

A third form appears wherever geometry leaves the design world: the
**mesh**.
A mesh describes a surface as a collection of flat triangles – concretely,
a list of corner points in space and a list of triangles, each connecting
three of them. Flat pieces cannot follow a curved surface exactly, so
curvature is rendered by quantity: where the surface bends, many small
triangles trace it; where it is flat, a few large ones suffice. The bore
that is a single cylindrical face with a radius in the boundary
representation becomes, in a mesh, a ring of a few dozen narrow facets – a
closer approximation the more triangles are spent on it. How many is a
choice made when the mesh is generated, usually as a tolerance: the largest
distance the faceted surface may deviate from the exact one. What remains
is a data structure of great simplicity – points and triangles, nothing
else: no dimensions, no named faces, no parameters. That simplicity is why
meshes are what 3D printers, simulation codes, and graphics hardware
consume. It is also why the step is one-way: the exact surfaces, and with
them the ability to change the design meaningfully, do not survive the
translation. In this book meshes appear where they belong – as derived
output for printing and simulation (Part III), never as the form in which a
design is kept.

% Figure: the same part three ways – CSG expression tree, B-Rep with faces
% and edges drawn, mesh with visible triangles at coarse tolerance.

Where does that leave the recipe – the operations, their order, their
parameters? Graphical CAD systems record it as a **feature tree** alongside the
geometry. In the approach of this book, the recipe is the program itself:
the source code holds the parameters, the construction steps, and the
design intent, while the kernel holds the evaluated boundary. This is why
the code may *read* like CSG – simple parts composed by booleans – while
every step in fact produces a full boundary representation, fillets and
free-form faces included. And it closes the loop on §1.1: version control
and review apply to the recipe; exchange files and meshes carry the result.

Chapter 2 puts vocabulary on the boundary representation by inspecting the
first models the reader builds; Chapter 5 examines its structure in depth;
Chapter 6 treats the mathematics of the surfaces themselves.

## Origins of Open-Source Code-First CAD

Describing parts in a formal language is older than interactive CAD –
numerically controlled machines were programmed from textual descriptions
of geometry before graphical workstations existed – and proprietary CAD
systems have carried scripting facilities for decades; the next section
returns to those. The line that leads to this
book's tools, however, is the open-source one, and it begins with a kernel.

In the early 1990s, Matra Datavision, a French CAD company, developed a
full boundary-representation kernel as the foundation for its next
generation of products. The business did not survive the decade; the kernel
did. In 1999 it was released as open source under the name **Open CASCADE
Technology**, OCCT, and it has been developed continuously ever since – since
2013 under the LGPL. The consequence is easy to understate: the hardest
part of a professional CAD system, the exact geometric core, has now been
openly available for a quarter of a century.

Software grew on it in several directions. **FreeCAD**, first released in
2002, wrapped the kernel in an open-source parametric CAD application in the
familiar graphical style and made it scriptable from Python. OpenSCAD,
first released in 2010 and carried by the 3D-printing wave, put a different
idea in front of a wide audience: the model *is* the script. Its geometry
was CSG and its output was meshes – the limits of the previous section in
working form – but it showed a generation of makers that parts can be text,
with much of what §1.1 describes: parameters, sharing, version control.

**CadQuery**, whose first releases appeared in 2013, joined the two
threads: parametric models as Python programs on the professional kernel,
with exact exchange formats rather than meshes alone as a first-class goal.
It now addresses the kernel through **OCP**, a set of thin Python bindings
to OCCT maintained as part of the CadQuery project. **build123d**, first
released in 2023, wraps the same bindings in an independent framework,
derived in part from CadQuery but organized around different API choices.
These two are today's main options for Python code-first CAD: a shared
foundation, two different convictions about what the interface should feel
like. This book works with CadQuery; Appendix B provides a phrasebook
between the two.

For quick orientation, the main steps in that line are these:

```{raw:typst}
#import "table-style.typ": tableStyle, columnStyle
```

| Year | Project | Why it matters |
|---|---|---|
| 1999 | OCCT | professional B-Rep kernel released as open source |
| 2002 | FreeCAD | graphical parametric CAD on OCCT, scriptable from Python |
| 2010 | OpenSCAD | popularized the idea that the model itself can be a script |
| 2013 | CadQuery | Python code-first CAD on a professional kernel |
| 2023 | build123d | alternative Python interface on the same OCCT/OCP foundation |

## The Stack Used in This Book


The tools of this book form a stack, easiest to describe from the bottom
up. At the bottom sits OCCT, the geometry kernel: it implements the boundary
representation – the solids and their faces, the boolean operations,
fillets and lofts, the exact surfaces, the reading and writing of exchange
formats. Above it sits OCP, the thin Python bindings that expose the kernel
to Python. Above those sits CadQuery, the modeling library used throughout
this book: it turns the kernel's raw interfaces into concise modeling code;
the book uses its function-based API, introduced in Chapter 2. Models are
viewed with the **OCP CAD Viewer** inside Visual Studio Code, and around
all of this lies the ordinary Python ecosystem, including the meshing,
simulation, and optimization libraries of Part III. Every layer is open
source.

% Figure: the layer diagram – kernel, bindings, modeling library, viewers,
% surrounding ecosystem.

It is worth stating what kind of software this is. Readers who know the
scripting facilities of graphical CAD systems – macros, journals, embedded
languages – know them as ways to automate an application: a session is
running, a document is open, and the script drives both. Here there is no
application. CadQuery is a library imported into an ordinary Python
program; the program is the model, and the kernel is called the way any
other library is called, in a plain Python process that runs wherever
Python runs – a laptop, a build server, a compute cluster. Both kinds of
automation have their place; they are different in kind.

The choice of Python deserves a word. The computations these models are
meant to join – meshing, simulation, optimization, data analysis – largely
live in Python already, so writing the geometry in the same language puts
model and computation into one interpreter, with nothing between them but
function calls. A general-purpose language also makes the model a full
citizen of a real programming environment: it can read a parts table, call
an optimizer, run under a test framework, and use any library it needs.
Python is, moreover, the language this book's two kinds of readers most
plausibly share – routinely taught to engineers, and home ground for
scientific computing. The mature open-source bindings to a professional
kernel happen to exist in Python, as the previous section explained, so the
choice follows the ecology as much as any abstract merit. Current AI
assistants are, as it happens, at their strongest in Python as well. Python
is not chosen for speed, and it does not need to be: the geometry
is computed inside the compiled kernel, and Python orchestrates. Readers
who use the scientific Python stack will recognize this division of labor.

Two things the stack does not cover should be said plainly. Engineering
drawings are outside the scope of this book, and integration with graphical
CAD systems goes only as far as the standard exchange formats carry.
Installation instructions age quickly and are kept where they can be
updated: Chapter 2 contains enough to get started, Appendix A the details.

## The Plan of This Book, and How to Read It

This book is organized in three parts. Part I teaches the mechanics of
building models as code: first solids, profiles, parameters, and the basic
operations that turn them into usable parts. Part II steps back and explains
what those models are built from: the structure of a boundary
representation, the mathematics of curves and surfaces, and the techniques
needed for free-form geometry. Part III treats models as engineering
artifacts inside a larger workflow: verified, assembled, exported, meshed,
simulated, and searched by computation. Several examples run through more
than one chapter – the battery pack, the enclosure generator, the clutch
brick, the fixture – so that individual techniques accumulate into larger
designs.

The book can be read straight through, but it is also meant to be used by
reference. Readers who are new to code-first CAD should begin at Chapter 2
and build in order. Readers who already work inside an established CAD
environment may find Chapters 5 and 9 natural entry points: one explains how
to read and reason about the geometry that code produces, the other how such
models fit into assembly and release processes that already exist. Adoption
is gradual by nature; the book is organized so that each part pays for
itself even if the whole stack is not adopted at once.

Two habits matter throughout this book and become more explicit as it
progresses: checking models under change, and writing code whose structure
is clear enough to test and compose. In the early chapters those habits
appear first as small printed measurements, validity checks, and functions
whose inputs and outputs are stated plainly; later they are made systematic.
Chapter 8 gathers that practice into a single argument and gives it a name.
