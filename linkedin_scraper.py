"""
LinkedIn Profile Scraper Module
Extracts candidate information from LinkedIn profile URLs
"""

import re
import requests
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from urllib.parse import urlparse
import time
import random

# Web scraping libraries
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LinkedInProfile:
    """Represents a LinkedIn profile data"""
    full_name: str = ""
    email: str = ""
    linkedin_url: str = ""
    location: str = ""
    current_company: str = ""
    current_position: str = ""
    headline: str = ""
    about: str = ""
    skills: List[str] = None
    experience: List[Dict[str, str]] = None
    education: List[Dict[str, str]] = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []
        if self.experience is None:
            self.experience = []
        if self.education is None:
            self.education = []

class LinkedInScraper:
    """LinkedIn profile scraper with multiple strategies"""
    
    def __init__(self):
        self.setup_session()
        
    def setup_session(self):
        """Setup requests session with proper headers"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def extract_profile_info(self, linkedin_url: str) -> LinkedInProfile:
        """
        Extract information from LinkedIn profile URL
        
        Args:
            linkedin_url: LinkedIn profile URL
            
        Returns:
            LinkedInProfile object with extracted information
        """
        profile = LinkedInProfile()
        profile.linkedin_url = self.normalize_linkedin_url(linkedin_url)
        
        if not self.is_valid_linkedin_url(linkedin_url):
            logger.error("Invalid LinkedIn URL format")
            return profile
        
        try:
            # Try different extraction methods
            success = False
            
            # Method 1: Try basic web scraping (often blocked)
            if not success:
                try:
                    profile = self.scrape_with_requests(profile)
                    if profile.full_name:
                        success = True
                        logger.info("Successfully scraped with requests method")
                except Exception as e:
                    logger.warning(f"Requests method failed: {e}")
            
            # Method 2: Try with Selenium (more reliable but slower)
            if not success and SELENIUM_AVAILABLE:
                try:
                    profile = self.scrape_with_selenium(profile)
                    if profile.full_name:
                        success = True
                        logger.info("Successfully scraped with Selenium method")
                except Exception as e:
                    logger.warning(f"Selenium method failed: {e}")
            
            # Method 3: Extract from URL pattern (limited info)
            if not success:
                profile = self.extract_from_url_pattern(profile)
                logger.info("Using URL pattern extraction (limited info)")
            
            return profile
            
        except Exception as e:
            logger.error(f"Error extracting LinkedIn profile: {e}")
            return profile
    
    def scrape_with_requests(self, profile: LinkedInProfile) -> LinkedInProfile:
        """Attempt to scrape using requests (often blocked by LinkedIn)"""
        try:
            # Add random delay to avoid rate limiting
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(profile.linkedin_url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"HTTP {response.status_code} response from LinkedIn")
                return profile
            
            if not BS4_AVAILABLE:
                logger.warning("BeautifulSoup not available for HTML parsing")
                return profile
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract name from title or meta tags
            title = soup.find('title')
            if title and title.text:
                # LinkedIn titles often have format "Name | LinkedIn"
                name_match = re.search(r'^([^|]+)', title.text.strip())
                if name_match:
                    profile.full_name = name_match.group(1).strip()
            
            # Try to extract other information from meta tags
            for meta in soup.find_all('meta'):
                property_name = meta.get('property', '')
                content = meta.get('content', '')
                
                if 'og:title' in property_name and content:
                    if not profile.full_name:
                        profile.full_name = content.split('|')[0].strip()
                elif 'og:description' in property_name and content:
                    profile.headline = content[:200]
            
            return profile
            
        except Exception as e:
            logger.error(f"Requests scraping failed: {e}")
            return profile
    
    def scrape_with_selenium(self, profile: LinkedInProfile) -> LinkedInProfile:
        """Attempt to scrape using Selenium (more reliable but requires Chrome)"""
        if not SELENIUM_AVAILABLE:
            logger.warning("Selenium not available")
            return profile
        
        driver = None
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Run in background
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Initialize driver
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(15)
            
            # Navigate to LinkedIn profile
            driver.get(profile.linkedin_url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extract information
            try:
                # Extract name
                name_selectors = [
                    'h1.text-heading-xlarge',
                    'h1.top-card-layout__title',
                    '.pv-text-details__left-panel h1'
                ]
                
                for selector in name_selectors:
                    try:
                        name_element = driver.find_element(By.CSS_SELECTOR, selector)
                        if name_element and name_element.text.strip():
                            profile.full_name = name_element.text.strip()
                            break
                    except:
                        continue
                
                # Extract headline/current position
                headline_selectors = [
                    '.text-body-medium.break-words',
                    '.top-card-layout__headline',
                    '.pv-text-details__left-panel .text-body-medium'
                ]
                
                for selector in headline_selectors:
                    try:
                        headline_element = driver.find_element(By.CSS_SELECTOR, selector)
                        if headline_element and headline_element.text.strip():
                            profile.headline = headline_element.text.strip()
                            profile.current_position = headline_element.text.strip()
                            break
                    except:
                        continue
                
                # Extract location
                location_selectors = [
                    '.text-body-small.inline.t-black--light.break-words',
                    '.top-card-layout__first-subline',
                    '.pv-text-details__left-panel .text-body-small'
                ]
                
                for selector in location_selectors:
                    try:
                        location_element = driver.find_element(By.CSS_SELECTOR, selector)
                        if location_element and location_element.text.strip():
                            text = location_element.text.strip()
                            # Filter out non-location text
                            if any(indicator in text.lower() for indicator in ['city', 'state', 'country', ',']):
                                profile.location = text
                                break
                    except:
                        continue
                
            except Exception as e:
                logger.warning(f"Error extracting specific elements: {e}")
            
            return profile
            
        except Exception as e:
            logger.error(f"Selenium scraping failed: {e}")
            return profile
        
        finally:
            if driver:
                driver.quit()
    
    def extract_from_url_pattern(self, profile: LinkedInProfile) -> LinkedInProfile:
        """Extract basic info from LinkedIn URL pattern"""
        try:
            # Extract username from URL
            url_parts = profile.linkedin_url.split('/')
            username = None
            
            for i, part in enumerate(url_parts):
                if part == 'in' and i + 1 < len(url_parts):
                    username = url_parts[i + 1]
                    break
            
            if username:
                # Try to convert username to readable name
                # Remove common suffixes
                username = re.sub(r'-\d+$', '', username)  # Remove trailing numbers
                username = username.replace('-', ' ')
                username = username.replace('_', ' ')
                
                # Capitalize words
                name_parts = username.split()
                capitalized_parts = [part.capitalize() for part in name_parts if part.isalpha()]
                
                if len(capitalized_parts) >= 2:
                    profile.full_name = ' '.join(capitalized_parts[:3])  # Limit to 3 parts
            
            return profile
            
        except Exception as e:
            logger.error(f"URL pattern extraction failed: {e}")
            return profile
    
    def is_valid_linkedin_url(self, url: str) -> bool:
        """Validate LinkedIn URL format"""
        if not url:
            return False
        
        # Normalize URL
        url = self.normalize_linkedin_url(url)
        
        # Check if it's a LinkedIn profile URL
        linkedin_pattern = re.compile(
            r'^https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+/?$',
            re.IGNORECASE
        )
        
        return bool(linkedin_pattern.match(url))
    
    def normalize_linkedin_url(self, url: str) -> str:
        """Normalize LinkedIn URL format"""
        if not url:
            return ""
        
        # Add https if missing
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Parse URL
        parsed = urlparse(url)
        
        # Ensure it's linkedin.com
        if 'linkedin.com' not in parsed.netloc.lower():
            return url  # Return as-is if not LinkedIn
        
        # Reconstruct clean URL
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) >= 2 and path_parts[0] == 'in':
            username = path_parts[1]
            # Remove any query parameters or extra parts
            username = re.sub(r'[^A-Za-z0-9_-]', '', username)
            return f"https://www.linkedin.com/in/{username}"
        
        return url
    
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from any text content"""
        if not text:
            return []
        
        # Common technical skills to look for
        common_skills = [
            'Python', 'Java', 'JavaScript', 'C++', 'C#', 'Ruby', 'PHP', 'Go', 'Rust', 'Swift',
            'React', 'Angular', 'Vue.js', 'Node.js', 'Django', 'Flask', 'Spring', 'Laravel',
            'HTML', 'CSS', 'TypeScript', 'SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis',
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Jenkins', 'Git', 'Linux',
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'Pandas', 'NumPy',
            'REST API', 'GraphQL', 'Microservices', 'DevOps', 'CI/CD', 'Agile', 'Scrum'
        ]
        
        found_skills = []
        text_lower = text.lower()
        
        for skill in common_skills:
            if skill.lower() in text_lower:
                # Check if it's a whole word match
                if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
                    found_skills.append(skill)
        
        return found_skills[:15]  # Limit to 15 skills

class LinkedInAPIClient:
    """
    LinkedIn API client for official data access
    Note: Requires LinkedIn API credentials and approval
    """
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
    
    def get_profile_by_url(self, linkedin_url: str) -> LinkedInProfile:
        """
        Get profile information using LinkedIn API
        Note: This requires proper LinkedIn API access and user consent
        """
        profile = LinkedInProfile()
        profile.linkedin_url = linkedin_url
        
        # This is a placeholder for actual LinkedIn API implementation
        # Real implementation would require:
        # 1. LinkedIn API credentials
        # 2. OAuth authentication flow
        # 3. Proper API endpoints
        
        logger.warning("LinkedIn API integration requires proper credentials and user consent")
        return profile

class LinkedInProfileExtractor:
    """Main class that combines different extraction methods"""
    
    def __init__(self, use_selenium: bool = False, api_client: LinkedInAPIClient = None):
        self.scraper = LinkedInScraper()
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.api_client = api_client
        
    def extract_profile(self, linkedin_url: str) -> LinkedInProfile:
        """
        Extract profile information using best available method
        
        Args:
            linkedin_url: LinkedIn profile URL
            
        Returns:
            LinkedInProfile object with extracted information
        """
        try:
            # Validate URL
            if not self.scraper.is_valid_linkedin_url(linkedin_url):
                logger.error("Invalid LinkedIn URL format")
                return LinkedInProfile(linkedin_url=linkedin_url)
            
            # Try API first if available
            if self.api_client and self.api_client.access_token:
                try:
                    profile = self.api_client.get_profile_by_url(linkedin_url)
                    if profile.full_name:
                        return profile
                except Exception as e:
                    logger.warning(f"API method failed: {e}")
            
            # Try scraping methods
            profile = self.scraper.extract_profile_info(linkedin_url)
            
            return profile
            
        except Exception as e:
            logger.error(f"Profile extraction failed: {e}")
            return LinkedInProfile(linkedin_url=linkedin_url)
    
    def extract_basic_info_from_url(self, linkedin_url: str) -> Dict[str, str]:
        """
        Extract basic information that can be inferred from URL
        This is a fallback when scraping fails
        """
        try:
            normalized_url = self.scraper.normalize_linkedin_url(linkedin_url)
            
            # Extract username
            username = ""
            url_parts = normalized_url.split('/')
            for i, part in enumerate(url_parts):
                if part == 'in' and i + 1 < len(url_parts):
                    username = url_parts[i + 1]
                    break
            
            # Convert username to potential name
            name = ""
            if username:
                name_parts = username.replace('-', ' ').replace('_', ' ').split()
                name_parts = [part.capitalize() for part in name_parts if part.isalpha()]
                if len(name_parts) >= 2:
                    name = ' '.join(name_parts[:3])
            
            return {
                'full_name': name,
                'linkedin_url': normalized_url,
                'extracted_method': 'url_pattern'
            }
            
        except Exception as e:
            logger.error(f"URL pattern extraction failed: {e}")
            return {
                'linkedin_url': linkedin_url,
                'extracted_method': 'failed'
            }
    
    def get_available_methods(self) -> List[str]:
        """Get list of available extraction methods"""
        methods = ['url_pattern']
        
        if BS4_AVAILABLE:
            methods.append('requests_scraping')
        
        if SELENIUM_AVAILABLE:
            methods.append('selenium_scraping')
        
        return methods

def install_dependencies():
    """Install required dependencies for LinkedIn scraping"""
    import subprocess
    import sys
    
    dependencies = [
        "requests",
        "beautifulsoup4",
        "selenium"
    ]
    
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"✅ Installed {dep}")
        except Exception as e:
            print(f"❌ Failed to install {dep}: {e}")
    
    print("\n📋 Additional Setup Required:")
    print("For Selenium scraping, you need to:")
    print("1. Download ChromeDriver from https://chromedriver.chromium.org/")
    print("2. Add ChromeDriver to your PATH")
    print("3. Or place chromedriver.exe in the same directory as this script")

def test_linkedin_extractor():
    """Test the LinkedIn extractor with sample URLs"""
    extractor = LinkedInProfileExtractor()
    
    # Test URLs (these are example URLs, replace with real ones for testing)
    test_urls = [
        "https://www.linkedin.com/in/johndoe",
        "linkedin.com/in/jane-smith",
        "https://linkedin.com/in/tech-professional-123"
    ]
    
    print("=== LinkedIn Extractor Test Results ===")
    print(f"Available methods: {extractor.get_available_methods()}")
    print()
    
    for url in test_urls:
        print(f"Testing URL: {url}")
        
        # Test basic info extraction (always works)
        basic_info = extractor.extract_basic_info_from_url(url)
        print(f"  Basic extraction: {basic_info}")
        
        # Test full extraction (may be limited)
        profile = extractor.extract_profile(url)
        print(f"  Full name: {profile.full_name}")
        print(f"  Normalized URL: {profile.linkedin_url}")
        print(f"  Headline: {profile.headline}")
        print()

if __name__ == "__main__":
    # Check dependencies
    missing_deps = []
    if not BS4_AVAILABLE:
        missing_deps.append("beautifulsoup4")
    if not SELENIUM_AVAILABLE:
        missing_deps.append("selenium")
    
    if missing_deps:
        print(f"Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install requests beautifulsoup4 selenium")
        print("\nNote: LinkedIn actively blocks scraping.")
        print("This module provides fallback methods but may have limited success.")
        print("For production use, consider LinkedIn API integration.")
    else:
        print("All dependencies available!")
    
    # Run test
    test_linkedin_extractor()
