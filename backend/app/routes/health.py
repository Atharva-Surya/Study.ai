from fastapi import APIRouter

# Create a router instance for health check
# We use prefix="/health" if we want, but keeping it empty or specific is standard.
# Let's keep the prefix empty and define the route directly.
router = APIRouter(tags=["Health"])

# ==========================================
# HEALTH ENDPOINT
# ==========================================
# This is a GET request. When you visit http://localhost:8000/api/v1/health
# you should receive a 200 OK status code and the JSON body below.
@router.get("/health", summary="Check API health status")
async def health_check():
    return {
        "status": "healthy",
        "message": "AI Study Assistant API is up and running"
    }
