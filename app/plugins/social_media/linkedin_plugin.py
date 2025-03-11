#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
LinkedIn Plugin for CreepyAI
Extracts location data from LinkedIn exports and profiles
"""

from app.plugins.geocoding_helper import GeocodingHelper
from app.plugins.base_plugin import BasePlugin, LocationPoint
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import os
import json
import logging
import re

logger = logging.getLogger(__name__)

class LinkedInPlugin(BasePlugin):
    """Plugin for extracting location data from LinkedIn data"""
    
    def __init__(self):
        super().__init__(
            name="LinkedIn",
            description="Extract location data from LinkedIn data exports and profiles"
        )
        self.version = "1.0.0"
        self.author = "CreepyAI Team"
        self.geocoder = GeocodingHelper()
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        """Return configuration options for this plugin"""
        return [
            {
                "name": "data_directory",
                "display_name": "LinkedIn Data Directory",
                "type": "directory",
                "default": "",
                "required": True,
                "description": "Directory containing LinkedIn data export"
            },
            {
                "name": "include_connections",
                "display_name": "Include Connections",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "Extract location data from LinkedIn connections"
            },
            {
                "name": "include_jobs",
                "display_name": "Include Job Locations",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "Extract location data from job history"
            },
            {
                "name": "include_education",
                "display_name": "Include Education Locations",
                "type": "boolean",
                "default": True,
                "required": False,
                "description": "Extract location data from education history"
            }
        ]
    
    def is_configured(self) -> Tuple[bool, str]:
        """Check if the plugin is properly configured"""
        data_dir = self.config.get("data_directory", "")
        
        if not data_dir:
            return False, "LinkedIn data directory not configured"
            
        if not os.path.exists(data_dir):
            return False, f"LinkedIn data directory does not exist: {data_dir}"
            
        return True, "LinkedIn plugin is configured"
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None,
                         date_to: Optional[datetime] = None) -> List[LocationPoint]:
        """
        Extract location data from LinkedIn data
        
        Args:
            target: Directory containing LinkedIn data or profile URL
            date_from: Optional start date filter
            date_to: Optional end date filter
            
        Returns:
            List of LocationPoint objects
        """
        locations = []
        
        # Check if target is a directory path or use configured directory
        data_dir = target
        if not os.path.exists(data_dir) or not os.path.isdir(data_dir):
            data_dir = self.config.get("data_directory", "")
            if not os.path.exists(data_dir):
                logger.warning(f"LinkedIn data directory not found: {data_dir}")
                return []
        
        # Process profile data
        profile_locations = self._process_profile(data_dir)
        locations.extend(profile_locations)
        
        # Process connections if enabled
        if self.config.get("include_connections", True):
            connection_locations = self._process_connections(data_dir)
            locations.extend(connection_locations)
        
        # Process job history if enabled
        if self.config.get("include_jobs", True):
            job_locations = self._process_jobs(data_dir)
            locations.extend(job_locations)
        
        # Process education history if enabled
        if self.config.get("include_education", True):
            education_locations = self._process_education(data_dir)
            locations.extend(education_locations)
        
        # Apply date filtering
        if date_from or date_to:
            locations = [
                loc for loc in locations 
                if (not date_from or loc.timestamp >= date_from) and
                   (not date_to or loc.timestamp <= date_to)
            ]
        
        return locations
    
    def _process_profile(self, data_dir: str) -> List[LocationPoint]:
        """Extract locations from user's profile data"""
        locations = []
        
        # Look for profile.json
        profile_file = os.path.join(data_dir, 'profile.json')
        if not os.path.exists(profile_file):
            profile_file = os.path.join(data_dir, 'Profile.json')
        
        if os.path.exists(profile_file):
            try:
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                
                # Extract user's location
                if 'location' in profile_data and profile_data['location']:
                    location_name = profile_data['location']
                    lat, lon = self.geocoder.geocode(location_name)
                    
                    if lat is not None and lon is not None:
                        locations.append(
                            LocationPoint(
                                latitude=lat,
                                longitude=lon,
                                timestamp=datetime.now(),
                                source="LinkedIn Profile",
                                context=f"LinkedIn profile location: {location_name}"
                            )
                        )
            except Exception as e:
                logger.error(f"Error processing LinkedIn profile: {e}")
        
        return locations
    
    def _process_connections(self, data_dir: str) -> List[LocationPoint]:
        """Extract locations from user's connections"""
        locations = []
        
        # Look for connections.csv or Connections.csv
        connections_file = os.path.join(data_dir, 'connections.csv')
        if not os.path.exists(connections_file):
            connections_file = os.path.join(data_dir, 'Connections.csv')
        
        if os.path.exists(connections_file):
            try:
                import csv
                with open(connections_file, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        try:
                            # Extract location if available
                            location = None
                            
                            # Try different possible column names
                            for col_name in ['Location', 'location', 'Company Location']:
                                if col_name in row and row[col_name]:
                                    location = row[col_name]
                                    break
                            
                            if location:
                                lat, lon = self.geocoder.geocode(location)
                                
                                if lat is not None and lon is not None:
                                    # Try to get a connection date
                                    connected_date = None
                                    for date_col in ['Connected On', 'connection_date']:
                                        if date_col in row and row[date_col]:
                                            try:
                                                connected_date = datetime.strptime(
                                                    row[date_col], '%d %b %Y')
                                            except ValueError:
                                                try:
                                                    connected_date = datetime.strptime(
                                                        row[date_col], '%Y-%m-%d')
                                                except ValueError:
                                                    pass
                                    
                                    # Default to now if parsing failed
                                    if not connected_date:
                                        connected_date = datetime.now()
                                    
                                    # Get connection name
                                    name = ""
                                    for name_col in ['First Name', 'Last Name', 'Name', 'full_name']:
                                        if name_col in row and row[name_col]:
                                            name += f"{row[name_col]} "
                                    
                                    name = name.strip() or "LinkedIn Connection"
                                    
                                    locations.append(
                                        LocationPoint(
                                            latitude=lat,
                                            longitude=lon,
                                            timestamp=connected_date,
                                            source="LinkedIn Connection",
                                            context=f"{name} - {location}"
                                        )
                                    )
                        except Exception as e:
                            logger.debug(f"Error processing connection: {e}")
            except Exception as e:
                logger.error(f"Error processing LinkedIn connections: {e}")
        
        return locations
    
    def _process_jobs(self, data_dir: str) -> List[LocationPoint]:
        """Extract locations from user's job history"""
        locations = []
        
        # Look for positions.json or work_experience.json
        jobs_file = None
        for filename in ['positions.json', 'work_experience.json', 'Jobs.json']:
            potential_file = os.path.join(data_dir, filename)
            if os.path.exists(potential_file):
                jobs_file = potential_file
                break
        
        if jobs_file:
            try:
                with open(jobs_file, 'r', encoding='utf-8') as f:
                    jobs_data = json.load(f)
                
                # Handle different formats
                job_list = []
                if isinstance(jobs_data, list):
                    job_list = jobs_data
                elif 'positions' in jobs_data:
                    job_list = jobs_data['positions']
                elif 'elements' in jobs_data:
                    job_list = jobs_data['elements']
                
                for job in job_list:
                    try:
                        # Extract location
                        location = None
                        for loc_key in ['locationName', 'location', 'companyLocation', 'location_name']:
                            if loc_key in job and job[loc_key]:
                                location = job[loc_key]
                                break
                        
                        if not location:
                            continue
                            
                        lat, lon = self.geocoder.geocode(location)
                        
                        if lat is not None and lon is not None:
                            # Try to get job start date
                            job_date = None
                            start_date = None
                            
                            # Try different date formats and fields
                            for date_key in ['startDate', 'start_date', 'timePeriod', 'date_range']:
                                if date_key in job:
                                    date_info = job[date_key]
                                    
                                    if isinstance(date_info, dict):
                                        # Handle nested date structure
                                        if 'year' in date_info:
                                            year = int(date_info['year'])
                                            month = int(date_info.get('month', 1))
                                            day = int(date_info.get('day', 1))
                                            job_date = datetime(year, month, day)
                                        elif 'start' in date_info:
                                            start_info = date_info['start']
                                            if isinstance(start_info, dict) and 'year' in start_info:
                                                year = int(start_info['year'])
                                                month = int(start_info.get('month', 1))
                                                day = int(start_info.get('day', 1))
                                                job_date = datetime(year, month, day)
                                    elif isinstance(date_info, str):
                                        # Try common date formats
                                        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%b %Y', '%B %Y']:
                                            try:
                                                job_date = datetime.strptime(date_info, fmt)
                                                break
                                            except ValueError:
                                                pass
                            
                            if not job_date:
                                job_date = datetime.now()
                            
                            # Get company and title information
                            company = ""
                            title = ""
                            
                            for company_key in ['companyName', 'company', 'company_name']:
                                if company_key in job and job[company_key]:
                                    company = job[company_key]
                                    break
                            
                            for title_key in ['title', 'position', 'job_title']:
                                if title_key in job and job[title_key]:
                                    title = job[title_key]
                                    break
                            
                            context = f"{title} at {company}, {location}" if company else f"{title} in {location}"
                            
                            locations.append(
                                LocationPoint(
                                    latitude=lat,
                                    longitude=lon,
                                    timestamp=job_date,
                                    source="LinkedIn Job",
                                    context=context
                                )
                            )
                    except Exception as e:
                        logger.debug(f"Error processing job: {e}")
            except Exception as e:
                logger.error(f"Error processing LinkedIn jobs: {e}")
        
        return locations
    
    def _process_education(self, data_dir: str) -> List[LocationPoint]:
        """Extract locations from user's education history"""
        locations = []
        
        # Look for education.json or Education.json
        education_file = os.path.join(data_dir, 'education.json')
        if not os.path.exists(education_file):
            education_file = os.path.join(data_dir, 'Education.json')
        
        if os.path.exists(education_file):
            try:
                with open(education_file, 'r', encoding='utf-8') as f:
                    education_data = json.load(f)
                
                # Handle different formats
                education_list = []
                if isinstance(education_data, list):
                    education_list = education_data
                elif 'elements' in education_data:
                    education_list = education_data['elements']
                elif 'schools' in education_data:
                    education_list = education_data['schools']
                
                for edu in education_list:
                    try:
                        # Extract school name
                        school_name = None
                        for name_key in ['schoolName', 'school_name', 'name', 'institution_name']:
                            if name_key in edu and edu[name_key]:
                                school_name = edu[name_key]
                                break
                        
                        if not school_name:
                            continue
                            
                        # Try to geocode the school name
                        lat, lon = self.geocoder.geocode(school_name)
                        
                        # If geocoding by school name fails, try location if available
                        if lat is None or lon is None:
                            school_location = None
                            for loc_key in ['location', 'locationName', 'school_location']:
                                if loc_key in edu and edu[loc_key]:
                                    school_location = edu[loc_key]
                                    break
                            
                            if school_location:
                                lat, lon = self.geocoder.geocode(school_location)
                        
                        if lat is not None and lon is not None:
                            # Try to get education start date
                            edu_date = None
                            
                            # Try different date fields and formats
                            for date_key in ['startDate', 'start_date', 'timePeriod', 'date_range']:
                                if date_key in edu:
                                    date_info = edu[date_key]
                                    
                                    if isinstance(date_info, dict):
                                        # Handle nested date structure
                                        if 'year' in date_info:
                                            year = int(date_info['year'])
                                            month = int(date_info.get('month', 1))
                                            day = int(date_info.get('day', 1))
                                            edu_date = datetime(year, month, day)
                                        elif 'start' in date_info:
                                            start_info = date_info['start']
                                            if isinstance(start_info, dict) and 'year' in start_info:
                                                year = int(start_info['year'])
                                                month = int(start_info.get('month', 1))
                                                day = int(start_info.get('day', 1))
                                                edu_date = datetime(year, month, day)
                                    elif isinstance(date_info, str):
                                        # Try common date formats
                                        for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%b %Y', '%B %Y']:
                                            try:
                                                edu_date = datetime.strptime(date_info, fmt)
                                                break
                                            except ValueError:
                                                pass
                            
                            if not edu_date:
                                edu_date = datetime.now()
                            
                            # Get degree information if available
                            degree = ""
                            for degree_key in ['degree', 'degreeName', 'field_of_study']:
                                if degree_key in edu and edu[degree_key]:
                                    degree = edu[degree_key]
                                    break
                            
                            context = f"{degree} at {school_name}" if degree else f"Attended {school_name}"
                            
                            locations.append(
                                LocationPoint(
                                    latitude=lat,
                                    longitude=lon,
                                    timestamp=edu_date,
                                    source="LinkedIn Education",
                                    context=context
                                )
                            )
                    except Exception as e:
                        logger.debug(f"Error processing education entry: {e}")
            except Exception as e:
                logger.error(f"Error processing LinkedIn education: {e}")
        
        return locations
