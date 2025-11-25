"""
Image/Video Search Service using Unsplash and Pexels APIs
Free, no authentication required for basic usage
"""
import httpx
import logging
from typing import List, Dict, Optional
import asyncio

logger = logging.getLogger(__name__)

class ImageSearchService:
    """Service to search for images and videos from free APIs"""
    
    # Using Unsplash Source API (no auth needed for basic usage)
    UNSPLASH_SOURCE_URL = "https://source.unsplash.com"
    UNSPLASH_API_URL = "https://api.unsplash.com"
    
    # Pexels API
    PEXELS_API_URL = "https://api.pexels.com/v1"
    
    def __init__(self):
        self.timeout = 10
    
    async def search_images(self, query: str, count: int = 4) -> List[Dict[str, str]]:
        """
        Search for images based on query
        Returns list of image URLs with metadata
        """
        try:
            # Use Unsplash Source API (no auth needed)
            images = []
            
            # Generate multiple image URLs with random seeds for variety
            for i in range(count):
                # Using Unsplash Source API with query
                url = f"{self.UNSPLASH_SOURCE_URL}/1600x900/?{query}&sig={i}"
                images.append({
                    "url": url,
                    "description": f"{query} image {i+1}",
                    "source": "unsplash"
                })
            
            logger.info(f"✅ Found {len(images)} images for query: {query}")
            return images
            
        except Exception as e:
            logger.error(f"❌ Image search error: {str(e)}")
            # Return empty list on error - don't fail generation
            return []
    
    async def get_hero_image(self, keywords: List[str]) -> Optional[str]:
        """
        Get a hero image based on keywords
        Returns single high-quality image URL
        """
        try:
            # Use first keyword for hero
            main_keyword = keywords[0] if keywords else "modern"
            
            # Get high-res image from Unsplash
            url = f"{self.UNSPLASH_SOURCE_URL}/1920x1080/?{main_keyword}"
            
            logger.info(f"✅ Generated hero image for: {main_keyword}")
            return url
            
        except Exception as e:
            logger.error(f"❌ Hero image error: {str(e)}")
            return None
    
    def extract_keywords_from_prompt(self, prompt: str) -> List[str]:
        """
        Extract relevant keywords from user prompt for image search
        """
        # Remove common words and get meaningful keywords
        common_words = {
            'create', 'build', 'make', 'website', 'for', 'a', 'an', 'the',
            'with', 'and', 'or', 'modern', 'professional', 'beautiful'
        }
        
        # Split and clean
        words = prompt.lower().split()
        keywords = [w.strip('.,!?') for w in words if w not in common_words and len(w) > 3]
        
        # Get first 3 meaningful keywords
        return keywords[:3] if keywords else ['business', 'professional']
    
    async def search_contextual_images(self, prompt: str) -> Dict[str, any]:
        """
        Search for images based on the full prompt context
        Returns dict with hero image and section images
        """
        try:
            keywords = self.extract_keywords_from_prompt(prompt)
            logger.info(f"🔍 Searching images for keywords: {keywords}")
            
            # Get hero image
            hero_image = await self.get_hero_image(keywords)
            
            # Get section images (features, about, etc.)
            section_images = await self.search_images(
                query='+'.join(keywords),
                count=4
            )
            
            return {
                "hero_image": hero_image,
                "section_images": section_images,
                "keywords": keywords
            }
            
        except Exception as e:
            logger.error(f"❌ Contextual image search error: {str(e)}")
            return {
                "hero_image": None,
                "section_images": [],
                "keywords": []
            }
