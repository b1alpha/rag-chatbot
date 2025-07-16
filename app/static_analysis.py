import os
import re
import json
import ast
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict

from rag_pipeline import get_answer


@dataclass
class LevelInfo:
    """Represents a test level with its characteristics"""
    name: str
    files: List[str]
    count: int
    patterns: List[str]
    description: str


@dataclass
class QualityIssue:
    """Represents a quality issue found during analysis"""
    category: str
    severity: str
    file_path: str
    line_number: Optional[int]
    issue: str
    recommendation: str
    context: str


@dataclass
class AnalysisReport:
    """Main analysis report containing all findings"""
    repo_path: str
    test_portfolio: Dict[str, LevelInfo]
    strategy_assessment: Dict[str, Any]
    quality_issues: List[QualityIssue]
    summary: Dict[str, Any]


class StaticAnalyzer:
    """Main static analysis engine that uses RAG to analyze code repositories"""
    
    def __init__(self, quality_chunks_dir: str = "../data/quality_chunks_processed"):
        self.quality_chunks_dir = quality_chunks_dir
        self.test_patterns = {
            'unit': [
                r'\.test\.(js|ts|py|java|cs)$',
                r'\.spec\.(js|ts|py|java|cs)$',
                r'test_.*\.py$',
                r'.*_test\.py$',
                r'\.test\.tsx?$',
                r'test/.*unit.*',
                r'tests/.*unit.*',
                r'__tests__/.*unit.*'
            ],
            'component': [
                r'\.component\.test\.(js|ts|tsx)$',
                r'\.component\.spec\.(js|ts|tsx)$',
                r'test/.*component.*',
                r'tests/.*component.*',
                r'__tests__/.*component.*'
            ],
            'integration': [
                r'\.integration\.test\.(js|ts|py|java|cs)$',
                r'\.integration\.spec\.(js|ts|py|java|cs)$',
                r'test/.*integration.*',
                r'tests/.*integration.*',
                r'__tests__/.*integration.*'
            ],
            'contract': [
                r'\.contract\.test\.(js|ts|py|java|cs)$',
                r'\.contract\.spec\.(js|ts|py|java|cs)$',
                r'test/.*contract.*',
                r'tests/.*contract.*',
                r'__tests__/.*contract.*',
                r'.*pact.*',
                r'.*contract.*'
            ],
            'e2e': [
                r'\.e2e\.test\.(js|ts|py|java|cs)$',
                r'\.e2e\.spec\.(js|ts|py|java|cs)$',
                r'test/.*e2e.*',
                r'tests/.*e2e.*',
                r'__tests__/.*e2e.*',
                r'.*cypress.*',
                r'.*playwright.*',
                r'.*selenium.*'
            ],
            'healthcheck': [
                r'\.health\.test\.(js|ts|py|java|cs)$',
                r'\.health\.spec\.(js|ts|py|java|cs)$',
                r'test/.*health.*',
                r'tests/.*health.*',
                r'__tests__/.*health.*',
                r'.*health.*check.*'
            ]
        }
    
    def load_quality_context(self) -> str:
        """Load all quality chunks into a single context string"""
        context = ""
        for filename in os.listdir(self.quality_chunks_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(self.quality_chunks_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    context += f"\n=== {filename} ===\n"
                    context += f.read()
                    context += "\n"
        return context
    
    def find_test_files(self, repo_path: str) -> Dict[str, LevelInfo]:
        """Analyze repository to find and categorize test files"""
        test_portfolio = {}
        
        for level_name, patterns in self.test_patterns.items():
            matching_files = []
            
            for root, dirs, files in os.walk(repo_path):
                # Skip common non-test directories
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'build', 'dist']]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    
                    for pattern in patterns:
                        if re.search(pattern, relative_path, re.IGNORECASE):
                            matching_files.append(relative_path)
                            break
            
            # Get description from RAG
            description = self._get_test_level_description(level_name)
            
            test_portfolio[level_name] = LevelInfo(
                name=level_name,
                files=matching_files,
                count=len(matching_files),
                patterns=patterns,
                description=description
            )
        
        return test_portfolio
    
    def _get_test_level_description(self, level_name: str) -> str:
        """Get description of test level from RAG system"""
        question = f"What is {level_name} testing? Provide a brief description of {level_name} tests and their purpose."
        try:
            return get_answer(question)
        except Exception as e:
            return f"Description unavailable: {str(e)}"
    
    def assess_strategy_compliance(self, repo_path: str) -> Dict[str, Any]:
        """Assess how well the repository follows the test strategy"""
        assessment = {
            'overall_score': 0,
            'areas': {},
            'recommendations': []
        }
        
        # Check test pyramid distribution
        test_portfolio = self.find_test_files(repo_path)
        total_tests = sum(level.count for level in test_portfolio.values())
        
        if total_tests > 0:
            unit_percentage = (test_portfolio['unit'].count / total_tests) * 100
            integration_percentage = (test_portfolio['integration'].count / total_tests) * 100
            e2e_percentage = (test_portfolio['e2e'].count / total_tests) * 100
            
            # Ask RAG about ideal test distribution
            distribution_question = "What is the ideal distribution of unit, integration, and e2e tests according to the test strategy?"
            ideal_distribution = get_answer(distribution_question)
            
            assessment['areas']['test_distribution'] = {
                'unit_percentage': unit_percentage,
                'integration_percentage': integration_percentage,
                'e2e_percentage': e2e_percentage,
                'ideal_distribution': ideal_distribution,
                'score': self._score_test_distribution(unit_percentage, integration_percentage, e2e_percentage)
            }
        
        # Check for CI/CD integration
        ci_files = self._find_ci_files(repo_path)
        assessment['areas']['ci_cd'] = {
            'files_found': ci_files,
            'has_ci': len(ci_files) > 0,
            'score': 80 if len(ci_files) > 0 else 20
        }
        
        # Check for test documentation
        doc_files = self._find_documentation_files(repo_path)
        assessment['areas']['documentation'] = {
            'files_found': doc_files,
            'has_docs': len(doc_files) > 0,
            'score': 70 if len(doc_files) > 0 else 30
        }
        
        # Calculate overall score
        scores = [area['score'] for area in assessment['areas'].values()]
        assessment['overall_score'] = sum(scores) / len(scores) if scores else 0
        
        # Get recommendations from RAG
        recommendations_question = f"Based on the test strategy, what are key recommendations for improving a codebase with {total_tests} tests distributed as: {unit_percentage:.1f}% unit, {integration_percentage:.1f}% integration, {e2e_percentage:.1f}% e2e?"
        assessment['recommendations'] = get_answer(recommendations_question).split('\n')
        
        return assessment
    
    def _score_test_distribution(self, unit_pct: float, integration_pct: float, e2e_pct: float) -> int:
        """Score test distribution based on test pyramid principles"""
        # Ideal: 70% unit, 20% integration, 10% e2e
        ideal_unit, ideal_integration, ideal_e2e = 70, 20, 10
        
        unit_score = max(0, 100 - abs(unit_pct - ideal_unit) * 2)
        integration_score = max(0, 100 - abs(integration_pct - ideal_integration) * 3)
        e2e_score = max(0, 100 - abs(e2e_pct - ideal_e2e) * 5)
        
        return int((unit_score + integration_score + e2e_score) / 3)
    
    def _find_ci_files(self, repo_path: str) -> List[str]:
        """Find CI/CD configuration files"""
        ci_patterns = [
            r'\.github/workflows/.*\.ya?ml$',
            r'\.gitlab-ci\.ya?ml$',
            r'\.travis\.ya?ml$',
            r'\.circleci/.*\.ya?ml$',
            r'Jenkinsfile$',
            r'azure-pipelines\.ya?ml$',
            r'buildkite\.ya?ml$'
        ]
        
        ci_files = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)
                
                for pattern in ci_patterns:
                    if re.search(pattern, relative_path, re.IGNORECASE):
                        ci_files.append(relative_path)
                        break
        
        return ci_files
    
    def _find_documentation_files(self, repo_path: str) -> List[str]:
        """Find documentation files related to testing"""
        doc_patterns = [
            r'README\.md$',
            r'TESTING\.md$',
            r'TEST.*\.md$',
            r'docs/.*test.*\.md$',
            r'documentation/.*test.*\.md$'
        ]
        
        doc_files = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, repo_path)
                
                for pattern in doc_patterns:
                    if re.search(pattern, relative_path, re.IGNORECASE):
                        doc_files.append(relative_path)
                        break
        
        return doc_files
    
    def find_quality_issues(self, repo_path: str) -> List[QualityIssue]:
        """Find quality issues in the codebase using RAG guidance"""
        issues = []
        
        # Check for common anti-patterns
        issues.extend(self._check_test_antipatterns(repo_path))
        issues.extend(self._check_code_quality_issues(repo_path))
        issues.extend(self._check_architecture_issues(repo_path))
        
        return issues
    
    def _check_test_antipatterns(self, repo_path: str) -> List[QualityIssue]:
        """Check for test anti-patterns using RAG knowledge"""
        issues = []
        
        # Get anti-patterns from RAG
        antipatterns_question = "What are common test anti-patterns that should be avoided? List specific patterns to look for in code."
        antipatterns_guidance = get_answer(antipatterns_question)
        
        # Look for specific patterns in test files
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                if any(re.search(pattern, file, re.IGNORECASE) for patterns in self.test_patterns.values() for pattern in patterns):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Check for specific anti-patterns
                        issues.extend(self._analyze_test_file_content(relative_path, content, antipatterns_guidance))
                    except Exception as e:
                        issues.append(QualityIssue(
                            category="File Analysis",
                            severity="LOW",
                            file_path=relative_path,
                            line_number=None,
                            issue=f"Could not analyze file: {str(e)}",
                            recommendation="Ensure file is readable and properly encoded",
                            context="File analysis error"
                        ))
        
        return issues
    
    def _analyze_test_file_content(self, file_path: str, content: str, guidance: str) -> List[QualityIssue]:
        """Analyze individual test file content for issues"""
        issues = []
        lines = content.split('\n')
        
        # Check for long test methods
        for i, line in enumerate(lines, 1):
            if re.search(r'(test_|it\(|describe\()', line, re.IGNORECASE):
                # Count lines in this test method (simplified)
                method_lines = 1
                for j in range(i, min(i + 100, len(lines))):
                    if lines[j].strip() and not lines[j].startswith(' ') and not lines[j].startswith('\t'):
                        break
                    method_lines += 1
                
                if method_lines > 50:
                    issues.append(QualityIssue(
                        category="Test Quality",
                        severity="MEDIUM",
                        file_path=file_path,
                        line_number=i,
                        issue="Test method is too long",
                        recommendation="Break down large tests into smaller, focused tests",
                        context=f"Test method spans {method_lines} lines"
                    ))
        
        # Check for hardcoded values
        hardcoded_patterns = [
            r'http://localhost:\d+',
            r'127\.0\.0\.1',
            r'password.*=.*["\'].*["\']',
            r'api_key.*=.*["\'].*["\']'
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern in hardcoded_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append(QualityIssue(
                        category="Test Configuration",
                        severity="HIGH",
                        file_path=file_path,
                        line_number=i,
                        issue="Hardcoded value detected",
                        recommendation="Use configuration files or environment variables",
                        context=line.strip()
                    ))
        
        return issues
    
    def _check_code_quality_issues(self, repo_path: str) -> List[QualityIssue]:
        """Check for general code quality issues"""
        issues = []
        
        # Get code quality guidance from RAG
        quality_question = "What are key code quality indicators and common issues to look for in codebases?"
        quality_guidance = get_answer(quality_question)
        
        # Look for specific patterns
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'build', 'dist']]
            
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java', '.cs', '.go')):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        # Check file length
                        lines = content.split('\n')
                        if len(lines) > 500:
                            issues.append(QualityIssue(
                                category="Code Quality",
                                severity="MEDIUM",
                                file_path=relative_path,
                                line_number=None,
                                issue=f"File is too long ({len(lines)} lines)",
                                recommendation="Consider breaking down large files into smaller modules",
                                context=f"File has {len(lines)} lines"
                            ))
                        
                        # Check for TODO/FIXME comments
                        for i, line in enumerate(lines, 1):
                            if re.search(r'(TODO|FIXME|XXX|HACK)', line, re.IGNORECASE):
                                issues.append(QualityIssue(
                                    category="Code Maintenance",
                                    severity="LOW",
                                    file_path=relative_path,
                                    line_number=i,
                                    issue="Technical debt marker found",
                                    recommendation="Address technical debt items",
                                    context=line.strip()
                                ))
                        
                    except Exception:
                        continue
        
        return issues
    
    def _check_architecture_issues(self, repo_path: str) -> List[QualityIssue]:
        """Check for architectural issues"""
        issues = []
        
        # Check for missing important files
        important_files = ['README.md', 'requirements.txt', 'package.json', 'Dockerfile']
        for file in important_files:
            if not os.path.exists(os.path.join(repo_path, file)):
                issues.append(QualityIssue(
                    category="Project Structure",
                    severity="MEDIUM",
                    file_path=".",
                    line_number=None,
                    issue=f"Missing {file}",
                    recommendation=f"Add {file} to improve project documentation and setup",
                    context=f"Standard file {file} not found"
                ))
        
        return issues
    
    def generate_report(self, repo_path: str) -> AnalysisReport:
        """Generate comprehensive analysis report"""
        print(f"🔍 Analyzing repository: {repo_path}")
        
        # Load quality context
        print("📚 Loading quality guidance...")
        quality_context = self.load_quality_context()
        
        # Analyze test portfolio
        print("🧪 Analyzing test portfolio...")
        test_portfolio = self.find_test_files(repo_path)
        
        # Assess strategy compliance
        print("📋 Assessing strategy compliance...")
        strategy_assessment = self.assess_strategy_compliance(repo_path)
        
        # Find quality issues
        print("🐛 Finding quality issues...")
        quality_issues = self.find_quality_issues(repo_path)
        
        # Generate summary
        total_tests = sum(level.count for level in test_portfolio.values())
        total_issues = len(quality_issues)
        high_severity_issues = len([issue for issue in quality_issues if issue.severity == "HIGH"])
        
        summary = {
            'total_tests': total_tests,
            'total_issues': total_issues,
            'high_severity_issues': high_severity_issues,
            'overall_score': strategy_assessment['overall_score'],
            'test_levels_found': len([level for level in test_portfolio.values() if level.count > 0])
        }
        
        print("✅ Analysis complete!")
        
        return AnalysisReport(
            repo_path=repo_path,
            test_portfolio=test_portfolio,
            strategy_assessment=strategy_assessment,
            quality_issues=quality_issues,
            summary=summary
        )
    
    def print_report(self, report: AnalysisReport):
        """Print formatted analysis report"""
        print(f"\n{'='*80}")
        print(f"📊 STATIC ANALYSIS REPORT: {report.repo_path}")
        print(f"{'='*80}")
        
        # Summary
        print(f"\n📋 SUMMARY")
        print(f"{'─'*40}")
        print(f"Total Tests: {report.summary['total_tests']}")
        print(f"Test Levels Found: {report.summary['test_levels_found']}/6")
        print(f"Overall Score: {report.summary['overall_score']:.1f}/100")
        print(f"Total Issues: {report.summary['total_issues']}")
        print(f"High Severity Issues: {report.summary['high_severity_issues']}")
        
        # Test Portfolio
        print(f"\n🧪 TEST PORTFOLIO")
        print(f"{'─'*40}")
        for level_name, level in report.test_portfolio.items():
            print(f"{level_name.upper()}: {level.count} tests")
            if level.count > 0:
                print(f"  Files: {', '.join(level.files[:3])}")
                if len(level.files) > 3:
                    print(f"  ... and {len(level.files) - 3} more")
            print()
        
        # Strategy Assessment
        print(f"\n📋 STRATEGY COMPLIANCE")
        print(f"{'─'*40}")
        print(f"Overall Score: {report.strategy_assessment['overall_score']:.1f}/100")
        
        for area_name, area_data in report.strategy_assessment['areas'].items():
            print(f"\n{area_name.replace('_', ' ').title()}: {area_data['score']}/100")
            
            if area_name == 'test_distribution':
                print(f"  Unit: {area_data['unit_percentage']:.1f}%")
                print(f"  Integration: {area_data['integration_percentage']:.1f}%")
                print(f"  E2E: {area_data['e2e_percentage']:.1f}%")
            elif area_name == 'ci_cd':
                print(f"  CI/CD Present: {'Yes' if area_data['has_ci'] else 'No'}")
                if area_data['files_found']:
                    print(f"  Files: {', '.join(area_data['files_found'])}")
        
        # Quality Issues
        print(f"\n🐛 QUALITY ISSUES")
        print(f"{'─'*40}")
        
        # Group issues by severity
        issues_by_severity = defaultdict(list)
        for issue in report.quality_issues:
            issues_by_severity[issue.severity].append(issue)
        
        for severity in ['HIGH', 'MEDIUM', 'LOW']:
            if severity in issues_by_severity:
                print(f"\n{severity} SEVERITY ({len(issues_by_severity[severity])} issues):")
                for issue in issues_by_severity[severity][:5]:  # Show first 5 of each severity
                    print(f"  📁 {issue.file_path}")
                    if issue.line_number:
                        print(f"     Line {issue.line_number}: {issue.issue}")
                    else:
                        print(f"     {issue.issue}")
                    print(f"     💡 {issue.recommendation}")
                    print()
                
                if len(issues_by_severity[severity]) > 5:
                    print(f"  ... and {len(issues_by_severity[severity]) - 5} more {severity.lower()} issues")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS")
        print(f"{'─'*40}")
        for i, rec in enumerate(report.strategy_assessment['recommendations'][:10], 1):
            if rec.strip():
                print(f"{i}. {rec.strip()}")
        
        print(f"\n{'='*80}")
        print("📊 Report Complete")
        print(f"{'='*80}")


def analyze_repository(repo_path: str) -> AnalysisReport:
    """Main function to analyze a repository"""
    analyzer = StaticAnalyzer()
    report = analyzer.generate_report(repo_path)
    analyzer.print_report(report)
    return report


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python static_analysis.py <repo_path>")
        sys.exit(1)
    
    repo_path = sys.argv[1]
    if not os.path.exists(repo_path):
        print(f"Error: Repository path '{repo_path}' does not exist")
        sys.exit(1)
    
    analyze_repository(repo_path)
