"""Test script for the Simple Agent that calls your A2A agent."""

import asyncio
import logging
import os
from dotenv import load_dotenv

from simple_agent import SimpleAgent

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Test the simple agent."""
    logger.info("🚀 Starting Simple Agent Test")
    
    # Check if OpenAI API key is set
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY environment variable not set")
        logger.info("Please set your OpenAI API key in the .env file")
        return
    
    # Create the simple agent
    logger.info("📱 Creating Simple Agent...")
    agent = SimpleAgent()
    
    try:
        # Test 1: Direct question (should respond directly)
        logger.info("\n" + "="*50)
        logger.info("🧪 Test 1: Direct Question")
        logger.info("Question: Hello, how are you?")
        
        response1 = await agent.chat("Hello, how are you?")
        logger.info(f"✅ Response: {response1}")
        
        # Test 2: Question that requires A2A agent (should call A2A agent)
        logger.info("\n" + "="*50)
        logger.info("🧪 Test 2: A2A Agent Call")
        logger.info("Question: What are the latest developments in AI?")
        
        response2 = await agent.chat("What are the latest developments in AI?")
        logger.info(f"✅ Response: {response2}")
        
        # Test 3: Follow-up question (should call A2A agent again)
        logger.info("\n" + "="*50)
        logger.info("🧪 Test 3: Follow-up Question")
        logger.info("Question: Can you summarize the key findings?")
        
        response3 = await agent.chat("Can you summarize the key findings?")
        logger.info(f"✅ Response: {response3}")
        
        # Test 4: Another information request
        logger.info("\n" + "="*50)
        logger.info("🧪 Test 5: Another Direct Question")
        logger.info("Question: Find recent papers on transformer architectures")
        
        response4 = await agent.chat("Find recent papers on transformer architectures")
        logger.info(f"✅ Response: {response4}")
        
        # Test 5: Direct question again
        logger.info("\n" + "="*50)
        logger.info("🧪 Test 5: Another Direct Question")
        logger.info("Question: What is your name?")
        
        response5 = await agent.chat("What is your name?")
        logger.info(f"✅ Response: {response5}")
        
        logger.info("\n" + "="*50)
        logger.info("🎉 All tests completed!")
        
    except Exception as e:
        logger.error(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        await agent.close()
        logger.info("🧹 Cleanup completed")


async def interactive_mode():
    """Run the agent in interactive mode for manual testing."""
    logger.info("🎮 Starting Interactive Mode")
    logger.info("Type 'quit' to exit")
    
    if not os.getenv('OPENAI_API_KEY'):
        logger.error("❌ OPENAI_API_KEY environment variable not set")
        return
    
    agent = SimpleAgent()
    
    try:
        while True:
            try:
                # Get user input
                user_input = input("\n🤖 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    logger.info("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Get response from agent
                logger.info("🔄 Processing...")
                response = await agent.chat(user_input)
                logger.info(f"🤖 Simple Agent: {response}")
                
            except KeyboardInterrupt:
                logger.info("\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"❌ Error: {e}")
    
    finally:
        await agent.close()
        logger.info("🧹 Cleanup completed")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(main())
