# Workflow Examples

This directory contains example GitHub Actions workflows demonstrating various use cases for the Coval GitHub Action.

## Available Examples

### 1. Basic PR Check (`basic-pr-check.yml`)
**Use Case:** Automatically run evaluations on every pull request

Simple workflow that triggers on PRs to main branch with minimal configuration.

```yaml
on:
  pull_request:
    branches: [main]
```

### 2. Manual Dispatch (`manual-dispatch.yml`)
**Use Case:** On-demand testing with custom parameters

Allows manual triggering from GitHub Actions UI with dropdown selections for iteration count.

```yaml
on:
  workflow_dispatch:
    inputs:
      agent_id: ...
```

### 3. Advanced Configuration (`advanced-config.yml`)
**Use Case:** Full-featured evaluation with all options

Demonstrates custom metrics, iteration count, concurrency, metadata, and commit commenting.

```yaml
with:
  metric_ids: '["id1", "id2"]'
  iteration_count: 3
  concurrency: 2
  metadata: '{...}'
```

### 4. Multi-Environment (`multi-environment.yml`)
**Use Case:** Different agents per environment

Tests different agents based on branch (main → production, staging → staging, dev → development).

```yaml
on:
  push:
    branches: [main, staging, dev]
```

### 5. Parallel Personas (`parallel-personas.yml`)
**Use Case:** Test same agent with multiple user personas

Uses matrix strategy to test against multiple personas in parallel.

```yaml
strategy:
  matrix:
    persona:
      - { id: "...", name: "Friendly" }
      - { id: "...", name: "Frustrated" }
```

### 6. Scheduled Regression (`scheduled-regression.yml`)
**Use Case:** Nightly comprehensive testing

Runs extensive tests on schedule with high iteration count and creates issues on failure.

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily
```

### 7. PR Comment (`pr-comment.yml`)
**Use Case:** Post results directly on pull requests

Evaluates on PR and posts/updates a comment with results, failing workflow on evaluation failure.

## Usage

1. Copy the relevant example to your repository's `.github/workflows/` directory
2. Replace placeholder IDs with your actual Coval IDs:
   - `agent_id`: Your 22-character agent ID
   - `persona_id`: Your 22-character persona ID
   - `test_set_id`: Your 8-character test set ID
   - `metric_ids`: Your 22-character metric IDs (if using custom metrics)
3. Ensure `COVAL_API_KEY` is set in your repository secrets
4. Commit and push to trigger the workflow

## Customization Tips

### Adjusting Timing
- `max_wait_time`: Increase for larger test sets (default: 600s)
- `check_interval`: Decrease for more frequent updates (default: 30s)

### Concurrency
- Use `concurrency: 2-5` for faster test completion
- Balance against API rate limits

### Iteration Count
- Use `iteration_count: 1` for quick feedback
- Use `iteration_count: 3-5` for statistical reliability
- Use `iteration_count: 10` for comprehensive regression testing

### Metadata
Add custom tracking fields:
```yaml
metadata: '{
  "environment": "production",
  "version": "1.2.3",
  "commit": "${{ github.sha }}",
  "pr": "${{ github.event.pull_request.number }}"
}'
```

## Common Patterns

### Conditional Execution
```yaml
if: github.event_name == 'pull_request' && github.base_ref == 'main'
```

### Multiple Test Sets
```yaml
strategy:
  matrix:
    test_set: [testSet1, testSet2, testSet3]
```

### Failure Notifications
```yaml
- name: Notify on Failure
  if: failure()
  # Send Slack notification, create issue, etc.
```

## Need Help?

- [Full Documentation](https://docs.coval.dev/getting_started/github_actions_tutorial)
- [GitHub Action Repository](https://github.com/coval-ai/coval-github-action)
- [Support](mailto:support@coval.dev)
