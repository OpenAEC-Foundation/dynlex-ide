# Code editor

Import `editor/source_workspace.dl` to add language analysis to source controls.
A workspace discovers every `editor` in an instance and owns its document models.
It follows page and tab selection, prioritizes focused/visible sources, debounces
edits, and rejects results from older source revisions or project contexts.

```dynlex
set workspace to a UI source workspace in instance rooted at "file:///workspace"
set editor to the UI source editor labeled "Plan" in workspace
set files to a new JSON-RPC object
configure UI source document (editor's document) named "plan.dl" at "file:///workspace/plan.dl" prefixed by "import project/vocabulary.dl\n\n" using UI CPU analysis with files files
free files
```

Each source control starts with its own project, so examples that share `main.dl`
do not leak names or import suggestions into each other. The main document is
`editor's document's project's entry`. A project owns its `profiles`, `files`,
main document and imported document models. Additional files are copied; analysis
profiles are consumed. Profiles are JSON data, including CPU, fragment, and
combined vertex/fragment helpers; the client accepts arbitrary profile sets.

`the UI source files of project` returns an owned JSON source map for analysis or
execution, including the configured main filename, protected prefix and all
provided files. Free that snapshot after serialization. Synchronize its workspace
before collecting it so current edits are included. Later edits do not change the
snapshot, and collecting it does not modify the provided file map.

`the UI source files of project with main source source` builds the same owned
snapshot using a supplied main source. It retains the configured prefix and
provided files, while preserving the editable draft, document revisions and
language-service context. This lets an application rebuild a saved, applied
program while the user continues editing a newer draft.

To retain imported source in the same project, use `a UI source document named
filename at uri containing source in project`. These models have no hidden prefix
and start read-only. `the UI source document at uri in project` returns an existing
model or a null pointer when the URI has not been loaded. Project changes
invalidate dependent analysis and queries without changing another file's source
revision when its contents stay the same. Replacing a provided file updates its
loaded snapshot and revision. Removing it marks that model unavailable; restoring
the file revives the retained model with current content. Imported libraries
outside the provided file map keep their snapshots. Read-only views follow the
document model, so their preceding control text cannot overwrite a replaced file.
Free standalone projects with `free UI source project project`; workspace
cleanup releases the projects belonging to its controls.

Import `editor/source_panes.dl` for `source pane "Plan" containing text using
appearance`. This is an ordinary immutable description containing an editor,
filename, Back, Main file, Outline, Instances and Find buttons. A workspace scopes those controls to their
pane. Bare editors and panes use identical document and interaction code.
Find/Replace is also library code shared by every pane. Ctrl/Cmd+F opens Find;
Ctrl/Cmd+H focuses Replace. F3/Shift+F3 or query Enter/Shift+Enter move between
matches without taking typing focus away. Replace Enter or Ctrl/Cmd+Enter replaces
one match; adding Alt to Ctrl/Cmd+Enter replaces all matches in one undoable
transaction. Alt+Enter enters a literal query or replacement newline. Escape
closes Find and returns to the source selection. Queries, options and replacement
text belong to the pane, including when visiting imported sources. Search folds
Unicode simple case and optionally requires whole words; CRLF, LF and CR query
line breaks match while retaining original source byte ranges. These are literal
queries, without regular-expression or replacement-template interpretation.
Read-only sources remain searchable and reject replacements. Search and current
match marks occupy their own named layers, independently of execution and other
application annotations.

Enable `editor/source_tools.dl` once per workspace for completion and definition
navigation. Right-click opens Go to Definition for the clicked token; Shift+F10 opens the context menu at the caret. Ctrl-click or Cmd-click looks up the symbol under the pointer. F12 uses the caret. Alt+Left returns through the location history. Visits retain each
file's independent undo/redo, annotations, Unicode selection and scroll position.
Imported sources are read-only; the main source's own read-only policy is restored
on return.
Runtime policy updates also survive navigation, including updates made while an
imported file is visible. Document protection and application policy share the
same editing gate, without overwriting each other's state.
Disabled controls use the shared foreground presentation rule for captions,
inline links and semantic text. Drawing retains authored appearances and token
colors, so enabling a control restores them. Read-only text keeps its colors.
Disabled inline links retire their hover underline immediately.

Token themes also accept modifier selectors, such as `function.callDepth1`,
`variable.constant`, `*.constant`, or `function.constant.callDepth1`. Modifier
names and bit positions come from each document's language-server legend. Rules
with more matching modifiers win; an exact token type wins over a wildcard at
equal modifier counts. The last rule wins a remaining tie. A rule naming an
unavailable modifier does not match. Modifier legends are retained per document,
so changing a connection's legend cannot recolor another retained project.
The default call colors are generated from DynLex's canonical
`shared/call-colors.json`. Run `python3 scripts/generate_source_colors.py
--dynlex <compiler-checkout>` after changing that palette. SDK export and shared
tests check that the generated declarations match it.

Ctrl+Shift+O (Cmd+Shift+O on macOS) opens an outline of authored sections, including nested declarations. Choosing
a section visits its selection range through the same Unicode and protected
context mapping as definition navigation. F8 lists inferred instances at the
caret and initially selects the compiler's current instance. Choosing another
instance notifies the language service, then refreshes semantic colors and hover
facts after acknowledgement. Both tools support read-only imports. Stale results
and acknowledgements are discarded when their source or project changes.

A contextual lightbulb appears only after the language service returns an enabled code action for the current selection. Ctrl+. (Cmd+. on macOS), F7 or clicking the lightbulb opens diagnostic quick fixes. The request retains opaque
compiler diagnostic data, maps Unicode and hidden context through the shared
source model, and refreshes diagnostics immediately before dispatch. Opening
fixes while analysis is pending therefore uses the completed analysis. Disabled
actions cannot be selected. Edits are staged and committed through the standard
text-edit planner, with one undo operation per changed source. A command following
an action uses the same command handler as completion.

`editor/source_transactions.dl` adapts workspace text edits to project-owned source
models. Prepare with `a UI source transaction applying edit for editor in view`,
then call `commit UI source transaction transaction in view` and free its owned
data with `free UI source transaction transaction`. Pass the transaction's address
to the latter two operations. Preparation synchronizes existing control edits,
then stages the requested changes. Commit rechecks source snapshots and access
policy before modifying any text. It updates all models and buffers before
notifying application handlers. Parked sources retain their own undo and caret;
updating one does not replace the visible imported source. Ordered versioned text
changes use the preceding staged snapshot. Invalid, stale, protected or read-only
targets reject the whole proposed edit. Resource operations such as creating,
renaming or deleting files belong to project storage and are not text edits.

`ui/choice_popovers.dl` supplies the same choice surface for completion and
inspection, without a JSON or language-service dependency. Callers add labels and
enabled states, supply placement, a borrowed view font and appearance, then handle
input results: 0 passes through, 1 consumes input, 2 activates the selected row,
and 3 requests dismissal. Arrows, Home/End, Page Up/Down, wheel and pointer input
share selection and scrolling. Disabled rows are skipped; an invisible menu
cannot activate a choice. Dismissal retires its hit geometry. Release owned rows
with `clear UI choice popover popup in view` before freeing the caller's state.

Source tools also provide pointer hover inspection in every registered source
control. Requests follow the document's protected-prefix/Unicode mapping and are
rejected when its source or project changes. The popover inherits its editor's
font and colors. Plain signatures and Markdown code descriptions retain literal
backticks and source escapes. Its text supports selection and copying; a short
leave interval allows crossing the gap from the inspected text into the popover.
Completion menus, composition and source-selection gestures take precedence.
An unchanged popover becomes idle.

Use `the UI main source of editor in workspace at seconds seconds` for Run, Save
or Share, rather than reading the currently displayed control. Use `the UI text
state for document in editor in instance` to apply execution marks to a parked
main source while an import is displayed.

`replace UI main source of editor in view with text at seconds seconds` starts a
fresh edit session for the main document without navigating away from an import.
It clears undo/redo and annotations and retires that control's IME context, even
when the incoming text is unchanged. `load UI main source of editor in view from
text at seconds seconds` also returns to the main file and clears navigation
history. Both accept borrowed source strings and preserve unrelated focus and
composition in other controls. Explicit `show UI source document document in
editor in view` focuses a document; `bind UI source document document in editor
in view` changes its presentation without taking focus.

The language client keeps one open model and version per file while retaining
its main file's inference context. Moving between files in a project does not
close them. Before answering an imported-file query, it synchronizes the main
source and refreshes dependent semantics without sending a text change for an
unchanged import. Leaving the project closes every open model before replacing
the source set.

The visible editor sends minimal UTF-16 range edits and versioned
`dynlex/activeCursorChanged` notifications. Single-line drafts retain the last
committed semantic context until the caret leaves the line or editing focus
leaves the source. Completion and lexical highlighting still use the live draft.
Newlines and edits spanning multiple lines commit immediately. Moving within a
line sends no additional cursor notification. Imported writable documents use the
same connection and line locks; typing does not replace their project transport.

Diagnostics belong to the project analysis snapshot. Reports are retained by URI,
including sources whose views have not been created. The main semantic-token
response is the ordered completion barrier for its analysis; committing that
snapshot clears old reports for clean imports as well. Opening a view applies
the retained report. Closed and superseded project replies do not overwrite it.
Changed reports advance a presentation generation independently of source edits;
identical reports preserve it.

During an update, call `the next visible UI source work in workspace in view at
(view's seconds) seconds`. It synchronizes source text and editing focus before
scheduling work, including cursor-only line commits and focus loss. A nonzero
`step` owns a JSON `payload` to send through the language transport. Deliver its
reply to `the UI language reply response at step step in (workspace's client)`;
that returns the next work item. Synchronize the workspace before delivering
replies so programmatic edits also invalidate outstanding results. The platform
implements `project`, `exchange`, and `reset`; document policy stays in DynLex.
A zero step has no payload. Free each sent payload after serializing it.

A query may set `parameters factory` to a DynLex function pointer receiving
`a pointer to UI source query` and `a pointer to UI source document`, returning
`nothing`. It refreshes the query's owned `parameters` in place after source
analysis and immediately before serialization. Preparing parameters preserves the
request's generation and cancellation rules. Each new request clears the slot's
previous callback. The complete `source_query_preparation` fixture exercises
dispatch and slot reuse; quick fixes use the hook for diagnostic context.

`present UI source workspace workspace using (the default UI source token theme)`
applies results to their source controls. Each binding may point `diagnostics`
and `status` at optional text controls. `clean text` and `ready text` configure
empty diagnostic and successful-analysis captions without changing editor policy. Source colors and diagnostics share UTF-16
to UTF-8 mapping through hidden imports, including same-line prefixes and astral
characters. Execution background marks remain independent. Theme entries are
ordinary `UI source token style` data. Call `free UI source workspace workspace`
before closing its UI instance. Transport failures should call `fail UI source
workspace workspace`; shared presentation then reports the failure in each active
source editor.

Use `the light UI source token theme` for a light editor and
`the default UI source token theme` for a dark editor. Both use the compiler's
canonical colors for nested calls. Variables, named parameters and variable arguments share
one neutral foreground per theme. Studio uses the OpenAEC secondary text colors,
`#D6D3D1` on dark backgrounds and `#57534E` on light backgrounds. [OpenAEC color tokens](https://github.com/OpenAEC-Foundation/OpenAEC-style-book/blob/main/packages/tokens/tokens/colors.json)

Tokens without a matching style inherit the
editor's foreground; an explicit `*` selector can color every token instead.
Changing themes keeps execution backgrounds, editor contents and undo history.

The shared client handles both directions of the language protocol. It replies
to semantic-token refresh requests and reports method-not-found for unsupported
server requests, preserving numeric and string identifiers. Replies are sent
before pending editor work resumes. A refresh requests tokens again without
resending unchanged source. Changed token data advances a separate presentation
generation, so inferred-instance choices can change colors without an edit.
Identical data retains cached colors.
Refreshes received after closing a document are acknowledged without invalidating
its retained results. A closed project stays idle until it needs analysis again.
The server's diagnostic clearing on close likewise leaves the editor's cached
results intact.

