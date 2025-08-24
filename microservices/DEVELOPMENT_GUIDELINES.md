# 🏗️ CartHub Microservices Development Guidelines

## 📁 **Repository Structure**

All development should happen within the `microservices/` directory structure:

```
microservices/
├── frontend/           # Frontend microservice
│   ├── public/        # Static files (HTML, CSS, JS)
│   ├── src/           # React/TypeScript source
│   ├── k8s/           # Kubernetes manifests
│   └── Dockerfile     # Container configuration
├── backend/           # Backend API microservice
│   ├── app/           # Python application code
│   ├── k8s/           # Kubernetes manifests
│   └── Dockerfile     # Container configuration
└── database/          # Database microservice
    ├── k8s/           # Kubernetes manifests
    └── Dockerfile     # Container configuration
```

## 🚫 **What NOT to Do**

### **❌ Root Directory Files:**
- Do NOT create HTML, CSS, or JS files in the root directory
- Do NOT create test files outside of microservices structure
- Do NOT put application code in the root

### **❌ Scattered Code:**
- Do NOT duplicate code across multiple locations
- Do NOT create multiple versions of the same functionality
- Do NOT leave temporary files in the repository

## ✅ **Best Practices**

### **🎯 Frontend Changes:**
- **HTML files**: `microservices/frontend/public/index.html`
- **CSS files**: `microservices/frontend/public/css/cart.css`
- **JavaScript**: `microservices/frontend/public/js/shopping-cart.js`
- **React components**: `microservices/frontend/src/components/`

### **🎯 Backend Changes:**
- **API routes**: `microservices/backend/app/routes/`
- **Business logic**: `microservices/backend/app/services/`
- **Data models**: `microservices/backend/app/models/`
- **Configuration**: `microservices/backend/app/config/`

### **🎯 Database Changes:**
- **Migrations**: `microservices/database/scripts/`
- **Schema**: `microservices/database/`
- **Tests**: `microservices/database/tests/`

## 🔄 **Development Workflow**

### **1. Make Changes in Microservices:**
```bash
# Frontend changes
cd microservices/frontend/public/
# Edit HTML, CSS, JS files here

# Backend changes  
cd microservices/backend/app/
# Edit Python files here
```

### **2. Test Locally:**
```bash
# Frontend
cd microservices/frontend/
python -m http.server 8080

# Backend
cd microservices/backend/
python -m app.main
```

### **3. Build and Deploy:**
```bash
# Build Docker images
docker build -t carthub-frontend microservices/frontend/
docker build -t carthub-backend microservices/backend/

# Deploy to Kubernetes
kubectl apply -f microservices/frontend/k8s/
kubectl apply -f microservices/backend/k8s/
```

## 📋 **File Organization Rules**

### **✅ Correct Locations:**
- **Main application**: `microservices/frontend/public/index.html`
- **Styles**: `microservices/frontend/public/css/`
- **Scripts**: `microservices/frontend/public/js/`
- **API endpoints**: `microservices/backend/app/routes/`
- **Business logic**: `microservices/backend/app/services/`

### **❌ Incorrect Locations:**
- **Root directory**: No application files
- **Random folders**: No scattered code
- **Duplicate locations**: Single source of truth only

## 🎯 **Key Principles**

1. **Single Source of Truth**: Each file has one authoritative location
2. **Microservices Architecture**: Keep services separate and focused
3. **Clean Repository**: No temporary or test files in root
4. **Proper Structure**: Follow established directory conventions
5. **Container Ready**: All code should be containerizable

## 🚀 **Deployment Pipeline**

Changes in microservices automatically trigger:
1. **CodeCommit**: Source control
2. **CodeBuild**: Build and test
3. **ECR**: Container registry
4. **EKS**: Kubernetes deployment

## 📝 **Remember**

- **All application code belongs in `microservices/`**
- **No HTML/CSS/JS files in root directory**
- **Follow the established structure**
- **Keep it clean and organized**

---

**🎯 Always develop within the microservices structure for consistency and maintainability!**
