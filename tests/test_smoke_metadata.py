"""Validate metadata used by the generated-project smoke tests."""

import sys

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


@pytest.mark.parametrize("project_layout", ["src", "flat"])
def test_flit_metadata(cookies, project_layout):
    """Flit must receive PEP 621 metadata and the actual module name."""
    result = cookies.bake(
        extra_context={
            "build_system": "flit",
            "project_layout": project_layout,
            "package_slug": "different_module",
        }
    )
    assert result.exit_code == 0
    metadata = tomllib.loads(
        (result.project_path / "pyproject.toml").read_text()
    )
    assert "packages" not in metadata["project"]
    assert metadata["tool"]["flit"]["module"]["name"] == "different_module"


@pytest.mark.parametrize("build_system", ["poetry", "uv"])
@pytest.mark.parametrize("engine", ["sphinx(rst)", "jupyter-book", "quarto"])
def test_documentation_dependencies(cookies, build_system, engine):
    """Documentation projects must declare compatible build dependencies."""
    result = cookies.bake(
        extra_context={
            "build_system": build_system,
            "documentation_engine": engine,
            "use_makim": "yes",
        }
    )
    assert result.exit_code == 0
    metadata = tomllib.loads(
        (result.project_path / "pyproject.toml").read_text()
    )
    if build_system == "poetry":
        dependencies = metadata["tool"]["poetry"]["group"]["dev"][
            "dependencies"
        ]
        assert "click" in dependencies
        if engine == "quarto":
            assert dependencies["griffe"] == "<2"
        elif engine == "jupyter-book":
            assert dependencies["jupyter-book"] == ">=0.15.1,<2"
    else:
        dependencies = metadata["project"]["optional-dependencies"]["dev"]
        assert "click >= 8" in dependencies
        if engine == "quarto":
            assert "griffe < 2" in dependencies
        elif engine == "jupyter-book":
            assert "jupyter-book >= 0.15.1,<2" in dependencies
