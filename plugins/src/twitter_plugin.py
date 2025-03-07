import os
import json
import glob
from datetime import datetime
from typing import List, Dict, Any, Optional
import zipfile
from plugins.base_plugin import BasePlugin, LocationPoint

class TwitterPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="Twitter",
            description="Extract location data from Twitter archive files without API"
        )
    
    def is_configured(self):
        # Check if the plugin is properly configured
        return True, "TwitterPlugin is configured"
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "archive_location",
                "display_name": "Twitter Archive Location",
                "type": "directory",
                "default": "",
                "required": True,
                "description": "Directory containing your Twitter data archive (ZIP or extracted)"
            }
        ]
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None, 
                         date_to: Optional[datetime] = None) -> List[LocationPoint]:
        locations = []
        archive_location = self.config.get("archive_location", "")
        
        if not archive_location or not os.path.exists(archive_location):
            return locations
        
        # Handle ZIP archives
        if archive_location.endswith('.zip') and zipfile.is_zipfile(archive_location):
            with zipfile.ZipFile(archive_location, 'r') as zip_ref:
                temp_dir = os.path.join(self.data_dir, "temp_twitter_extract")
                os.makedirs(temp_dir, exist_ok=True)
                zip_ref.extractall(temp_dir)
                archive_location = temp_dir
        
        # Look for tweet.js or tweets.json files
        tweet_files = []
        for pattern in ["**/tweet.js", "**/tweets.json", "**/tweet_*.js"]:
            tweet_files.extend(glob.glob(os.path.join(archive_location, pattern), recursive=True))
        
        for tweet_file in tweet_files:
            try:
                with open(tweet_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Twitter archives often prefix JSON with a variable assignment
                    if content.startswith("window.YTD.tweet"):
                        content = content[content.index('['):]
                    
                    tweets = json.loads(content)
                    
                    # Handle different archive formats
                    if isinstance(tweets, dict) and "tweets" in tweets:
                        tweets = tweets["tweets"]
                    
                    for tweet in tweets:
                        # Handle different archive formats
                        if isinstance(tweet, dict) and "tweet" in tweet:
                            tweet = tweet["tweet"]
                        
                        if "geo" in tweet and tweet["geo"] and "coordinates" in tweet["geo"]:
                            coords = tweet["geo"]["coordinates"]
                            lat, lon = coords[0], coords[1]
                            
                            # Get timestamp
                            created_at = tweet.get("created_at")
                            if created_at:
                                try:
                                    tweet_time = datetime.strptime(
                                        created_at, "%a %b %d %H:%M:%S %z %Y"
                                    )
                                except ValueError:
                                    try:
                                        tweet_time = datetime.fromisoformat(created_at)
                                    except ValueError:
                                        tweet_time = datetime.now()
                            else:
                                tweet_time = datetime.now()
                            
                            # Filter by date if needed
                            if date_from and tweet_time < date_from:
                                continue
                            if date_to and tweet_time > date_to:
                                continue
                            
                            context = tweet.get("full_text", tweet.get("text", ""))
                            
                            locations.append(
                                LocationPoint(
                                    latitude=lat,
                                    longitude=lon,
                                    timestamp=tweet_time,
                                    source=f"Twitter - {tweet.get('id_str', 'Unknown')}",
                                    context=context[:200]
                                )
                            )
            except Exception as e:
                print(f"Error processing {tweet_file}: {e}")
                
        return locations
