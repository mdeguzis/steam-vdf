from sphinx.cmd.build import build_main


def build_docs():
    build_main(["-b", "html", "docs", "docs/_build"])


if __name__ == "__main__":
    build_docs()
