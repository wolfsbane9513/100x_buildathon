import asyncio
from llama_index import ServiceContext, VectorStoreIndex
from llama_index.llms import OpenAI
from llama_index.tools import QueryEngineTool, ToolMetadata
from dotenv import load_dotenv
import os

async def test_basic_functionality():
    """Test basic functionality of core components."""
    try:
        print("Testing LlamaIndex components...")
        
        # Test LLM initialization
        print("\n1. Testing LLM initialization...")
        llm = OpenAI(model="gpt-3.5-turbo")
        print("✓ LLM initialized")
        
        # Test ServiceContext
        print("\n2. Testing ServiceContext...")
        service_context = ServiceContext.from_defaults(llm=llm)
        print("✓ ServiceContext created")
        
        # Test VectorStoreIndex
        print("\n3. Testing VectorStoreIndex...")
        documents = []  # Empty for testing
        index = VectorStoreIndex.from_documents(
            documents,
            service_context=service_context
        )
        print("✓ VectorStoreIndex created")
        
        # Test QueryEngine
        print("\n4. Testing QueryEngine...")
        query_engine = index.as_query_engine()
        print("✓ QueryEngine created")
        
        print("\nAll components tested successfully! ✓")
        return True
        
    except Exception as e:
        print(f"\nError during testing: {str(e)}")
        return False

async def main():
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not found in environment variables")
        return
    
    success = await test_basic_functionality()
    if success:
        print("\nAll tests passed! The environment is properly set up.")
    else:
        print("\nSome tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
