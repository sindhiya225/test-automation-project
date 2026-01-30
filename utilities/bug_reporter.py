"""
Advanced Bug Reporting Utility with automatic reproduction steps
"""
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from jinja2 import Template
from src.core.logger import TestLogger

logger = TestLogger.get_logger(__name__)

class BugReporter:
    """Automated bug reporting with detailed reproduction steps"""
    
    def __init__(self, template_path: str = "templates/bug_report_template.md"):
        self.template_path = template_path
        self.reports_dir = "reports/bugs"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def create_bug_report(
        self,
        test_name: str,
        error: str,
        steps_to_reproduce: str,
        environment: Optional[Dict[str, Any]] = None,
        attachments: Optional[list] = None,
        severity: str = "Medium",
        priority: str = "P2"
    ) -> str:
        """Create a detailed bug report"""
        
        # Generate unique bug ID
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        bug_id = f"BUG-{timestamp}"
        
        # Default environment info
        if environment is None:
            environment = {
                "browser": os.getenv("BROWSER", "chrome"),
                "os": os.platform,
                "python_version": os.sys.version,
                "test_framework": "pytest"
            }
        
        # Prepare bug data
        bug_data = {
            "bug_id": bug_id,
            "title": f"Test Failure: {test_name}",
            "description": self._generate_description(error, steps_to_reproduce),
            "steps_to_reproduce": steps_to_reproduce,
            "expected_result": "Test should pass without errors",
            "actual_result": f"Test failed with error: {error}",
            "environment": environment,
            "severity": severity,
            "priority": priority,
            "status": "Open",
            "created_date": datetime.now().isoformat(),
            "attachments": attachments or [],
            "logs": self._collect_relevant_logs(test_name)
        }
        
        # Generate report using template
        report_content = self._generate_report_from_template(bug_data)
        
        # Save report
        report_filename = f"{self.reports_dir}/{bug_id}.md"
        with open(report_filename, "w") as f:
            f.write(report_content)
        
        # Also save as JSON for machine reading
        json_filename = f"{self.reports_dir}/{bug_id}.json"
        with open(json_filename, "w") as f:
            json.dump(bug_data, f, indent=2)
        
        logger.info(f"Bug report created: {report_filename}")
        return report_filename
    
    def _generate_description(self, error: str, steps: str) -> str:
        """Generate bug description"""
        description = f"""
## Bug Description

A test failure occurred during automated testing. The error indicates a potential issue with the application.

### Error Details:

### Impact:
This failure affects the reliability of the feature and may indicate a regression or undiscovered bug.

### Additional Context:
The failure occurred during automated test execution. Manual verification is recommended.
"""
        return description
    
    def _collect_relevant_logs(self, test_name: str) -> list:
        """Collect relevant logs for the bug"""
        logs = []
        log_files = [
            "logs/test_execution.log",
            f"reports/logs/browser_{test_name}*.json",
            f"reports/screenshots/failure_{test_name}*.png"
        ]
        
        import glob
        for pattern in log_files:
            for filepath in glob.glob(pattern):
                if os.path.exists(filepath):
                    logs.append({
                        "type": os.path.splitext(filepath)[1][1:],
                        "path": filepath,
                        "size": os.path.getsize(filepath)
                    })
        
        return logs
    
    def _generate_report_from_template(self, bug_data: Dict[str, Any]) -> str:
        """Generate bug report from template"""
        template_content = """
# Bug Report: {{ bug_id }}

**Title:** {{ title }}

**Status:** {{ status }} | **Severity:** {{ severity }} | **Priority:** {{ priority }}

**Created:** {{ created_date }}

---

## Description
{{ description }}

## Steps to Reproduce
1. {{ steps_to_reproduce }}

## Expected Result
{{ expected_result }}

## Actual Result
{{ actual_result }}

## Environment
{% for key, value in environment.items() %}
- **{{ key }}:** {{ value }}
{% endfor %}

## Attachments
{% if attachments %}
{% for attachment in attachments %}
- [{{ attachment.type }}] {{ attachment.path }}
{% endfor %}
{% else %}
No attachments available
{% endif %}

## Relevant Logs
{% if logs %}
{% for log in logs %}
- {{ log.type }}: {{ log.path }} ({{ log.size }} bytes)
{% endfor %}
{% else %}
No logs available
{% endif %}

## Notes
This bug was automatically generated by the test automation framework.
"""
        
        template = Template(template_content)
        return template.render(**bug_data)
    
    def link_to_jira(self, bug_data: Dict[str, Any], jira_config: Dict[str, str]):
        """Link bug report to JIRA (simulated)"""
        # This would integrate with JIRA API in a real implementation
        jira_payload = {
            "fields": {
                "project": {"key": jira_config.get("project_key", "TEST")},
                "summary": bug_data["title"],
                "description": bug_data["description"],
                "issuetype": {"name": "Bug"},
                "priority": {"name": bug_data["priority"]},
                "labels": ["automated-testing", "bug"]
            }
        }
        
        logger.info(f"Simulated JIRA integration for bug: {bug_data['bug_id']}")
        # In real implementation: requests.post(jira_url, json=jira_payload, auth=...)
        
        return f"JIRA-{bug_data['bug_id']}"