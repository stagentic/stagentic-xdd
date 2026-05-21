#!/usr/bin/env python3
"""Wrapper that patches behave's three hard-coded `.feature` extension checks
to require `.ability` instead, then invokes behave's main with the remaining argv.

Why a wrapper:
- behave hard-codes the .feature extension in three places:
  1. behave/runner_util.py:534 (directory walk in collect_feature_locations)
  2. behave/runner_util.py:543 (explicit filename validation)
  3. behave/runner.py:1076    (base-dir sanity check inside Runner.setup_paths)
- environment.py loads AFTER these checks, so the patches must happen earlier.
- A pre-launch wrapper is the smallest place that runs before any of them.
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCREENPLAY_ROOT = HERE.parent
sys.path.insert(0, str(SCREENPLAY_ROOT))

from behave import runner_util
from behave.runner_util import (
    FileLocation, FileLocationParser, FeatureListParser,
)
from behave.runner import path_getrootdir
from behave.exception import FileNotFoundError, InvalidFilenameError, ConfigError


_ALLOWED_EXTENSION = ".ability"


def _patched_collect_feature_locations(paths, strict=True):
    """Copy of behave.runner_util.collect_feature_locations with .feature
    replaced by _ALLOWED_EXTENSION in the two literal checks."""
    locations = []
    for path in paths:
        if os.path.isdir(path):
            for dirpath, dirnames, filenames in os.walk(path, followlinks=True):
                dirnames.sort()
                for filename in sorted(filenames):
                    if filename.endswith(_ALLOWED_EXTENSION):
                        location = FileLocation(os.path.join(dirpath, filename))
                        locations.append(location)
        elif path.startswith("@"):
            locations.extend(FeatureListParser.parse_file(path[1:]))
        else:
            location = FileLocationParser.parse(path)
            if not location.filename.endswith(_ALLOWED_EXTENSION):
                raise InvalidFilenameError(location.filename)
            if location.exists():
                locations.append(location)
            elif strict:
                raise FileNotFoundError(path)
    return locations


runner_util.collect_feature_locations = _patched_collect_feature_locations
# behave/runner.py does `from .runner_util import collect_feature_locations`
# at import time, so the name is bound there too — patch both.
from behave import runner as _behave_runner
_behave_runner.collect_feature_locations = _patched_collect_feature_locations


def _patched_setup_paths(self):
    """Copy of behave.runner.Runner.setup_paths with .feature replaced by
    _ALLOWED_EXTENSION in the base-dir sanity check."""
    if self.config.paths:
        if self.config.verbose:
            print('Supplied path:', self.config.paths)
        first_path = self.config.paths[0]
        if hasattr(first_path, "filename"):
            first_path = first_path.filename
        base_dir = first_path
        if base_dir.startswith("@"):
            base_dir = base_dir[1:]
            file_locations = self.feature_locations()
            if file_locations:
                base_dir = os.path.dirname(file_locations[0].filename)
        base_dir = os.path.abspath(base_dir)
        if os.path.isfile(base_dir):
            if self.config.verbose:
                print("Primary path is to a file so using its directory")
            base_dir = os.path.dirname(base_dir)
    else:
        if self.config.verbose:
            print('Using default path "{}"'.format(self.DEFAULT_DIRECTORY))
        base_dir = os.path.abspath(self.DEFAULT_DIRECTORY)

    root_dir = path_getrootdir(base_dir)
    new_base_dir = base_dir
    steps_dir = self.config.steps_dir
    environment_file = self.config.environment_file

    while True:
        if self.config.verbose:
            print("Trying base directory:", new_base_dir)
        if os.path.isdir(os.path.join(new_base_dir, steps_dir)):
            break
        if os.path.isfile(os.path.join(new_base_dir, environment_file)):
            break
        if new_base_dir == root_dir:
            break
        new_base_dir = os.path.dirname(new_base_dir)

    if new_base_dir == root_dir:
        raise ConfigError('No %s directory in %r' % (steps_dir, base_dir))

    base_dir = new_base_dir
    self.config.base_dir = base_dir

    for dirpath, dirnames, filenames in os.walk(base_dir, followlinks=True):
        if [fn for fn in filenames if fn.endswith(_ALLOWED_EXTENSION)]:
            break
    else:
        raise ConfigError('No feature files in %r' % base_dir)

    self.base_dir = base_dir
    self.path_manager.add(base_dir)
    if not self.config.paths:
        self.config.paths = [base_dir]
    if base_dir != os.getcwd():
        self.path_manager.add(os.getcwd())


_behave_runner.Runner.setup_paths = _patched_setup_paths

# Run behave from the spike directory so paths = behaviours resolves.
os.chdir(HERE)

from behave.__main__ import main
# behave's Configuration.make_command_args defaults to sys.argv[1:] only when
# sys.argv[0] contains "behave". Our wrapper is named bdd-run.py, so we must
# pass argv explicitly or all CLI flags (including -D) get silently dropped.
sys.exit(main(sys.argv[1:]))
