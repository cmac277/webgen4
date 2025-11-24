#!/usr/bin/env python3
"""
Debug test to see what's actually being generated
"""

import asyncio
import aiohttp
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def debug_generation():
    """Debug what's being generated"""
    base_url = "https://codeweaver-30.preview.emergentagent.com/api"
    
    async with aiohttp.ClientSession() as session:
        # Create session
        logger.info("Creating session...")
        async with session.post(
            f"{base_url}/session/create",
            json={"project_name": "Debug Test"},
            headers={"Content-Type": "application/json"}
        ) as response:
            data = await response.json()
            session_id = data.get('session_id')
            logger.info(f"✅ Created session: {session_id}")
        
        # Generate website
        logger.info("Generating website...")
        async with session.post(
            f"{base_url}/generate/website",
            json={
                "session_id": session_id,
                "prompt": "Create a fitness app landing page",
                "model": "gpt-5",
                "framework": "html"
            },
            headers={"Content-Type": "application/json"},
            timeout=aiohttp.ClientTimeout(total=180)
        ) as response:
            data = await response.json()
            html_content = data.get('html_content', '')
            
            logger.info(f"HTML length: {len(html_content)} chars")
            
            # Extract title
            title_start = html_content.find('<title>')
            if title_start != -1:
                title_end = html_content.find('</title>', title_start)
                if title_end != -1:
                    title = html_content[title_start + 7:title_end]
                    logger.info(f"Title: {title}")
            
            # Check first 1000 chars
            logger.info("First 1000 chars of HTML:")
            logger.info(html_content[:1000])
            
            # Check for common sections
            sections = ['hero', 'features', 'pricing', 'contact', 'footer', 'video', 'tube']
            for section in sections:
                if section in html_content.lower():
                    logger.info(f"✅ Found: {section}")
                else:
                    logger.info(f"❌ Missing: {section}")

async def main():
    await debug_generation()

if __name__ == "__main__":
    asyncio.run(main())