set shell := ['/bin/bash', '-cu']

@_default:
    just --list --unsorted --justfile {{justfile()}}


# HATCH
# show hatch metadata
metadata:
    hatch project metadata

# hatch build
build:
    hatch build

# remove build artifacts
clean:
    hatch run clean


# PYTEST
# pytest collection
collect *args:
    hatch run pytest --collect-only {{args}}

# run tests using hatch (try "-k name" to filter tests)
test *args:
    hatch run test {{args}}

# generate and show html of coverage
covhtml:
    hatch run covhtml

# build a wheel, install it in a fresh venv, and import every module
check-install:
    #!/usr/bin/env bash
    set -euo pipefail
    cd "{{justfile_directory()}}"

    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT

    hatch build -t wheel "$tmp/dist"
    python3 -m venv "$tmp/venv"
    "$tmp/venv/bin/pip" install -q "$tmp"/dist/*.whl
    "$tmp/venv/bin/pip" check

    cd "$tmp"
    "$tmp/venv/bin/python" -I -c '
    import importlib
    import os
    import pkgutil
    import sys
    import warnings

    import pandas

    import icoscp

    venv = os.path.realpath(sys.argv[1])
    where = os.path.realpath(icoscp.__file__)
    print("icoscp: " + icoscp.__version__ + " from " + where)
    print("python: " + sys.version.split()[0] + ", pandas: " + pandas.__version__)
    if not where.startswith(venv + os.sep):
        print("❌ icoscp was not imported from the temp venv", file=sys.stderr)
        sys.exit(1)

    ok = 0
    failed = []
    # onerror: a broken subpackage is already counted below; keep walking
    walk = pkgutil.walk_packages(icoscp.__path__, "icoscp.", onerror=lambda name: None)
    for mod in walk:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                # icoscp.cpb resets the filter to "always", so mute output too
                warnings.showwarning = lambda *args, **kwargs: None
                importlib.import_module(mod.name)
            ok += 1
        except Exception as exc:
            failed.append("%s: %s: %s" % (mod.name, type(exc).__name__, exc))

    print("ok: %d, failed: %d" % (ok, len(failed)))
    for line in failed:
        print("  " + line)
    sys.exit(1 if failed else 0)
    ' "$tmp/venv"

    echo "✓ installed wheel imports cleanly"


# RUFF
lint:
    hatch run lint:lint


# RELEASE
# usage: just release            (defaults to patch)
#        just release minor
#        just release major
# bump version + __date__, lint, test, build, upload to test.pypi.org
release part="patch":
    #!/usr/bin/env bash
    set -euo pipefail
    cd "{{justfile_directory()}}"

    if [[ -n "$(git status --porcelain)" ]]; then
        echo "❌ working tree is dirty — commit or stash first" >&2
        exit 1
    fi

    just lint
    just test

    old_version=$(hatch version)
    hatch version {{part}}
    new_version=$(hatch version)
    today=$(date -u +%Y-%m-%d)
    sed -i -E "s|^__date__ = .*|__date__ = \"${today}\"|" src/icoscp/__init__.py
    echo "→ bumped ${old_version} → ${new_version} (${today})"

    if ! grep -qE "^## ${new_version}([[:space:]]|$)" docs/icoscp/changelog.md; then
        echo "❌ docs/icoscp/changelog.md is missing a '## ${new_version}' entry" >&2
        echo "   add the entry, then re-run. revert version bump with:" >&2
        echo "     git checkout -- src/icoscp/__init__.py" >&2
        exit 1
    fi

    just clean
    just build

    test_token_file="${HOME}/.ssh/icoscp_testpypi.token"
    if [[ ! -r "${test_token_file}" ]]; then
        echo "❌ token file not found: ${test_token_file}" >&2
        echo "   create one at https://test.pypi.org/manage/account/#api-tokens" >&2
        echo "   and save the raw token (the 'pypi-AgEN...' string, no prefix)" >&2
        echo "   to ${test_token_file}. hatch uploads with user=__token__," >&2
        echo "   password=<that token>." >&2
        exit 1
    fi
    HATCH_INDEX_USER=__token__ \
        HATCH_INDEX_AUTH="$(<"${test_token_file}")" \
        hatch publish -r test

    echo
    echo "✓ uploaded ${new_version} to test.pypi.org"
    echo
    echo "smoke test in a fresh venv:"
    echo "  pip install --index-url https://test.pypi.org/simple/ \\"
    echo "      --extra-index-url https://pypi.org/simple \\"
    echo "      \"icoscp==${new_version}\""
    echo
    echo "then run 'just publish' to push to pypi.org and tag the release"


# upload current dist/ to pypi.org, commit version bump, tag release
publish:
    #!/usr/bin/env bash
    set -euo pipefail
    cd "{{justfile_directory()}}"

    version=$(hatch version)

    if [[ ! -d dist || -z "$(ls -A dist 2>/dev/null)" ]]; then
        echo "❌ dist/ is empty — run 'just release' first" >&2
        exit 1
    fi

    pypi_token_file="${HOME}/.ssh/icoscp_pypi.token"
    if [[ -r "${pypi_token_file}" ]]; then
        HATCH_INDEX_USER=__token__ \
            HATCH_INDEX_AUTH="$(<"${pypi_token_file}")" \
            hatch publish
    else
        echo "ℹ no token file at ${pypi_token_file} — hatch will prompt." >&2
        echo "  username: __token__" >&2
        echo "  password: your pypi.org token (NOT the test.pypi one)" >&2
        echo "  tip: save the raw token to ${pypi_token_file} to skip this prompt next time." >&2
        hatch publish
    fi

    git add src/icoscp/__init__.py docs/icoscp/changelog.md
    git commit -m "release ${version}"
    git tag "v${version}"
    echo "✓ published ${version} and tagged v${version}"
    echo "  push with: git push && git push --tags"
