import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
import os

class FeatureEngineer:
    """
    Transforms raw log data into ML-ready features for insider threat detection.
    Creates temporal, behavioral, and IP-based features.
    """
    
    def __init__(self):
        """Initialize the feature engineering pipeline."""
        # Time-based thresholds
        self.business_hours_start = 8  # 8 AM
        self.business_hours_end = 18   # 6 PM
        
        # Default feature configuration
        self.time_window_days = 7     # Lookback window for behavioral baselines
    
    def extract_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract time-based features from timestamps.
        
        Args:
            df: DataFrame containing log data with 'timestamp' column
            
        Returns:
            DataFrame with additional time-based features
        """
        # Ensure timestamp is datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Extract time components
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek  # 0=Monday, 6=Sunday
        df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)  # 5=Sat, 6=Sun
        df['is_business_hours'] = df.apply(
            lambda x: 1 if (self.business_hours_start <= x['hour'] <= self.business_hours_end and x['is_weekend'] == 0) else 0, 
            axis=1
        )
        df['is_night'] = df.apply(lambda x: 1 if (x['hour'] < 6 or x['hour'] >= 22) else 0, axis=1)
        
        # Add day part categories
        df['day_part'] = pd.cut(
            df['hour'], 
            bins=[0, 6, 12, 18, 24], 
            labels=['Night', 'Morning', 'Afternoon', 'Evening'],
            right=False
        )
        
        return df
    
    def extract_user_behavior_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract user behavioral features based on historical patterns.
        
        Args:
            df: DataFrame containing log data
            
        Returns:
            DataFrame with additional user behavioral features
        """
        # Clone input dataframe
        result_df = df.copy()
        
        # Sort by timestamp for sliding window calculations
        result_df = result_df.sort_values('timestamp')
        
        # Calculate user-specific behavioral features
        # 1. User's common IP addresses
        user_common_ips = {}
        for user in result_df['user_id'].unique():
            user_ips = result_df[result_df['user_id'] == user]['ip_address'].value_counts()
            if not user_ips.empty:
                common_ips = set(user_ips.nlargest(3).index.tolist())
                user_common_ips[user] = common_ips
        
        # Flag new/unusual IPs (not in user's top 3 common IPs)
        result_df['is_unusual_ip'] = result_df.apply(
            lambda row: 1 if (row['ip_address'] not in user_common_ips.get(row['user_id'], set())) else 0,
            axis=1
        )
        
        # 2. User's common access hours
        user_hour_patterns = {}
        for user in result_df['user_id'].unique():
            user_hours = result_df[result_df['user_id'] == user]['hour'].value_counts()
            if not user_hours.empty:
                common_hours = set(user_hours.nlargest(10).index.tolist())
                user_hour_patterns[user] = common_hours
        
        # Flag unusual access hours (not in user's top 10 common hours)
        result_df['is_unusual_hour'] = result_df.apply(
            lambda row: 1 if (row['hour'] not in user_hour_patterns.get(row['user_id'], set())) else 0,
            axis=1
        )
        
        # 3. User's typical data volume
        user_data_stats = result_df.groupby('user_id')['data_size'].agg(['mean', 'std']).reset_index()
        user_data_stats_dict = {
            row['user_id']: {'mean': row['mean'], 'std': max(row['std'], 1)}  # Avoid div by zero
            for _, row in user_data_stats.iterrows()
        }
        
        # Calculate z-score for data size
        result_df['data_size_zscore'] = result_df.apply(
            lambda row: (row['data_size'] - user_data_stats_dict.get(row['user_id'], {'mean': 0, 'std': 1})['mean']) / 
                        user_data_stats_dict.get(row['user_id'], {'mean': 0, 'std': 1})['std'],
            axis=1
        )
        
        # Flag large data transfers (z-score > 2)
        result_df['is_large_data_transfer'] = result_df['data_size_zscore'].apply(lambda x: 1 if x > 2 else 0)
        
        # 4. Calculate access frequency
        # Group by user and date, count occurrences
        daily_access_counts = result_df.groupby([
            'user_id', 
            result_df['timestamp'].dt.date
        ]).size().reset_index(name='daily_access_count')
        
        # Get average daily access count per user
        user_avg_daily_access = daily_access_counts.groupby('user_id')['daily_access_count'].mean().reset_index()
        user_avg_access_dict = dict(zip(user_avg_daily_access['user_id'], user_avg_daily_access['daily_access_count']))
        
        # Add date column for merging
        result_df['date'] = result_df['timestamp'].dt.date
        result_df = result_df.merge(
            daily_access_counts[['user_id', 'date', 'daily_access_count']],
            on=['user_id', 'date'],
            how='left'
        )
        
        # Calculate access frequency ratio compared to user's average
        result_df['access_frequency_ratio'] = result_df.apply(
            lambda row: row['daily_access_count'] / max(user_avg_access_dict.get(row['user_id'], 1), 1),
            axis=1
        )
        
        # Flag high access frequency (>2x user's average)
        result_df['is_high_access_frequency'] = result_df['access_frequency_ratio'].apply(lambda x: 1 if x > 2 else 0)
        
        return result_df
    
    def extract_action_based_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features based on actions and resources accessed.
        
        Args:
            df: DataFrame containing log data
            
        Returns:
            DataFrame with additional action-based features
        """
        # Clone input dataframe
        result_df = df.copy()
        
        # Flag sensitive actions
        sensitive_actions = ['DELETE', 'UPDATE']
        result_df['is_sensitive_action'] = result_df['action'].apply(lambda x: 1 if x in sensitive_actions else 0)
        
        # Calculate actions per user
        user_action_counts = {}
        for user in result_df['user_id'].unique():
            user_df = result_df[result_df['user_id'] == user]
            action_counts = user_df['action'].value_counts(normalize=True).to_dict()
            user_action_counts[user] = action_counts
        
        # Identify unusual actions for each user
        def is_unusual_action(row):
            user = row['user_id']
            action = row['action']
            
            if user not in user_action_counts:
                return 0
            
            # If action is rare for this user (<10% of their actions)
            if action in user_action_counts[user]:
                if user_action_counts[user][action] < 0.1:
                    return 1
            else:
                return 1  # Brand new action for this user
            
            return 0
        
        result_df['is_unusual_action'] = result_df.apply(is_unusual_action, axis=1)
        
        # Calculate resource entropy per user (higher entropy = accessing many different resources)
        user_resource_counts = {}
        for user in result_df['user_id'].unique():
            user_resources = result_df[result_df['user_id'] == user]['resource'].value_counts(normalize=True)
            entropy = -sum(p * np.log(p) for p in user_resources)
            user_resource_counts[user] = {'count': len(user_resources), 'entropy': entropy}
        
        # Add resource diversity features
        result_df['resource_count'] = result_df['user_id'].apply(
            lambda x: user_resource_counts.get(x, {}).get('count', 0)
        )
        
        result_df['resource_entropy'] = result_df['user_id'].apply(
            lambda x: user_resource_counts.get(x, {}).get('entropy', 0)
        )
        
        return result_df
    
    def extract_geo_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract features based on geolocation data (if available).
        
        Args:
            df: DataFrame containing log data with geolocation columns
            
        Returns:
            DataFrame with additional geo-based features
        """
        # Skip if geo columns don't exist
        if 'geo_country' not in df.columns:
            return df
        
        # Clone input dataframe
        result_df = df.copy()
        
        # Build user-country mapping (which countries are normal for each user)
        user_countries = {}
        for user in result_df['user_id'].unique():
            countries = result_df[result_df['user_id'] == user]['geo_country'].value_counts()
            common_countries = set(countries[countries > 1].index.tolist())
            user_countries[user] = common_countries
        
        # Flag accesses from unusual countries
        result_df['is_unusual_country'] = result_df.apply(
            lambda row: 1 if row['geo_country'] not in user_countries.get(row['user_id'], set()) else 0,
            axis=1
        )
        
        # Calculate speed-based features (impossible travel)
        result_df = result_df.sort_values(['user_id', 'timestamp'])
        
        # For each user, calculate time and distance between consecutive logins
        prev_rows = {}
        travel_speeds = []
        
        for _, row in result_df.iterrows():
            user = row['user_id']
            
            if user in prev_rows:
                prev = prev_rows[user]
                
                # Calculate time difference in hours
                time_diff = (row['timestamp'] - prev['timestamp']).total_seconds() / 3600
                
                # If we have geo coordinates and time diff is >0
                if ('geo_latitude' in row and 'geo_longitude' in row and 
                    'geo_latitude' in prev and 'geo_longitude' in prev and time_diff > 0):
                    
                    # Calculate distance using Haversine formula (approximate)
                    from math import radians, sin, cos, sqrt, atan2
                    
                    R = 6371  # Earth radius in km
                    
                    lat1 = radians(prev['geo_latitude'])
                    lon1 = radians(prev['geo_longitude'])
                    lat2 = radians(row['geo_latitude'])
                    lon2 = radians(row['geo_longitude'])
                    
                    dlon = lon2 - lon1
                    dlat = lat2 - lat1
                    
                    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                    c = 2 * atan2(sqrt(a), sqrt(1-a))
                    distance = R * c
                    
                    # Calculate speed in km/h
                    if time_diff > 0:
                        speed = distance / time_diff
                    else:
                        speed = 0
                    
                    travel_speeds.append({
                        'index': row.name,
                        'travel_speed_kmh': speed,
                        'distance_km': distance,
                        'time_diff_hours': time_diff
                    })
            
            # Store current row as previous
            prev_rows[user] = row
        
        # Create DataFrame from speeds
        if travel_speeds:
            speed_df = pd.DataFrame(travel_speeds)
            
            # Merge with result_df
            result_df = result_df.join(speed_df.set_index('index'))
            
            # Flag impossible travel (>900 km/h, approximate speed of commercial flights)
            result_df['is_impossible_travel'] = result_df['travel_speed_kmh'].apply(
                lambda x: 1 if x is not None and x > 900 else 0
            )
            
            # Fill NAs
            result_df['travel_speed_kmh'] = result_df['travel_speed_kmh'].fillna(0)
            result_df['distance_km'] = result_df['distance_km'].fillna(0)
            result_df['time_diff_hours'] = result_df['time_diff_hours'].fillna(0)
        
        return result_df
    
    def create_feature_vector(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Apply all feature engineering steps and create the final feature vector.
        
        Args:
            df: DataFrame containing raw log data
            
        Returns:
            DataFrame with engineered features ready for ML
        """
        # Apply all feature extraction steps
        result_df = self.extract_time_features(df)
        result_df = self.extract_user_behavior_features(result_df)
        result_df = self.extract_action_based_features(result_df)
        result_df = self.extract_geo_features(result_df)
        
        # Create aggregated risk score based on individual feature flags
        risk_features = [
            'is_unusual_ip', 'is_unusual_hour', 'is_large_data_transfer',
            'is_high_access_frequency', 'is_sensitive_action', 'is_unusual_action',
            'is_weekend', 'is_night'
        ]
        
        # Add geo features if available
        if 'is_unusual_country' in result_df.columns:
            risk_features.append('is_unusual_country')
        
        if 'is_impossible_travel' in result_df.columns:
            risk_features.append('is_impossible_travel')
        
        # Calculate naive risk score (sum of risk factors)
        for feature in risk_features:
            if feature not in result_df.columns:
                result_df[feature] = 0
        
        result_df['risk_score'] = result_df[risk_features].sum(axis=1) / len(risk_features)
        
        return result_df
    
    def transform(self, df: pd.DataFrame, output_path: str = None) -> pd.DataFrame:
        """
        End-to-end transformation pipeline.
        
        Args:
            df: Raw log DataFrame
            output_path: Optional path to save the transformed data
            
        Returns:
            Transformed DataFrame with all engineered features
        """
        print("Starting feature engineering process...")
        
        # Apply all transformations
        result_df = self.create_feature_vector(df)
        
        print(f"Feature engineering complete. Extracted {len(result_df.columns)} features.")
        
        # Save to disk if path provided
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            result_df.to_csv(output_path, index=False)
            print(f"Saved engineered features to {output_path}")
        
        return result_df

if __name__ == "__main__":
    # Example usage
    try:
        # Try to load geo-enriched data if available
        logs_df = pd.read_csv('../logs/geo_enriched_logs.csv')
        print("Using geo-enriched logs for feature engineering")
    except FileNotFoundError:
        # Fall back to regular logs
        try:
            logs_df = pd.read_csv('../logs/sample_logs.csv')
            print("Using standard logs (without geo data) for feature engineering")
        except FileNotFoundError:
            print("Error: No log files found. Run the log generator first.")
            exit(1)
    
    # Initialize feature engineer
    engineer = FeatureEngineer()
    
    # Transform data
    features_df = engineer.transform(logs_df, output_path='../logs/engineered_features.csv')
    
    # Display sample of engineered features
    print("\nSample engineered features:")
    print(features_df.iloc[:5, :10])  # First 5 rows, first 10 columns
    
    # Show summary of risk scores
    print("\nRisk score statistics:")
    print(features_df['risk_score'].describe())
    
    # Show distribution by anomaly label (if available)
    if 'is_anomaly' in features_df.columns:
        print("\nRisk score by anomaly label:")
        print(features_df.groupby('is_anomaly')['risk_score'].describe())