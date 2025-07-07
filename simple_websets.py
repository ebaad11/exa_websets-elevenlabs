#!/usr/bin/env python3
"""Series A Funding Tracker

Tracks companies in San Francisco that have recently completed Series A funding rounds using the Exa Websets API.
"""

import os
import time
import json
import requests
from datetime import datetime, timedelta
import pathlib
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class SeriesATracker:
    def __init__(self, 
                 exa_api_key=None,
                 timeout_minutes=10,
                 query="companies in SF that just raised their series A this week",
                 criteria=None,
                 days_lookback=7,
                 result_count=5,
                 entity_type="company",
                 enrichments=None,
                 output_dir="websites",
                 file_prefix="series_a_companies"):
        """Initialize the Series A tracker with configurable parameters.
        
        Args:
            exa_api_key (str, optional): Exa API key. Defaults to environment variable EXA_API_KEY.
            timeout_minutes (int, optional): Minutes to wait for webset completion. Defaults to 10.
            query (str, optional): Base search query. Defaults to companies in SF with series A funding.
            criteria (list, optional): List of search criteria dictionaries. Defaults to SF and recent funding.
            days_lookback (int, optional): Number of days to look back for funding. Defaults to 7.
            result_count (int, optional): Number of results to retrieve. Defaults to 5.
            entity_type (str, optional): Type of entity to search for. Defaults to "company".
            enrichments (list, optional): List of enrichment dictionaries. Defaults to Series A Amount.
            output_dir (str, optional): Directory to save results. Defaults to "websites".
            file_prefix (str, optional): Filename prefix for saved results. Defaults to "series_a_companies".
        """
        # Use provided API key or get from environment
        self.exa_api_key = exa_api_key or os.getenv('EXA_API_KEY')
        self.timeout_minutes = timeout_minutes
        self.webset_id = None
        self.query = query
        self.days_lookback = days_lookback
        self.result_count = result_count
        self.entity_type = entity_type
        self.output_dir = output_dir
        self.file_prefix = file_prefix
        
        # Default criteria if none provided
        self.criteria = criteria or [
            { "description": "company is headquartered in san francisco, ca" },
            { "description": "completed a series a fundraising round" }
        ]
        
        # Default enrichments if none provided
        self.enrichments = enrichments or [
            {
                "description": "Series A Amount",
                "format": "number"
            }
        ]
        
        # API Headers
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.exa_api_key
        }
        
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration."""
        if not self.exa_api_key:
            raise ValueError("EXA_API_KEY is required in environment variables")
    
    def create_webset(self):
        """Create a new webset to track Series A companies based on configured parameters."""
        # Get dates for the time period
        today = datetime.now()
        past_date = today - timedelta(days=self.days_lookback)
        date_format = "%Y-%m-%d"
        
        # Create a copy of criteria to avoid modifying the original
        criteria = list(self.criteria)
        
        # Add date range to criteria if there's a lookback period
        if self.days_lookback > 0:
            date_criteria = {"description": f"completed a series a fundraising round between {past_date.strftime(date_format)} and {today.strftime(date_format)}"}
            criteria.append(date_criteria)
        
        # Webset configuration
        payload = {
            "search": {
                "query": self.query,
                "criteria": criteria,
                "count": self.result_count,
                "entity": {"type": self.entity_type}
            },
            "enrichments": self.enrichments
        }
        
        print("📊 Creating webset for Series A companies in SF...")
        
        try:
            # Print detailed payload for debugging
            print("\n🔍 API Request Payload:")
            print(json.dumps(payload, indent=2))
            
            # Print headers (without the API key for security)
            debug_headers = dict(self.headers)
            debug_headers['x-api-key'] = '***REDACTED***'
            print("\n🔍 API Request Headers:")
            print(json.dumps(debug_headers, indent=2))
            
            response = requests.post(
                "https://api.exa.ai/websets/v0/websets", 
                headers=self.headers, 
                json=payload
            )
            
            if response.status_code != 200 and response.status_code != 201:
                print(f"\n❌ Error response status: {response.status_code}")
                print(f"\n❌ Error response body: {response.text}")
            
            response.raise_for_status()
            result = response.json()
            self.webset_id = result['id']
            print(f"✅ Webset created successfully with ID: {self.webset_id}")
            return result
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating webset: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"❌ Error response body: {e.response.text}")
            raise
    
    def get_webset_status(self):
        """Get the current status of the webset."""
        if not self.webset_id:
            raise ValueError("No webset created yet. Call create_webset() first.")
        
        try:
            response = requests.get(
                f"https://api.exa.ai/websets/v0/websets/{self.webset_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"❌ Error getting webset status: {e}")
            raise
    
    def wait_for_completion(self):
        """Monitor the webset until it completes or times out."""
        if not self.webset_id:
            raise ValueError("No webset created yet. Call create_webset() first.")
        
        start_time = time.time()
        timeout_seconds = self.timeout_minutes * 60
        
        print(f"⏳ Waiting for webset to complete (timeout: {self.timeout_minutes} minutes)...")
        
        while time.time() - start_time < timeout_seconds:
            # Get the updated webset status
            webset = self.get_webset_status()
            
            if webset['status'] == "idle":
                print("✅ Webset processing completed!")
                return webset
            
            # Check progress if available
            progress_info = ""
            if webset['searches'] and len(webset['searches']) > 0:
                search = webset['searches'][0]
                if 'progress' in search and search['progress']:
                    progress = search['progress']
                    found = progress.get('found', 0)
                    analyzed = progress.get('analyzed', 0)
                    completion = progress.get('completion', 0)
                    progress_info = f"Progress: {completion}% (Found: {found}, Analyzed: {analyzed})"
            
            print(f"🔄 Webset status: {webset['status']}. {progress_info}")
            time.sleep(30)  # Check every 30 seconds
        
        print(f"⚠️ Timeout after {self.timeout_minutes} minutes. Webset processing incomplete.")
        return None
    
    def get_webset_items(self):
        """Get all items from the webset."""
        if not self.webset_id:
            raise ValueError("No webset created yet. Call create_webset() first.")
        
        all_items = []
        page_token = None
        
        print("📄 Retrieving webset items...")
        
        try:
            while True:
                # Prepare parameters
                params = {}
                if page_token:
                    params['pageToken'] = page_token
                
                # Make API request
                response = requests.get(
                    f"https://api.exa.ai/websets/v0/websets/{self.webset_id}/items",
                    headers=self.headers,
                    params=params
                )
                response.raise_for_status()
                result = response.json()
                
                # Add items to the list
                items = result.get('data', [])
                all_items.extend(items)
                
                # Check for next page
                page_token = result.get('next_page_token')
                if not page_token:
                    break
            
            print(f"✅ Retrieved {len(all_items)} items from webset")
            return all_items
        except requests.exceptions.RequestException as e:
            print(f"❌ Error retrieving webset items: {e}")
            raise
    
    def save_results(self):
        """Save the webset results to a file."""
        if not self.webset_id:
            raise ValueError("No webset created yet. Call create_webset() first.")
            
        # Create output directory if it doesn't exist
        pathlib.Path(self.output_dir).mkdir(exist_ok=True)
        
        # Get all items from the webset
        items = self.get_webset_items()
        
        # Save to a dated file
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"{self.output_dir}/{self.file_prefix}_{today}.json"
        
        with open(filename, 'w') as f:
            json.dump(items, f, indent=2)
            
        print(f"💾 Saved {len(items)} companies to {filename}")
        return filename
    
    def run(self):
        """Run the full workflow."""
        try:
            self.create_webset()
            webset = self.wait_for_completion()
            
            if webset:
                return self.save_results()
            else:
                print("⚠️ Webset did not complete in time. No results saved.")
                return None
        except Exception as e:
            print(f"❌ Error in tracker: {e}")
            return None

if __name__ == "__main__":
    print("🔍 Series A Tracker - Starting")
    tracker = SeriesATracker()
    results_file = tracker.run()
    
    if results_file:
        print(f"🎉 Process completed successfully. Results saved to {results_file}")
    else:
        print("❌ Process did not complete successfully.")