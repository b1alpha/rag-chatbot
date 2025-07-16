#!/usr/bin/env python3
"""
Static Analysis CLI for Code Quality Assessment

This tool analyzes code repositories using RAG-based quality guidance
to assess test portfolios, strategy compliance, and quality issues.
"""

import argparse
import os
import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.static_analysis import StaticAnalyzer, analyze_repository


def main():
    parser = argparse.ArgumentParser(
        description="Analyze code repositories for quality issues using RAG-based guidance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_code.py /path/to/repo
  python analyze_code.py ../my-project --output report.json
  python analyze_code.py /path/to/repo --format json
        """
    )
    
    parser.add_argument(
        'repo_path',
        help='Path to the repository to analyze'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Output file path (optional)'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['console', 'json', 'markdown'],
        default='console',
        help='Output format (default: console)'
    )
    
    parser.add_argument(
        '--quality-chunks',
        default='./data/quality_chunks_processed',
        help='Path to quality chunks directory (default: ./data/quality_chunks_processed)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate repository path
    if not os.path.exists(args.repo_path):
        print(f"❌ Error: Repository path '{args.repo_path}' does not exist")
        sys.exit(1)
    
    if not os.path.isdir(args.repo_path):
        print(f"❌ Error: '{args.repo_path}' is not a directory")
        sys.exit(1)
    
    # Validate quality chunks directory
    if not os.path.exists(args.quality_chunks):
        print(f"❌ Error: Quality chunks directory '{args.quality_chunks}' does not exist")
        sys.exit(1)
    
    try:
        # Initialize analyzer
        analyzer = StaticAnalyzer(quality_chunks_dir=args.quality_chunks)
        
        # Run analysis
        print(f"🚀 Starting static analysis of {args.repo_path}")
        report = analyzer.generate_report(args.repo_path)
        
        # Output results
        if args.format == 'console':
            analyzer.print_report(report)
        elif args.format == 'json':
            output_json(report, args.output)
        elif args.format == 'markdown':
            output_markdown(report, args.output)
        
        # Summary for exit code
        if report.summary['high_severity_issues'] > 0:
            print(f"\n⚠️  Found {report.summary['high_severity_issues']} high severity issues")
            sys.exit(1)
        else:
            print(f"\n✅ Analysis complete! Overall score: {report.summary['overall_score']:.1f}/100")
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def output_json(report, output_path=None):
    """Output report in JSON format"""
    import json
    from dataclasses import asdict
    
    # Convert report to dict
    report_dict = asdict(report)
    
    # Convert to JSON
    json_output = json.dumps(report_dict, indent=2, default=str)
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(json_output)
        print(f"📄 Report saved to {output_path}")
    else:
        print(json_output)


def output_markdown(report, output_path=None):
    """Output report in Markdown format"""
    from collections import defaultdict
    import datetime
    
    md_content = f"""# Static Analysis Report

**Repository:** `{report.repo_path}`  
**Analysis Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Tests:** {report.summary['total_tests']}
- **Test Levels Found:** {report.summary['test_levels_found']}/6
- **Overall Score:** {report.summary['overall_score']:.1f}/100
- **Total Issues:** {report.summary['total_issues']}
- **High Severity Issues:** {report.summary['high_severity_issues']}

## Test Portfolio

| Test Level | Count | Files |
|------------|-------|-------|
"""
    
    for level_name, level in report.test_portfolio.items():
        files_str = ", ".join(level.files[:3])
        if len(level.files) > 3:
            files_str += f" ... and {len(level.files) - 3} more"
        md_content += f"| {level_name.title()} | {level.count} | {files_str} |\n"
    
    md_content += f"""
## Strategy Compliance

**Overall Score:** {report.strategy_assessment['overall_score']:.1f}/100

"""
    
    for area_name, area_data in report.strategy_assessment['areas'].items():
        md_content += f"### {area_name.replace('_', ' ').title()}\n"
        md_content += f"**Score:** {area_data['score']}/100\n\n"
        
        if area_name == 'test_distribution':
            md_content += f"- Unit: {area_data['unit_percentage']:.1f}%\n"
            md_content += f"- Integration: {area_data['integration_percentage']:.1f}%\n"
            md_content += f"- E2E: {area_data['e2e_percentage']:.1f}%\n\n"
    
    md_content += "## Quality Issues\n\n"
    
    # Group issues by severity
    issues_by_severity = defaultdict(list)
    for issue in report.quality_issues:
        issues_by_severity[issue.severity].append(issue)
    
    for severity in ['HIGH', 'MEDIUM', 'LOW']:
        if severity in issues_by_severity:
            md_content += f"### {severity} Severity ({len(issues_by_severity[severity])} issues)\n\n"
            for issue in issues_by_severity[severity][:10]:  # Show first 10 of each severity
                md_content += f"#### {issue.file_path}\n"
                if issue.line_number:
                    md_content += f"**Line {issue.line_number}:** {issue.issue}\n\n"
                else:
                    md_content += f"**Issue:** {issue.issue}\n\n"
                md_content += f"**Recommendation:** {issue.recommendation}\n\n"
                md_content += "---\n\n"
    
    md_content += "## Recommendations\n\n"
    for i, rec in enumerate(report.strategy_assessment['recommendations'][:10], 1):
        if rec.strip():
            md_content += f"{i}. {rec.strip()}\n"
    
    if output_path:
        with open(output_path, 'w') as f:
            f.write(md_content)
        print(f"📄 Report saved to {output_path}")
    else:
        print(md_content)


if __name__ == "__main__":
    main()
