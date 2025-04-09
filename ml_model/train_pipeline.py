#!/usr/bin/env python3
"""
End-to-end training pipeline for Insider Threat Detection system.
This script orchestrates the entire pipeline from data simulation to model training.
"""

import os
import sys
import argparse
import logging
import pandas as pd
from datetime import datetime

# Add parent directory to path to import from sibling directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import project modules
from data_ingestion.simulate_log_generator import CloudLogSimulator
from data_preprocessing.geoip_resolver import GeoIPResolver
from data_preprocessing.feature_engineering import FeatureEngineer
from ml_model.isolation_forest import train_model_pipeline, InsiderThreatDetector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('training_pipeline.log')
    ]
)
logger = logging.getLogger("TrainingPipeline")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Insider Threat Detection Training Pipeline')
    
    parser.add_argument('--num-logs', type=int, default=10000,
                        help='Number of log entries to simulate (default: 10000)')
    
    parser.add_argument('--anomaly-ratio', type=float, default=0.05,
                        help='Ratio of anomalous logs to generate (default: 0.05)')
    
    parser.add_argument('--use-geo', action='store_true',
                        help='Enable GeoIP resolution (requires internet connection)')
    
    parser.add_argument('--max-geo-ips', type=int, default=100,
                        help='Maximum number of IPs to resolve (to avoid API rate limits)')
    
    parser.add_argument('--skip-data-gen', action='store_true',
                        help='Skip data generation and use existing data')
    
    parser.add_argument('--output-dir', type=str, default='../logs',
                        help='Directory to store generated data (default: ../logs)')
    
    parser.add_argument('--model-dir', type=str, default='../ml_model/trained_models',
                        help='Directory to store trained models (default: ../ml_model/trained_models)')
    
    return parser.parse_args()

def run_pipeline(args):
    """Run the full training pipeline."""
    start_time = datetime.now()
    logger.info(f"Starting training pipeline at {start_time}")
    
    # Create directories if they don't exist
    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(args.model_dir, exist_ok=True)
    
    # Define file paths
    raw_logs_path = os.path.join(args.output_dir, 'sample_logs.csv')
    geo_logs_path = os.path.join(args.output_dir, 'geo_enriched_logs.csv')
    features_path = os.path.join(args.output_dir, 'engineered_features.csv')
    
    # Step 1: Generate simulated log data (unless skipped)
    if not args.skip_data_gen:
        logger.info(f"Generating {args.num_logs} simulated log entries (anomaly ratio: {args.anomaly_ratio})")
        simulator = CloudLogSimulator(
            num_users=20,
            days_of_data=30,
            anomaly_ratio=args.anomaly_ratio
        )
        logs_df = simulator.generate_logs(total_logs=args.num_logs)
        csv_path, json_path = simulator.save_logs(logs_df, output_dir=args.output_dir)
        logger.info(f"Saved {len(logs_df)} log entries to {csv_path}")
    else:
        logger.info(f"Skipping data generation, using existing data at {raw_logs_path}")
        if not os.path.exists(raw_logs_path):
            logger.error(f"No existing data found at {raw_logs_path}. Aborting.")
            return False
        logs_df = pd.read_csv(raw_logs_path)
        logger.info(f"Loaded {len(logs_df)} existing log entries")
    
    # Step 2: GeoIP Resolution (if enabled)
    if args.use_geo:
        logger.info("Performing GeoIP resolution")
        resolver = GeoIPResolver(cache_file=os.path.join(args.output_dir, 'ip_cache.json'))
        geo_df = resolver.batch_resolve(logs_df, max_ips=args.max_geo_ips)
        geo_df.to_csv(geo_logs_path, index=False)
        logger.info(f"Saved geo-enriched logs to {geo_logs_path}")
        input_for_feature_eng = geo_df
    else:
        logger.info("Skipping GeoIP resolution")
        input_for_feature_eng = logs_df
    
    # Step 3: Feature Engineering
    logger.info("Performing feature engineering")
    engineer = FeatureEngineer()
    features_df = engineer.transform(input_for_feature_eng, output_path=features_path)
    logger.info(f"Generated {len(features_df.columns)} features, saved to {features_path}")
    
    # Step 4: Train Model
    logger.info("Training anomaly detection model")
    detector = train_model_pipeline(features_path, args.model_dir)
    
    # Step 5: Generate training report
    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"Pipeline completed in {duration}")
    
    # Create summary report
    report_path = os.path.join(args.model_dir, 'training_report.txt')
    with open(report_path, 'w') as f:
        f.write("Insider Threat Detection - Training Report\n")
        f.write("========================================\n\n")
        f.write(f"Training completed: {end_time}\n")
        f.write(f"Duration: {duration}\n\n")
        f.write("Dataset Statistics:\n")
        f.write(f"- Total logs: {len(logs_df)}\n")
        if 'is_anomaly' in logs_df.columns:
            anomaly_count = logs_df['is_anomaly'].sum()
            f.write(f"- Anomalous logs: {anomaly_count} ({anomaly_count/len(logs_df):.2%})\n\n")
        
        f.write("Feature Engineering:\n")
        f.write(f"- Features generated: {len(features_df.columns)}\n\n")
        
        f.write("Model Configuration:\n")
        f.write(f"- Algorithm: {detector.model_metadata['model_type']}\n")
        f.write(f"- Contamination: {detector.model_metadata['contamination']}\n")
        f.write(f"- Estimators: {detector.model_metadata['n_estimators']}\n\n")
        
        f.write("Files Generated:\n")
        f.write(f"- Raw logs: {raw_logs_path}\n")
        if args.use_geo:
            f.write(f"- Geo-enriched logs: {geo_logs_path}\n")
        f.write(f"- Engineered features: {features_path}\n")
        f.write(f"- Model directory: {args.model_dir}\n")
    
    logger.info(f"Training report saved to {report_path}")
    return True

def main():
    """Main entrypoint."""
    args = parse_arguments()
    if run_pipeline(args):
        logger.info("Training pipeline completed successfully")
    else:
        logger.error("Training pipeline failed")
        sys.exit(1)

if __name__ == "__main__":
    main()