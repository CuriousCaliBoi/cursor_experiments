"""
Async/Await Hooks

Advanced async hook patterns using context managers, coroutines, and concurrent execution.
"""

import asyncio
from typing import Callable, TypeVar, ParamSpec, AsyncContextManager, Optional, Any
from contextlib import asynccontextmanager
from functools import wraps
import time
from dataclasses import dataclass
from collections.abc import AsyncIterator

P = ParamSpec('P')
R = TypeVar('R')


class AsyncHookRegistry:
    """
    Async hook registry supporting:
    - Async hook execution
    - Concurrent hook processing
    - Async context managers for resource management
    - Hook cancellation and timeout
    """
    
    def __init__(self):
        self._hooks: dict[str, list[Callable]] = {}
        self._pre_hooks: dict[str, list[Callable]] = {}
        self._post_hooks: dict[str, list[Callable]] = {}
    
    def register(self, event: str, hook: Callable):
        """Register an async hook"""
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(hook)
    
    def register_pre(self, event: str, hook: Callable):
        """Register a pre-hook (runs before main hooks)"""
        if event not in self._pre_hooks:
            self._pre_hooks[event] = []
        self._pre_hooks[event].append(hook)
    
    def register_post(self, event: str, hook: Callable):
        """Register a post-hook (runs after main hooks)"""
        if event not in self._post_hooks:
            self._post_hooks[event] = []
        self._post_hooks[event].append(hook)
    
    async def trigger(
        self,
        event: str,
        *args,
        concurrent: bool = True,
        timeout: Optional[float] = None,
        **kwargs
    ) -> list[Any]:
        """
        Trigger async hooks
        
        Args:
            event: Event name
            concurrent: Run hooks concurrently (True) or sequentially (False)
            timeout: Maximum time to wait for hooks
            *args, **kwargs: Arguments to pass to hooks
        """
        async def run_hooks(hook_list: list[Callable]):
            if concurrent:
                tasks = [hook(*args, **kwargs) for hook in hook_list]
                return await asyncio.gather(*tasks, return_exceptions=True)
            else:
                results = []
                for hook in hook_list:
                    result = await hook(*args, **kwargs)
                    results.append(result)
                return results
        
        # Run pre-hooks
        pre_results = []
        if event in self._pre_hooks:
            pre_results = await run_hooks(self._pre_hooks[event])
        
        # Run main hooks
        main_results = []
        if event in self._hooks:
            if timeout:
                main_results = await asyncio.wait_for(
                    run_hooks(self._hooks[event]),
                    timeout=timeout
                )
            else:
                main_results = await run_hooks(self._hooks[event])
        
        # Run post-hooks
        post_results = []
        if event in self._post_hooks:
            post_results = await run_hooks(self._post_hooks[event])
        
        return {
            'pre': pre_results,
            'main': main_results,
            'post': post_results
        }


# Global async registry
async_registry = AsyncHookRegistry()


class AsyncHookContext:
    """
    Async context manager for hook lifecycle management
    Provides setup/teardown hooks and resource management
    """
    
    def __init__(self, name: str):
        self.name = name
        self._setup_hooks: list[Callable] = []
        self._teardown_hooks: list[Callable] = []
        self._resources: dict[str, Any] = {}
    
    def setup(self, hook: Callable):
        """Register setup hook"""
        self._setup_hooks.append(hook)
        return hook
    
    def teardown(self, hook: Callable):
        """Register teardown hook"""
        self._teardown_hooks.append(hook)
        return hook
    
    async def __aenter__(self):
        """Execute setup hooks"""
        for hook in self._setup_hooks:
            result = await hook()
            if isinstance(result, dict):
                self._resources.update(result)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Execute teardown hooks"""
        for hook in reversed(self._teardown_hooks):
            await hook(self._resources)
        return False
    
    def get_resource(self, key: str) -> Any:
        """Get a resource set up during context entry"""
        return self._resources.get(key)


def async_hook(event: str, concurrent: bool = True):
    """Decorator for registering async hooks"""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        async_registry.register(event, func)
        return func
    return decorator


@asynccontextmanager
async def async_resource_hook(
    setup: Callable,
    teardown: Optional[Callable] = None
) -> AsyncIterator[Any]:
    """
    Create an async context manager hook for resource management
    
    Example:
        async with async_resource_hook(setup_db, teardown_db) as db:
            # Use db
            pass
    """
    resource = await setup()
    try:
        yield resource
    finally:
        if teardown:
            await teardown(resource)


class AsyncPipeline:
    """
    Async pipeline that processes data through multiple async hooks
    Supports streaming, error handling, and parallel processing
    """
    
    def __init__(self):
        self._stages: list[Callable] = []
        self._error_handlers: dict[int, Callable] = {}
    
    def add_stage(self, stage: Callable, error_handler: Optional[Callable] = None):
        """Add a processing stage"""
        index = len(self._stages)
        self._stages.append(stage)
        if error_handler:
            self._error_handlers[index] = error_handler
        return self
    
    async def process(self, data: Any) -> Any:
        """Process data through all stages"""
        current_data = data
        for i, stage in enumerate(self._stages):
            try:
                if asyncio.iscoroutinefunction(stage):
                    current_data = await stage(current_data)
                else:
                    current_data = stage(current_data)
            except Exception as e:
                if i in self._error_handlers:
                    current_data = await self._error_handlers[i](current_data, e)
                else:
                    raise
        return current_data
    
    async def process_stream(self, data_stream: AsyncIterator) -> AsyncIterator:
        """Process a stream of data through all stages"""
        async for item in data_stream:
            yield await self.process(item)


class AsyncRateLimiter:
    """
    Async rate limiter hook that limits execution rate
    """
    
    def __init__(self, max_calls: int, period: float):
        self.max_calls = max_calls
        self.period = period
        self.calls: list[float] = []
        self._lock = asyncio.Lock()
    
    async def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            async with self._lock:
                now = time.time()
                # Remove old calls outside the period
                self.calls = [call_time for call_time in self.calls if now - call_time < self.period]
                
                if len(self.calls) >= self.max_calls:
                    sleep_time = self.period - (now - self.calls[0])
                    if sleep_time > 0:
                        await asyncio.sleep(sleep_time)
                        now = time.time()
                        self.calls = []
                
                self.calls.append(now)
            
            return await func(*args, **kwargs)
        
        return wrapper


# Example usage
if __name__ == "__main__":
    async def main():
        # Register async hooks
        @async_hook("data.processed")
        async def log_processing(data: dict):
            print(f"Logging: {data}")
            await asyncio.sleep(0.1)
            return "logged"
        
        @async_hook("data.processed")
        async def save_to_db(data: dict):
            print(f"Saving to DB: {data}")
            await asyncio.sleep(0.2)
            return "saved"
        
        # Trigger hooks concurrently
        results = await async_registry.trigger("data.processed", {"id": 1, "value": "test"})
        print(f"Results: {results}")
        
        # Async context manager example
        async with AsyncHookContext("database") as ctx:
            @ctx.setup
            async def setup_db():
                print("Setting up database connection")
                return {"db": "connection_object"}
            
            @ctx.teardown
            async def teardown_db(resources):
                print(f"Closing database: {resources.get('db')}")
            
            db = ctx.get_resource("db")
            print(f"Using database: {db}")
        
        # Pipeline example
        pipeline = AsyncPipeline()
        pipeline.add_stage(lambda x: x * 2)
        pipeline.add_stage(lambda x: x + 10)
        
        result = await pipeline.process(5)
        print(f"Pipeline result: {result}")
    
    asyncio.run(main())

