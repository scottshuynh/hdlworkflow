import pytest


# Marks every test parametrized with `eda_tool` with a marker of the same name (e.g. eda_tool="nvc" -> @pytest.mark.nvc).
# Markers are registered only in pyproject.toml; an eda_tool value without a registered marker raises
# PytestUnknownMarkWarning, which filterwarnings = ["error"] turns into a collection error.
# tryfirst so the marks are in place before pytest's own -m deselection runs.
@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(items):
    for item in items:
        callspec = getattr(item, "callspec", None)
        if callspec is None:
            continue
        eda_tool = callspec.params.get("eda_tool")
        if eda_tool is None:
            continue
        if item.get_closest_marker(eda_tool) is None:
            item.add_marker(eda_tool)
