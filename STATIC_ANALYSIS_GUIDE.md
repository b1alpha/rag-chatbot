# Static Analysis Workflow Guide

This guide explains how to use the RAG-based static analysis tool to assess code quality and test strategies in repositories.

## Overview

The static analysis tool uses your processed quality chunks to:

1. **Analyze Test Portfolio**: Categorize tests by level (unit, integration, e2e, etc.)
2. **Assess Strategy Compliance**: Compare against your documented test strategies
3. **Find Quality Issues**: Identify anti-patterns and quality problems
4. **Generate Reports**: Provide actionable insights and recommendations

## Quick Start

### 1. Basic Analysis

```bash
python analyze_code.py /path/to/target/repo
```

### 2. Generate JSON Report

```bash
python analyze_code.py /path/to/target/repo --format json --output report.json
```

### 3. Generate Markdown Report

```bash
python analyze_code.py /path/to/target/repo --format markdown --output report.md
```

### 4. Demo on Current Repo

```bash
python demo_analysis.py
```

## What Gets Analyzed

### Test Portfolio Analysis

- **Unit Tests**: Fast, isolated tests for individual components
- **Component Tests**: Tests for UI components in isolation
- **Integration Tests**: Tests for service interactions
- **Contract Tests**: API contract validation tests
- **E2E Tests**: End-to-end user workflow tests
- **Health Check Tests**: System health and monitoring tests

### Strategy Compliance Assessment

- **Test Distribution**: Evaluates test pyramid adherence
- **CI/CD Integration**: Checks for automation pipelines
- **Documentation**: Verifies test documentation presence
- **Best Practices**: Compares against your documented strategies

### Quality Issues Detection

- **Test Anti-patterns**: Long tests, hardcoded values, etc.
- **Code Quality**: File length, technical debt markers
- **Architecture**: Missing important files, structure issues

## Output Formats

### Console Output

Rich, colored terminal output with sections for:

- Summary statistics
- Test portfolio breakdown
- Strategy compliance scores
- Quality issues by severity
- Actionable recommendations

### JSON Output

Structured data format suitable for:

- Integration with other tools
- Automated processing
- Dashboard creation
- Trend analysis

### Markdown Output

Documentation-friendly format for:

- Code reviews
- Team reports
- Wiki documentation
- Issue tracking

## Configuration

### Quality Chunks Directory

The tool reads from `./data/quality_chunks_processed` by default. You can specify a different location:

```bash
python analyze_code.py /path/to/repo --quality-chunks /custom/path/to/chunks
```

### Customizing Test Patterns

Edit `app/static_analysis.py` to modify the test file patterns:

```python
self.test_patterns = {
    'unit': [
        r'\.test\.(js|ts|py)$',
        r'\.spec\.(js|ts|py)$',
        # Add custom patterns
    ],
    # ... other levels
}
```

## Integration with RAG

The tool leverages your RAG system to:

1. **Load Quality Context**: Reads all processed quality chunks
2. **Query Best Practices**: Asks specific questions about standards
3. **Generate Recommendations**: Provides context-aware suggestions
4. **Assess Compliance**: Compares findings against your documentation

## Example Workflow

1. **Process Quality Documents**: Ensure your quality chunks are up-to-date
2. **Run Analysis**: Point the tool at your target repository
3. **Review Results**: Examine the test portfolio and compliance scores
4. **Address Issues**: Work through high-severity quality issues
5. **Track Progress**: Re-run analysis to monitor improvements

## Advanced Usage

### Custom Issue Detection

Extend the `_check_test_antipatterns` method to add custom quality checks:

```python
def _check_custom_patterns(self, repo_path: str) -> List[QualityIssue]:
    issues = []
    # Your custom logic here
    return issues
```

### Integration with CI/CD

Add to your pipeline:

```yaml
- name: Quality Analysis
  run: |
    python analyze_code.py . --format json --output quality-report.json
    # Process results or fail build based on issues
```

### Batch Analysis

Analyze multiple repositories:

```bash
for repo in /path/to/repos/*; do
    python analyze_code.py "$repo" --output "reports/$(basename "$repo").json"
done
```

## Troubleshooting

### Common Issues

1. **Missing quality chunks**: Ensure `./data/quality_chunks_processed` exists
2. **RAG connection**: Verify your OpenAI API key is configured
3. **File permissions**: Ensure the target repository is readable
4. **Large repositories**: Consider using `--verbose` for detailed progress

### Performance Tips

- Use `--format json` for faster processing
- Skip documentation generation for quick checks
- Focus on specific directories when analyzing large codebases

## Next Steps

1. **Customize Patterns**: Adapt test patterns to your tech stack
2. **Add Metrics**: Integrate with your quality metrics dashboard
3. **Automate Reports**: Set up scheduled analysis runs
4. **Team Training**: Share findings with development teams
5. **Continuous Improvement**: Update quality chunks as standards evolve
