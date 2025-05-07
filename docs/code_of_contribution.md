# Code of Contribution

Any contributions you make are greatly appreciated. Please note the following:

1. The project has three branches, each with the following positioning:

    - **main**:
        - Retains only the most necessary and core code and functionality, with the highest readability and the smallest codebase.
        - **PR policy**: Almost no PRs will be accepted, except for those that fix bugs.

    - **dev-open**:
        - Based on the main branch, it is open to any functional additions and code optimizations.
        - **PR policy**: Open to any PRs, but the code that overlaps with the main branch must remain consistent.

    - **pre-v0.6.6**:
        - An early version of the project, used only for backup and has been abandoned.
        - **PR policy**: No PRs will be accepted.

2. Compared to a single PR containing a large number of changes, we prefer multiple PRs with smaller changes. This will help to shorten the time required to merge PRs.

3. All scripts under the `examples/` directory have corresponding outputs, and these records also serve as a proof of code execution. Please ensure that your pull request does not change the corresponding output records (or provide reasonable explanations).