"""
AI Agent Orchestration Hooks

Chain multiple AI agents with hook-based workflows for complex multi-agent systems.
"""

from typing import Callable, Optional, Any, Dict, List
from dataclasses import dataclass
from enum import Enum
import asyncio
from functools import wraps


class AgentRole(Enum):
    """Roles for different AI agents"""
    PLANNER = "planner"
    EXECUTOR = "executor"
    REVIEWER = "reviewer"
    COORDINATOR = "coordinator"


@dataclass
class AgentMessage:
    """Message passed between agents"""
    role: AgentRole
    content: str
    metadata: Dict[str, Any]
    previous_messages: List['AgentMessage'] = None
    
    def __post_init__(self):
        if self.previous_messages is None:
            self.previous_messages = []


class AgentHook:
    """
    Hook for agent communication and orchestration
    """
    
    def __init__(self, agent_id: str, role: AgentRole):
        self.agent_id = agent_id
        self.role = role
        self._pre_hooks: List[Callable] = []
        self._post_hooks: List[Callable] = []
        self._error_hooks: List[Callable] = []
    
    def before_execution(self, hook: Callable):
        """Register hook to run before agent execution"""
        self._pre_hooks.append(hook)
        return hook
    
    def after_execution(self, hook: Callable):
        """Register hook to run after agent execution"""
        self._post_hooks.append(hook)
        return hook
    
    def on_error(self, hook: Callable):
        """Register hook to run on agent errors"""
        self._error_hooks.append(hook)
        return hook
    
    async def execute(self, message: AgentMessage) -> AgentMessage:
        """Execute agent with hooks"""
        # Pre-execution hooks
        for hook in self._pre_hooks:
            if asyncio.iscoroutinefunction(hook):
                await hook(message)
            else:
                hook(message)
        
        try:
            # Agent execution (to be implemented by subclasses)
            result = await self._process(message)
            
            # Post-execution hooks
            for hook in self._post_hooks:
                if asyncio.iscoroutinefunction(hook):
                    await hook(message, result)
                else:
                    hook(message, result)
            
            return result
        
        except Exception as e:
            # Error hooks
            for hook in self._error_hooks:
                if asyncio.iscoroutinefunction(hook):
                    await hook(message, e)
                else:
                    hook(message, e)
            raise
    
    async def _process(self, message: AgentMessage) -> AgentMessage:
        """Override in subclasses"""
        raise NotImplementedError


class AgentOrchestrator:
    """
    Orchestrates multiple agents using hook-based workflows
    """
    
    def __init__(self):
        self._agents: Dict[str, AgentHook] = {}
        self._workflows: Dict[str, List[str]] = {}
        self._global_hooks: List[Callable] = []
    
    def register_agent(self, agent: AgentHook):
        """Register an agent"""
        self._agents[agent.agent_id] = agent
    
    def register_workflow(self, name: str, agent_sequence: List[str]):
        """Register a workflow as a sequence of agent IDs"""
        self._workflows[name] = agent_sequence
    
    def register_global_hook(self, hook: Callable):
        """Register a hook that runs for all agents"""
        self._global_hooks.append(hook)
    
    async def execute_workflow(
        self,
        workflow_name: str,
        initial_message: AgentMessage,
        parallel: bool = False
    ) -> List[AgentMessage]:
        """
        Execute a workflow of agents
        
        Args:
            workflow_name: Name of registered workflow
            initial_message: Starting message
            parallel: Run agents in parallel (if workflow supports it)
        """
        if workflow_name not in self._workflows:
            raise ValueError(f"Workflow {workflow_name} not found")
        
        agent_sequence = self._workflows[workflow_name]
        messages = [initial_message]
        current_message = initial_message
        
        # Run global hooks
        for hook in self._global_hooks:
            if asyncio.iscoroutinefunction(hook):
                await hook(workflow_name, current_message)
            else:
                hook(workflow_name, current_message)
        
        if parallel:
            # Execute all agents concurrently
            tasks = []
            for agent_id in agent_sequence:
                if agent_id in self._agents:
                    agent = self._agents[agent_id]
                    tasks.append(agent.execute(current_message))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            messages.extend([r for r in results if isinstance(r, AgentMessage)])
        else:
            # Execute agents sequentially
            for agent_id in agent_sequence:
                if agent_id in self._agents:
                    agent = self._agents[agent_id]
                    result = await agent.execute(current_message)
                    messages.append(result)
                    current_message = result
        
        return messages


class SimpleAgent(AgentHook):
    """Simple agent implementation for testing"""
    
    def __init__(self, agent_id: str, role: AgentRole, processor: Callable):
        super().__init__(agent_id, role)
        self.processor = processor
    
    async def _process(self, message: AgentMessage) -> AgentMessage:
        """Process message using the provided processor function"""
        if asyncio.iscoroutinefunction(self.processor):
            content = await self.processor(message.content)
        else:
            content = self.processor(message.content)
        
        return AgentMessage(
            role=self.role,
            content=content,
            metadata=message.metadata,
            previous_messages=message.previous_messages + [message]
        )


# Example usage
async def example_workflow():
    """Example of agent orchestration"""
    orchestrator = AgentOrchestrator()
    
    # Create agents
    planner = SimpleAgent(
        "planner",
        AgentRole.PLANNER,
        lambda x: f"Plan: {x}"
    )
    
    executor = SimpleAgent(
        "executor",
        AgentRole.EXECUTOR,
        lambda x: f"Execute: {x}"
    )
    
    reviewer = SimpleAgent(
        "reviewer",
        AgentRole.REVIEWER,
        lambda x: f"Review: {x}"
    )
    
    # Register agents
    orchestrator.register_agent(planner)
    orchestrator.register_agent(executor)
    orchestrator.register_agent(reviewer)
    
    # Register workflow
    orchestrator.register_workflow(
        "plan-execute-review",
        ["planner", "executor", "reviewer"]
    )
    
    # Add hooks
    @planner.before_execution
    def log_planning(msg: AgentMessage):
        print(f"Planning: {msg.content}")
    
    @executor.after_execution
    def log_execution(msg: AgentMessage, result: AgentMessage):
        print(f"Executed: {result.content}")
    
    # Execute workflow
    initial = AgentMessage(
        role=AgentRole.COORDINATOR,
        content="Build a feature",
        metadata={"task": "feature"}
    )
    
    results = await orchestrator.execute_workflow("plan-execute-review", initial)
    return results


if __name__ == "__main__":
    results = asyncio.run(example_workflow())
    for msg in results:
        print(f"{msg.role.value}: {msg.content}")

