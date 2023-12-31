"""
This file is a proposed solution to a task number two from TE-MPE-CB - coding exercise two.

Write a small program, which:

 1. Reads a JSON file from a fixed filesystem location, e.g. /tmp/deps.json, containing a list of packages and their dependencies.
 In this JSON file, a key represents a package name, and the value is a list of dependencies (package names) for that key:

'{
  "pkg1": ["pkg2", "pkg3"],
  "pkg2": ["pkg3"],
  "pkg3": []
}'

2. Traverses the dependencies loaded from the JSON file and reconstructs the full dependency graph.
For the input above, the full graph would be the following:

- pkg1
  - pkg2
    - pkg3
  - pkg3
- pkg2
  - pkg3
- pkg3

3. Has a function that takes a filename as an input and returns an object representing the fully resolved graph.
Please provide a test case that validates this function. Use any testing framework of your choice.

4. Is a valid Python package or module and is runnable with `python -m program_name command`.
Running this command should print the graph to stdout. The format in which it prints is not important.

In addition, setup a CI pipeline (using Gitlab CI, Github Actions or equivalent)to ensure
the best possible automation for the quality of your code.


Assumptions taken:
    - valid format of the dependency json file is as given,
    - any deviation from the format is prohibited,
    - cyclic dependencies result in failure,
    - all packages in dependencies must be listed themselves in the root of the structure,
    - other file extensions are allowed, if JSON decoder can extract valid JSON out of them ('.txt').
    - order of listed packages does not influence the validity of a solution

Possible improvements:
    -current recursive scheme is inefficient, one builds package chains repeatedly,
     while it would be much more interesting to "cache" the results on recursion method return
"""

# system imports
import os
from json import load, JSONDecodeError
from typing import Union, Any
from pathlib import Path


# global variables
TARGET_PATH = "/tmp/deps.json"


class CyclicDependencyError(Exception):
    """
    Raised if cyclic dependency is detected during verification of the dependency file
    """
    ...


class MissingPackageError(Exception):
    """
    Raised if a missing package is detected during verification of the dependency file
    """
    ...


class Package:
    """Class that represents a package, with its dependencies and depth in the dependency graph
    """
    def __init__(self, name: str):
        self.name = name
        self.dependencies: list['Package'] = []

    def __repr__(self):
        class_name = type(self).__name__
        return f"{class_name}(name={self.name!r}, dependencies={[dependency.name for dependency in self.dependencies]})"

    def __eq__(self, other: Any) -> bool:
        try:
            ret = True if (self.name == other.name) and (self.dependencies == other.dependencies) else False
        except AttributeError:
            return False
        return ret

    def structural_print(self, depth_level: int = 0):
        """
        Convenience method that recursively prints dependency structure of a package
        """
        print(f"{depth_level*'  '}- {self.name}")
        for dep in self.dependencies:
            dep.structural_print(depth_level+1)


# custom type hints definition
dependency_tree = dict[str, Package]


class DependencyResolver:
    def verify_dependency_structure(self, dependency_data: dict[str, list]) -> None:
        """Method verifies if the content of JSON file is valid for further processing.

        NOTE: Verification process could be done more computationally efficient, but this approach
        is easier to extend, clearly communicates it's components functionality and is more readable

        Args:
            dependency_data (dict[str, list]): Data containing dependency relations read from a JSON file.
        """
        self.verify_dependency_fields(dependency_data)
        self.verify_presence(dependency_data)

    def verify_dependency_fields(self, dependency_data: dict[str, list]) -> None:
        """Function verifying if the data structure provided by JSON file is valid.

        Args:
            dependency_data (dict[str, list]): Data containing dependency relations read from a JSON file.

        Raises:
            TypeError: raises if argument 'dependency_data' is not a dict,
            TypeError: raises if keys of the dict are not strings,
            TypeError: raises if values of the dict are not lists.
        """
        if not isinstance(dependency_data, dict):
            raise TypeError("Loaded JSON file does not provide a dictionary")
        for pkg, deps in dependency_data.items():
            if not isinstance(pkg, str):
                raise TypeError(f"ERROR: Package name {pkg!r} is not a string")
            if not isinstance(deps, list):
                raise TypeError(f"ERROR: Package {pkg!r} dependencies are not a list")

    def verify_presence(self, dependency_data: dict[str, list]) -> None:
        """Function verifying if all dependencies are listed as a package.

        Args:
            dependency_data (dict[str, list]): Data containing dependency relations read from a JSON file.

        Raises:
            MissingPackageError: raise if a package is listed in dependencies, while not being listed on its own.
        """
        pkgs = dependency_data.keys()
        for _, deps in dependency_data.items():
            for dep in deps:
                if dep not in pkgs:
                    raise MissingPackageError(f"ERROR: Package {dep!r} was not found in dependency list")

    def resolve_graph(self, file_path: Union[str, Path]) -> dependency_tree:
        """A method retrieving 'dependency_tree' structure from a file defined by 'file_path' argument.

        Args:
            file_path (Union[str, Path]): string or Path objects defining location of JSON dependency structure file

        Raises:
            FileNotFoundError: if file defined 'file_path' does not exist
        Returns:
            dependency_tree: a list of structurally constructed Package objects
        """
        def resolve_dependency(pkg: str, recursion_depth: int) -> Package:
            """Recursive function utilized for building the 'dependency_tree' object.
            Recursion end once package has no dependencies.

            Args:
                pkg (str): name of a package in 'dependency_data'

            Returns:
                Package: returns a Package with its dependencies
            """
            if recursion_depth >= max_recursion_depth:
                raise CyclicDependencyError(f"Depth of recursion reached its limit {max_recursion_depth!r}")

            package = Package(pkg)

            for dependency in dependency_data[pkg]:
                # looking up resolved packages
                dependency_resolved = dependency_graph.get(dependency, None)

                if dependency_resolved is None:
                    # stepping deeper with recursion, adding Packages in dependencies with one bigger depth
                    dependency_resolved = resolve_dependency(dependency, recursion_depth+1)

                package.dependencies.append(dependency_resolved)
            # caching resolved package
            if dependency_graph.get(pkg, None) is None:
                dependency_graph[pkg] = package
            return package

        # check for existence of a file, shortcircuit for errors
        if os.path.isfile(file_path) is False:
            raise FileNotFoundError(f"Error. File at the path {file_path} does not exist.")

        # opens a file with context manager to prevent resource leaking
        with open(file_path) as json_file:
            try:
                dependency_data: dict = load(json_file)
            except JSONDecodeError:
                print(f"File {file_path} does not hold valid JSON format. Exiting program")
                raise
        try:
            # checking for validity of data loaded
            self.verify_dependency_structure(dependency_data)
        except TypeError:
            print("Aborting program due to data structure issues.")
            raise
        except (MissingPackageError, CyclicDependencyError):
            print("Aborting program due to dependency structure issues.")
            raise
        else:
            max_recursion_depth = len(dependency_data)
            dependency_graph: dict[str, Package] = {}
            for pkg in dependency_data.keys():
                if dependency_graph.get(pkg, None) is None:
                    dependency_graph[pkg] = resolve_dependency(pkg, 0)

            return dependency_graph

    def print_dependency_graph(self, file_path: Union[str, Path]) -> None:
        """Prints a formatted dependency graph defined by 'file_path' file

        Args:
            file_path (Union[str, Path]): JSON file containing dependency relations
        """
        resolved_graph = self.resolve_graph(file_path)

        for node in resolved_graph.keys():
            resolved_graph[node].structural_print()


# convenience methods
def show_dependency_graph(target_path: str = TARGET_PATH):
    """
    Convenience method for invoking dependency graph plot.
    Provides required default path to dependency json at '/tmp/deps.json'.

    Args:
        target_path (str, optional): an absolute path to dependency file in json format. Defaults to TARGET_PATH.
    """
    dr = DependencyResolver()
    # print dependency graph
    dr.print_dependency_graph(target_path)


def build_dependency_graph(target_path: str = TARGET_PATH) -> dependency_tree:
    """
    Convenience method for constructing and retrieving 'dependency_tree'.
    Provides required default path to dependency json at '/tmp/deps.json'.

    Args:
        target_path (str, optional): an absolute path to dependency file in json format. Defaults to TARGET_PATH.

    Returns:
        dependency_tree: a list of structurally constructed Package objects
    """
    dr = DependencyResolver()
    # return retrieved 'dependency_tree'
    return dr.resolve_graph(target_path)


# example uses
if __name__ == "__main__":

    dr = DependencyResolver()
    graph = dr.resolve_graph(TARGET_PATH)
    print(graph)

    show_dependency_graph()
