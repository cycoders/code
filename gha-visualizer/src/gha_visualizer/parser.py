from pathlib import Path
import yaml
from typing import Dict, Any, List

from .models import Job


def parse_workflow(file_path: Path) -> Dict[str, Any]:
    """Parse a GitHub Actions workflow YAML file into a dict."""

    try:
        with file_path.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        if not isinstance(data, dict):
            raise ValueError("Root must be a mapping (dict)")
        if 'jobs' not in data:
            raise ValueError("No 'jobs' key found in workflow")
        return data
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in {file_path}: {str(e)}") from e
    except FileNotFoundError:
        raise ValueError(f"Workflow file not found: {file_path}") from None
    except PermissionError:
        raise ValueError(f"Permission denied reading {file_path}") from None


def extract_jobs(workflow: Dict[str, Any]) -> List[Job]:
    """Extract typed Job models from workflow dict."""

    jobs_dict = workflow.get('jobs', {})
    if not isinstance(jobs_dict, dict):
        raise ValueError("'jobs' must be a mapping")

    jobs: List[Job] = []
    for name, job_def in jobs_dict.items():
        if not isinstance(job_def, dict):
            raise ValueError(f"Job '{name}' must be a mapping")

        needs = job_def.get('needs', [])
        if isinstance(needs, str):
            needs = [needs]
        steps = job_def.get('steps', [])
        strategy = job_def.get('strategy')

        jobs.append(Job(
            name=name,
            needs=needs,
            steps=steps,
            strategy=strategy,
        ))
    return jobs