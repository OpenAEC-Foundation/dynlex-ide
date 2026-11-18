# DynLex IDE

DynLex Studio is the browser IDE at [dynlex.com/ide/](https://dynlex.com/ide/). This repository owns Studio and the reusable DynLex code editor used by Studio, Farm and River.

## Run Studio

With Git, Python 3.10+ and Node.js 22+ installed, run these commands from this checkout.

```sh
python3 scripts/build.py
python3 -m http.server --bind 127.0.0.1 --directory build/site 8000
```

Open <http://127.0.0.1:8000/ide/>. The build fetches the pinned [website host](https://github.com/OpenAEC-Foundation/dynlex-website), installs its locked build tools, and compiles this checkout's Studio sources with its pinned compiler and UI packages. This preserves the production routes, shader gallery, saved theme and links from documentation. Deployment belongs to the website repository.

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
