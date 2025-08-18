"""Simple Agent using LangGraph that can call your A2A agent through A2A protocol."""

import asyncio
import logging
import os
from typing import Dict, Any, Annotated, TypedDict, List
from uuid import uuid4

import httpx
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SimpleAgentState(TypedDict):
    """State schema for the simple agent that will call your A2A agent."""
    messages: Annotated[List, add_messages]
    a2a_response: Any  # Store responses from A2A calls
    final_response: str  # The final answer to give to the user


class A2AClientWrapper:
    """Wrapper for making calls to your A2A agent."""
    
    def __init__(self, base_url: str = "http://localhost:10000"):
        self.base_url = base_url
        self.httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(60.0))
        self.resolver = None
        self.client = None
        self._initialized = False
    
    async def _initialize_client(self):
        """Initialize the A2A client."""
        if self._initialized:
            return
            
        try:
            self.resolver = A2ACardResolver(
                httpx_client=self.httpx_client,
                base_url=self.base_url
            )
            agent_card = await self.resolver.get_agent_card()
            self.client = A2AClient(
                httpx_client=self.httpx_client,
                agent_card=agent_card
            )
            self._initialized = True
            logger.info("A2A client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize A2A client: {e}")
            raise
    
    async def send_message(self, message: str, task_id: str = None, context_id: str = None):
        """Send a message to the A2A agent and get response."""
        await self._initialize_client()
        
        try:
            send_message_payload = {
                'message': {
                    'role': 'user',
                    'parts': [{'kind': 'text', 'text': message}],
                    'message_id': uuid4().hex,
                },
            }
            
            if task_id and context_id:
                send_message_payload['message']['task_id'] = task_id
                send_message_payload['message']['context_id'] = context_id
            
            request = SendMessageRequest(
                id=str(uuid4()),
                params=MessageSendParams(**send_message_payload)
            )
            
            response = await self.client.send_message(request)
            return response
            
        except Exception as e:
            logger.error(f"Error sending message to A2A agent: {e}")
            return None


def simple_agent_node(state: SimpleAgentState, a2a_client: A2AClientWrapper) -> Dict[str, Any]:
    """Main node that decides whether to call A2A agent or respond directly."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # Simple logic: if user asks for information, call A2A agent
    # If user asks for clarification, respond directly
    
    # Questions that should go to A2A agent (information-seeking)
    a2a_keywords = ['search', 'find', 'latest', 'recent', 'papers', 'news', 'developments', 'ai', 'artificial intelligence', 'transformer']
    
    # Questions that can be answered directly (greetings, clarification)
    direct_keywords = ['hello', 'hi', 'how are you', 'name', 'what is your name', 'who are you']
    
    user_content = last_message.content.lower()
    
    if any(keyword in user_content for keyword in a2a_keywords):
        # Need to call A2A agent
        logger.info("Routing to A2A agent call")
        return {"a2a_response": "pending"}
    elif any(keyword in user_content for keyword in direct_keywords):
        # Can respond directly
        logger.info("Responding directly")
        if 'name' in user_content:
            return {"final_response": "I am a Simple Agent built with LangGraph that can call your A2A agent for information requests."}
        elif 'hello' in user_content or 'hi' in user_content:
            return {"final_response": "Hello! I'm a Simple Agent. I can help you with information requests by calling my A2A agent friend."}
        elif 'how are you' in user_content:
            return {"final_response": "I'm doing well, thank you! I'm ready to help you with information requests."}
        else:
            return {"final_response": "I can help you with that directly. Could you be more specific about what you'd like to know?"}
    else:
        # Default to A2A agent for unknown queries
        logger.info("Unknown query type, routing to A2A agent call")
        return {"a2a_response": "pending"}


async def a2a_call_node(state: SimpleAgentState, a2a_client: A2AClientWrapper) -> Dict[str, Any]:
    """Node that makes the actual A2A call."""
    messages = state["messages"]
    last_message = messages[-1]
    
    try:
        logger.info(f"Calling A2A agent with: {last_message.content}")
        
        # Call the A2A agent
        response = await a2a_client.send_message(last_message.content)
        
        if response and hasattr(response, 'root') and hasattr(response.root, 'result'):
            # Extract the response content
            result = response.root.result
            
            # Check if there are messages in the result
            if hasattr(result, 'messages') and result.messages:
                # Get the last message content
                last_a2a_message = result.messages[-1]
                if hasattr(last_a2a_message, 'parts') and last_a2a_message.parts:
                    a2a_response = last_a2a_message.parts[0].text
                else:
                    a2a_response = str(last_a2a_message)
            else:
                a2a_response = f"A2A agent responded: {result}"
                
            logger.info(f"A2A agent response: {a2a_response[:100]}...")
            
        else:
            a2a_response = "Error: Could not get response from A2A agent"
            logger.warning("No valid response from A2A agent")
            
        return {"a2a_response": a2a_response}
        
    except Exception as e:
        error_msg = f"Error calling A2A agent: {str(e)}"
        logger.error(error_msg)
        return {"a2a_response": error_msg}


# Removed sync wrapper; we use native async node now


def response_generation_node(state: SimpleAgentState, model) -> Dict[str, Any]:
    """Node that generates the final response."""
    messages = state["messages"]
    a2a_response = state.get("a2a_response", "")
    final_response = state.get("final_response", "")
    
    if final_response:
        # We already have a final response from the agent node
        logger.info(f"Using existing final response: {final_response[:100]}...")
        return {"final_response": final_response}
    elif a2a_response and a2a_response != "pending":
        # We have a response from A2A agent, format it
        if a2a_response.startswith("Error:"):
            final_response = f"I encountered an issue: {a2a_response}"
        else:
            final_response = f"Based on the A2A agent's response: {a2a_response}"
        logger.info(f"Generated A2A response: {final_response[:100]}...")
        return {"final_response": final_response}
    else:
        # No response available
        final_response = "I'm processing your request..."
        logger.info(f"Generated fallback response: {final_response}")
        return {"final_response": final_response}


def route_simple_agent(state: SimpleAgentState) -> str:
    """Route to the next node based on state."""
    a2a_response = state.get("a2a_response")
    
    if a2a_response == "pending":
        return "a2a_call"
    else:
        return "response_generation"


def should_end(state: SimpleAgentState) -> str:
    """Determine if we should end the conversation."""
    return "end" if "final_response" in state and state["final_response"] else "continue"


def build_simple_agent_graph(model, a2a_client: A2AClientWrapper):
    """Build the simple agent graph."""
    
    # Create the graph
    graph = StateGraph(SimpleAgentState)
    
    # Add nodes
    graph.add_node("agent", lambda state: simple_agent_node(state, a2a_client))

    # Create an async wrapper so LangGraph properly awaits the coroutine
    async def _a2a_call_wrapped(state: SimpleAgentState) -> Dict[str, Any]:
        return await a2a_call_node(state, a2a_client)

    graph.add_node("a2a_call", _a2a_call_wrapped)
    graph.add_node("response_generation", lambda state: response_generation_node(state, model))
    
    # Set entry point
    graph.set_entry_point("agent")
    
    # Add conditional edges
    graph.add_conditional_edges(
        "agent",
        route_simple_agent,
        {
            "a2a_call": "a2a_call",
            "response_generation": "response_generation"
        }
    )
    
    graph.add_edge("a2a_call", "response_generation")
    
    # Add conditional end
    graph.add_conditional_edges(
        "response_generation",
        should_end,
        {"end": END, "continue": "response_generation"}
    )
    
    return graph.compile()


class SimpleAgent:
    """Simple agent that can call your A2A agent."""
    
    def __init__(self, a2a_base_url: str = "http://localhost:10000"):
        self.model = ChatOpenAI(
            model=os.getenv('TOOL_LLM_NAME', 'gpt-4o-mini'),
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            temperature=0,
        )
        self.a2a_client = A2AClientWrapper(a2a_base_url)
        self.graph = build_simple_agent_graph(self.model, self.a2a_client)
        self._initialized = True
    
    async def chat(self, message: str) -> str:
        """Async chat method using LangGraph async streaming/invoke."""
        inputs = {'messages': [HumanMessage(content=message)]}
        
        # Use async interface
        result = await self.graph.ainvoke(inputs)
        return result.get("final_response", "No response generated")
    
    async def astream(self, message: str):
        """Async generator yielding intermediate states (optional)."""
        inputs = {'messages': [HumanMessage(content=message)]}
        async for chunk in self.graph.astream(inputs):
            yield chunk
    
    async def close(self):
        """Close the A2A client."""
        if self.a2a_client:
            await self.a2a_client.httpx_client.aclose()
