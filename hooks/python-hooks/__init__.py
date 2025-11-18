"""
Advanced Python Hooks

Cutting-edge Python hook patterns using decorators, async, and event-driven architectures.
"""

from .decorator_hooks import (
    HookRegistry,
    HookPriority,
    hook,
    ComposableDecorator,
    timing_hook,
    retry_hook,
    cache_hook,
    compose_hooks,
    registry,
)

from .async_hooks import (
    AsyncHookRegistry,
    AsyncHookContext,
    async_hook,
    async_resource_hook,
    AsyncPipeline,
    AsyncRateLimiter,
    async_registry,
)

__all__ = [
    # Decorator hooks
    "HookRegistry",
    "HookPriority",
    "hook",
    "ComposableDecorator",
    "timing_hook",
    "retry_hook",
    "cache_hook",
    "compose_hooks",
    "registry",
    # Async hooks
    "AsyncHookRegistry",
    "AsyncHookContext",
    "async_hook",
    "async_resource_hook",
    "AsyncPipeline",
    "AsyncRateLimiter",
    "async_registry",
]

