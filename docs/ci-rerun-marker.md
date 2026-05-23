# CI Rerun Marker

This file exists to trigger a fresh GitHub Actions run on the latest main branch after the worker task restoration fix.

Last purpose: verify that `apps.api.main` can import `evaluate_job` from `worker.tasks` on the current branch state.
