#!/usr/bin/env python3
"""
Coval GitHub Action - Launch and monitor evaluation runs using the v1 Runs API.

This script launches a new simulation run via POST /v1/runs and polls GET /v1/runs/{run_id}
until the run completes, fails, or times out.
"""

import os
import json
import time
import requests
from typing import Dict, Any


class CovalRunLauncher:
    """Launches and monitors Coval evaluation runs using the v1 Runs API."""

    def __init__(self):
        """Initialize the launcher with environment variables and validate inputs."""
        # Required inputs
        self.api_key = self._get_required_env("COVAL_API_KEY")
        self.agent_id = self._get_required_env("AGENT_ID")
        self.persona_id = self._get_required_env("PERSONA_ID")
        self.test_set_id = self._get_required_env("TEST_SET_ID")

        # Optional inputs
        self.metric_ids = self._parse_json_env("METRIC_IDS", default=None)
        self.iteration_count = int(os.getenv("ITERATION_COUNT", "1"))
        self.concurrency = int(os.getenv("CONCURRENCY", "1"))
        self.metadata = self._parse_json_env("METADATA", default={})

        # Configuration
        self.max_wait_time = int(os.getenv("MAX_WAIT_TIME", "600"))
        self.check_interval = int(os.getenv("CHECK_INTERVAL", "30"))
        self.api_base_url = os.getenv("API_BASE_URL", "https://api.coval.dev/v1")

        # API endpoints
        self.runs_endpoint = f"{self.api_base_url}/runs"

        # Validate inputs
        self._validate_inputs()

    def _get_required_env(self, key: str) -> str:
        """Get required environment variable or raise error."""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value

    def _parse_json_env(self, key: str, default: Any = None) -> Any:
        """Parse JSON from environment variable, return default if not set or invalid."""
        value = os.getenv(key)
        if not value:
            return default
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid JSON in '{key}': {e}. Using default value.")
            return default

    def _validate_inputs(self):
        """Validate input parameters against API constraints."""
        # Validate ID lengths per OpenAPI spec
        if len(self.agent_id) != 22:
            raise ValueError(f"agent_id must be 22 characters, got {len(self.agent_id)}")
        if len(self.persona_id) != 22:
            raise ValueError(f"persona_id must be 22 characters, got {len(self.persona_id)}")
        if len(self.test_set_id) != 8:
            raise ValueError(f"test_set_id must be 8 characters, got {len(self.test_set_id)}")

        # Validate metric_ids if provided
        if self.metric_ids is not None:
            if not isinstance(self.metric_ids, list):
                raise ValueError("metric_ids must be a JSON array")
            for metric_id in self.metric_ids:
                if len(metric_id) != 22:
                    raise ValueError(f"Each metric_id must be 22 characters, got '{metric_id}'")

        # Validate options
        if not 1 <= self.iteration_count <= 10:
            raise ValueError(f"iteration_count must be between 1 and 10, got {self.iteration_count}")
        if not 1 <= self.concurrency <= 5:
            raise ValueError(f"concurrency must be between 1 and 5, got {self.concurrency}")

    def _build_launch_request(self) -> Dict[str, Any]:
        """Build the LaunchRunRequest payload according to the v1 API schema."""
        payload = {
            "agent_id": self.agent_id,
            "persona_id": self.persona_id,
            "test_set_id": self.test_set_id,
        }

        # Add optional metric_ids
        if self.metric_ids is not None:
            payload["metric_ids"] = self.metric_ids

        # Add options if non-default
        if self.iteration_count != 1 or self.concurrency != 1:
            payload["options"] = {}
            if self.iteration_count != 1:
                payload["options"]["iteration_count"] = self.iteration_count
            if self.concurrency != 1:
                payload["options"]["concurrency"] = self.concurrency

        # Add metadata if provided
        if self.metadata:
            payload["metadata"] = self.metadata

        return payload

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make an authenticated API request with proper headers."""
        headers = kwargs.pop("headers", {})
        headers.update({
            "Content-Type": "application/json",
            "X-API-Key": self.api_key,
        })

        try:
            response = requests.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self._handle_api_error(e)

    def _handle_api_error(self, error: requests.exceptions.RequestException):
        """Handle API errors with detailed error messages."""
        print(f"\n{'='*60}")
        print("API Request Failed")
        print(f"{'='*60}")

        if hasattr(error, 'response') and error.response is not None:
            response = error.response
            print(f"Status Code: {response.status_code}")
            print(f"URL: {response.url}")

            try:
                error_data = response.json()
                if "error" in error_data:
                    err = error_data["error"]
                    print(f"\nError Code: {err.get('code', 'UNKNOWN')}")
                    print(f"Message: {err.get('message', 'No message provided')}")

                    if "details" in err:
                        print("\nDetails:")
                        for detail in err["details"]:
                            field = detail.get("field", "")
                            desc = detail.get("description", "")
                            if field:
                                print(f"  - {field}: {desc}")
                            else:
                                print(f"  - {desc}")
                else:
                    print(f"\nResponse: {json.dumps(error_data, indent=2)}")
            except json.JSONDecodeError:
                print(f"\nResponse Body: {response.text}")
        else:
            print(f"Error: {str(error)}")

        print(f"{'='*60}\n")
        raise SystemExit(1)

    def launch_run(self) -> str:
        """Launch a new evaluation run and return the run_id."""
        print("\n" + "="*60)
        print("Launching Coval Evaluation Run")
        print("="*60)

        payload = self._build_launch_request()
        print("\nRequest Payload:")
        print(json.dumps(payload, indent=2))

        print(f"\nPOST {self.runs_endpoint}")
        response = self._make_request("POST", self.runs_endpoint, json=payload)

        result = response.json()
        run = result.get("run", {})
        run_id = run.get("run_id")

        if not run_id:
            print("Error: No run_id in API response")
            print(json.dumps(result, indent=2))
            raise SystemExit(1)

        print("\n✓ Run launched successfully")
        print(f"Run ID: {run_id}")
        print(f"Status: {run.get('status', 'UNKNOWN')}")

        # Set GitHub Actions output
        self._set_github_output("run_id", run_id)
        self._set_github_output("run_url", f"https://app.coval.dev/runs/{run_id}")

        return run_id

    def get_run_status(self, run_id: str) -> Dict[str, Any]:
        """Get the current status and details of a run."""
        url = f"{self.runs_endpoint}/{run_id}"
        response = self._make_request("GET", url)
        return response.json().get("run", {})

    def wait_for_completion(self, run_id: str):
        """Poll the run status until it completes, fails, or times out."""
        print(f"\n{'='*60}")
        print("Monitoring Run Progress")
        print(f"{'='*60}\n")

        start_time = time.time()
        last_status = None
        last_progress = None

        while time.time() - start_time < self.max_wait_time:
            run = self.get_run_status(run_id)
            status = run.get("status")
            progress = run.get("progress", {})

            # Print status update if changed
            if status != last_status or progress != last_progress:
                elapsed = int(time.time() - start_time)
                print(f"[{elapsed}s] Status: {status}")

                if progress:
                    total = progress.get("total_test_cases", 0)
                    completed = progress.get("completed_test_cases", 0)
                    failed = progress.get("failed_test_cases", 0)
                    in_progress = progress.get("in_progress_test_cases", 0)

                    print(f"  Progress: {completed}/{total} completed, {failed} failed, {in_progress} in progress")

                last_status = status
                last_progress = progress

            # Check terminal states
            if status == "COMPLETED":
                self._handle_completion(run)
                return
            elif status == "FAILED":
                self._handle_failure(run)
                return
            elif status in ["CANCELLED", "DELETED"]:
                print(f"\n✗ Run was {status.lower()}")
                raise SystemExit(1)

            # Wait before next check
            time.sleep(self.check_interval)

        # Timeout
        print(f"\n✗ Run timed out after {self.max_wait_time} seconds")
        print(f"Final status: {last_status}")
        raise SystemExit(1)

    def _handle_completion(self, run: Dict[str, Any]):
        """Handle successful run completion."""
        print(f"\n{'='*60}")
        print("✓ Run Completed Successfully")
        print(f"{'='*60}\n")

        self._set_github_output("status", "COMPLETED")

        # Print results summary
        results = run.get("results", {})
        if results:
            print("Results Summary:")

            output_ids = results.get("output_ids", [])
            print(f"  Output IDs: {len(output_ids)} simulation outputs generated")

            metrics = results.get("metrics", {})
            if metrics:
                print("\n  Metrics:")
                for metric_name, stats in metrics.items():
                    mean = stats.get("mean", 0)
                    min_val = stats.get("min", 0)
                    max_val = stats.get("max", 0)
                    print(f"    {metric_name}:")
                    print(f"      Mean: {mean:.3f}, Min: {min_val:.3f}, Max: {max_val:.3f}")

        print(f"\nView full results: https://app.coval.dev/runs/{run.get('run_id')}")

    def _handle_failure(self, run: Dict[str, Any]):
        """Handle run failure."""
        print(f"\n{'='*60}")
        print("✗ Run Failed")
        print(f"{'='*60}\n")

        self._set_github_output("status", "FAILED")

        error = run.get("error")
        if error:
            print(f"Error: {error}")

        progress = run.get("progress", {})
        if progress:
            failed = progress.get("failed_test_cases", 0)
            print(f"Failed test cases: {failed}")

        raise SystemExit(1)

    def _set_github_output(self, name: str, value: str):
        """Set GitHub Actions output variable."""
        github_output = os.getenv("GITHUB_OUTPUT")
        if github_output:
            with open(github_output, "a") as f:
                f.write(f"{name}={value}\n")

    def run(self):
        """Execute the full launch and monitor workflow."""
        try:
            run_id = self.launch_run()
            self.wait_for_completion(run_id)
        except SystemExit:
            raise
        except Exception as e:
            print(f"\n✗ Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise SystemExit(1)


if __name__ == "__main__":
    launcher = CovalRunLauncher()
    launcher.run()
