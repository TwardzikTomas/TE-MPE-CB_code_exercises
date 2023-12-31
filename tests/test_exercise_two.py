# system imports
from os.path import dirname, abspath, join
import json

# local imports
from exercise_two.exercise_two import (CyclicDependencyError, MissingPackageError, Package, DependencyResolver,
                                       show_dependency_graph, build_dependency_graph)

# third-party imports
import pytest


# helper function
def add_test_path(file_name: str):
    return join(dirname(abspath(__file__)), "test_jsons", file_name)


def test_package_eq():
    package_name = 'pkg'
    p1 = Package(package_name)
    p2 = Package(package_name)
    p3 = Package('dep')
    p1.dependencies = p3
    p2.dependencies = p3
    assert p1 == p2


@pytest.mark.parametrize('test_name, test_dependency_flag',
                         [('pkg2', True),
                          ('pkg', False),
                          ])
def test_package_noteq(test_name, test_dependency_flag):
    dep_p = Package('dep_pkg')
    p1 = Package('pkg')
    p1.dependencies = [dep_p]
    p2 = Package(test_name)
    if test_dependency_flag is True:
        p2.dependencies = [dep_p]
    assert p1 != p2


def test_package_eq_type_mismatch():
    p1 = Package('pkg')
    assert p1 != 'package'


def test_package_repr(log_stdout):
    p1 = Package('pkg')
    print(p1)
    assert log_stdout["stdout"] == "Package(name='pkg', dependencies=[])\n"


def test_file_presence():
    with pytest.raises(FileNotFoundError):
        dr = DependencyResolver()
        assert dr.resolve_graph(add_test_path("non_existent_path.json"))


def test_empty_json_load():
    with pytest.raises(json.JSONDecodeError):
        dr = DependencyResolver()
        assert dr.resolve_graph(add_test_path("empty.json"))


def test_invalid_json_load():
    with pytest.raises(json.JSONDecodeError):
        dr = DependencyResolver()
        assert dr.resolve_graph(add_test_path("invalid_json.json"))


def test_json_structure():
    with pytest.raises(TypeError):
        dr = DependencyResolver()
        assert dr.resolve_graph(add_test_path("list_json.json"))


def test_dependency_structure():
    with pytest.raises(TypeError):
        dr = DependencyResolver()
        assert dr.resolve_graph(add_test_path("invalid_dependencies.json"))


def test_dependency_presence():
    with pytest.raises(MissingPackageError):
        dr = DependencyResolver()
        assert dr.resolve_graph(add_test_path("missing_package.json"))


@pytest.mark.parametrize('file_name',
                         [('cyclic_import.json'),
                          ('self_import.json'),
                          ('cyclic_import_worst_case_fail.json')])
def test_cyclic_import(file_name):
    with pytest.raises(CyclicDependencyError):
        dr = DependencyResolver()
        assert dr.resolve_graph(add_test_path(file_name))


def test_cyclic_import_pass():
    p1 = Package('pkg1')
    p2 = Package('pkg2')
    p3 = Package('pkg3')
    p4 = Package('pkg4')
    p1.dependencies = [p2]
    p2.dependencies = [p3]
    p3.dependencies = [p4]
    comp_dict = dict(pkg1=p1,
                     pkg2=p2,
                     pkg3=p3,
                     pkg4=p4)

    dr = DependencyResolver()
    assert dr.resolve_graph(add_test_path(add_test_path('cyclic_import_worst_case_pass.json'))) == comp_dict


def test_empty_dependencies():
    dr = DependencyResolver()
    assert dr.resolve_graph(add_test_path("empty_dependencies.json")) == {}


def test_simple_package():
    dr = DependencyResolver()
    assert dr.resolve_graph(add_test_path("simple_dependencies.json")) == {'pkg1': Package("pkg1")}


@pytest.mark.parametrize('file_name',
                         [('deps.json'),
                          ('deps.txt')])
def test_example(example_structure, file_name):
    dr = DependencyResolver()
    assert dr.resolve_graph(add_test_path(file_name)) == example_structure


def test_build_dependency_graph(example_structure):
    assert build_dependency_graph(add_test_path("deps.json")) == example_structure


def test_structured_print(log_stdout):
    dr = DependencyResolver()
    dr.print_dependency_graph(add_test_path("deps.json"))

    comp_string = "- pkg3\n"       \
                  "- pkg2\n"       \
                  "  - pkg3\n"     \
                  "- pkg1\n"       \
                  "  - pkg2\n"     \
                  "    - pkg3\n"   \
                  "  - pkg3\n"

    assert log_stdout["stdout"] == comp_string


def test_show_dependency_graph(log_stdout):
    show_dependency_graph(add_test_path("deps.json"))
    comp_string = "- pkg3\n"       \
                  "- pkg2\n"       \
                  "  - pkg3\n"     \
                  "- pkg1\n"       \
                  "  - pkg2\n"     \
                  "    - pkg3\n"   \
                  "  - pkg3\n"
    assert log_stdout["stdout"] == comp_string
