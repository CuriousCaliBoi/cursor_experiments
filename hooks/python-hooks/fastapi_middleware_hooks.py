"""
FastAPI Middleware Hooks

Advanced FastAPI middleware patterns using hooks for request/response lifecycle management.
"""

from typing import Callable, Optional, Any
from fastapi import Request, Response, HTTPException
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class HookMiddleware(BaseHTTPMiddleware):
    """
    Base middleware that supports hook registration for request/response lifecycle
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self._pre_request_hooks: list[Callable] = []
        self._post_request_hooks: list[Callable] = []
        self._error_hooks: list[Callable] = []
    
    def register_pre_request(self, hook: Callable):
        """Register a hook that runs before request processing"""
        self._pre_request_hooks.append(hook)
        return hook
    
    def register_post_request(self, hook: Callable):
        """Register a hook that runs after request processing"""
        self._post_request_hooks.append(hook)
        return hook
    
    def register_error(self, hook: Callable):
        """Register a hook that runs on errors"""
        self._error_hooks.append(hook)
        return hook
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Pre-request hooks
        for hook in self._pre_request_hooks:
            try:
                if callable(hook):
                    if hasattr(hook, '__call__'):
                        result = await hook(request) if hasattr(hook, '__await__') else hook(request)
            except Exception as e:
                logger.error(f"Error in pre-request hook: {e}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Post-request hooks
            for hook in self._post_request_hooks:
                try:
                    if callable(hook):
                        if hasattr(hook, '__await__'):
                            await hook(request, response)
                        else:
                            hook(request, response)
                except Exception as e:
                    logger.error(f"Error in post-request hook: {e}")
            
            return response
        
        except Exception as e:
            # Error hooks
            for hook in self._error_hooks:
                try:
                    if callable(hook):
                        if hasattr(hook, '__await__'):
                            await hook(request, e)
                        else:
                            hook(request, e)
                except Exception as hook_error:
                    logger.error(f"Error in error hook: {hook_error}")
            raise


class TimingMiddleware(HookMiddleware):
    """Middleware that adds timing information to responses"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response


class AuthHookMiddleware(HookMiddleware):
    """Middleware with authentication hooks"""
    
    def __init__(self, app: ASGIApp, auth_validator: Optional[Callable] = None):
        super().__init__(app)
        self.auth_validator = auth_validator
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Run pre-request hooks (including auth)
        for hook in self._pre_request_hooks:
            result = await hook(request) if hasattr(hook, '__await__') else hook(request)
            if result is False:  # Hook can return False to block request
                raise HTTPException(status_code=403, detail="Request blocked by hook")
        
        return await call_next(request)


class LoggingMiddleware(HookMiddleware):
    """Middleware with logging hooks"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        logger.info(f"{request.method} {request.url.path}")
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response


def route_hook(path: str, method: str = "GET"):
    """
    Decorator for registering route-specific hooks
    
    Example:
        @route_hook("/api/users", "POST")
        async def validate_user_creation(request: Request):
            # Validate request
            pass
    """
    def decorator(func: Callable):
        # Store hook metadata on function
        if not hasattr(func, '_route_hooks'):
            func._route_hooks = []
        func._route_hooks.append((path, method))
        return func
    return decorator


class HookedRoute(APIRoute):
    """
    Custom route class that supports hooks
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._before_hooks: list[Callable] = []
        self._after_hooks: list[Callable] = []
    
    def before(self, hook: Callable):
        """Register a hook to run before route handler"""
        self._before_hooks.append(hook)
        return hook
    
    def after(self, hook: Callable):
        """Register a hook to run after route handler"""
        self._after_hooks.append(hook)
        return hook
    
    async def get_route_handler(self) -> Callable:
        original_route_handler = await super().get_route_handler()
        
        async def hooked_route_handler(request: Request) -> Response:
            # Run before hooks
            for hook in self._before_hooks:
                if asyncio.iscoroutinefunction(hook):
                    result = await hook(request)
                else:
                    result = hook(request)
                if result is False:
                    raise HTTPException(status_code=403, detail="Request blocked")
            
            # Execute route handler
            response = await original_route_handler(request)
            
            # Run after hooks
            for hook in self._after_hooks:
                if asyncio.iscoroutinefunction(hook):
                    await hook(request, response)
                else:
                    hook(request, response)
            
            return response
        
        return hooked_route_handler


# Example usage functions
def create_app_with_hooks():
    """Example of creating a FastAPI app with hook middleware"""
    from fastapi import FastAPI
    
    app = FastAPI()
    
    # Add timing middleware
    app.add_middleware(TimingMiddleware)
    
    # Add logging middleware
    app.add_middleware(LoggingMiddleware)
    
    return app


# Import asyncio for route handler
import asyncio

