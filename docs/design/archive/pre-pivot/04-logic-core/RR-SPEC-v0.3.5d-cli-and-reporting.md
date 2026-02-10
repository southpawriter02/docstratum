# v0.3.5d — CLI Interface & Report Generation

> Command-line interface for test orchestration, interactive mode, and comprehensive report generation in multiple formats.

## Objective

Design and implement a user-friendly CLI that:
- Supports subcommands for test execution (`run`, `suite`, `report`, `export`)
- Provides interactive mode for exploratory testing
- Generates formatted reports (terminal, markdown, HTML)
- Exports results to multiple formats (JSON, CSV, markdown)
- Integrates with CI/CD pipelines
- Prepares data for v0.4.x Streamlit dashboard

## Scope Boundaries

- **In scope**: CLI design (argparse), interactive mode, report generation (3+ formats), export (4+ formats), CI/CD integration (GitHub Actions template), Streamlit data preparation
- **Out of scope**: Web dashboard implementation (v0.4.x), real-time streaming, report scheduling
- **Constraints**: All reports must complete in <30s for 20-question suite; terminal output must work in ANSI-compliant terminals; exports must be human-readable

## Dependency Diagram

```
┌────────────────────────────────────────────────┐
│         cli.py (argparse entry point)          │
├────────────────────────────────────────────────┤
│ run / suite / report / export subcommands      │
└──────────┬──────────────────────────────────────┘
           │
    ┌──────┴────────────────────────┐
    │                               │
┌───▼──────────────┐    ┌──────────▼────────┐
│  TestOrchestrator │    │ ReportGenerator    │
│  (execution)      │    │ (formatting)       │
└───────┬───────────┘    └───────┬───────────┘
        │                        │
    ┌───┴────┬────┬──────┬───────┴──────────────┐
    │        │    │      │                      │
┌───▼──┐ ┌──▼─┐ ┌─▼────┐ ┌────────┐ ┌──────┐ ┌▼──────┐
│JSON  │ │CSV │ │YAML  │ │Terminal│ │HTML  │ │Markdown│
│Export│ │    │ │      │ │Report  │ │      │ │Report  │
└──────┘ └────┘ └──────┘ └────────┘ └──────┘ └────────┘
```

## Content Sections

### 1. CLI Design with Argparse

**File: `run_ab_test.py`**

```python
#!/usr/bin/env python3
"""
DocStratum v0.3.5 A/B Test Harness CLI

Usage:
    python run_ab_test.py run --question "What is DocStratum?"
    python run_ab_test.py suite --name core_coverage
    python run_ab_test.py report --session <session_id>
    python run_ab_test.py export --session <session_id> --format json
    python run_ab_test.py interactive
"""

import argparse
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import json

from ab_test_harness import ABTestHarness, LLMSource
from question_bank import QuestionBank, SuiteBuilder
from metrics import MetricsSummary, HeuristicQualityScorer, LLMAsJudgeScorer
from reports import (
    TerminalReportGenerator,
    MarkdownReportGenerator,
    HTMLReportGenerator,
    ExportManager,
)


class DocStratumCLI:
    """Main CLI orchestrator."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path('./docstratum_config.json')
        self.config = self._load_config()
        self.harness = self._init_harness()
        self.question_bank = QuestionBank(Path('./question_bank.yaml'))

    def _load_config(self) -> dict:
        """Load CLI configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {
            'llms_source_path': './llms.txt',
            'baseline_model': 'claude-3-5-sonnet',
            'docstratum_model': 'claude-3-5-sonnet',
            'results_dir': './results',
            'quality_scorer': 'heuristic',  # or 'llm_as_judge'
        }

    def _init_harness(self) -> ABTestHarness:
        """Initialize the test harness."""
        return ABTestHarness(
            llms_source=LLMSource(self.config['llms_source_path']),
            baseline_model=self.config['baseline_model'],
            docstratum_model=self.config['docstratum_model'],
        )

    def cmd_run(self, args) -> int:
        """Execute a single test question."""
        print(f"Running single question test...")
        print(f"Question: {args.question}")

        try:
            result = self.harness.run_test(args.question)

            # Display quick result
            terminal_gen = TerminalReportGenerator()
            terminal_gen.print_result(result)

            # Optionally save
            if args.save:
                self.harness.persist_result(result)
                print(f"Result saved to session: {result.session_id}")

            return 0

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    def cmd_suite(self, args) -> int:
        """Execute a test suite."""
        print(f"Running test suite: {args.name}")

        # Load suite
        suite_questions = self.question_bank.get_suite(args.name)
        if not suite_questions:
            print(f"Error: Suite '{args.name}' not found", file=sys.stderr)
            return 1

        print(f"Suite contains {len(suite_questions)} questions")
        print(f"Estimated runtime: {len(suite_questions) * 2} seconds")

        if args.interactive and not args.yes:
            response = input("Continue? (y/n) ")
            if response.lower() != 'y':
                return 0

        try:
            # Run suite
            results = []
            for i, question in enumerate(suite_questions, 1):
                print(f"  [{i}/{len(suite_questions)}] {question.id}...", end=' ')
                result = self.harness.run_test(question.text)
                results.append(result)
                print("done")

            # Compute metrics
            print("\nComputing metrics...")
            scorer = self._get_quality_scorer()
            metrics = MetricsSummary.compute(
                results,
                session_id=self.harness.current_session.session_id,
                suite_name=args.name,
                quality_scorer=scorer,
            )

            # Display summary
            terminal_gen = TerminalReportGenerator()
            terminal_gen.print_suite_summary(metrics)

            # Save results
            self.harness.persist_results(results)
            print(f"\nResults saved to session: {metrics.session_id}")

            return 0

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    def cmd_report(self, args) -> int:
        """Generate report from saved session."""
        print(f"Generating report for session: {args.session}")

        try:
            session = self.harness.persistence.load_session(args.session)
            if not session:
                print(f"Error: Session '{args.session}' not found", file=sys.stderr)
                return 1

            # Compute metrics
            scorer = self._get_quality_scorer() if not args.no_quality else None
            metrics = MetricsSummary.compute(
                session.results,
                session_id=args.session,
                quality_scorer=scorer,
            )

            # Generate report(s)
            if args.format == 'terminal' or args.format == 'all':
                terminal_gen = TerminalReportGenerator()
                terminal_gen.print_full_report(metrics)

            if args.format == 'markdown' or args.format == 'all':
                md_path = self._save_markdown_report(metrics)
                print(f"Markdown report saved to: {md_path}")

            if args.format == 'html' or args.format == 'all':
                html_path = self._save_html_report(metrics)
                print(f"HTML report saved to: {html_path}")

            return 0

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    def cmd_export(self, args) -> int:
        """Export session results to various formats."""
        print(f"Exporting session: {args.session}")

        try:
            session = self.harness.persistence.load_session(args.session)
            if not session:
                print(f"Error: Session '{args.session}' not found", file=sys.stderr)
                return 1

            export_mgr = ExportManager(Path(self.config['results_dir']))

            if args.format == 'json' or args.format == 'all':
                path = export_mgr.export_json(session)
                print(f"JSON exported to: {path}")

            if args.format == 'csv' or args.format == 'all':
                path = export_mgr.export_csv(session)
                print(f"CSV exported to: {path}")

            if args.format == 'yaml' or args.format == 'all':
                path = export_mgr.export_yaml(session)
                print(f"YAML exported to: {path}")

            return 0

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    def cmd_interactive(self, args) -> int:
        """Interactive mode for exploratory testing."""
        print("DocStratum A/B Test Interactive Mode")
        print("Type 'help' for commands, 'quit' to exit")
        print("-" * 50)

        while True:
            try:
                prompt = input("\n> ").strip()

                if not prompt:
                    continue

                if prompt == 'quit' or prompt == 'exit':
                    print("Goodbye!")
                    return 0

                if prompt == 'help':
                    self._print_interactive_help()
                    continue

                if prompt.startswith('test '):
                    question = prompt[5:].strip()
                    result = self.harness.run_test(question)
                    terminal_gen = TerminalReportGenerator()
                    terminal_gen.print_result(result)
                    continue

                if prompt.startswith('suite '):
                    suite_name = prompt[6:].strip()
                    suite = self.question_bank.get_suite(suite_name)
                    if suite:
                        print(f"Suite '{suite_name}' has {len(suite)} questions")
                    else:
                        print(f"Suite '{suite_name}' not found")
                    continue

                if prompt == 'list suites':
                    for suite_name in self.question_bank.suites.keys():
                        print(f"  - {suite_name}")
                    continue

                if prompt == 'list sessions':
                    sessions = self.harness.persistence.list_sessions()
                    for session_id in sessions:
                        print(f"  - {session_id}")
                    continue

                # Default: treat as question
                result = self.harness.run_test(prompt)
                terminal_gen = TerminalReportGenerator()
                terminal_gen.print_result(result)

            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'quit' to exit.")
            except Exception as e:
                print(f"Error: {e}")

    def _get_quality_scorer(self):
        """Get configured quality scorer."""
        if self.config['quality_scorer'] == 'llm_as_judge':
            return LLMAsJudgeScorer(
                self.harness.llms_source,
                judge_model=self.config.get('judge_model', 'claude-3-5-sonnet'),
            )
        return HeuristicQualityScorer()

    def _save_markdown_report(self, metrics: MetricsSummary) -> Path:
        """Save markdown report to file."""
        md_gen = MarkdownReportGenerator()
        md_content = md_gen.generate(metrics)

        output_dir = Path(self.config['results_dir']) / 'reports'
        output_dir.mkdir(exist_ok=True, parents=True)

        filename = f"report__{metrics.session_id}.md"
        filepath = output_dir / filename

        with open(filepath, 'w') as f:
            f.write(md_content)

        return filepath

    def _save_html_report(self, metrics: MetricsSummary) -> Path:
        """Save HTML report to file."""
        html_gen = HTMLReportGenerator()
        html_content = html_gen.generate(metrics)

        output_dir = Path(self.config['results_dir']) / 'reports'
        output_dir.mkdir(exist_ok=True, parents=True)

        filename = f"report__{metrics.session_id}.html"
        filepath = output_dir / filename

        with open(filepath, 'w') as f:
            f.write(html_content)

        return filepath

    @staticmethod
    def _print_interactive_help():
        """Print interactive mode help."""
        help_text = """
Available commands:
  test <question>       Run single question test
  suite <name>          Show suite info
  list suites          List all available suites
  list sessions        List all saved sessions
  help                 Show this help
  quit                 Exit interactive mode

Example:
  > test What is DocStratum?
  > suite core_coverage
        """
        print(help_text)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='DocStratum v0.3.5 A/B Test Harness',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_ab_test.py run --question "What is DocStratum?"
  python run_ab_test.py suite --name core_coverage
  python run_ab_test.py report --session abc123
  python run_ab_test.py export --session abc123 --format json
  python run_ab_test.py interactive
        """,
    )

    parser.add_argument(
        '--config',
        type=Path,
        default='./docstratum_config.json',
        help='Path to config file',
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # run subcommand
    run_parser = subparsers.add_parser('run', help='Run single question test')
    run_parser.add_argument('--question', required=True, help='Question to test')
    run_parser.add_argument('--save', action='store_true', help='Save result to session')

    # suite subcommand
    suite_parser = subparsers.add_parser('suite', help='Run test suite')
    suite_parser.add_argument('--name', required=True, help='Suite name')
    suite_parser.add_argument('--yes', action='store_true', help='Skip confirmation')
    suite_parser.add_argument('--interactive', action='store_true', default=True)

    # report subcommand
    report_parser = subparsers.add_parser('report', help='Generate report')
    report_parser.add_argument('--session', required=True, help='Session ID')
    report_parser.add_argument(
        '--format',
        choices=['terminal', 'markdown', 'html', 'all'],
        default='terminal',
        help='Report format',
    )
    report_parser.add_argument('--no-quality', action='store_true', help='Skip quality scoring')

    # export subcommand
    export_parser = subparsers.add_parser('export', help='Export session results')
    export_parser.add_argument('--session', required=True, help='Session ID')
    export_parser.add_argument(
        '--format',
        choices=['json', 'csv', 'yaml', 'all'],
        default='json',
        help='Export format',
    )

    # interactive subcommand
    subparsers.add_parser('interactive', help='Interactive test mode')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize CLI
    cli = DocStratumCLI(args.config)

    # Dispatch to command handler
    if args.command == 'run':
        return cli.cmd_run(args)
    elif args.command == 'suite':
        return cli.cmd_suite(args)
    elif args.command == 'report':
        return cli.cmd_report(args)
    elif args.command == 'export':
        return cli.cmd_export(args)
    elif args.command == 'interactive':
        return cli.cmd_interactive(args)

    return 1


if __name__ == '__main__':
    sys.exit(main())
```

### 2. Interactive Mode Implementation

Enhanced interactive session management:

```python
class InteractiveSession:
    """Manages stateful interactive testing."""

    def __init__(self, harness: ABTestHarness, question_bank: QuestionBank):
        self.harness = harness
        self.question_bank = question_bank
        self.session_tests = []
        self.history = []

    def add_test(self, question: str):
        """Add test result to session."""
        result = self.harness.run_test(question)
        self.session_tests.append(result)
        self.history.append({
            'question': question,
            'timestamp': datetime.utcnow().isoformat(),
            'success': result.both_successful,
        })
        return result

    def show_session_summary(self):
        """Display current session summary."""
        if not self.session_tests:
            print("No tests in current session")
            return

        successful = sum(1 for r in self.session_tests if r.both_successful)
        total = len(self.session_tests)

        print(f"\nSession Summary ({total} tests)")
        print(f"Success rate: {successful}/{total} ({successful*100/total:.1f}%)")

        # Token efficiency
        total_baseline_tokens = sum(r.baseline.total_tokens for r in self.session_tests)
        total_docstratum_tokens = sum(r.docstratum.total_tokens for r in self.session_tests)
        token_diff = total_docstratum_tokens - total_baseline_tokens

        print(f"Token usage: {total_baseline_tokens} (baseline) vs {total_docstratum_tokens} (docstratum)")
        print(f"Difference: {token_diff:+d} tokens ({token_diff*100/total_baseline_tokens:+.1f}%)")

    def save_session(self) -> str:
        """Save interactive session to disk."""
        session = self.harness.create_session(
            results=self.session_tests,
            notes="Interactive session",
        )
        self.harness.persistence.save_session(session)
        return session.session_id
```

### 3. Report Generation (Terminal, Markdown, HTML)

**Terminal Report Generator:**

```python
from colorama import Fore, Back, Style, init

init(autoreset=True)

class TerminalReportGenerator:
    """Generate terminal-formatted reports with colors."""

    def print_result(self, result: ABTestResult):
        """Print single test result to terminal."""
        print(f"\nTest: {result.question[:80]}")
        print("=" * 80)

        # Baseline
        print(f"{Fore.BLUE}Baseline{Style.RESET_ALL}")
        print(f"  Tokens: {result.baseline.total_tokens}")
        print(f"  Latency: {result.baseline.latency_ms:.2f}ms")
        print(f"  Length: {len(result.baseline.response)} chars")
        if result.baseline.error:
            print(f"  {Fore.RED}Error: {result.baseline.error}{Style.RESET_ALL}")

        # DocStratum
        print(f"\n{Fore.GREEN}DocStratum{Style.RESET_ALL}")
        print(f"  Tokens: {result.docstratum.total_tokens}")
        print(f"  Latency: {result.docstratum.latency_ms:.2f}ms")
        print(f"  Length: {len(result.docstratum.response)} chars")
        if result.docstratum.error:
            print(f"  {Fore.RED}Error: {result.docstratum.error}{Style.RESET_ALL}")

        # Comparison
        print(f"\n{Fore.CYAN}Comparison{Style.RESET_ALL}")
        token_color = Fore.GREEN if result.token_overhead < 0 else Fore.RED if result.token_overhead > 0 else Fore.WHITE
        latency_color = Fore.GREEN if result.latency_diff_ms < 0 else Fore.RED if result.latency_diff_ms > 0 else Fore.WHITE

        print(f"  Token overhead: {token_color}{result.token_overhead:+d}{Style.RESET_ALL} ({result.token_overhead_pct:+.1f}%)")
        print(f"  Latency diff: {latency_color}{result.latency_diff_ms:+.2f}ms{Style.RESET_ALL} ({result.latency_improvement_pct:+.1f}%)")
        print(f"  Length ratio: {result.response_length_ratio:.2f}x")

    def print_suite_summary(self, metrics: MetricsSummary):
        """Print suite-level summary."""
        print(f"\n{Fore.CYAN}Test Suite Summary{Style.RESET_ALL}")
        print(f"Suite: {metrics.suite_name}")
        print(f"Tests: {metrics.aggregate_metrics.total_tests}")
        print(f"Success rate: {metrics.aggregate_metrics.success_rate*100:.1f}%")
        print(f"\n{Fore.YELLOW}Key Findings:{Style.RESET_ALL}")
        for finding in metrics.key_findings:
            print(f"  • {finding}")

    def print_full_report(self, metrics: MetricsSummary):
        """Print comprehensive report."""
        print(f"\n{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}A/B Test Report - Session {metrics.session_id}{Style.RESET_ALL}")
        print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")

        print(f"\nSuite: {metrics.suite_name}")
        print(f"Timestamp: {metrics.timestamp.isoformat()}")

        # Aggregate metrics
        agg = metrics.aggregate_metrics
        print(f"\n{Fore.CYAN}Aggregate Metrics{Style.RESET_ALL}")
        print(f"  Token overhead: {agg.mean_token_overhead:+.0f} ± {agg.std_token_overhead:.0f} tokens")
        print(f"  Latency diff: {agg.mean_latency_diff_ms:+.2f} ± {agg.std_latency_diff_ms:.2f} ms")
        print(f"  Response length ratio: {agg.mean_length_ratio:.2f}x")

        # Statistical significance
        print(f"\n{Fore.CYAN}Statistical Significance{Style.RESET_ALL}")
        print(f"  Token overhead: {metrics.token_overhead_significance.summary()}")
        print(f"  Latency diff: {metrics.latency_diff_significance.summary()}")

        # Key findings
        print(f"\n{Fore.YELLOW}Key Findings{Style.RESET_ALL}")
        for finding in metrics.key_findings:
            print(f"  • {finding}")

        # Winner
        winner_color = Fore.GREEN if metrics.overall_winner == 'docstratum' else Fore.BLUE if metrics.overall_winner == 'baseline' else Fore.WHITE
        print(f"\n{winner_color}Overall Winner: {metrics.overall_winner.upper()}{Style.RESET_ALL}")
```

**Markdown Report Generator:**

```python
class MarkdownReportGenerator:
    """Generate markdown-formatted reports."""

    def generate(self, metrics: MetricsSummary) -> str:
        """Generate complete markdown report."""
        lines = []

        lines.append(f"# A/B Test Report - {metrics.suite_name}")
        lines.append(f"\n**Session ID:** `{metrics.session_id}`")
        lines.append(f"**Generated:** {metrics.timestamp.isoformat()}")

        # Summary
        lines.append("\n## Summary")
        lines.append(f"**Winner:** {metrics.overall_winner.upper()}")
        lines.append(f"**Tests:** {metrics.aggregate_metrics.total_tests}")
        lines.append(f"**Success Rate:** {metrics.aggregate_metrics.success_rate*100:.1f}%")

        # Key Findings
        lines.append("\n## Key Findings")
        for finding in metrics.key_findings:
            lines.append(f"- {finding}")

        # Metrics
        agg = metrics.aggregate_metrics
        lines.append("\n## Metrics Summary")
        lines.append("\n### Token Efficiency")
        lines.append(f"- Mean overhead: {agg.mean_token_overhead:+.0f} tokens")
        lines.append(f"- Std dev: {agg.std_token_overhead:.0f}")
        lines.append(f"- Range: {agg.min_token_overhead} to {agg.max_token_overhead}")

        lines.append("\n### Latency")
        lines.append(f"- Mean difference: {agg.mean_latency_diff_ms:+.2f} ms")
        lines.append(f"- Std dev: {agg.std_latency_diff_ms:.2f}")
        lines.append(f"- Range: {agg.min_latency_diff_ms:.2f} to {agg.max_latency_diff_ms:.2f}")

        lines.append("\n### Response Quality")
        lines.append(f"- Mean length ratio: {agg.mean_length_ratio:.2f}x")
        lines.append(f"- Mean URLs (baseline): {agg.mean_url_count_baseline:.1f}")
        lines.append(f"- Mean URLs (docstratum): {agg.mean_url_count_docstratum:.1f}")

        # Statistical Tests
        lines.append("\n## Statistical Analysis")
        lines.append(f"- **Token Test:** {metrics.token_overhead_significance.summary()}")
        lines.append(f"- **Latency Test:** {metrics.latency_diff_significance.summary()}")

        # Per-question breakdown (truncated)
        lines.append("\n## Per-Question Results (first 5)")
        lines.append("|Question|Tokens|Latency|URL Count|")
        lines.append("|--------|------|-------|---------|")
        for metric in metrics.per_question_metrics[:5]:
            q_short = metric.question_text[:30]
            lines.append(
                f"|{q_short}|{metric.token_overhead:+d}|"
                f"{metric.latency_diff_ms:+.1f}ms|"
                f"{metric.url_count_docstratum - metric.url_count_baseline:+d}|"
            )

        return '\n'.join(lines)
```

**HTML Report Generator:**

```python
class HTMLReportGenerator:
    """Generate HTML reports for portfolio/documentation."""

    def generate(self, metrics: MetricsSummary) -> str:
        """Generate complete HTML report."""
        agg = metrics.aggregate_metrics

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>DocStratum A/B Test Report - {metrics.suite_name}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; background: #f5f5f5; }}
        .header {{ background: #2c3e50; color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
        .metric {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric h3 {{ margin-top: 0; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        .metric-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 10px; }}
        .metric-item {{ padding: 10px; background: #f9f9f9; border-radius: 4px; }}
        .winner {{ font-size: 1.2em; font-weight: bold; padding: 10px; border-radius: 4px; }}
        .winner.docstratum {{ background: #d4edda; color: #155724; }}
        .winner.baseline {{ background: #cfe2ff; color: #084298; }}
        table {{ width: 100%; border-collapse: collapse; background: white; margin-top: 10px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #2c3e50; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .positive {{ color: #27ae60; }}
        .negative {{ color: #e74c3c; }}
        .finding {{ padding: 10px; margin: 5px 0; background: #e8f4f8; border-left: 4px solid #3498db; border-radius: 4px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>DocStratum A/B Test Report</h1>
        <p><strong>Suite:</strong> {metrics.suite_name}</p>
        <p><strong>Session ID:</strong> {metrics.session_id}</p>
        <p><strong>Generated:</strong> {metrics.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
    </div>

    <div class="metric">
        <h3>Overall Result</h3>
        <div class="winner {metrics.overall_winner}">
            Winner: {metrics.overall_winner.upper()}
        </div>
    </div>

    <div class="metric">
        <h3>Key Findings</h3>
        {''.join(f'<div class="finding">{f}</div>' for f in metrics.key_findings)}
    </div>

    <div class="metric">
        <h3>Aggregate Metrics</h3>
        <div class="metric-row">
            <div class="metric-item">
                <strong>Token Efficiency</strong><br>
                Mean: <span class="{'positive' if agg.mean_token_overhead < 0 else 'negative'}">{agg.mean_token_overhead:+.0f}</span> tokens<br>
                Std: {agg.std_token_overhead:.0f}<br>
                Range: {agg.min_token_overhead} to {agg.max_token_overhead}
            </div>
            <div class="metric-item">
                <strong>Latency</strong><br>
                Mean: <span class="{'positive' if agg.mean_latency_diff_ms < 0 else 'negative'}">{agg.mean_latency_diff_ms:+.2f}</span> ms<br>
                Std: {agg.std_latency_diff_ms:.2f}<br>
                Range: {agg.min_latency_diff_ms:.2f} to {agg.max_latency_diff_ms:.2f}
            </div>
        </div>
    </div>

    <div class="metric">
        <h3>Statistical Significance</h3>
        <table>
            <tr><th>Test</th><th>Statistic</th><th>P-Value</th><th>Effect Size</th><th>Significant?</th></tr>
            <tr>
                <td>Token Overhead</td>
                <td>{metrics.token_overhead_significance.statistic:.3f}</td>
                <td>{metrics.token_overhead_significance.p_value:.4f}</td>
                <td>{metrics.token_overhead_significance.effect_size:.3f}</td>
                <td>{'Yes' if metrics.token_overhead_significance.significant_at_05 else 'No'}</td>
            </tr>
            <tr>
                <td>Latency Difference</td>
                <td>{metrics.latency_diff_significance.statistic:.3f}</td>
                <td>{metrics.latency_diff_significance.p_value:.4f}</td>
                <td>{metrics.latency_diff_significance.effect_size:.3f}</td>
                <td>{'Yes' if metrics.latency_diff_significance.significant_at_05 else 'No'}</td>
            </tr>
        </table>
    </div>

    <div class="metric">
        <h3>Response Quality</h3>
        <table>
            <tr><th>Metric</th><th>Baseline</th><th>DocStratum</th><th>Difference</th></tr>
            <tr>
                <td>Mean Length Ratio</td>
                <td>1.00</td>
                <td>{agg.mean_length_ratio:.2f}</td>
                <td>{agg.mean_length_ratio - 1:+.2f}</td>
            </tr>
            <tr>
                <td>Mean URL Count</td>
                <td>{agg.mean_url_count_baseline:.1f}</td>
                <td>{agg.mean_url_count_docstratum:.1f}</td>
                <td>{agg.mean_url_count_docstratum - agg.mean_url_count_baseline:+.1f}</td>
            </tr>
        </table>
    </div>

</body>
</html>
"""
        return html
```

### 4. Export Manager (JSON, CSV, YAML, Markdown)

```python
import yaml

class ExportManager:
    """Handle exports in multiple formats."""

    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir) / 'exports'
        self.output_dir.mkdir(exist_ok=True, parents=True)

    def export_json(self, session: TestSession) -> Path:
        """Export session to JSON."""
        filename = f"session__{session.session_id}.json"
        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            json.dump(session.to_dict(), f, indent=2, default=str)

        return filepath

    def export_csv(self, session: TestSession) -> Path:
        """Export session results to CSV."""
        import csv

        filename = f"session__{session.session_id}.csv"
        filepath = self.output_dir / filename

        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    'question',
                    'baseline_tokens',
                    'docstratum_tokens',
                    'token_overhead',
                    'token_overhead_pct',
                    'baseline_latency_ms',
                    'docstratum_latency_ms',
                    'latency_diff_ms',
                    'latency_improvement_pct',
                    'response_length_ratio',
                    'baseline_urls',
                    'docstratum_urls',
                    'baseline_success',
                    'docstratum_success',
                ],
            )
            writer.writeheader()

            for result in session.results:
                writer.writerow({
                    'question': result.question[:100],
                    'baseline_tokens': result.baseline.total_tokens,
                    'docstratum_tokens': result.docstratum.total_tokens,
                    'token_overhead': result.token_overhead,
                    'token_overhead_pct': f'{result.token_overhead_pct:.2f}',
                    'baseline_latency_ms': f'{result.baseline.latency_ms:.2f}',
                    'docstratum_latency_ms': f'{result.docstratum.latency_ms:.2f}',
                    'latency_diff_ms': f'{result.latency_diff_ms:.2f}',
                    'latency_improvement_pct': f'{result.latency_improvement_pct:.2f}',
                    'response_length_ratio': f'{result.response_length_ratio:.2f}',
                    'baseline_urls': 0,  # Computed from response
                    'docstratum_urls': 0,
                    'baseline_success': result.baseline.success,
                    'docstratum_success': result.docstratum.success,
                })

        return filepath

    def export_yaml(self, session: TestSession) -> Path:
        """Export session to YAML."""
        filename = f"session__{session.session_id}.yaml"
        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            yaml.dump(session.to_dict(), f, default_flow_style=False)

        return filepath

    def export_markdown(self, metrics: MetricsSummary) -> Path:
        """Export metrics as markdown."""
        md_gen = MarkdownReportGenerator()
        md_content = md_gen.generate(metrics)

        filename = f"metrics__{metrics.session_id}.md"
        filepath = self.output_dir / filename

        with open(filepath, 'w') as f:
            f.write(md_content)

        return filepath
```

### 5. CI/CD Integration (GitHub Actions)

**File: `.github/workflows/ab_test_suite.yaml`**

```yaml
name: DocStratum A/B Test Suite

on:
  push:
    branches: [main, develop]
    paths:
      - 'docstratum/**'
      - 'llms.txt'
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install anthropic pytest colorama pyyaml scipy numpy

      - name: Run core coverage suite
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python run_ab_test.py suite --name core_coverage --yes

      - name: Generate reports
        run: |
          # Get latest session ID
          LATEST_SESSION=$(python -c "import json; sessions = []; exec(open('list_sessions.py').read()); print(sessions[0] if sessions else '')")
          python run_ab_test.py report --session $LATEST_SESSION --format all

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: ab-test-results
          path: results/

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const report = fs.readFileSync('results/reports/latest.md', 'utf8');
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: '## A/B Test Results\n\n' + report
            });
```

### 6. Streamlit Data Preparation

Prepare data structures for v0.4.x dashboard:

```python
class StreamlitDataAdapter:
    """Adapter to prepare data for Streamlit dashboard."""

    @staticmethod
    def metrics_to_df(metrics: MetricsSummary) -> dict:
        """Convert metrics to pandas-compatible dict for Streamlit."""
        import pandas as pd

        per_q_data = []
        for m in metrics.per_question_metrics:
            per_q_data.append({
                'question': m.question_id,
                'token_overhead': m.token_overhead,
                'latency_diff': m.latency_diff_ms,
                'length_ratio': m.length_ratio,
                'baseline_success': m.baseline_success,
                'docstratum_success': m.docstratum_success,
            })

        return {
            'session_id': metrics.session_id,
            'suite_name': metrics.suite_name,
            'per_question_df': pd.DataFrame(per_q_data) if per_q_data else pd.DataFrame(),
            'aggregate_metrics': metrics.aggregate_metrics.to_dict(),
            'statistical_results': {
                'token_test': metrics.token_overhead_significance.summary(),
                'latency_test': metrics.latency_diff_significance.summary(),
            },
            'key_findings': metrics.key_findings,
        }
```

## Deliverables

1. **DocStratumCLI main class** (300 lines)
   - config loading and harness initialization
   - run, suite, report, export command handlers
   - interactive mode dispatch

2. **Argparse CLI setup** (120 lines)
   - 4 subcommands with required/optional args
   - help text and examples
   - main() entry point

3. **InteractiveSession class** (100 lines)
   - stateful test management
   - session summary display
   - save/load functionality

4. **TerminalReportGenerator** (150 lines)
   - print_result() with colors
   - print_suite_summary()
   - print_full_report()
   - ANSI color codes

5. **MarkdownReportGenerator** (120 lines)
   - generate() returns markdown string
   - Includes metrics tables
   - Per-question breakdown

6. **HTMLReportGenerator** (180 lines)
   - generate() returns standalone HTML
   - CSS styling embedded
   - Responsive layout
   - Statistics tables

7. **ExportManager class** (140 lines)
   - JSON, CSV, YAML exports
   - Markdown export
   - Proper file handling

8. **CI/CD GitHub Actions workflow** (60 lines)
   - Runs core_coverage suite
   - Generates all reports
   - Comments on PRs
   - Uploads artifacts

9. **StreamlitDataAdapter** (50 lines)
   - Converts metrics to Streamlit-compatible format
   - Dataframe preparation

## Acceptance Criteria

- [ ] All 4 subcommands (run, suite, report, export) execute without errors
- [ ] Interactive mode accepts user input and processes commands correctly
- [ ] Terminal report uses ANSI colors for emphasis (baseline=blue, docstratum=green)
- [ ] Markdown report generates valid markdown (passes lint check)
- [ ] HTML report renders correctly in modern browsers
- [ ] All exports preserve data without loss (round-trip consistency)
- [ ] CSV export opens correctly in Excel/Sheets
- [ ] YAML export is valid and parseable
- [ ] Reports complete in <30s for 20-question suite
- [ ] GitHub Actions workflow runs on schedule and PR
- [ ] PR comment includes summary metrics
- [ ] Config file is optional with sensible defaults
- [ ] Error messages are helpful and actionable
- [ ] Streamlit adapter produces valid dataframe
- [ ] No API keys or secrets in output files

## Next Step

→ Phase v0.3.5 complete. Proceed to **v0.4.x — Visualization Layer** to build the Streamlit dashboard for real-time metrics visualization and interactive test exploration.
