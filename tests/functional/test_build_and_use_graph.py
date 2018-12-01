from grimp import build_graph

"""
For ease of reference, these are the imports of all the files:

testpackage: None
testpackage.one: None
testpackage.one.alpha: sys, pytest
testpackage.one.beta: testpackage.one.alpha
testpackage.one.gamma: testpackage.one.beta
testpackage.one.delta: None
testpackage.one.delta.blue: None
testpackage.two: None:
testpackage.two.alpha: testpackage.one.alpha
testpackage.two.beta: testpackage.one.alpha
testpackage.two.gamma: testpackage.two.beta, testpackage.utils
testpackage.utils: testpackage.one, testpackage.two.alpha

"""

# Mechanics
# ---------

def test_modules():
    graph = build_graph('testpackage')

    assert graph.modules == {
        'testpackage',
        'testpackage.one',
        'testpackage.one.alpha',
        'testpackage.one.beta',
        'testpackage.one.gamma',
        'testpackage.one.delta',
        'testpackage.one.delta.blue',
        'testpackage.two',
        'testpackage.two.alpha',
        'testpackage.two.beta',
        'testpackage.two.gamma',
        'testpackage.utils',
    }


def test_add_module():
    graph = build_graph('testpackage')
    number_of_modules = len(graph.modules)

    graph.add_module('foo')
    assert 'foo' in graph.modules
    assert number_of_modules + 1 == len(graph.modules)


def test_add_and_remove_import():
    graph = build_graph('testpackage')
    a = 'testpackage.one.delta.blue'
    b = 'testpackage.two.alpha'

    assert not graph.direct_import_exists(importer=b, imported=a)

    graph.add_import(importer=b, imported=a)

    assert graph.direct_import_exists(importer=b, imported=a)

    graph.remove_import(importer=b, imported=a)

    assert not graph.direct_import_exists(importer=b, imported=a)


# Descendants
# -----------

def test_find_children():
    graph = build_graph('testpackage')

    assert graph.find_children('testpackage.one') == {
        'testpackage.one.alpha',
        'testpackage.one.beta',
        'testpackage.one.gamma',
        'testpackage.one.delta',
    }


def test_find_descendants():
    graph = build_graph('testpackage')

    assert graph.find_descendants('testpackage.one') == {
        'testpackage.one.alpha',
        'testpackage.one.beta',
        'testpackage.one.gamma',
        'testpackage.one.delta',
        'testpackage.one.delta.blue',
    }


# Direct imports
# --------------

def test_find_modules_directly_imported_by():
    graph = build_graph('testpackage')

    assert graph.find_modules_directly_imported_by('testpackage.utils') == {
        'testpackage.one', 'testpackage.two.alpha',
    }


def test_find_modules_that_directly_import():
    graph = build_graph('testpackage')

    assert graph.find_modules_that_directly_import('testpackage.one.alpha') == {
        'testpackage.one.beta',
        'testpackage.two.alpha',
        'testpackage.two.beta'
    }

def test_direct_import_exists():
    graph = build_graph('testpackage')

    assert False is graph.direct_import_exists(
        importer='testpackage.one.alpha',
        imported='testpackage.two.alpha',
    )
    assert True is graph.direct_import_exists(
        importer='testpackage.two.alpha',
        imported='testpackage.one.alpha',
    )


def test_get_import_details():
    graph = build_graph('testpackage')
    expected_import_details = {
        'testpackage.utils': {
            {
                'imported': 'testpackage.two.alpha',
                'line_number': 5,
                'line_contents': 'from .two import alpha',
            },
        }
    }
    assert expected_import_details == graph.get_import_details(
        importer='testpackage.utils',
        imported='testpackage.two.alpha',
    )


# Indirect imports
# ----------------

def test_path_exists():
    graph = build_graph('testpackage')

    assert not graph.path_exists(
        upstream_module='testpackage.utils',
        downstream_module='testpackage.one.alpha',
    )

    assert graph.path_exists(
        upstream_module='testpackage.one.alpha',
        downstream_module='testpackage.utils',
    )


def test_find_shortest_path():
    graph = build_graph('testpackage')

    assert graph.find_shortest_path(
        upstream_module='testpackage.utils',
        downstream_module='testpackage.one.alpha'
    ) == (
        'testpackage.utils',
        'testpackage.two.alpha',
        'testpackage.one.alpha',
    )


def test_find_downstream_modules():
    graph = build_graph('testpackage')

    assert graph.find_downstream_modules('testpackage.one.alpha') == {
        'testpackage.one.beta',
        'testpackage.one.gamma',
        'testpackage.two.alpha',
        'testpackage.two.beta',
        'testpackage.two.gamma',
        'testpackage.utils',
    }


def test_find_upstream_modules():
    graph = build_graph('testpackage')

    assert graph.find_upstream_modules('testpackage.one.alpha') == set()

    assert graph.find_upstream_modules('testpackage.utils') == {
        'testpackage.one',
        'testpackage.two.alpha',
        'testpackage.one.alpha',
    }
