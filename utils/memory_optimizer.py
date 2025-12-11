"""
Memory optimization utilities for low-spec systems
"""
import gc
import sys


class MemoryOptimizer:
    """Handles memory optimization for low-spec systems"""

    @staticmethod
    def force_garbage_collection():
        """Force Python garbage collection"""
        gc.collect()

    @staticmethod
    def get_memory_usage():
        """Get approximate memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            # psutil not available, return estimate
            return sys.getsizeof(gc.get_objects()) / 1024 / 1024

    @staticmethod
    def optimize_for_low_memory():
        """Apply optimizations for low-memory systems"""
        # Enable garbage collection
        gc.enable()

        # Set garbage collection thresholds more aggressively
        # (gen0, gen1, gen2) - lower numbers mean more frequent collection
        gc.set_threshold(400, 5, 5)

    @staticmethod
    def clear_unused_cache():
        """Clear Python's internal caches"""
        # Clear method cache
        if hasattr(sys, 'getrefcount'):
            gc.collect()

        # Clear import cache for unused modules
        modules_to_clear = []
        for module_name in list(sys.modules.keys()):
            # Don't clear core modules
            if module_name.startswith('_') or module_name in ['sys', 'gc', 'os']:
                continue

            module = sys.modules.get(module_name)
            if module and hasattr(module, '__file__'):
                ref_count = sys.getrefcount(module)
                # If only referenced by sys.modules and this function
                if ref_count <= 3:
                    modules_to_clear.append(module_name)

        for module_name in modules_to_clear:
            try:
                del sys.modules[module_name]
            except:
                pass

    @staticmethod
    def periodic_cleanup():
        """Perform periodic memory cleanup"""
        gc.collect()
        # Force collection of all generations
        gc.collect(2)


# Global optimizer instance
_optimizer = MemoryOptimizer()


def get_optimizer():
    """Get the memory optimizer instance"""
    return _optimizer
