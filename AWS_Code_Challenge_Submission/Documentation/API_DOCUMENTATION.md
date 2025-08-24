# Carthub API Documentation

## Overview
The Carthub API provides RESTful endpoints for managing shopping cart operations across three different architectural implementations. All endpoints return JSON responses and follow standard HTTP status codes.

**Current Version**: 2.0.0  
**Last Updated**: August 21, 2025

## Base URLs

### Production Environments
```
Serverless:     https://<api-gateway-id>.execute-api.us-west-2.amazonaws.com/prod
ECS:           https://<alb-hostname>
EKS:           https://<alb-hostname>
```

### Development Environment
```
Local Backend:  http://localhost:8000
```

## Architecture-Specific Implementations

### 🚀 **Serverless API (Lambda + DynamoDB)**
- **Technology**: AWS Lambda + DynamoDB + API Gateway
- **Best for**: Low-moderate traffic, rapid prototyping
- **Scaling**: Automatic based on requests
- **Cold starts**: Yes (first request may be slower)

### 🐳 **Microservices API (FastAPI + PostgreSQL)**
- **Technology**: FastAPI + PostgreSQL + Docker + Kubernetes
- **Best for**: High traffic, enterprise requirements
- **Scaling**: Horizontal Pod Autoscaler (2-15 replicas)
- **Cold starts**: No (containers always running)

## Authentication
All API requests require authentication using JWT tokens in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

*Note: For development and testing, authentication may be disabled.*

## API Endpoints

### Health Check

#### Check Service Health
```http
GET /health
```

**Description**: Check the health status of the API service and its dependencies.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-21T18:15:28.819Z",
  "version": "2.0.0",
  "database": "connected",
  "environment": "production"
}
```

**Status Codes**:
- `200 OK`: Service is healthy
- `503 Service Unavailable`: Service or dependencies are unhealthy

---

### Cart Operations

#### Get Cart Contents
```http
GET /api/v1/cart/{customer_id}
```

**Description**: Retrieve all items in a customer's cart with calculated totals.

**Parameters**:
- `customer_id` (path, required): Unique identifier for the customer

**Example Request**:
```bash
curl -X GET "https://api.carthub.com/api/v1/cart/customer-123" \
  -H "Authorization: Bearer your-jwt-token"
```

**Response**:
```json
{
  "success": true,
  "data": {
    "customer_id": "customer-123",
    "items": [
      {
        "id": 1,
        "product_id": "prod-456",
        "product_name": "Gaming Laptop",
        "price": 1299.99,
        "quantity": 1,
        "subtotal": 1299.99,
        "created_at": "2025-08-21T18:15:28.819Z"
      },
      {
        "id": 2,
        "product_id": "prod-789",
        "product_name": "Wireless Mouse",
        "price": 29.99,
        "quantity": 2,
        "subtotal": 59.98,
        "created_at": "2025-08-21T18:16:15.234Z"
      }
    ],
    "total_items": 3,
    "subtotal": 1359.97,
    "tax": 108.80,
    "shipping": 15.99,
    "total": 1484.76,
    "created_at": "2025-08-21T18:15:28.819Z",
    "updated_at": "2025-08-21T18:16:15.234Z"
  }
}
```

#### Add Item to Cart
```http
POST /api/v1/cart/items
```

**Description**: Add a new item to the cart or update quantity if item already exists.

**Request Body**:
```json
{
  "customer_id": "customer-123",
  "product_id": "prod-456",
  "product_name": "Gaming Laptop",
  "price": 1299.99,
  "quantity": 1
}
```

**Example Request**:
```bash
curl -X POST "https://api.carthub.com/api/v1/cart/items" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "customer-123",
    "product_id": "prod-456",
    "product_name": "Gaming Laptop",
    "price": 1299.99,
    "quantity": 1
  }'
```

**Response**:
```json
{
  "success": true,
  "message": "Item added to cart successfully",
  "data": {
    "customer_id": "customer-123",
    "item": {
      "id": 1,
      "product_id": "prod-456",
      "product_name": "Gaming Laptop",
      "price": 1299.99,
      "quantity": 1,
      "subtotal": 1299.99
    },
    "cart_summary": {
      "total_items": 1,
      "subtotal": 1299.99,
      "total": 1419.98
    }
  }
}
```

#### Update Item Quantity
```http
PUT /api/v1/cart/{customer_id}/items/{product_id}
```

**Description**: Update the quantity of a specific item in the cart.

**Parameters**:
- `customer_id` (path, required): Unique identifier for the customer
- `product_id` (path, required): Unique identifier for the product

**Request Body**:
```json
{
  "quantity": 3
}
```

**Example Request**:
```bash
curl -X PUT "https://api.carthub.com/api/v1/cart/customer-123/items/prod-456" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 3}'
```

**Response**:
```json
{
  "success": true,
  "message": "Item quantity updated successfully",
  "data": {
    "customer_id": "customer-123",
    "item": {
      "id": 1,
      "product_id": "prod-456",
      "product_name": "Gaming Laptop",
      "price": 1299.99,
      "quantity": 3,
      "subtotal": 3899.97
    },
    "cart_summary": {
      "total_items": 3,
      "subtotal": 3899.97,
      "total": 4259.97
    }
  }
}
```

#### Remove Item from Cart
```http
DELETE /api/v1/cart/{customer_id}/items/{product_id}
```

**Description**: Remove a specific item from the cart completely.

**Parameters**:
- `customer_id` (path, required): Unique identifier for the customer
- `product_id` (path, required): Unique identifier for the product

**Example Request**:
```bash
curl -X DELETE "https://api.carthub.com/api/v1/cart/customer-123/items/prod-456" \
  -H "Authorization: Bearer your-jwt-token"
```

**Response**:
```json
{
  "success": true,
  "message": "Item removed from cart successfully",
  "data": {
    "customer_id": "customer-123",
    "removed_item": {
      "product_id": "prod-456",
      "product_name": "Gaming Laptop",
      "quantity": 3,
      "subtotal": 3899.97
    },
    "cart_summary": {
      "remaining_items": 0,
      "subtotal": 0.00,
      "total": 0.00
    }
  }
}
```

#### Clear Cart
```http
DELETE /api/v1/cart/{customer_id}
```

**Description**: Remove all items from the customer's cart.

**Parameters**:
- `customer_id` (path, required): Unique identifier for the customer

**Example Request**:
```bash
curl -X DELETE "https://api.carthub.com/api/v1/cart/customer-123" \
  -H "Authorization: Bearer your-jwt-token"
```

**Response**:
```json
{
  "success": true,
  "message": "Cart cleared successfully",
  "data": {
    "customer_id": "customer-123",
    "items_removed": 5,
    "total_value_removed": 2599.97,
    "cart_summary": {
      "total_items": 0,
      "subtotal": 0.00,
      "total": 0.00
    }
  }
}
```

---

### Checkout Operations

#### Process Checkout
```http
POST /api/v1/cart/checkout
```

**Description**: Process the checkout for a customer's cart, creating an order and clearing the cart.

**Request Body**:
```json
{
  "customer_id": "customer-123",
  "shipping_address": {
    "street": "123 Main St",
    "city": "Anytown",
    "state": "CA",
    "zip_code": "12345",
    "country": "US"
  },
  "billing_address": {
    "street": "123 Main St",
    "city": "Anytown", 
    "state": "CA",
    "zip_code": "12345",
    "country": "US"
  },
  "payment_method": {
    "type": "credit_card",
    "card_number": "****-****-****-1234",
    "expiry_month": 12,
    "expiry_year": 2025,
    "cvv": "***"
  }
}
```

**Example Request**:
```bash
curl -X POST "https://api.carthub.com/api/v1/cart/checkout" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "customer-123",
    "shipping_address": {
      "street": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "zip_code": "12345",
      "country": "US"
    },
    "payment_method": {
      "type": "credit_card",
      "card_number": "****-****-****-1234"
    }
  }'
```

**Response**:
```json
{
  "success": true,
  "message": "Checkout processed successfully",
  "data": {
    "order_id": "order-789",
    "customer_id": "customer-123",
    "order_items": [
      {
        "product_id": "prod-456",
        "product_name": "Gaming Laptop",
        "price": 1299.99,
        "quantity": 1,
        "subtotal": 1299.99
      }
    ],
    "order_summary": {
      "subtotal": 1299.99,
      "tax": 104.00,
      "shipping": 15.99,
      "total_amount": 1419.98
    },
    "payment_status": "completed",
    "shipping_info": {
      "estimated_delivery": "2025-08-28",
      "tracking_number": "TRK123456789",
      "carrier": "UPS"
    },
    "created_at": "2025-08-21T18:15:28.819Z"
  }
}
```

---

## Error Handling

### HTTP Status Codes
- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters or body
- `401 Unauthorized`: Authentication required or invalid
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation errors
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid product quantity",
    "details": {
      "field": "quantity",
      "value": -1,
      "constraint": "must be greater than 0"
    },
    "timestamp": "2025-08-21T18:15:28.819Z"
  }
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Request validation failed | 422 |
| `CART_NOT_FOUND` | Customer cart not found | 404 |
| `ITEM_NOT_FOUND` | Cart item not found | 404 |
| `INSUFFICIENT_INVENTORY` | Product out of stock | 400 |
| `PAYMENT_FAILED` | Payment processing failed | 400 |
| `DATABASE_ERROR` | Database operation failed | 500 |
| `SERVICE_UNAVAILABLE` | Service temporarily down | 503 |

## Rate Limiting
- **Limit**: 1000 requests per hour per API key
- **Headers**: Rate limit information included in response headers
  - `X-RateLimit-Limit`: Maximum requests per hour
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time when rate limit resets (Unix timestamp)

**Example Headers**:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1692640528
```

## SDK and Libraries

### JavaScript/Node.js
```javascript
import { CarthubAPI } from '@carthub/api-client';

const client = new CarthubAPI({
  baseURL: 'https://api.carthub.com/api/v1',
  apiKey: 'your-api-key'
});

// Add item to cart
const result = await client.cart.addItem({
  customer_id: 'customer-123',
  product_id: 'prod-456',
  product_name: 'Gaming Laptop',
  price: 1299.99,
  quantity: 1
});

// Get cart contents
const cart = await client.cart.getCart('customer-123');

// Process checkout
const order = await client.cart.checkout({
  customer_id: 'customer-123',
  shipping_address: { /* address details */ },
  payment_method: { /* payment details */ }
});
```

### Python
```python
from carthub_api import CarthubClient

client = CarthubClient(
    base_url='https://api.carthub.com/api/v1',
    api_key='your-api-key'
)

# Add item to cart
result = client.cart.add_item(
    customer_id='customer-123',
    product_id='prod-456',
    product_name='Gaming Laptop',
    price=1299.99,
    quantity=1
)

# Get cart contents
cart = client.cart.get_cart('customer-123')

# Process checkout
order = client.cart.checkout(
    customer_id='customer-123',
    shipping_address={},  # address details
    payment_method={}     # payment details
)
```

### cURL Examples

#### Add Item to Cart
```bash
curl -X POST "https://api.carthub.com/api/v1/cart/items" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "customer-123",
    "product_id": "prod-456",
    "product_name": "Gaming Laptop",
    "price": 1299.99,
    "quantity": 1
  }'
```

#### Get Cart Contents
```bash
curl -X GET "https://api.carthub.com/api/v1/cart/customer-123" \
  -H "Authorization: Bearer your-jwt-token"
```

#### Update Item Quantity
```bash
curl -X PUT "https://api.carthub.com/api/v1/cart/customer-123/items/prod-456" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 2}'
```

#### Remove Item
```bash
curl -X DELETE "https://api.carthub.com/api/v1/cart/customer-123/items/prod-456" \
  -H "Authorization: Bearer your-jwt-token"
```

#### Clear Cart
```bash
curl -X DELETE "https://api.carthub.com/api/v1/cart/customer-123" \
  -H "Authorization: Bearer your-jwt-token"
```

#### Process Checkout
```bash
curl -X POST "https://api.carthub.com/api/v1/cart/checkout" \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "customer-123",
    "shipping_address": {
      "street": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "zip_code": "12345",
      "country": "US"
    },
    "payment_method": {
      "type": "credit_card",
      "card_number": "****-****-****-1234"
    }
  }'
```

## Testing

### Postman Collection
A comprehensive Postman collection is available for testing all API endpoints:
- **Download**: [Carthub API Postman Collection](./postman/carthub-api.json)
- **Environment variables**: Included for different environments (dev, staging, prod)
- **Pre-request scripts**: Automatic token management
- **Test scripts**: Response validation and assertions

### OpenAPI/Swagger Documentation
Interactive API documentation is available at:
- **Swagger UI**: `https://api.carthub.com/docs`
- **ReDoc**: `https://api.carthub.com/redoc`
- **OpenAPI Spec**: `https://api.carthub.com/openapi.json`

### Test Data
Sample test data for development and testing:

```json
{
  "customers": [
    {
      "customer_id": "test-customer-1",
      "name": "John Doe",
      "email": "john.doe@example.com"
    }
  ],
  "products": [
    {
      "product_id": "prod-laptop-001",
      "product_name": "Gaming Laptop",
      "price": 1299.99,
      "category": "Electronics"
    },
    {
      "product_id": "prod-mouse-001", 
      "product_name": "Wireless Mouse",
      "price": 29.99,
      "category": "Accessories"
    }
  ]
}
```

## Changelog

### Version 2.0.0 (2025-08-21)
- **Added**: Complete microservices API implementation
- **Added**: FastAPI backend with PostgreSQL
- **Added**: Comprehensive error handling and validation
- **Added**: Health check endpoints
- **Added**: OpenAPI/Swagger documentation
- **Enhanced**: Response formats with detailed cart summaries
- **Enhanced**: Checkout process with order creation
- **Enhanced**: Rate limiting and security features

### Version 1.1.0 (2025-07-15)
- **Added**: Cart clearing functionality
- **Added**: Item quantity updates
- **Improved**: Input validation
- **Added**: Health check endpoint

### Version 1.0.0 (2025-06-01)
- **Initial**: API release with basic cart operations
- **Initial**: Serverless implementation
- **Initial**: Authentication system

## Support
For API support and questions:
- **Email**: api-support@carthub.com
- **Documentation**: https://docs.carthub.com
- **Status Page**: https://status.carthub.com
- **GitHub Issues**: https://github.com/carthub/api/issues

## Architecture-Specific Notes

### Serverless Implementation
- **Cold Starts**: First request may take 2-3 seconds
- **Scaling**: Automatic based on request volume
- **Database**: DynamoDB with eventual consistency
- **Best for**: Variable traffic patterns

### Microservices Implementation  
- **Always Available**: No cold starts
- **Scaling**: Horizontal Pod Autoscaler (2-15 replicas)
- **Database**: PostgreSQL with ACID compliance
- **Best for**: Consistent high traffic

Choose the implementation that best fits your traffic patterns and requirements.
