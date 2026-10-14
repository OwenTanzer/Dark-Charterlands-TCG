# Completed after-game reports

Save completed reports at:

    reports/<game-slug>/<version-slug>/YYYY-MM-DD-session-NN.md

From this directory, the path begins with the game slug. A version slug should
identify the tested rules plus set revision or software build (for example,
rules-v0.2-set-r3 or build-a1b2c3d). The report header holds the full exact
identifiers, including commit SHA and local charter/variant revision. Never
overwrite a report after a version change; add a new file and cross-reference
earlier finding IDs. For a mixed-version session, list each version and the
time at which it was used, or split into separate reports.

Start by copying [the shared core](../templates/core.md) and appending one
[module](../README.md#modules). An empty template is not a completed report.
Do not commit names, precise location traces or other personal data.
