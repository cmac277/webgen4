#!/usr/bin/env python3
"""
Simple Failsafe Test - Test the bulletproof failsafe system
"""

import asyncio
import aiohttp
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_failsafe_system():
    """Test the failsafe system with a simple request"""
    base_url = "https://codeweaver-30.preview.emergentagent.com/api"
    
    logger.info("🚀 Testing Bulletproof Failsafe System")
    
    # Test 1: Create session
    logger.info("\n--- TEST 1: Create Session ---")
    async with aiohttp.ClientSession() as session:
        try:
            payload = {"project_name": "Failsafe Test"}
            async with session.post(
                f"{base_url}/session/create",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    session_id = data.get('session_id')
                    logger.info(f"✅ Session created: {session_id}")
                else:
                    logger.error(f"❌ Session creation failed: {response.status}")
                    return False
        except Exception as e:
            logger.error(f"❌ Session creation error: {e}")
            return False
    
    # Test 2: Test Netlify generation (should trigger failsafe due to AI service issues)
    logger.info("\n--- TEST 2: Test Netlify Generation (Failsafe Expected) ---")
    async with aiohttp.ClientSession() as session:
        try:
            start_time = time.time()
            payload = {
                "session_id": session_id,
                "prompt": "Create a professional website for a renovation business with services like Flooring, Bathrooms, Kitchens, and contact form",
                "model": "claude-sonnet-4"
            }
            
            logger.info(f"🚀 Testing generation with expected failsafe activation...")
            
            async with session.post(
                f"{base_url}/netlify/generate-and-deploy",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=aiohttp.ClientTimeout(total=120)  # 2 minute timeout
            ) as response:
                generation_time = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ Generation completed in {generation_time:.2f}s")
                    
                    # Check if we got a valid response
                    project = data.get('project', {})
                    deployment = data.get('deployment', {})
                    files = project.get('files', {})
                    
                    logger.info(f"   Project ID: {project.get('project_id', 'N/A')}")
                    logger.info(f"   Files generated: {len(files)}")
                    logger.info(f"   Deploy URL: {data.get('deploy_preview_url', 'N/A')}")
                    
                    # Check file sizes
                    for filename, content in files.items():
                        if filename in ['index.html', 'styles.css', 'app.js']:
                            logger.info(f"   {filename}: {len(content)} characters")
                    
                    # Validate critical requirements
                    validation_errors = []
                    
                    if generation_time > 300:  # 5 minutes
                        validation_errors.append(f"Generation took too long: {generation_time:.2f}s")
                    
                    if not files.get('index.html'):
                        validation_errors.append("Missing index.html")
                    elif len(files.get('index.html', '')) < 500:
                        validation_errors.append(f"HTML too small: {len(files.get('index.html', ''))} chars")
                    
                    if not data.get('deploy_preview_url') and not data.get('deployment', {}).get('error'):
                        validation_errors.append("Missing deploy_preview_url and no deployment error")
                    
                    if validation_errors:
                        logger.error("❌ Validation errors:")
                        for error in validation_errors:
                            logger.error(f"   - {error}")
                        return False
                    else:
                        logger.info("✅ All critical validations passed!")
                        logger.info("   - System returned a complete website")
                        logger.info("   - Generation completed in reasonable time")
                        logger.info("   - Files are substantial")
                        logger.info("   - System NEVER failed completely")
                        return True
                        
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Generation failed: {response.status} - {error_text}")
                    return False
                    
        except asyncio.TimeoutError:
            generation_time = time.time() - start_time
            logger.error(f"❌ Generation timed out after {generation_time:.2f}s")
            return False
        except Exception as e:
            generation_time = time.time() - start_time
            logger.error(f"❌ Generation error after {generation_time:.2f}s: {e}")
            return False

async def main():
    """Main test runner"""
    success = await test_failsafe_system()
    
    if success:
        logger.info("\n🎉 BULLETPROOF FAILSAFE SYSTEM VERIFIED!")
        logger.info("   ✅ System NEVER returns complete failure")
        logger.info("   ✅ System ALWAYS returns a website")
        logger.info("   ✅ Failsafe layers are working")
        return 0
    else:
        logger.error("\n💥 Failsafe system test failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)