"""
Low-memory configuration for systems with 2GB RAM or less
This file contains optimized settings for resource-constrained systems
"""

# Database settings
DATABASE_PATH = "pos_database.db"

# Memory optimization settings
CACHE_MAX_SIZE = 30  # Maximum number of cached queries (reduced from 50)
CACHE_TTL_SECONDS = 90  # Cache time-to-live in seconds (reduced from 120)

# Pagination settings
STATISTICS_PAGE_SIZE = 15  # Items per page in statistics view
HISTORY_PAGE_SIZE = 30  # Items per page in history view
EMPLOYEE_PAGE_SIZE = 20  # Items per page in employee view

# UI settings - Reduce visual effects
ENABLE_ANIMATIONS = False  # Disable animations to save CPU/memory
TABLE_ICON_SIZE = 32  # Smaller icon size (default: 48)
BUTTON_MIN_HEIGHT = 35  # Smaller buttons (default: 40)

# Loading behavior
LAZY_LOAD_ORDER_ITEMS = True  # Don't load order items unless explicitly needed
PRELOAD_IMAGES = False  # Don't preload product images

# Auto-cleanup settings
AUTO_CLEAR_OLD_CACHE = True  # Automatically clear old cache entries
CACHE_CLEANUP_INTERVAL = 60  # Seconds between cache cleanups

# Date range limits (to prevent loading too much data)
MAX_DATE_RANGE_DAYS = 90  # Maximum days that can be loaded at once
DEFAULT_DATE_RANGE_DAYS = 30  # Default date range for reports

# Database query optimization
USE_INDEXED_QUERIES = True  # Ensure all queries use indexes
BATCH_SIZE = 100  # Maximum records to process in a batch

# Logging (reduce file I/O)
LOG_LEVEL = "WARNING"  # Only log warnings and errors
LOG_TO_FILE = False  # Don't write logs to file to save disk I/O

# Print settings
PRINT_QUEUE_SIZE = 5  # Maximum print jobs to queue
