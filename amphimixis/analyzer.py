"""Module that analyzes project's repository and creates file with its information"""

import glob
from os import listdir, path

import yaml

from amphimixis import general, logger

log = logger.setup_logger("ANALYZER")

ci_list = ["**/ci", "**/.github/workflows"]

build_systems_list = {
    "cmake": ["**/CMakeLists.txt"],
    "meson": ["**/*meson*"],
    "bazel": ["**/*bazel*", "**/BUILD"],
    "make": ["**/Makefile", "**/makefile"],
    "SCons": ["**SCons*"],
    "autotools": ["**/configure.ac", "**/configure.in"],
    "needs_bootstrap": ["bootstrap"],
}


def analyze(project: general.Project):
    """Analyzes project and collects its information"""

    results = {
        "tests": [],
        "benchmarks": [],
        "ci": [],
        "build_systems": {k: False for k in build_systems_list},
        "dependencies": [],
    }

    proj_path = project.path

    if not path.exists(proj_path):
        log.error("Directory '%s' not found", proj_path)
        raise FileNotFoundError(f'Directory "{proj_path}" not found')

    log.info("Analyzing %s", path.basename(path.normpath(proj_path)))

    _search_tests(proj_path, results)
    _search_benchmarks(proj_path, results)
    _search_ci(proj_path, results)
    _search_build_systems(proj_path, results)
    _search_dependencies(proj_path, results)

    _file_output(results["build_systems"])

    log.info("Analyzing done")

    return results


def _rel_path(proj_path, paths):
    parent_dir = path.dirname(path.normpath(proj_path))
    return [path.relpath(p, parent_dir) for p in paths]


def _find_paths(proj_path, pattern, dirs_only=True):
    paths = glob.glob(path.join(proj_path, pattern), recursive=True)
    return [p for p in paths if path.isdir(p)] if dirs_only else paths


def _log_results(proj_path, results, key, paths):
    rel_paths = _rel_path(proj_path, paths) if paths else []
    if rel_paths:
        results[key] = rel_paths[0]
        log.info("found %s: %s", key, rel_paths[0])
    else:
        log.info("%s not found", key)


def _file_output(results, file_name="amphimixis.analyzed"):
    with open(
        file_name,
        "w",
        encoding="utf8",
    ) as file:
        yaml.dump(results, file, sort_keys=False)


def _search_tests(proj_path, results):
    paths = _find_paths(proj_path, "**/*test*")
    _log_results(proj_path, results, "tests", paths)


def _search_benchmarks(proj_path, results):
    paths = _find_paths(proj_path, "**/*bench*")
    _log_results(proj_path, results, "benchmarks", paths)


def _search_ci(proj_path, results):
    paths = []
    for pattern in ci_list:
        paths.extend(_find_paths(proj_path, pattern))
    _log_results(proj_path, results, "ci", paths)


def _search_build_systems(proj_path, results):
    log.info("build systems:")
    found = False
    for system, patterns in build_systems_list.items():
        for pat in patterns:
            if _find_paths(proj_path, pat, dirs_only=False):
                results["build_systems"][system] = True
                log.info(" %s", system)
                found = True
                break
    if not found:
        log.info(" not found")


def _search_dependencies(proj_path, results):
    log.info("dependencies:")
    dep_path = path.join(proj_path, "third_party")
    if path.exists(dep_path):
        dirs = [d for d in listdir(dep_path) if path.isdir(path.join(dep_path, d))]
        results["dependencies"].extend(dirs)
    if results["dependencies"]:
        for dep in results["dependencies"]:
            log.info(" %s", dep)
    else:
        log.info(" not found")
