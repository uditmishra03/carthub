from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Shopping Cart API",
    description="Microservice for shopping cart operations",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory cart storage for demo
cart_storage = {}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "backend"}

# Cart endpoints
@app.get("/api/v1/cart/{user_id}")
async def get_cart(user_id: str):
    cart = cart_storage.get(user_id, {"items": [], "total": 0})
    return {"success": True, "data": cart}

@app.post("/api/v1/cart/{user_id}/items")
async def add_to_cart(user_id: str, item: dict):
    if user_id not in cart_storage:
        cart_storage[user_id] = {"items": [], "total": 0}
    
    cart_storage[user_id]["items"].append(item)
    cart_storage[user_id]["total"] += item.get("price", 0)
    
    return {"success": True, "data": cart_storage[user_id]}

@app.delete("/api/v1/cart/{user_id}/items/{item_id}")
async def remove_from_cart(user_id: str, item_id: str):
    if user_id in cart_storage:
        cart_storage[user_id]["items"] = [
            item for item in cart_storage[user_id]["items"] 
            if item.get("id") != item_id
        ]
        cart_storage[user_id]["total"] = sum(
            item.get("price", 0) for item in cart_storage[user_id]["items"]
        )
    
    return {"success": True, "data": cart_storage.get(user_id, {"items": [], "total": 0})}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception handler caught: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"}
    )

# Root endpoint
@app.get("/")
async def root():
    return {
        "service": "Shopping Cart Backend",
        "version": "2.0.0",
        "status": "running",
        "message": "Demo backend with in-memory storage"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
