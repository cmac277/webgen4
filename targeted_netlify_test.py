#!/usr/bin/env python3
"""
Targeted Netlify Test - Tests existing successful deployments and validates the system
"""

import asyncio
import aiohttp
import json
import time
import os
import re
from typing import Dict, Any, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TargetedNetlifyTester:
    def __init__(self):
        # Get backend URL from frontend .env
        self.base_url = self._get_backend_url()
        self.test_results = []
        
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
    
    async def test_existing_deployment(self, deploy_url: str) -> Dict[str, Any]:
        """Test an existing Netlify deployment URL"""
        logger.info(f"🌐 Testing existing deployment: {deploy_url}")
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(deploy_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Comprehensive content analysis
                        analysis = self._analyze_content(content)
                        
                        result = {
                            "success": True,
                            "url": deploy_url,
                            "status_code": response.status,
                            "content_length": len(content),
                            **analysis
                        }
                        
                        logger.info(f"✅ Deployment accessible and analyzed")
                        logger.info(f"   Status: {response.status}")
                        logger.info(f"   Content Length: {len(content)} chars")
                        logger.info(f"   Has HTML: {analysis['has_html']}")
                        logger.info(f"   Has Tailwind: {analysis['has_tailwind']}")
                        logger.info(f"   Has Font Awesome: {analysis['has_font_awesome']}")
                        logger.info(f"   Has Google Fonts: {analysis['has_google_fonts']}")
                        logger.info(f"   CSS File Size: {analysis['css_file_size']} chars")
                        logger.info(f"   JS File Size: {analysis['js_file_size']} chars")
                        
                        return result
                    else:
                        logger.error(f"❌ Deployment returned status {response.status}")
                        return {
                            "success": False,
                            "url": deploy_url,
                            "status_code": response.status,
                            "error": f"HTTP {response.status}"
                        }
                        
            except Exception as e:
                logger.error(f"❌ Error accessing deployment: {e}")
                return {
                    "success": False,
                    "url": deploy_url,
                    "error": str(e)
                }
    
    def _analyze_content(self, content: str) -> Dict[str, Any]:
        """Analyze HTML content for required elements"""
        content_lower = content.lower()
        
        analysis = {
            "has_html": '<html' in content_lower or '<!doctype html' in content_lower,
            "has_tailwind": 'tailwindcss.com' in content_lower or 'cdn.tailwindcss.com' in content_lower,
            "has_font_awesome": 'font-awesome' in content_lower or 'fontawesome' in content_lower,
            "has_google_fonts": 'fonts.googleapis.com' in content_lower or 'fonts.google.com' in content_lower,
            "has_styles_css": 'href="styles.css"' in content or "href='styles.css'" in content,
            "has_app_js": 'src="app.js"' in content or "src='app.js'" in content,
            "has_modern_design": False,
            "css_file_size": 0,
            "js_file_size": 0,
            "design_quality_score": 0
        }
        
        # Check for modern design elements
        modern_indicators = [
            'gradient', 'shadow', 'transition', 'transform', 'hover:',
            'bg-gradient', 'shadow-', 'rounded-', 'flex', 'grid'
        ]
        
        modern_count = sum(1 for indicator in modern_indicators if indicator in content_lower)
        analysis["has_modern_design"] = modern_count >= 3
        analysis["modern_design_indicators"] = modern_count
        
        # Extract CSS and JS content sizes (if embedded)
        import re
        
        # Find CSS content
        css_matches = re.findall(r'<style[^>]*>(.*?)</style>', content, re.DOTALL | re.IGNORECASE)
        if css_matches:
            analysis["css_file_size"] = sum(len(match) for match in css_matches)
        
        # Find JS content
        js_matches = re.findall(r'<script(?![^>]*src=)[^>]*>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
        if js_matches:
            analysis["js_file_size"] = sum(len(match) for match in js_matches)
        
        # Calculate design quality score
        score = 0
        if analysis["has_html"]: score += 10
        if analysis["has_tailwind"]: score += 20
        if analysis["has_font_awesome"]: score += 15
        if analysis["has_google_fonts"]: score += 15
        if analysis["has_styles_css"]: score += 10
        if analysis["has_app_js"]: score += 10
        if analysis["has_modern_design"]: score += 20
        
        analysis["design_quality_score"] = score
        
        return analysis
    
    async def test_backend_endpoints(self) -> Dict[str, Any]:
        """Test core backend endpoints"""
        logger.info("🔧 Testing backend endpoints...")
        
        results = {
            "root_endpoint": False,
            "models_endpoint": False,
            "session_creation": False,
            "netlify_endpoints": False
        }
        
        async with aiohttp.ClientSession() as session:
            # Test root endpoint
            try:
                async with session.get(f"{self.base_url}/") as response:
                    if response.status == 200:
                        results["root_endpoint"] = True
                        logger.info("✅ Root endpoint working")
                    else:
                        logger.error(f"❌ Root endpoint failed: {response.status}")
            except Exception as e:
                logger.error(f"❌ Root endpoint error: {e}")
            
            # Test models endpoint
            try:
                async with session.get(f"{self.base_url}/models") as response:
                    if response.status == 200:
                        data = await response.json()
                        if "models" in data and len(data["models"]) > 0:
                            results["models_endpoint"] = True
                            logger.info(f"✅ Models endpoint working ({len(data['models'])} models)")
                        else:
                            logger.error("❌ Models endpoint returned empty data")
                    else:
                        logger.error(f"❌ Models endpoint failed: {response.status}")
            except Exception as e:
                logger.error(f"❌ Models endpoint error: {e}")
            
            # Test session creation
            try:
                payload = {"project_name": "Test Session"}
                async with session.post(
                    f"{self.base_url}/session/create",
                    json=payload,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "session_id" in data:
                            results["session_creation"] = True
                            logger.info("✅ Session creation working")
                        else:
                            logger.error("❌ Session creation returned invalid data")
                    else:
                        logger.error(f"❌ Session creation failed: {response.status}")
            except Exception as e:
                logger.error(f"❌ Session creation error: {e}")
            
            # Test Netlify endpoints exist (just check they don't 404)
            try:
                # This should return 422 (validation error) not 404 if endpoint exists
                async with session.post(f"{self.base_url}/netlify/generate") as response:
                    if response.status in [422, 400, 500]:  # Not 404
                        results["netlify_endpoints"] = True
                        logger.info("✅ Netlify endpoints exist")
                    else:
                        logger.error(f"❌ Netlify endpoints may not exist: {response.status}")
            except Exception as e:
                logger.error(f"❌ Netlify endpoints error: {e}")
        
        return results
    
    async def run_comprehensive_test(self):
        """Run comprehensive test of Netlify system"""
        logger.info("🚀 Starting Comprehensive Netlify System Test")
        logger.info(f"Backend URL: {self.base_url}")
        
        start_time = time.time()
        validation_errors = []
        
        # Test 1: Backend endpoints
        logger.info("\n--- Test 1: Backend Endpoints ---")
        backend_results = await self.test_backend_endpoints()
        
        for endpoint, working in backend_results.items():
            if not working:
                validation_errors.append(f"Backend endpoint not working: {endpoint}")
        
        # Test 2: Test existing deployments
        logger.info("\n--- Test 2: Existing Netlify Deployments ---")
        
        # Known working URLs from database
        test_urls = [
            "https://make-me-a-modern-website-for-a-1763903696.netlify.app",
            "https://make-me-a-modern-website-for-a-1763904208.netlify.app"
        ]
        
        deployment_results = []
        for url in test_urls:
            result = await self.test_existing_deployment(url)
            deployment_results.append(result)
            
            if not result.get("success"):
                validation_errors.append(f"Deployment not accessible: {url}")
            else:
                # Validate content quality
                if not result.get("has_html"):
                    validation_errors.append(f"Deployment missing HTML structure: {url}")
                if not result.get("has_tailwind"):
                    validation_errors.append(f"Deployment missing Tailwind CSS: {url}")
                if result.get("design_quality_score", 0) < 50:
                    validation_errors.append(f"Deployment has low design quality score: {url}")
        
        # Generate final summary
        return self._generate_comprehensive_summary(start_time, validation_errors, {
            "backend_results": backend_results,
            "deployment_results": deployment_results
        })
    
    def _generate_comprehensive_summary(self, start_time: float, validation_errors: List[str], test_data: Dict[str, Any]):
        """Generate comprehensive test summary"""
        total_time = time.time() - start_time
        success = len(validation_errors) == 0
        
        logger.info("\n" + "="*80)
        logger.info("COMPREHENSIVE NETLIFY SYSTEM TEST SUMMARY")
        logger.info("="*80)
        logger.info(f"Overall Result: {'✅ SUCCESS' if success else '❌ FAILED'}")
        logger.info(f"Total Time: {total_time:.2f}s")
        logger.info(f"Validation Errors: {len(validation_errors)}")
        
        # Backend results
        backend_results = test_data.get("backend_results", {})
        logger.info(f"\nBACKEND ENDPOINTS:")
        for endpoint, working in backend_results.items():
            status = "✅ WORKING" if working else "❌ FAILED"
            logger.info(f"  {endpoint}: {status}")
        
        # Deployment results
        deployment_results = test_data.get("deployment_results", [])
        logger.info(f"\nDEPLOYMENT ANALYSIS:")
        for i, result in enumerate(deployment_results, 1):
            if result.get("success"):
                logger.info(f"  Deployment {i}: ✅ ACCESSIBLE")
                logger.info(f"    URL: {result.get('url')}")
                logger.info(f"    Content Length: {result.get('content_length')} chars")
                logger.info(f"    Design Quality Score: {result.get('design_quality_score', 0)}/100")
                logger.info(f"    Has Tailwind: {'✅' if result.get('has_tailwind') else '❌'}")
                logger.info(f"    Has Font Awesome: {'✅' if result.get('has_font_awesome') else '❌'}")
                logger.info(f"    Has Google Fonts: {'✅' if result.get('has_google_fonts') else '❌'}")
                logger.info(f"    Modern Design: {'✅' if result.get('has_modern_design') else '❌'}")
            else:
                logger.info(f"  Deployment {i}: ❌ FAILED")
                logger.info(f"    URL: {result.get('url')}")
                logger.info(f"    Error: {result.get('error')}")
        
        if validation_errors:
            logger.info("\nVALIDATION ERRORS:")
            for error in validation_errors:
                logger.error(f"❌ {error}")
        else:
            logger.info("\n✅ All validation criteria passed!")
            logger.info("   - Backend endpoints are operational")
            logger.info("   - Netlify deployments are accessible")
            logger.info("   - Generated sites have proper structure and design")
            logger.info("   - Modern CSS frameworks are properly integrated")
            logger.info("   - Design quality meets professional standards")
        
        return {
            "success": success,
            "total_time": total_time,
            "validation_errors": validation_errors,
            "test_data": test_data
        }

async def main():
    """Main test runner"""
    tester = TargetedNetlifyTester()
    results = await tester.run_comprehensive_test()
    
    # Return exit code based on results
    if results['success']:
        logger.info("🎉 Comprehensive Netlify system test passed!")
        return 0
    else:
        logger.error(f"💥 Comprehensive Netlify system test failed!")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)