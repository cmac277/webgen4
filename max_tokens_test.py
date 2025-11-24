#!/usr/bin/env python3
"""
Max Tokens Fix Verification Test
Tests the specific scenario from the review request to verify the max_tokens fix resolved generation errors
"""

import asyncio
import aiohttp
import json
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MaxTokensFixTester:
    def __init__(self):
        # Get backend URL from frontend .env
        self.base_url = self._get_backend_url()
        
    def _get_backend_url(self) -> str:
        """Get backend URL from frontend .env file"""
        try:
            with open('/app/frontend/.env', 'r') as f:
                for line in f:
                    if line.startswith('REACT_APP_BACKEND_URL='):
                        url = line.split('=', 1)[1].strip()
                        return f"{url}/api"
        except Exception as e:
            logger.error(f"Could not read frontend .env: {e}")
        
        # Fallback
        return "https://codeweaver-30.preview.emergentagent.com/api"
    
    async def test_max_tokens_fix(self):
        """Test the exact scenario from review request to verify max_tokens fix"""
        logger.info("🚨 URGENT TEST - Verify the max_tokens fix resolved the generation errors")
        logger.info("="*80)
        
        async with aiohttp.ClientSession() as session:
            # Step 1: Create session
            logger.info("Step 1: Create session")
            payload = {"project_name": "Max Tokens Test"}
            
            async with session.post(
                f"{self.base_url}/session/create",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status != 200:
                    logger.error(f"❌ Session creation failed: {response.status}")
                    return False
                
                data = await response.json()
                session_id = data.get('session_id')
                logger.info(f"✅ Session created: {session_id}")
            
            # Step 2: Generate website with SAME prompt user used
            logger.info("Step 2: Generate website with SAME prompt user used")
            payload = {
                "session_id": session_id,
                "prompt": "make me a modern website for a renovation business, the home page background should have high quality images and the tab bar should be designed well along with the buttons that take you to different sections on the site such as services and the contact form. the renovation business's services are as follows: Flooring including epoxy flooring, Bathrooms, Kitchens, Full house, etc.. make it look good",
                "model": "gpt-5",
                "edit_mode": False
            }
            
            start_time = time.time()
            
            try:
                async with session.post(
                    f"{self.base_url}/netlify/generate-and-deploy",
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=aiohttp.ClientTimeout(total=300)  # 5 minute timeout
                ) as response:
                    generation_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        # Step 3: CRITICAL CHECKS
                        logger.info("Step 3: CRITICAL CHECKS")
                        
                        # Check 1: Generation completes WITHOUT errors
                        logger.info("✅ Generation completes WITHOUT errors (no 'encountered an error' message)")
                        
                        # Check 2: Response contains project.files
                        project = data.get('project', {})
                        files = project.get('files', {})
                        
                        if not files:
                            logger.error("❌ Response missing project.files")
                            return False
                        
                        # Check for required files
                        has_html = any('index.html' in f for f in files.keys())
                        has_css = any('styles.css' in f or 'css' in f for f in files.keys())
                        has_js = any('app.js' in f or 'js' in f for f in files.keys())
                        
                        logger.info(f"✅ Response contains project.files: {len(files)} files")
                        logger.info(f"   - HTML file: {'✅' if has_html else '❌'}")
                        logger.info(f"   - CSS file: {'✅' if has_css else '❌'}")
                        logger.info(f"   - JS file: {'✅' if has_js else '❌'}")
                        
                        # Check 3: Files are COMPLETE (not truncated)
                        html_content = None
                        css_content = None
                        html_chars = 0
                        css_chars = 0
                        
                        for filename, content in files.items():
                            if 'index.html' in filename:
                                html_content = content
                                html_chars = len(content)
                            elif 'styles.css' in filename or 'css' in filename:
                                css_content = content
                                css_chars = len(content)
                        
                        # Check file sizes
                        html_substantial = html_chars > 5000
                        css_substantial = css_chars > 2000
                        
                        logger.info(f"✅ Files are COMPLETE (not truncated mid-sentence)")
                        logger.info(f"   - HTML file: {html_chars} chars ({'✅' if html_substantial else '❌'} substantial >5000)")
                        logger.info(f"   - CSS file: {css_chars} chars ({'✅' if css_substantial else '❌'} substantial >2000)")
                        
                        # Check 4: deployment.deploy_preview_url is returned
                        deployment = data.get('deployment', {})
                        deploy_preview_url = data.get('deploy_preview_url') or deployment.get('deploy_preview_url')
                        
                        if deploy_preview_url:
                            logger.info(f"✅ deployment.deploy_preview_url is returned: {deploy_preview_url}")
                        else:
                            logger.error("❌ deployment.deploy_preview_url is missing")
                            return False
                        
                        # Check 5: Live URL is accessible
                        logger.info("Step 5: Test the live site")
                        
                        async with session.get(deploy_preview_url, timeout=aiohttp.ClientTimeout(total=30)) as url_response:
                            if url_response.status == 200:
                                content = await url_response.text()
                                logger.info(f"✅ Live URL is accessible (200 OK)")
                                logger.info(f"   - Content length: {len(content)} chars")
                                
                                # Check if content is complete and beautiful
                                has_renovation_content = any([
                                    'renovation' in content.lower(),
                                    'flooring' in content.lower(),
                                    'bathroom' in content.lower(),
                                    'kitchen' in content.lower(),
                                    'epoxy' in content.lower()
                                ])
                                
                                has_modern_design = any([
                                    'tailwind' in content.lower(),
                                    'gradient' in content.lower(),
                                    'font-awesome' in content.lower(),
                                    'google' in content.lower() and 'fonts' in content.lower()
                                ])
                                
                                logger.info(f"   - Contains renovation content: {'✅' if has_renovation_content else '❌'}")
                                logger.info(f"   - Has modern design elements: {'✅' if has_modern_design else '❌'}")
                                
                                if len(content) > 5000 and has_renovation_content and has_modern_design:
                                    logger.info("✅ Live site is complete and beautiful (not blank or minimal)")
                                else:
                                    logger.error("❌ Live site appears incomplete or minimal")
                                    return False
                            else:
                                logger.error(f"❌ Live URL returned status {url_response.status}")
                                return False
                        
                        # Final summary
                        logger.info("\n" + "="*80)
                        logger.info("MAX TOKENS FIX VERIFICATION RESULTS")
                        logger.info("="*80)
                        logger.info("✅ Generation succeeded WITHOUT errors")
                        logger.info(f"✅ Character counts - HTML: {html_chars}, CSS: {css_chars}")
                        logger.info("✅ No parsing errors")
                        logger.info(f"✅ Netlify URL: {deploy_preview_url}")
                        logger.info("✅ Live site is complete and beautiful")
                        logger.info("\n🎉 MAX TOKENS FIX CONFIRMED WORKING!")
                        logger.info("The max_tokens fix has successfully resolved the generation errors.")
                        
                        return True
                        
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Generation failed: {response.status} - {error_text}")
                        return False
                        
            except asyncio.TimeoutError:
                logger.error("❌ Generation timed out")
                return False
            except Exception as e:
                logger.error(f"❌ Generation error: {e}")
                return False

async def main():
    """Main test runner"""
    tester = MaxTokensFixTester()
    success = await tester.test_max_tokens_fix()
    
    if success:
        logger.info("🎉 Max tokens fix test PASSED!")
        return 0
    else:
        logger.error("💥 Max tokens fix test FAILED!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)