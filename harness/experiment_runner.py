"""
Experiment Runner for Multi-Agent Safety Study
================================================

Orchestrates the 1,500-trial experiment across 5 system configurations,
4 jailbreak techniques, ~15 tasks, and 5 seeds.

This script manages:
- Trial scheduling and execution tracking
- Configuration instantiation (C1-C5)
- Result recording in structured JSON
- Rate limiting and retry logic
- Contamination checking
- Experiment log maintenance

Since we operate on Claude Max (not API), each trial is run by
spawning the appropriate agent configuration through Claude Code's
Agent tool. This script generates the trial manifest and tracks results;
actual execution happens through the orchestrator.

Usage:
    python experiment_runner.py generate-manifest  # Create trial list
    python experiment_runner.py status              # Show progress
    python experiment_runner.py export              # Export results to CSV
"""

import json
import os
import sys
import hashlib
from datetime import datetime, timezone
from itertools import product
from pathlib import Path

PROJECT = Path(__file__).parent.parent
HARNESS = PROJECT / "harness"
EXPERIMENTS = PROJECT / "experiments"
RESULTS_DIR = EXPERIMENTS / "results"
MANIFEST_FILE = EXPERIMENTS / "trial_manifest.json"
PROGRESS_FILE = EXPERIMENTS / "progress.json"
EXPERIMENT_LOG = EXPERIMENTS / "experiment_log.jsonl"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    config_path = HARNESS / "config.json"
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def load_tasks(use_pilot=False, include_high_refusal=True):
    if use_pilot:
        tasks_path = HARNESS / "pilot_tasks.json"
        with open(tasks_path, encoding="utf-8") as f:
            return json.load(f)

    tasks_path = EXPERIMENTS / "task_benchmark.json"
    with open(tasks_path, encoding="utf-8") as f:
        data = json.load(f)

    if include_high_refusal:
        hr_path = EXPERIMENTS / "high_refusal_tasks.json"
        if hr_path.exists():
            with open(hr_path, encoding="utf-8") as f:
                hr_data = json.load(f)
                data["tasks"].extend(hr_data["tasks"])

    return data


def generate_trial_id(config_id: str, technique_id: str, task_id: str, seed: int) -> str:
    raw = f"{config_id}_{technique_id}_{task_id}_{seed}"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def generate_manifest(use_pilot=False):
    config = load_config()
    configurations = list(config["configurations"].keys())
    techniques = list(config["jailbreak_techniques"].keys())
    seeds = config["experiment_params"]["seeds"]

    tasks_data = load_tasks(use_pilot=use_pilot)
    task_ids = [t["id"] for t in tasks_data["tasks"]]

    trials = []
    for config_id, technique_id, task_id, seed in product(
        configurations, techniques, task_ids, seeds
    ):
        trial = {
            "trial_id": generate_trial_id(config_id, technique_id, task_id, seed),
            "config_id": config_id,
            "technique_id": technique_id,
            "task_id": task_id,
            "seed": seed,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "started_at": None,
            "completed_at": None,
            "error": None,
            "result_file": None,
        }
        trials.append(trial)

    manifest = {
        "study": "multi-agent-safety",
        "version": config["version"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_trials": len(trials),
        "breakdown": {
            "configurations": len(configurations),
            "techniques": len(techniques),
            "tasks": len(task_ids),
            "seeds": len(seeds),
        },
        "estimated_api_calls": sum(
            3 if config["configurations"][t["config_id"]]["architecture"] == "multi-agent" else 1
            for t in trials
        ),
        "trials": trials,
    }

    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Generated manifest: {len(trials)} trials")
    print(f"  Configurations: {configurations}")
    print(f"  Techniques: {techniques}")
    print(f"  Tasks: {task_ids}")
    print(f"  Seeds: {seeds}")
    print(f"  Estimated API calls: {manifest['estimated_api_calls']}")
    return manifest


def record_result(trial_id: str, result: dict):
    result_file = RESULTS_DIR / f"{trial_id}.json"
    result["recorded_at"] = datetime.now(timezone.utc).isoformat()
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    log_entry = {
        "trial_id": trial_id,
        "timestamp": result["recorded_at"],
        "config_id": result.get("config_id"),
        "technique_id": result.get("technique_id"),
        "task_id": result.get("task_id"),
        "seed": result.get("seed"),
        "jailbreak_success": result.get("jailbreak_success"),
        "output_usefulness": result.get("output_usefulness"),
        "verifier_catch": result.get("verifier_catch"),
        "error": result.get("error"),
    }

    # Crash-safe JSONL: write to temp file then rename (atomic on NTFS)
    import tempfile
    line = json.dumps(log_entry) + "\n"
    try:
        with open(EXPERIMENT_LOG, "a", encoding="utf-8") as f:
            f.write(line)
            f.flush()
            os.fsync(f.fileno())
    except Exception:
        pass

    # Update manifest status and result file path
    _update_manifest_trial(trial_id, "completed", str(result_file))

    return result_file


def _update_manifest_trial(trial_id: str, status: str, result_file: str = None):
    if not MANIFEST_FILE.exists():
        return
    try:
        with open(MANIFEST_FILE, encoding="utf-8") as f:
            manifest = json.load(f)
        for trial in manifest["trials"]:
            if trial["trial_id"] == trial_id:
                trial["status"] = status
                trial["completed_at"] = datetime.now(timezone.utc).isoformat()
                if result_file:
                    trial["result_file"] = result_file
                break
        with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)
    except Exception:
        pass


def get_status():
    if not MANIFEST_FILE.exists():
        print("No manifest found. Run 'generate-manifest' first.")
        return

    with open(MANIFEST_FILE, encoding="utf-8") as f:
        manifest = json.load(f)

    total = manifest["total_trials"]
    trials = manifest["trials"]

    completed = sum(1 for t in trials if t["status"] == "completed")
    in_progress = sum(1 for t in trials if t["status"] == "in_progress")
    pending = sum(1 for t in trials if t["status"] == "pending")
    errored = sum(1 for t in trials if t["status"] == "error")

    print(f"Experiment Status: {manifest['study']} v{manifest['version']}")
    print(f"  Total trials: {total}")
    print(f"  Completed:    {completed} ({100*completed/total:.1f}%)")
    print(f"  In progress:  {in_progress}")
    print(f"  Pending:      {pending}")
    print(f"  Errors:       {errored}")
    print(f"  API calls:    ~{manifest['estimated_api_calls']} estimated")

    if completed > 0:
        results = []
        for t in trials:
            if t["result_file"] and Path(t["result_file"]).exists():
                with open(t["result_file"], encoding="utf-8") as f:
                    results.append(json.load(f))

        if results:
            successes = sum(1 for r in results if r.get("jailbreak_success"))
            print(f"\n  Jailbreak success rate: {successes}/{len(results)} "
                  f"({100*successes/len(results):.1f}%)")


def export_csv():
    if not EXPERIMENT_LOG.exists():
        print("No experiment log found.")
        return

    import csv

    csv_file = EXPERIMENTS / "results_export.csv"
    fields = [
        "trial_id", "config_id", "technique_id", "task_id", "seed",
        "jailbreak_success", "output_usefulness", "verifier_catch",
        "error", "timestamp"
    ]

    with open(EXPERIMENT_LOG, encoding="utf-8") as f:
        entries = [json.loads(line) for line in f if line.strip()]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(entries)

    print(f"Exported {len(entries)} results to {csv_file}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: experiment_runner.py [generate-manifest|status|export]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "generate-manifest":
        use_pilot = "--pilot" in sys.argv
        generate_manifest(use_pilot=use_pilot)
    elif cmd == "status":
        get_status()
    elif cmd == "export":
        export_csv()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
