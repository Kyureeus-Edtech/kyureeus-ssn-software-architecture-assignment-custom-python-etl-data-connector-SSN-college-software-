"""
ETL Orchestrator
Unified orchestrator for CERT.at threat intelligence ETL pipeline
Handles both CSV threat feeds and RSS security updates
"""

import os
import sys
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from csv_feeds import CSVExtractor, CSVTransformer, CSVLoader
from rss_feeds import RSSExtractor, RSSTransformer, RSSLoader


class ETLOrchestrator:
    """Unified ETL orchestrator for CERT.at threat intelligence"""
    
    def __init__(self, config: Dict):
        """
        Initialize ETL orchestrator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.logger = self._setup_logging()
        self.results = {
            'start_time': None,
            'end_time': None,
            'duration_seconds': 0,
            'csv_pipeline': {},
            'rss_pipeline': {},
            'errors': []
        }
        
        self.logger.info("=" * 80)
        self.logger.info("CERT.at Threat Intelligence ETL Pipeline Initialized")
        self.logger.info("=" * 80)
        self._log_configuration()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"etl_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=self.config.get('log_level', logging.INFO),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info(f"Logging initialized. Log file: {log_file}")
        
        return logger
    
    def _log_configuration(self) -> None:
        """Log current configuration"""
        self.logger.info("\nConfiguration:")
        self.logger.info(f"  Database: {self.config['db_name']}")
        self.logger.info(f"  Max Records (CSV): {self.config['max_records_csv']}")
        self.logger.info(f"  Max Records (RSS): {self.config['max_records_rss']}")
        self.logger.info(f"  CSV Data Directory: {self.config.get('csv_data_dir', 'data')}")
        self.logger.info(f"  Run CSV Pipeline: {self.config.get('run_csv', True)}")
        self.logger.info(f"  Run RSS Pipeline: {self.config.get('run_rss', True)}")
        self.logger.info(f"  Clean Before Load: {self.config.get('clean_before', True)}")
        self.logger.info(f"  Use Upsert: {self.config.get('use_upsert', False)}")
    
    def _print_banner(self, title: str) -> None:
        """Print section banner"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info(f"  {title}")
        self.logger.info("=" * 80)
    
    def _print_phase_header(self, phase: str, description: str) -> None:
        """Print phase header"""
        self.logger.info("\n" + "-" * 80)
        self.logger.info(f"[{phase}] {description}")
        self.logger.info("-" * 80)
    
    def run_csv_pipeline(self) -> Dict:
        """
        Run CSV threat intelligence pipeline
        
        Returns:
            Dictionary with pipeline results
        """
        self._print_banner("CSV THREAT INTELLIGENCE PIPELINE")
        
        csv_results = {
            'extract': {},
            'transform': {},
            'load': {},
            'success': False
        }
        
        try:
            # Initialize components
            extractor = CSVExtractor(self.config.get('csv_data_dir', 'data'))
            transformer = CSVTransformer(self.config['max_records_csv'])
            loader = CSVLoader(self.config['mongo_uri'], self.config['db_name'])
            
            # PHASE 1: EXTRACT
            self._print_phase_header("EXTRACT", "Reading CSV threat feeds")
            
            extracted_data = extractor.extract_all_feeds()
            
            csv_results['extract'] = {
                feed: data['record_count'] if data else 0
                for feed, data in extracted_data.items()
            }
            
            successful_extracts = sum(1 for v in extracted_data.values() if v)
            total_records = sum(v for v in csv_results['extract'].values())
            
            self.logger.info(f"✓ Extracted {successful_extracts}/3 feeds ({total_records} records)")
            
            if not any(extracted_data.values()):
                raise Exception("No CSV data extracted")
            
            # PHASE 2: TRANSFORM
            self._print_phase_header("TRANSFORM", "Normalizing threat data")
            
            transformed_data = transformer.transform_all_feeds(extracted_data)
            
            csv_results['transform'] = {
                feed: data['transformed_count'] if data else 0
                for feed, data in transformed_data.items()
            }
            
            total_transformed = sum(v for v in csv_results['transform'].values())
            self.logger.info(f"✓ Transformed {total_transformed} records")
            
            # Get severity distribution
            severity_stats = transformer.get_severity_stats(transformed_data)
            self.logger.info(f"Severity distribution: {severity_stats}")
            
            # PHASE 3: LOAD
            self._print_phase_header("LOAD", "Loading into MongoDB")
            
            if not loader.connect():
                raise Exception("Failed to connect to MongoDB")
            
            load_results = loader.load_all_feeds(
                transformed_data,
                clean_before=self.config.get('clean_before', True),
                upsert=self.config.get('use_upsert', False)
            )
            
            csv_results['load'] = load_results
            
            total_inserted = sum(stats['inserted'] for stats in load_results.values())
            total_updated = sum(stats['updated'] for stats in load_results.values())
            
            self.logger.info(f"✓ Loaded: {total_inserted} inserted, {total_updated} updated")
            
            # Get collection stats
            stats = loader.get_collection_stats()
            self.logger.info("\nCSV Collection Statistics:")
            for collection, count in stats.items():
                self.logger.info(f"  {collection}: {count} documents")
            
            csv_results['success'] = True
            
        except Exception as e:
            error_msg = f"CSV Pipeline Error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.results['errors'].append(error_msg)
            csv_results['success'] = False
        
        finally:
            if 'loader' in locals():
                loader.close()
        
        return csv_results
    
    def run_rss_pipeline(self) -> Dict:
        """
        Run RSS feed pipeline
        
        Returns:
            Dictionary with pipeline results
        """
        self._print_banner("RSS SECURITY FEEDS PIPELINE")
        
        rss_results = {
            'extract': {},
            'transform': {},
            'load': {},
            'success': False
        }
        
        try:
            # Initialize components
            extractor = RSSExtractor()
            transformer = RSSTransformer(self.config['max_records_rss'])
            loader = RSSLoader(self.config['mongo_uri'], self.config['db_name'])
            
            # PHASE 1: EXTRACT
            self._print_phase_header("EXTRACT", "Fetching RSS feeds from CERT.at")
            
            # Get specific feeds if configured
            if self.config.get('rss_feeds'):
                extracted_data = extractor.fetch_specific_feeds(self.config['rss_feeds'])
            else:
                extracted_data = extractor.fetch_all_feeds()
            
            rss_results['extract'] = {
                feed: data['entry_count'] if data else 0
                for feed, data in extracted_data.items()
            }
            
            successful_extracts = sum(1 for v in extracted_data.values() if v)
            total_entries = sum(v for v in rss_results['extract'].values())
            
            self.logger.info(f"✓ Extracted {successful_extracts} feeds ({total_entries} entries)")
            
            if not any(extracted_data.values()):
                raise Exception("No RSS data extracted")
            
            # PHASE 2: TRANSFORM
            self._print_phase_header("TRANSFORM", "Normalizing RSS entries")
            
            transformed_data = transformer.transform_all_feeds(extracted_data)
            
            rss_results['transform'] = {
                feed: data['transformed_count'] if data else 0
                for feed, data in transformed_data.items()
            }
            
            total_transformed = sum(v for v in rss_results['transform'].values())
            self.logger.info(f"✓ Transformed {total_transformed} entries")
            
            # PHASE 3: LOAD
            self._print_phase_header("LOAD", "Loading into MongoDB")
            
            if not loader.connect():
                raise Exception("Failed to connect to MongoDB")
            
            load_results = loader.load_all_feeds(
                transformed_data,
                clean_before=self.config.get('clean_before', True),
                upsert=self.config.get('use_upsert', False)
            )
            
            rss_results['load'] = load_results
            
            total_inserted = sum(stats['inserted'] for stats in load_results.values())
            total_updated = sum(stats['updated'] for stats in load_results.values())
            
            self.logger.info(f"✓ Loaded: {total_inserted} inserted, {total_updated} updated")
            
            # Get collection stats
            stats = loader.get_collection_stats()
            self.logger.info("\nRSS Collection Statistics:")
            for collection, count in stats.items():
                self.logger.info(f"  {collection}: {count} documents")
            
            rss_results['success'] = True
            
        except Exception as e:
            error_msg = f"RSS Pipeline Error: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            self.results['errors'].append(error_msg)
            rss_results['success'] = False
        
        finally:
            if 'loader' in locals():
                loader.close()
        
        return rss_results
    
    def run(self) -> Dict:
        """
        Run complete ETL pipeline
        
        Returns:
            Dictionary with complete pipeline results
        """
        start_time = datetime.now()
        self.results['start_time'] = start_time.isoformat()
        
        self.logger.info("\n" + "=" * 80)
        self.logger.info(f"ETL PIPELINE STARTED AT {start_time}")
        self.logger.info("=" * 80)
        
        # Run CSV pipeline if enabled
        if self.config.get('run_csv', True):
            self.results['csv_pipeline'] = self.run_csv_pipeline()
        else:
            self.logger.info("CSV pipeline disabled")
        
        # Run RSS pipeline if enabled
        if self.config.get('run_rss', True):
            self.results['rss_pipeline'] = self.run_rss_pipeline()
        else:
            self.logger.info("RSS pipeline disabled")
        
        # Calculate duration
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.results['end_time'] = end_time.isoformat()
        self.results['duration_seconds'] = duration
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _print_summary(self) -> None:
        """Print pipeline execution summary"""
        self.logger.info("\n" + "=" * 80)
        self.logger.info("ETL PIPELINE SUMMARY")
        self.logger.info("=" * 80)
        
        self.logger.info(f"\nExecution Time:")
        self.logger.info(f"  Start: {self.results['start_time']}")
        self.logger.info(f"  End: {self.results['end_time']}")
        self.logger.info(f"  Duration: {self.results['duration_seconds']:.2f} seconds")
        
        # CSV Pipeline Summary
        if self.results.get('csv_pipeline'):
            csv_results = self.results['csv_pipeline']
            self.logger.info(f"\nCSV Threat Intelligence Pipeline:")
            self.logger.info(f"  Status: {'✓ SUCCESS' if csv_results.get('success') else '✗ FAILED'}")
            
            if csv_results.get('extract'):
                total_extracted = sum(csv_results['extract'].values())
                self.logger.info(f"  Extracted: {total_extracted} records")
            
            if csv_results.get('transform'):
                total_transformed = sum(csv_results['transform'].values())
                self.logger.info(f"  Transformed: {total_transformed} records")
            
            if csv_results.get('load'):
                total_inserted = sum(stats['inserted'] for stats in csv_results['load'].values())
                total_updated = sum(stats['updated'] for stats in csv_results['load'].values())
                self.logger.info(f"  Loaded: {total_inserted} inserted, {total_updated} updated")
        
        # RSS Pipeline Summary
        if self.results.get('rss_pipeline'):
            rss_results = self.results['rss_pipeline']
            self.logger.info(f"\nRSS Security Feeds Pipeline:")
            self.logger.info(f"  Status: {'✓ SUCCESS' if rss_results.get('success') else '✗ FAILED'}")
            
            if rss_results.get('extract'):
                total_extracted = sum(rss_results['extract'].values())
                self.logger.info(f"  Extracted: {total_extracted} entries")
            
            if rss_results.get('transform'):
                total_transformed = sum(rss_results['transform'].values())
                self.logger.info(f"  Transformed: {total_transformed} entries")
            
            if rss_results.get('load'):
                total_inserted = sum(stats['inserted'] for stats in rss_results['load'].values())
                total_updated = sum(stats['updated'] for stats in rss_results['load'].values())
                self.logger.info(f"  Loaded: {total_inserted} inserted, {total_updated} updated")
        
        # Errors
        if self.results['errors']:
            self.logger.error(f"\nErrors ({len(self.results['errors'])}):")
            for error in self.results['errors']:
                self.logger.error(f"  • {error}")
        else:
            self.logger.info(f"\n✓ Pipeline completed successfully with no errors")
        
        self.logger.info("\n" + "=" * 80)


def load_config_from_env() -> Dict:
    """
    Load configuration from environment variables
    
    Returns:
        Configuration dictionary
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    config = {
        'mongo_uri': os.getenv('MONGO_URI'),
        'db_name': os.getenv('DB_NAME', 'certat_intelligence_db'),
        'max_records_csv': int(os.getenv('MAX_RECORDS_CSV', '100')),
        'max_records_rss': int(os.getenv('MAX_RECORDS_RSS', '100')),
        'csv_data_dir': os.getenv('CSV_DATA_DIR', 'data'),
        'run_csv': os.getenv('RUN_CSV_PIPELINE', 'true').lower() == 'true',
        'run_rss': os.getenv('RUN_RSS_PIPELINE', 'true').lower() == 'true',
        'clean_before': os.getenv('CLEAN_BEFORE_LOAD', 'true').lower() == 'true',
        'use_upsert': os.getenv('USE_UPSERT', 'false').lower() == 'true',
        'log_level': logging.INFO
    }
    
    # Validate required config
    if not config['mongo_uri']:
        raise ValueError("MONGO_URI environment variable is required!")
    
    # Parse specific RSS feeds if provided
    rss_feeds_env = os.getenv('RSS_FEEDS', '')
    if rss_feeds_env:
        config['rss_feeds'] = [f.strip() for f in rss_feeds_env.split(',')]
    
    return config


def main():
    """Main entry point"""
    try:
        # Load configuration
        config = load_config_from_env()
        
        # Create and run orchestrator
        orchestrator = ETLOrchestrator(config)
        results = orchestrator.run()
        
        # Exit with appropriate code
        if results['errors']:
            sys.exit(1)
        else:
            sys.exit(0)
    
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()