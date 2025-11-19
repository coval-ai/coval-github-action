# Coval GitHub Action

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Launch and monitor AI agent evaluation runs in your CI/CD pipeline using the Coval API.

## Features

- **v1 Runs API**: Uses the official `POST /v1/runs` and `GET /v1/runs/{run_id}` endpoints
- **Real-time Monitoring**: Polls run status with detailed progress reporting
- **Comprehensive Error Handling**: Field-level validation feedback from API errors
- **Flexible Configuration**: Support for custom metrics, iteration counts, concurrency, and metadata
- **GitHub Actions Integration**: Native outputs for run_id, status, and dashboard URL

## Quick Start

### Prerequisites

1. A Coval account with API access
2. Your Coval API key stored as a GitHub secret (`COVAL_API_KEY`)
3. Valid IDs for:
   - Agent (22 characters)
   - Persona (22 characters)
   - Test Set (8 characters)

### Basic Usage

Create `.github/workflows/coval-eval.yml`:

```yaml
name: Run Coval Evaluation

on:
  pull_request:
    branches: [main]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - name: Run Coval Evaluation
        uses: coval-ai/coval-github-action@v1
        env:
          COVAL_API_KEY: ${{ secrets.COVAL_API_KEY }}
        with:
          agent_id: "gk3jK9mPq2xRt5vW8yZaBc"
          persona_id: "hL4kL0nQr3ySt6vX9zAcDd"
          test_set_id: "aB1cD2eF"
```

### Manual Trigger with Inputs

```yaml
name: Manual Coval Evaluation

on:
  workflow_dispatch:
    inputs:
      agent_id:
        description: "Agent ID (22 chars)"
        required: true
        type: string
      persona_id:
        description: "Persona ID (22 chars)"
        required: true
        type: string
      test_set_id:
        description: "Test Set ID (8 chars)"
        required: true
        type: string

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - name: Run Evaluation
        uses: coval-ai/coval-github-action@v1
        env:
          COVAL_API_KEY: ${{ secrets.COVAL_API_KEY }}
        with:
          agent_id: ${{ inputs.agent_id }}
          persona_id: ${{ inputs.persona_id }}
          test_set_id: ${{ inputs.test_set_id }}
```

### Advanced Configuration

```yaml
- name: Run Advanced Evaluation
  uses: coval-ai/coval-github-action@v1
  env:
    COVAL_API_KEY: ${{ secrets.COVAL_API_KEY }}
  with:
    agent_id: "gk3jK9mPq2xRt5vW8yZaBc"
    persona_id: "hL4kL0nQr3ySt6vX9zAcDd"
    test_set_id: "aB1cD2eF"
    metric_ids: '["iM5lM1oRs4zTu7wY0aBdEe", "jN6mN2pSt5aUv8xZ1bCeFf"]'
    iteration_count: 3
    concurrency: 2
    metadata: '{"campaign_id": "q4_2025", "created_by": "ci/cd", "environment": "staging"}'
    max_wait_time: 900
    check_interval: 45
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `agent_id` | Agent ID to test (22 characters) | Yes | - |
| `persona_id` | Simulated persona ID (22 characters) | Yes | - |
| `test_set_id` | Test set ID (8 characters) | Yes | - |
| `metric_ids` | JSON array of metric IDs (22 chars each) | No | Agent defaults |
| `iteration_count` | Number of times to run each test case (1-10) | No | `1` |
| `concurrency` | Number of concurrent simulations (1-5) | No | `1` |
| `metadata` | JSON object for custom metadata | No | `{}` |
| `max_wait_time` | Maximum wait time in seconds | No | `600` |
| `check_interval` | Status check interval in seconds | No | `30` |
| `api_base_url` | Coval API base URL | No | `https://api.coval.dev/v1` |

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `COVAL_API_KEY` | Your Coval API key | Yes |

## Outputs

| Output | Description | Example |
|--------|-------------|---------|
| `run_id` | Unique identifier for the run | `8EktrIgaVxn9LfxkIynagX` |
| `status` | Final run status | `COMPLETED` |
| `run_url` | Dashboard URL for the run | `https://app.coval.dev/runs/...` |

### Using Outputs

```yaml
- name: Run Evaluation
  id: coval
  uses: coval-ai/coval-github-action@v1
  env:
    COVAL_API_KEY: ${{ secrets.COVAL_API_KEY }}
  with:
    agent_id: "gk3jK9mPq2xRt5vW8yZaBc"
    persona_id: "hL4kL0nQr3ySt6vX9zAcDd"
    test_set_id: "aB1cD2eF"

- name: Comment on PR
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: `✓ Coval evaluation completed: ${{ steps.coval.outputs.run_url }}`
      })
```

## API Reference

This action uses the Coval v1 Runs API:

### Launch Run: `POST /v1/runs`

**Request Schema (LaunchRunRequest):**
```json
{
  "agent_id": "string (22 chars)",
  "persona_id": "string (22 chars)",
  "test_set_id": "string (8 chars)",
  "metric_ids": ["string (22 chars)"],
  "options": {
    "iteration_count": 1,
    "concurrency": 1
  },
  "metadata": {
    "custom_field": "value"
  }
}
```

### Get Run Status: `GET /v1/runs/{run_id}`

**Response Schema (Run):**
```json
{
  "run": {
    "run_id": "string",
    "status": "PENDING | IN QUEUE | IN PROGRESS | COMPLETED | FAILED | CANCELLED | DELETED",
    "create_time": "2025-10-14T12:00:00Z",
    "update_time": "2025-10-14T12:15:00Z",
    "progress": {
      "total_test_cases": 10,
      "completed_test_cases": 10,
      "failed_test_cases": 0,
      "in_progress_test_cases": 0
    },
    "results": {
      "output_ids": ["sim_output_1"],
      "metrics": {
        "availability": {
          "mean": 0.95,
          "min": 0.85,
          "max": 1.0
        }
      }
    }
  }
}
```

## Error Handling

The action provides detailed error messages for common issues:

### Invalid API Key
```
API Request Failed
Status Code: 401
Error Code: UNAUTHENTICATED
Message: Invalid or missing API key
Details:
  - X-API-Key: API key is required in the X-API-Key header
```

### Invalid Agent ID
```
API Request Failed
Status Code: 400
Error Code: INVALID_ARGUMENT
Message: Invalid agent_id: Agent not found
Details:
  - agent_id: Agent 'xyz123' does not exist or is not accessible
```

### Validation Errors
```
API Request Failed
Status Code: 400
Error Code: INVALID_ARGUMENT
Message: Request validation failed
Details:
  - iteration_count: Value must be between 1 and 10
```

## Run Statuses

| Status | Description |
|--------|-------------|
| `PENDING` | Run created, waiting to start |
| `IN QUEUE` | Queued for execution |
| `IN PROGRESS` | Currently running test cases |
| `COMPLETED` | All test cases completed successfully |
| `FAILED` | Run failed (see error field) |
| `CANCELLED` | Run was cancelled by user |
| `DELETED` | Run was deleted |

## Examples

### Environment-Specific Evaluations

```yaml
name: Environment Evaluations

on:
  push:
    branches: [main, staging, dev]

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - name: Determine Environment
        id: env
        run: |
          if [[ "${{ github.ref }}" == "refs/heads/main" ]]; then
            echo "env=production" >> $GITHUB_OUTPUT
            echo "agent_id=prodAgentId12345678" >> $GITHUB_OUTPUT
          elif [[ "${{ github.ref }}" == "refs/heads/staging" ]]; then
            echo "env=staging" >> $GITHUB_OUTPUT
            echo "agent_id=stgAgentId123456789" >> $GITHUB_OUTPUT
          else
            echo "env=development" >> $GITHUB_OUTPUT
            echo "agent_id=devAgentId123456789" >> $GITHUB_OUTPUT
          fi

      - name: Run Evaluation
        uses: coval-ai/coval-github-action@v1
        env:
          COVAL_API_KEY: ${{ secrets.COVAL_API_KEY }}
        with:
          agent_id: ${{ steps.env.outputs.agent_id }}
          persona_id: "hL4kL0nQr3ySt6vX9zAcDd"
          test_set_id: "aB1cD2eF"
          metadata: '{"environment": "${{ steps.env.outputs.env }}", "commit": "${{ github.sha }}"}'
```

### Parallel Evaluations

```yaml
name: Parallel Persona Testing

on:
  workflow_dispatch:

jobs:
  evaluate:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        persona:
          - id: "persona1Id1234567890ab"
            name: "Friendly Customer"
          - id: "persona2Id1234567890cd"
            name: "Frustrated Customer"
          - id: "persona3Id1234567890ef"
            name: "Technical Customer"
    steps:
      - name: Evaluate with ${{ matrix.persona.name }}
        uses: coval-ai/coval-github-action@v1
        env:
          COVAL_API_KEY: ${{ secrets.COVAL_API_KEY }}
        with:
          agent_id: "gk3jK9mPq2xRt5vW8yZaBc"
          persona_id: ${{ matrix.persona.id }}
          test_set_id: "aB1cD2eF"
          metadata: '{"persona_name": "${{ matrix.persona.name }}"}'
```

### Scheduled Regression Testing

```yaml
name: Nightly Regression Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Run at 2 AM daily

jobs:
  regression:
    runs-on: ubuntu-latest
    steps:
      - name: Run Comprehensive Tests
        uses: coval-ai/coval-github-action@v1
        env:
          COVAL_API_KEY: ${{ secrets.COVAL_API_KEY }}
        with:
          agent_id: "gk3jK9mPq2xRt5vW8yZaBc"
          persona_id: "hL4kL0nQr3ySt6vX9zAcDd"
          test_set_id: "regrTest"
          iteration_count: 5
          concurrency: 3
          metadata: '{"type": "nightly_regression", "date": "${{ github.event.repository.updated_at }}"}'
          max_wait_time: 1800
```

## Finding Your IDs

### Agent ID
1. Navigate to the Agents page in Coval
2. Click on your agent
3. Copy the 22-character agent ID from the URL or details page

### Persona ID
1. Navigate to the Personas page
2. Select your persona
3. Copy the 22-character persona ID

### Test Set ID
1. Go to Test Sets
2. Find your test set
3. Copy the 8-character test set ID

### Metric IDs
1. Navigate to the Metrics page
2. Click on your desired metric
3. Copy the 22-character metric ID
4. Repeat for all metrics you want to include

## Troubleshooting

### Action fails with "Invalid agent_id"
- Verify the agent ID is exactly 22 characters
- Ensure the agent exists in your organization
- Check that your API key has access to the agent

### Timeout errors
- Increase `max_wait_time` for larger test sets
- Reduce `concurrency` if experiencing rate limits
- Check Coval dashboard for run status

### "COVAL_API_KEY environment variable is required"
- Ensure you've added the secret to your repository
- Verify the `env` block includes `COVAL_API_KEY`

### Invalid JSON in inputs
- Use single quotes around JSON strings in YAML
- Validate JSON syntax before committing
- For metric_ids: `'["id1", "id2"]'`
- For metadata: `'{"key": "value"}'`

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: https://docs.coval.dev
- **API Reference**: https://docs.coval.dev/api-reference
- **Issues**: https://github.com/coval-ai/coval-github-action/issues
- **Email**: support@coval.dev
