"""
Production-ready Fennec application example
"""

from fennec import Application, Router, JSONResponse
from fennec.security import SecurityHeadersMiddleware, RequestSizeLimitMiddleware
from fennec.config import Config
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load and validate configuration
Config.load_from_file('.env')
Config.validate()

# Create application
app = Application(
    title="Fennec API",
    version="1.0.0",
    docs_enabled=Config.DEBUG
)

# Add security middleware
app.middleware_manager.add(SecurityHeadersMiddleware())
app.middleware_manager.add(RequestSizeLimitMiddleware(max_size=Config.MAX_REQUEST_SIZE))

# Create router
router = Router(prefix="/api")


@router.get("/")
async def root():
    """API root endpoint"""
    return JSONResponse(data={
        "message": "Welcome to Fennec API",
        "version": "1.0.0",
        "status": "operational"
    })


@router.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    return JSONResponse(data={
        "status": "healthy",
        "service": "fennec-api"
    })


# Include router
app.include_router(router)


# Startup event
@app.middleware("http")
async def log_requests(request, call_next):
    """Log all requests"""
    logger.info(f"{request.method} {request.path}")
    response = await call_next(request)
    return response


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting Fennec API")
    logger.info(f"Debug mode: {Config.DEBUG}")
    logger.info(f"Host: {Config.HOST}:{Config.PORT}")
    
    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        log_level="info"
    )
