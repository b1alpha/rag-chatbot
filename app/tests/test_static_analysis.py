"""
Test the static analysis functionality
"""
import os
import re
import pytest
from unittest.mock import Mock, patch, mock_open
import sys

# Add the parent directory to the Python path to import from app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from static_analysis import StaticAnalyzer, QualityIssue, LevelInfo


@pytest.fixture
def mock_analyzer():
    """Create a mock analyzer for testing"""
    with patch('static_analysis.get_answer') as mock_get_answer:
        mock_get_answer.return_value = "Mock RAG response"
        analyzer = StaticAnalyzer()
        yield analyzer


@pytest.mark.unit
def test_test_pattern_matching(mock_analyzer):
    """Test that test patterns correctly identify test files"""
    analyzer = mock_analyzer
    
    # Test unit test patterns
    unit_patterns = analyzer.test_patterns['unit']
    assert any(re.search(pattern, 'test_example.py') for pattern in unit_patterns)
    assert any(re.search(pattern, 'example.test.js') for pattern in unit_patterns)
    assert any(re.search(pattern, 'example.spec.ts') for pattern in unit_patterns)


@pytest.mark.unit
def test_quality_issue_creation():
    """Test QualityIssue creation and attributes"""
    issue = QualityIssue(
        category="Test Quality",
        severity="HIGH",
        file_path="test/example.py",
        line_number=42,
        issue="Test is too long",
        recommendation="Break into smaller tests",
        context="Test method has 100 lines"
    )
    
    assert issue.category == "Test Quality"
    assert issue.severity == "HIGH"
    assert issue.file_path == "test/example.py"
    assert issue.line_number == 42
    assert "too long" in issue.issue
    assert "smaller tests" in issue.recommendation


@pytest.mark.unit
def test_test_level_creation():
    """Test LevelInfo creation and attributes"""
    level = LevelInfo(
        name="unit",
        files=["test_example.py", "test_another.py"],
        count=2,
        patterns=[r'test_.*\.py$'],
        description="Unit tests verify individual components"
    )
    
    assert level.name == "unit"
    assert level.count == 2
    assert len(level.files) == 2
    assert "test_example.py" in level.files


@pytest.mark.unit
@patch('os.path.exists')
@patch('os.walk')
def test_find_test_files(mock_walk, mock_exists, mock_analyzer):
    """Test finding test files in a repository"""
    mock_exists.return_value = True
    mock_walk.return_value = [
        ('/repo', ['src', 'test'], ['README.md']),
        ('/repo/src', [], ['main.py']),
        ('/repo/test', [], ['test_main.py', 'integration.test.js'])
    ]
    
    analyzer = mock_analyzer
    test_portfolio = analyzer.find_test_files('/repo')
    
    assert 'unit' in test_portfolio
    assert 'integration' in test_portfolio
    assert test_portfolio['unit'].count >= 1  # Should find test_main.py


@pytest.mark.unit
@patch('os.path.exists')
def test_find_ci_files(mock_exists, mock_analyzer):
    """Test finding CI/CD files"""
    mock_exists.return_value = True
    
    with patch('os.walk') as mock_walk:
        mock_walk.return_value = [
            ('/repo', ['.github'], ['README.md']),
            ('/repo/.github', ['workflows'], []),
            ('/repo/.github/workflows', [], ['ci.yml', 'deploy.yaml'])
        ]
        
        analyzer = mock_analyzer
        ci_files = analyzer._find_ci_files('/repo')
        
        assert len(ci_files) >= 1
        assert any('ci.yml' in f for f in ci_files)


@pytest.mark.unit
def test_score_test_distribution(mock_analyzer):
    """Test test distribution scoring"""
    analyzer = mock_analyzer
    
    # Perfect distribution (70% unit, 20% integration, 10% e2e)
    perfect_score = analyzer._score_test_distribution(70, 20, 10)
    assert perfect_score == 100
    
    # Poor distribution (10% unit, 10% integration, 80% e2e)
    poor_score = analyzer._score_test_distribution(10, 10, 80)
    assert poor_score < 50


@pytest.mark.unit
@patch('os.listdir')
def test_load_quality_context(mock_listdir, mock_analyzer):
    """Test loading quality context from chunks"""
    mock_listdir.return_value = ['chunk1.txt', 'chunk2.txt', 'other.py']
    
    with patch('builtins.open', mock_open(read_data="Quality content")):
        analyzer = mock_analyzer
        context = analyzer.load_quality_context()
        
        assert "Quality content" in context
        assert "chunk1.txt" in context
        assert "chunk2.txt" in context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
