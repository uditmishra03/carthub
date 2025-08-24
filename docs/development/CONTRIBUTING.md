# Contributing to Shopping Cart API

Thank you for your interest in contributing to the Shopping Cart API project! This document provides guidelines and workflows for contributing.

## 📋 Table of Contents

- [Development Workflow](#development-workflow)
- [Version Management](#version-management)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Release Process](#release-process)
- [Architecture Guidelines](#architecture-guidelines)

## 🔄 Development Workflow

### Branch Strategy

We use **Git Flow** with the following branches:

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - Feature development branches
- `release/*` - Release preparation branches
- `hotfix/*` - Critical bug fixes

### Getting Started

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/shopping-cart-api.git
   cd shopping-cart-api
   ```

2. **Set up development environment**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   cd frontend && npm install && cd ..
   
   # Install pre-commit hooks
   pip install pre-commit
   pre-commit install
   ```

3. **Create feature branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

### Development Process

1. **Make changes** following our coding standards
2. **Write tests** for new functionality (TDD approach)
3. **Run tests locally**
   ```bash
   python -m pytest tests/ -v
   ```
4. **Commit changes** with descriptive messages
5. **Push and create Pull Request**

## 📦 Version Management

### Semantic Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0) - Breaking changes
- **MINOR** (0.X.0) - New features (backward compatible)
- **PATCH** (0.0.X) - Bug fixes (backward compatible)

### Version Commands

```bash
# Check current version
./scripts/version.sh current

# Bump version
./scripts/version.sh bump patch   # 1.0.0 -> 1.0.1
./scripts/version.sh bump minor   # 1.0.0 -> 1.1.0
./scripts/version.sh bump major   # 1.0.0 -> 2.0.0

# Set specific version
./scripts/version.sh set 2.1.0

# Create release
./scripts/release.sh patch
```

## 🎨 Code Standards

### Python Code Style

- **Formatter**: Black (line length: 88)
- **Import sorting**: isort
- **Linting**: flake8
- **Type checking**: mypy
- **Security**: bandit

### Pre-commit Hooks

All code is automatically checked with pre-commit hooks:

```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### Code Quality Checks

- **Black formatting**: `black .`
- **Import sorting**: `isort .`
- **Linting**: `flake8 .`
- **Type checking**: `mypy . --ignore-missing-imports`
- **Security scan**: `bandit -r .`

## 🧪 Testing

### Test Structure

```
tests/
├── unit/                 # Unit tests
│   ├── domain/          # Domain layer tests
│   ├── application/     # Application layer tests
│   └── infrastructure/  # Infrastructure layer tests
├── integration/         # Integration tests
└── e2e/                # End-to-end tests
```

### Testing Guidelines

1. **Follow TDD**: Write tests before implementation
2. **Test Coverage**: Maintain >90% coverage
3. **Test Naming**: Use descriptive test names
4. **Test Structure**: Arrange-Act-Assert pattern

### Running Tests

```bash
# All tests
python -m pytest tests/ -v

# With coverage
python -m pytest tests/ --cov=. --cov-report=html

# Specific test categories
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v

# Watch mode (for development)
python -m pytest tests/ -v --tb=short -x --ff
```

## 🔀 Pull Request Process

### Before Creating PR

1. **Ensure tests pass**
   ```bash
   python -m pytest tests/ -v
   ```

2. **Run code quality checks**
   ```bash
   pre-commit run --all-files
   ```

3. **Update documentation** if needed

4. **Update CHANGELOG.md** under `[Unreleased]` section

### PR Requirements

- [ ] Tests pass
- [ ] Code quality checks pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Descriptive PR title and description
- [ ] Linked to relevant issues

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

## 🚀 Release Process

### Automated Release

Use the release script for automated releases:

```bash
# Patch release (bug fixes)
./scripts/release.sh patch

# Minor release (new features)
./scripts/release.sh minor

# Major release (breaking changes)
./scripts/release.sh major

# Custom version
./scripts/release.sh custom
```

### Manual Release Steps

1. **Prepare release branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b release/2.1.0
   ```

2. **Update version and changelog**
   ```bash
   ./scripts/version.sh set 2.1.0
   # Update CHANGELOG.md
   ```

3. **Test release candidate**
   ```bash
   python -m pytest tests/ -v
   # Deploy to staging environment
   ```

4. **Merge to main**
   ```bash
   git checkout main
   git merge release/2.1.0
   git tag -a v2.1.0 -m "Release version 2.1.0"
   git push origin main --tags
   ```

5. **Merge back to develop**
   ```bash
   git checkout develop
   git merge main
   git push origin develop
   ```

## 🏗️ Architecture Guidelines

### Clean Architecture Layers

1. **Domain Layer** (`domain/`)
   - Business entities and rules
   - No external dependencies
   - Pure Python classes

2. **Application Layer** (`application/`)
   - Use cases and business logic
   - Orchestrates domain objects
   - Depends only on domain layer

3. **Infrastructure Layer** (`infrastructure/`)
   - External concerns (database, APIs)
   - Implements interfaces from application layer
   - Framework-specific code

4. **Presentation Layer** (`presentation/`)
   - API handlers and controllers
   - Request/response formatting
   - Framework integration

### Microservices Guidelines

1. **Single Responsibility**: Each service has one business purpose
2. **Database per Service**: No shared databases
3. **API Contracts**: Well-defined interfaces
4. **Independent Deployment**: Services can be deployed separately
5. **Fault Tolerance**: Handle failures gracefully

### Kubernetes Best Practices

1. **Resource Limits**: Always set CPU/memory limits
2. **Health Checks**: Implement liveness and readiness probes
3. **Security**: Use security contexts and network policies
4. **Scaling**: Configure HPA and resource requests
5. **Monitoring**: Expose metrics and structured logging

## 🔒 Security Guidelines

### Code Security

- **No secrets in code**: Use environment variables or secret management
- **Input validation**: Validate all inputs with Pydantic
- **SQL injection prevention**: Use parameterized queries
- **Authentication**: Implement proper auth mechanisms
- **Authorization**: Check permissions for all operations

### Container Security

- **Non-root containers**: Run as non-root user
- **Minimal base images**: Use distroless or alpine images
- **Security scanning**: Scan images for vulnerabilities
- **Read-only filesystems**: Use read-only root filesystems
- **Capability dropping**: Drop unnecessary Linux capabilities

### Infrastructure Security

- **Network policies**: Restrict pod-to-pod communication
- **RBAC**: Use role-based access control
- **Secrets management**: Use Kubernetes secrets or external systems
- **TLS everywhere**: Encrypt all communications
- **Regular updates**: Keep dependencies updated

## 📚 Documentation Standards

### Code Documentation

- **Docstrings**: All public functions and classes
- **Type hints**: Use type annotations
- **Comments**: Explain complex business logic
- **README**: Keep README.md updated

### API Documentation

- **OpenAPI**: FastAPI auto-generates documentation
- **Examples**: Provide request/response examples
- **Error codes**: Document all error responses
- **Versioning**: Document API version changes

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow project guidelines

### Getting Help

- **Issues**: Create GitHub issues for bugs/features
- **Discussions**: Use GitHub discussions for questions
- **Documentation**: Check existing documentation first
- **Code Review**: Participate in code reviews

## 📞 Contact

For questions or support:
- Create an issue on GitHub
- Check existing documentation
- Review code examples in the repository

Thank you for contributing to the Shopping Cart API project! 🎉
