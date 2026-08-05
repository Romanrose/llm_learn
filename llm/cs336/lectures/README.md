# Spring 2026 CS336 lectures

This repository contains the lecture materials for Stanford's Language Modeling from Scratch (CS336).

## Executable lectures

These are named `lecture_XX.py`.

### Setup

        uv sync
        git clone https://github.com/percyliang/edtrace

You can compile a lecture by running:

        python execute.py -m lecture_01

which generates a `var/traces/lecture_01.json` and caches any images as
appropriate.

To view it locally:

Load a local server to view at `http://localhost:5173?trace=var/traces/sample.json`:

        npm run --prefix=edtrace/frontend dev

Deploy to the main website:

        npm run --prefix=edtrace/frontend build
        git add assets
        git ci -am "<some message>"
        git push

## Non-executable lectures

These are named `lecture_XX.pdf`.
