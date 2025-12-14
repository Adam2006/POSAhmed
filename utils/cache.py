"""
Simple caching utility for database queries
"""
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json


class QueryCache:
    """Simple LRU cache for database queries"""

    def __init__(self, max_size=100, ttl_seconds=300):
        self.cache = {}
        self.access_times = {}
        self.func_names = {}  # Map hash -> func_name for pattern matching
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds

    def _generate_key(self, func_name, args, kwargs):
        """Generate cache key from function name and arguments"""
        key_dict = {
            'func': func_name,
            'args': str(args),
            'kwargs': str(sorted(kwargs.items()))
        }
        key_str = json.dumps(key_dict, sort_keys=True)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        # Store the function name for this hash
        self.func_names[key_hash] = func_name
        return key_hash

    def _is_expired(self, key):
        """Check if cache entry is expired"""
        if key not in self.access_times:
            return True
        age = datetime.now() - self.access_times[key]
        return age.total_seconds() > self.ttl_seconds

    def _evict_oldest(self):
        """Remove oldest cache entry"""
        if not self.access_times:
            return
        oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        self.cache.pop(oldest_key, None)
        self.access_times.pop(oldest_key, None)
        self.func_names.pop(oldest_key, None)

    def get(self, func_name, args, kwargs):
        """Get cached result"""
        key = self._generate_key(func_name, args, kwargs)

        if key not in self.cache or self._is_expired(key):
            return None

        self.access_times[key] = datetime.now()
        return self.cache[key]

    def set(self, func_name, args, kwargs, result):
        """Cache a result"""
        key = self._generate_key(func_name, args, kwargs)

        # Evict oldest if cache is full
        if len(self.cache) >= self.max_size:
            self._evict_oldest()

        self.cache[key] = result
        self.access_times[key] = datetime.now()

    def invalidate_all(self):
        """Clear entire cache"""
        self.cache.clear()
        self.access_times.clear()
        self.func_names.clear()

    def invalidate_pattern(self, pattern):
        """Invalidate cache entries matching a pattern (e.g., 'Order', 'Employee', 'Client')"""
        keys_to_remove = []
        for key, func_name in self.func_names.items():
            if pattern in func_name:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            self.cache.pop(key, None)
            self.access_times.pop(key, None)
            self.func_names.pop(key, None)


# Global cache instance
# Reduced for low-memory systems (2GB RAM)
_cache = QueryCache(max_size=50, ttl_seconds=120)  # 50 items, 2 minutes TTL


def cached_query(cache_instance=None):
    """Decorator to cache query results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = cache_instance or _cache

            # Generate unique function identifier including module and qualname
            func_id = f"{func.__module__}.{func.__qualname__}"

            # Try to get from cache
            cached_result = cache.get(func_id, args, kwargs)
            if cached_result is not None:
                return cached_result

            # Execute query
            result = func(*args, **kwargs)

            # Cache result
            cache.set(func_id, args, kwargs, result)

            return result
        return wrapper
    return decorator


def invalidate_cache(pattern=None):
    """Invalidate cache entries"""
    if pattern:
        _cache.invalidate_pattern(pattern)
    else:
        _cache.invalidate_all()


def get_cache():
    """Get global cache instance"""
    return _cache
