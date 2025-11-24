#!/usr/bin/env python3
"""
Simple Backend Test - Test basic endpoints first
"""

import asyncio
import aiohttp
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_basic_endpoints():
    """Test basic endpoints to see if backend is working"""
    base_url = "https://codeweaver-30.preview.emergentagent.com/api"
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Root endpoint
        logger.info("Testing root endpoint...")
        try:
            async with session.get(f"{base_url}/") as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Root endpoint: {data}")
                else:
                    logger.error(f"❌ Root endpoint failed: {response.status}")
        except Exception as e:
            logger.error(f"❌ Root endpoint error: {e}")
        
        # Test 2: Create session
        logger.info("Testing session creation...")
        try:
            payload = {"project_name": "Simple Test"}
            async with session.post(
                f"{base_url}/session/create",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    session_id = data.get('session_id')
                    logger.info(f"✅ Session created: {session_id}")
                    
                    # Test 3: Get session
                    logger.info("Testing session retrieval...")
                    async with session.get(f"{base_url}/session/{session_id}") as get_response:
                        if get_response.status == 200:
                            session_data = await get_response.json()
                            logger.info(f"✅ Session retrieved: {session_data.get('project_name')}")
                        else:
                            logger.error(f"❌ Session retrieval failed: {get_response.status}")
                    
                    # Test 4: Test models endpoint
                    logger.info("Testing models endpoint...")
                    async with session.get(f"{base_url}/models") as models_response:
                        if models_response.status == 200:
                            models_data = await models_response.json()
                            logger.info(f"✅ Models endpoint: {len(models_data.get('models', []))} models available")
                        else:
                            logger.error(f"❌ Models endpoint failed: {models_response.status}")
                    
                    return session_id
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Session creation failed: {response.status} - {error_text}")
        except Exception as e:
            logger.error(f"❌ Session creation error: {e}")
    
    return None

async def test_netlify_generation_only(session_id: str):
    """Test just the Netlify generation (without deployment)"""
    base_url = "https://codeweaver-30.preview.emergentagent.com/api"
    
    logger.info("Testing Netlify generation only...")
    
    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "session_id": session_id,
                "prompt": "create a simple HTML page with hello world",
                "model": "gpt-5",
                "edit_mode": False
            }
            
            logger.info("🚀 Testing Netlify project generation...")
            
            async with session.post(
                f"{base_url}/netlify/generate",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=60)  # 1 minute timeout
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Netlify generation successful!")
                    logger.info(f"   Project ID: {data.get('project_id')}")
                    logger.info(f"   Files: {len(data.get('files', {}))}")
                    return data
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Netlify generation failed: {response.status} - {error_text}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"❌ Netlify generation timed out")
            return None
        except Exception as e:
            logger.error(f"❌ Netlify generation error: {e}")
            return None

async def main():
    """Main test runner"""
    logger.info("🚀 Starting Simple Backend Test")
    
    # Test basic endpoints
    session_id = await test_basic_endpoints()
    
    if session_id:
        # Test Netlify generation
        result = await test_netlify_generation_only(session_id)
        
        if result:
            logger.info("🎉 Basic tests passed!")
            return 0
        else:
            logger.error("💥 Netlify generation failed!")
            return 1
    else:
        logger.error("💥 Basic endpoint tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)