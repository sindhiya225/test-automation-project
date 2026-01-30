# Automated Testing Framework

## Overview
An enterprise-grade testing framework combining UI testing (Selenium/Playwright), API testing (Postman/requests), and advanced reporting. 

## Features
- **Cross-browser Testing**: Chrome, Firefox, Edge via Selenium Grid
- **API Testing**: REST API testing with schema validation
- **Postman Integration**: Run and convert Postman collections
- **Advanced Reporting**: HTML, Allure, and custom reports
- **Bug Auto-Reporting**: Automatic bug reports with reproduction steps
- **Docker Support**: Containerized test execution
- **Parallel Execution**: Distributed test execution
- **Retry Logic**: Automatic retry of failed tests
- **Security Testing**: SQL injection, XSS, and security header validation

## Prerequisites
- Python 3.8+
- Node.js (for Newman/Postman)
- Docker (optional)

## Installation

1. **Clone the repository**
```bash
git clone <sindhiya225/test-automation-project>
cd advanced-testing-framework
```

2. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

3. **Install Playwright browsers**

```bash
playwright install
```

4. **Install Newman (for Postman)**

```bash
npm install -g newman
```

5. **Set up environment variables**

```bash
cp .env.example .env
```


## Project Structure
```
advanced-testing-framework/
│
├── README.md
├── requirements.txt
├── pytest.ini
├── conftest.py
├── .env.example
│
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── browser_factory.py
│   │   ├── api_client.py
│   │   ├── logger.py
│   │   └── utilities.py
│   │
│   ├── pages/
│   │   ├── __init__.py
│   │   ├── base_page.py
│   │   ├── login_page.py
│   │   └── dashboard_page.py
│   │
│   └── api/
│       ├── __init__.py
│       ├── endpoints.py
│       └── schemas.py
│
├── tests/
│   ├── __init__.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── test_login.py
│   │   ├── test_forms.py
│   │   ├── test_validations.py
│   │   └── test_dashboard.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── test_auth_api.py
│   │   ├── test_user_api.py
│   │   └── test_data_validation.py
│   │
│   └── integration/
│       ├── __init__.py
│       └── test_ui_api_integration.py
│
├── test_data/
│   ├── __init__.py
│   ├── users.json
│   └── test_cases.yaml
│
├── config/
│   ├── __init__.py
│   ├── settings.py
│   └── urls.py
│
├── reports/
│   ├── assets/
│   └── archive/
│
├── logs/
│   └── test_execution.log
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
└── utilities/
    ├── __init__.py
    ├── bug_reporter.py
    ├── screenshot_manager.py
    └── postman_runner.py
```

**Run all tests**
```bash
pytest tests/ -v
```

**Run specific test types**
```bash
# UI tests only
pytest tests/ui/ -v -m ui

# API tests only
pytest tests/api/ -v -m api

# Smoke tests
pytest tests/ -v -m smoke

# Security tests
pytest tests/ -v -m security
```

**Docker Execution**

```bash
# Start Selenium Grid and run tests
docker-compose up --build
```

**Generate Reports**

```bash
# HTML Report
pytest tests/ -v --html=reports/report.html --self-contained-html

# Allure Report
pytest tests/ -v --alluredir=reports/allure-results
allure generate reports/allure-results -o reports/allure-report --clean
allure open reports/allure-report

# JSON Report
pytest tests/ -v --json=reports/report.json
```

## License
- This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
