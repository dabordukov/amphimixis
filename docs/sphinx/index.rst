Amphimixis Documentation
========================

Amphimixis is an automated project intelligence and evaluation tool for
performance and migration readiness. It helps inspect a project for existing
infrastructure such as CI, tests, benchmarks, dependencies, and build scripts,
then runs builds and collects performance data for further comparison.

Amphimixis uses ``perf`` for profiling and produces a cross-table with two
builds per CPU event for comparison.

Quick Run
---------

If you want to try Amphimixis right away, create a virtual environment, install
the package from GitHub, and run the full pipeline on a target project:

.. code-block:: bash

   python3 -m venv .venv
   source .venv/bin/activate
   pip install git+https://github.com/ebzych/amphimixis.git@stable
   amixis init local
   amixis run /path/to/project --config local.yml

Requirements
------------

- Python 3.12 or later
- Linux
- ``rsync`` on each machine
- ``sshpass`` on the machine where you run Amphimixis if you connect to remote
  machines with passwords
- ``perf`` on each ``run_machine``
- ``perf archive`` on each ``run_machine``
- a supported build setup in the target project: CMake as the build system and
  Make as the low-level runner

What Amphimixis Does
--------------------

Amphimixis can:

- analyze a project for CI, tests, benchmarks, build system configuration, and
  dependencies;
- build the project with configured recipes and platforms;
- profile executable runs and collect timing and ``perf``-based statistics;
- compare profiling outputs produced for different builds and put them into a
  cross-table for each CPU event.

User Guides
-----------

- :doc:`usage_guide`
- :doc:`config_instruction`

Main Workflows
--------------

- :doc:`api/analyzer`
- :doc:`api/configurator`
- :doc:`api/builder`
- :doc:`api/profiler`

Supporting Modules
------------------

- :doc:`api/amixis`
- :doc:`api/core_types`
- :doc:`api/misc`

.. toctree::
   :maxdepth: 2
   :caption: Main Modules
   :hidden:

   api/analyzer
   api/configurator
   api/builder
   api/profiler

.. toctree::
   :maxdepth: 2
   :caption: Supporting Modules
   :hidden:

   api/amixis
   api/core_types
   api/misc

.. toctree::
   :maxdepth: 2
   :caption: Guides

   usage_guide
   config_instruction
   input

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/index
