import uvicorn
import asyncio
from .init_db import init_db
from .init_admin import init_admin

async def main():
    try:
        # Initialize database
        await init_db()
        
        # Initialize admin user
        await init_admin()
        
        # Start the server
        config = uvicorn.Config(
            "admin.main:app",
            host="0.0.0.0",
            port=8001,
            reload=True
        )
        server = uvicorn.Server(config)
        await server.serve()
    except Exception as e:
        print(f"Error starting server: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 