# 🛒 CartHub - Modern Shopping Cart Application

A professional shopping cart application with modern design and full-stack architecture.

## 🚀 Quick Start

### Launch Application
- **[🛒 Launch Shopping Cart](frontend/public/index.html)** - Production-ready cart application

### Local Development
```bash
# Start local server
python -m http.server 8080

# Open in browser
open http://localhost:8080
```

## ✨ Key Features

### 🛒 Modern Shopping Experience
- **Side Panel Cart**: Slides in from right (modern UX pattern)
- **Always-Visible Badge**: Shows cart count even when empty
- **Professional Design**: Clean, modern styling
- **Mobile Responsive**: Works perfectly on all devices

### 🏗️ Full-Stack Architecture
- **Clean Architecture**: Domain-driven design
- **Microservices Ready**: Scalable service architecture
- **AWS Integration**: CDK infrastructure as code
- **Comprehensive Testing**: Unit and integration tests

## 📁 Project Structure

```
carthub/
├── frontend/public/        # 🛒 Production shopping cart
│   ├── index.html         # Main application
│   ├── css/cart.css       # Stylesheet
│   └── js/shopping-cart.js # Application logic
├── backend/               # 🔧 Backend API services
├── microservices/         # 🔄 Microservices architecture
├── infrastructure_cdk/    # ☁️ AWS CDK infrastructure
├── deployment/            # 🚀 Deployment scripts & docs
├── docs/                  # 📚 Complete documentation
├── tests/                 # 🧪 Test suites
└── index.html            # 🏠 Application landing page
```

## 📚 Documentation

### Quick References
- **[📁 Repository Structure](REPOSITORY_STRUCTURE.md)** - Complete directory guide
- **[🛒 Frontend Guide](frontend/README.md)** - Application implementation details
- **[📖 Complete Documentation](docs/README.md)** - All guides and references

### Detailed Guides
- **[🏗️ Architecture Overview](docs/architecture/ARCHITECTURE_OVERVIEW.md)**
- **[🚀 Deployment Guide](docs/deployment/quickstart.md)**
- **[👨‍💻 Development Log](docs/development/DEVELOPMENT_LOG.md)**

## 🛠️ Technology Stack

### Frontend
- **HTML5/CSS3**: Modern web standards
- **Vanilla JavaScript**: No framework dependencies
- **Responsive Design**: Mobile-first approach

### Backend
- **Python/Flask**: RESTful API framework
- **DynamoDB**: NoSQL database
- **AWS Lambda**: Serverless functions

### Infrastructure
- **AWS CDK**: Infrastructure as code
- **Amazon EKS**: Kubernetes orchestration
- **CI/CD Pipelines**: Automated deployment

## 🚀 Deployment

### Local Development
```bash
# Frontend
python -m http.server 8080

# Backend
python -m backend.app.main
```

### AWS Deployment
```bash
# Deploy infrastructure
cd infrastructure_cdk
cdk deploy

# Deploy microservices
./deployment/scripts/deploy-microservices-cicd.sh
```

## 🤝 Contributing

1. **Follow the structure**: Use appropriate directories
2. **Test thoroughly**: Verify all functionality
3. **Document changes**: Update relevant documentation
4. **Commit frequently**: All changes are tracked in git

See **[Contributing Guide](docs/development/CONTRIBUTING.md)** for detailed guidelines.

## 📄 License

This project is part of the Amazon Q Workshop and follows AWS best practices.

---

**🎯 Production-ready modern shopping cart with professional full-stack architecture!**
