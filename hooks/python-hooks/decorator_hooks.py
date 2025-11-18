"""
Advanced Decorator Hook Patterns

This module demonstrates cutting-edge decorator composition patterns for building
hook-based architectures. Decorators are Python's native hook mechanism.
"""

from functools import wraps
from typing import Callable, Any, TypeVar, ParamSpec, Optional
import time
import logging
from dataclasses import dataclass
from enum import Enum

# Type variables for better type hints
P = ParamSpec('P')
R = TypeVar('R')

logger = logging.getLogger(__name__)


class HookPriority(Enum):
    """Priority levels for hook execution order"""
    LOWEST = 0
    LOW = 1
    NORMAL = 2
    HIGH = 3
    HIGHEST = 4


@dataclass
class HookMetadata:
    """Metadata for a registered hook"""
    func: Callable
    priority: HookPriority
    name: str
    enabled: bool = True


class HookRegistry:
    """
    Advanced hook registry that supports:
    - Priority-based execution order
    - Conditional hook execution
    - Hook composition and chaining
    - Hook enable/disable at runtime
    """
    
    def __init__(self):
        self._hooks: dict[str, list[HookMetadata]] = {}
        self._global_hooks: list[HookMetadata] = []
    
    def register(
        self,
        event: Optional[str] = None,
        priority: HookPriority = HookPriority.NORMAL,
        name: Optional[str] = None,
        enabled: bool = True
    ):
        """
        Register a hook decorator
        
        Args:
            event: Event name to hook into (None for global hooks)
            priority: Execution priority
            name: Optional name for the hook
            enabled: Whether hook is enabled
        """
        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            hook_name = name or func.__name__
            metadata = HookMetadata(
                func=func,
                priority=priority,
                name=hook_name,
                enabled=enabled
            )
            
            if event is None:
                self._global_hooks.append(metadata)
                self._global_hooks.sort(key=lambda h: h.priority.value, reverse=True)
            else:
                if event not in self._hooks:
                    self._hooks[event] = []
                self._hooks[event].append(metadata)
                self._hooks[event].sort(key=lambda h: h.priority.value, reverse=True)
            
            return func
        
        return decorator
    
    def trigger(self, event: str, *args, **kwargs) -> list[Any]:
        """
        Trigger hooks for an event
        
        Returns:
            List of return values from hooks (in priority order)
        """
        results = []
        
        # Execute global hooks first
        for hook in self._global_hooks:
            if hook.enabled:
                try:
                    result = hook.func(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error in global hook {hook.name}: {e}")
        
        # Execute event-specific hooks
        if event in self._hooks:
            for hook in self._hooks[event]:
                if hook.enabled:
                    try:
                        result = hook.func(*args, **kwargs)
                        results.append(result)
                    except Exception as e:
                        logger.error(f"Error in hook {hook.name} for event {event}: {e}")
        
        return results
    
    def enable_hook(self, name: str):
        """Enable a hook by name"""
        for hook_list in [self._global_hooks] + list(self._hooks.values()):
            for hook in hook_list:
                if hook.name == name:
                    hook.enabled = True
    
    def disable_hook(self, name: str):
        """Disable a hook by name"""
        for hook_list in [self._global_hooks] + list(self._hooks.values()):
            for hook in hook_list:
                if hook.name == name:
                    hook.enabled = False


# Global registry instance
registry = HookRegistry()


def hook(event: Optional[str] = None, priority: HookPriority = HookPriority.NORMAL):
    """Convenience decorator for registering hooks"""
    return registry.register(event=event, priority=priority)


class ComposableDecorator:
    """
    Advanced decorator that can be composed with other decorators
    Supports method chaining and conditional application
    """
    
    def __init__(self, func: Optional[Callable] = None):
        self.func = func
        self._conditions: list[Callable] = []
        self._transformations: list[Callable] = []
    
    def __call__(self, func: Callable[P, R]) -> Callable[P, R]:
        if self.func is None:
            # Used as decorator
            self.func = func
            return self._wrap(func)
        else:
            # Used as function
            return self._wrap(func)
    
    def _wrap(self, func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Check conditions
            for condition in self._conditions:
                if not condition(*args, **kwargs):
                    return func(*args, **kwargs)
            
            # Apply transformations
            transformed_args = args
            transformed_kwargs = kwargs
            for transform in self._transformations:
                transformed_args, transformed_kwargs = transform(transformed_args, transformed_kwargs)
            
            return func(*transformed_args, **transformed_kwargs)
        
        return wrapper
    
    def when(self, condition: Callable):
        """Add a condition - decorator only applies if condition is True"""
        self._conditions.append(condition)
        return self
    
    def transform(self, transformer: Callable):
        """Add a transformation to modify arguments"""
        self._transformations.append(transformer)
        return self


def timing_hook(func: Callable[P, R]) -> Callable[P, R]:
    """Example hook: Measure execution time"""
    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.info(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper


def retry_hook(max_attempts: int = 3, delay: float = 1.0):
    """Example hook: Retry on failure"""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                        logger.warning(f"Attempt {attempt + 1} failed, retrying...")
                    else:
                        logger.error(f"All {max_attempts} attempts failed")
            raise last_exception
        return wrapper
    return decorator


def cache_hook(ttl: Optional[float] = None):
    """Example hook: Simple caching"""
    cache: dict[tuple, tuple[Any, float]] = {}
    
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            
            if key in cache:
                result, cached_time = cache[key]
                if ttl is None or (now - cached_time) < ttl:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result
        
        return wrapper
    return decorator


# Example: Composing multiple hooks
def compose_hooks(*decorators):
    """Compose multiple decorators into one"""
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        for dec in reversed(decorators):
            func = dec(func)
        return func
    return decorator


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Register event hooks
    @hook("user.created", priority=HookPriority.HIGH)
    def send_welcome_email(user_id: int):
        print(f"Sending welcome email to user {user_id}")
        return f"email_sent_{user_id}"
    
    @hook("user.created", priority=HookPriority.NORMAL)
    def create_user_profile(user_id: int):
        print(f"Creating profile for user {user_id}")
        return f"profile_created_{user_id}"
    
    # Trigger hooks
    results = registry.trigger("user.created", 123)
    print(f"Hook results: {results}")
    
    # Composable decorator example
    @compose_hooks(timing_hook, retry_hook(max_attempts=2))
    def risky_operation(x: int) -> int:
        if x < 0:
            raise ValueError("Negative not allowed")
        return x * 2
    
    print(risky_operation(5))
    print(risky_operation(-1))  # Will retry

