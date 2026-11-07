from semantic_compiler.expansion.registry import list_domains
from semantic_compiler.expansion.registry.loader import TEMPLATE_DIR, load_templates


def test_all_templates_load_and_validate():
    templates = load_templates()
    paths = list(TEMPLATE_DIR.glob("*.yaml"))
    assert paths
    stems = set()
    for path in paths:
        assert path.stem in templates, path.name
        assert templates[path.stem].domain == path.stem
        stems.add(path.stem)
    assert set(templates) == stems
    assert set(list_domains()) == stems
