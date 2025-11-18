"""
Example usage of advanced Python hooks

Demonstrates real-world patterns and use cases.
"""

import asyncio
from decorator_hooks import (
    hook,
    HookPriority,
    registry,
    timing_hook,
    retry_hook,
    compose_hooks,
)
from async_hooks import (
    async_hook,
    async_registry,
    AsyncHookContext,
    AsyncPipeline,
    AsyncRateLimiter,
)


# Example 1: Event-driven architecture with decorator hooks
class UserService:
    """Service that triggers hooks on user events"""
    
    def create_user(self, name: str, email: str):
        user_id = hash(name + email) % 10000
        print(f"Creating user {user_id}: {name}")
        
        # Trigger hooks
        results = registry.trigger("user.created", user_id=user_id, name=name, email=email)
        return user_id, results


# Register hooks for user creation
@hook("user.created", priority=HookPriority.HIGH)
def send_welcome_email(user_id: int, name: str, email: str):
    print(f"  [HIGH] Sending welcome email to {name} ({email})")
    return f"email_sent_{user_id}"


@hook("user.created", priority=HookPriority.NORMAL)
def create_user_profile(user_id: int, name: str, **kwargs):
    print(f"  [NORMAL] Creating profile for {name}")
    return f"profile_created_{user_id}"


@hook("user.created", priority=HookPriority.LOW)
def log_user_creation(user_id: int, name: str, **kwargs):
    print(f"  [LOW] Logging user creation: {name} (ID: {user_id})")
    return f"logged_{user_id}"


# Example 2: Composed decorators for robust functions
@compose_hooks(timing_hook, retry_hook(max_attempts=3))
def fetch_data(url: str) -> str:
    """Example function with timing and retry hooks"""
    if "error" in url:
        raise ValueError("Simulated error")
    return f"Data from {url}"


# Example 3: Async hooks for concurrent processing
@async_hook("payment.processed")
async def send_receipt(payment_id: int, amount: float):
    await asyncio.sleep(0.1)
    print(f"  Sending receipt for payment {payment_id}: ${amount}")
    return "receipt_sent"


@async_hook("payment.processed")
async def update_inventory(payment_id: int, amount: float):
    await asyncio.sleep(0.15)
    print(f"  Updating inventory for payment {payment_id}")
    return "inventory_updated"


@async_hook("payment.processed")
async def notify_analytics(payment_id: int, amount: float):
    await asyncio.sleep(0.05)
    print(f"  Notifying analytics for payment {payment_id}")
    return "analytics_notified"


async def process_payment(payment_id: int, amount: float):
    """Process payment and trigger async hooks concurrently"""
    print(f"Processing payment {payment_id}: ${amount}")
    results = await async_registry.trigger("payment.processed", payment_id, amount)
    print(f"  Hook results: {results}")
    return results


# Example 4: Async pipeline for data transformation
async def create_data_pipeline():
    """Create a pipeline that transforms data through multiple stages"""
    pipeline = AsyncPipeline()
    
    # Add transformation stages
    pipeline.add_stage(lambda x: x * 2)  # Double the value
    pipeline.add_stage(lambda x: x + 10)  # Add 10
    pipeline.add_stage(lambda x: x ** 2)  # Square it
    
    return pipeline


# Example 5: Rate-limited async operations
@AsyncRateLimiter(max_calls=3, period=1.0)
async def api_call(endpoint: str):
    """Rate-limited API call"""
    print(f"Calling API: {endpoint}")
    await asyncio.sleep(0.1)
    return f"Response from {endpoint}"


async def main():
    print("=" * 60)
    print("Example 1: Event-driven user creation")
    print("=" * 60)
    service = UserService()
    user_id, results = service.create_user("Alice", "alice@example.com")
    print(f"User created with hooks: {results}\n")
    
    print("=" * 60)
    print("Example 2: Composed decorators")
    print("=" * 60)
    try:
        result = fetch_data("https://api.example.com/data")
        print(f"Result: {result}\n")
    except Exception as e:
        print(f"Error (expected): {e}\n")
    
    print("=" * 60)
    print("Example 3: Async concurrent hooks")
    print("=" * 60)
    await process_payment(12345, 99.99)
    print()
    
    print("=" * 60)
    print("Example 4: Async pipeline")
    print("=" * 60)
    pipeline = await create_data_pipeline()
    result = await pipeline.process(5)
    print(f"Pipeline(5) = {result}\n")
    
    print("=" * 60)
    print("Example 5: Rate limiting")
    print("=" * 60)
    for i in range(5):
        result = await api_call(f"/endpoint/{i}")
        print(f"  {result}")


if __name__ == "__main__":
    asyncio.run(main())

