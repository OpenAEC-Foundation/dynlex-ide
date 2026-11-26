# DynLex IDE

DynLex Studio is the browser IDE at [dynlex.com/ide/](https://dynlex.com/ide/). This repository owns Studio and the reusable DynLex code editor used by Studio, Farm and River.

## Run Studio

With Git, Python 3.10+ and Node.js 22+ installed, run these commands from this checkout.

```sh
python3 scripts/build.py
python3 -m http.server --bind 127.0.0.1 --directory build/site 8000
```

Open <http://127.0.0.1:8000/ide/>. The build fetches the pinned [website host](https://github.com/OpenAEC-Foundation/dynlex-website), installs its locked build tools, and compiles this checkout's Studio sources with its pinned compiler and UI packages. This preserves the production routes, shader gallery, saved theme and links from documentation. Deployment belongs to the website repository.

## Work with project files

The **File**, **Run**, **Debug**, **View** and **Help** menus group Studio's commands. The toolbar provides Run, Debug, Stop and Save, with step controls during a debug session. Hover an icon to see its action. **View** switches the inspector between Files, Debug, Problems and keyboard shortcuts, and changes the theme.

Studio’s **Files** panel shows the current program or shader project. Choose **File → New file**, enter a project-relative path such as `tools/math.dl`, then press Enter or choose **Create file**. Escape cancels the form. Select a file to edit it. **File → Rename file** accepts a new path, including a different directory. Update source imports that refer to the old name. **Delete file** asks for confirmation. Expand **Libraries** to browse the read-only modules supplied by this build.

Run always compiles the project entry with all its files. Studio saves editable projects in this browser and keeps shared examples in separate drafts. Use **File → Save source**, the Save icon, or Ctrl+S (Cmd+S on macOS) to download the current project file. Program output appears in the console below the editor, with Copy and Clear controls.

Right-click a symbol and choose **Go to definition**, or use F12. Ctrl-click on Windows or Linux, or Cmd-click on macOS, opens the definition directly. On an import path, this opens the file that the compiler resolved. **Back** or Alt+Left returns to the previous location.

A lightbulb appears beside the code when a quick fix is available at the caret. Click it to open the fixes, or press Ctrl+. (Cmd+. on macOS) or F7. Shift+F10 opens the editor context menu with the keyboard.

## Debug a program

Choose the Debug icon or **Debug → Start debugging** to compile the project for
debugging and pause before its first statement. The inspector opens the call
stack, variables and breakpoints. Use the toolbar or Debug menu to step over,
into or out, continue, pause, or stop. Studio's shortcuts are F5 (debug/continue),
F10 (step over), F11 (step into), Shift+F11 (step out), Shift+F5 (stop) and F9
(toggle a breakpoint on the caret's line).

While paused, hover over a variable to see its current runtime value. Select a
call-stack row to inspect that frame and source location. Click an expandable
variable row to inspect fields, array elements or a pointer's target. The current
statement is highlighted in yellow; breakpoints are marked in red. Editing source,
changing the project or leaving Studio stops the current debug session.

Browser debugging requires JavaScript Promise Integration for WebAssembly
(`WebAssembly.Suspending` and `WebAssembly.promising`). Use a current browser
with those APIs enabled. Shader programs use the shader preview controls.

Choose **＋ Add Library** to search the library catalog, select a library and add
it under an import name such as `ui`. The picker also accepts a GitHub repository,
SDK archive URL or local folder. Installed libraries have Update, Remove and
Documentation actions; their source is read-only under Libraries. Project drafts
retain exact dependency locks, and source packages and assets are cached in
IndexedDB. Use Ctrl+. on a missing library import to open the same picker.


## Embed the editor

The `editor/` library depends on [dynlex-ui](https://github.com/OpenAEC-Foundation/dynlex-ui). Mount the two packages next to each other. Import `editor/control.dl` for a bare code editor, `editor/source_panes.dl` for a pane with navigation and Find/Replace, or `editor/source_tools.dl` for the workspace and language-service controller. See the [editor API](docs/editor.md).

The `studio/` modules supply the IDE page, program execution, shader preview, source-link handling and appearance. The website supplies routing, services, application state and game-specific vocabulary.

```sh
python3 scripts/export_sdk.py --output build/dynlex-ide.zip
```

Use the consuming website's `scripts/update_dependency.py` to pin the exported archive.

## Verify

```sh
python3 scripts/build.py --test
```

For native compiler, Wasm allocation, language-server and background browser checks, supply a built compiler checkout and a UI checkout.

```sh
python3 scripts/test.py --dynlex ../dynlex --ui ../dynlex-ui --browser
```

Studio's navigation, themes, shared code links, program execution and shader integration also run in the website test suite.
