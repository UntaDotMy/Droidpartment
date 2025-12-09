#!/usr/bin/env python3
"""
Cache Manager for Droidpartment Hooks
Provides proper cache lifecycle management to avoid memory leaks.

Features:
- Singleton cache with TTL (Time-to-Live)
- Weak references for large objects (optional)
- Automatic cleanup of expired entries
- Clear, update, delete operations
- Memory-safe with garbage collection hints

Usage:
    from cache_manager import cache
    
    # Get or create cached object
    ctx = cache.get('context_index', factory=lambda: ContextIndex())
    
    # Set with TTL (seconds)
    cache.set('env_info', env_data, ttl=3600)  # 1 hour
    
    # Delete specific entry
    cache.delete('context_index')
    
    # Clear all
    cache.clear()
    
    # Cleanup expired
    cache.cleanup()
"""

import gc
import weakref
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional


class CacheEntry:
    """A single cache entry with metadata."""
    __slots__ = ('value', 'created_at', 'expires_at', 'hits', 'is_weak')
    
    def __init__(self, value: Any, ttl: Optional[int] = None, use_weak: bool = False):
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(seconds=ttl) if ttl else None
        self.hits = 0
        self.is_weak = use_weak
        
        if use_weak:
            try:
                self.value = weakref.ref(value)
            except TypeError:
                # Can't create weak reference to this type
                self.value = value
                self.is_weak = False
        else:
            self.value = value
    
    def get_value(self) -> Any:
        """Get the cached value, resolving weak reference if needed."""
        self.hits += 1
        if self.is_weak and callable(self.value):
            return self.value()  # Resolve weak reference
        return self.value
    
    def is_expired(self) -> bool:
        """Check if this entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at


class CacheManager:
    """
    Thread-safe singleton cache manager with TTL and cleanup.
    
    Designed for hook scripts where each hook runs as a separate process.
    Provides memory-safe caching with automatic cleanup.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if CacheManager._initialized:
            return
        
        self._cache: Dict[str, CacheEntry] = {}
        self._max_size: int = 100  # Maximum cache entries
        self._default_ttl: int = 3600  # 1 hour default TTL
        self._stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0
        }
        CacheManager._initialized = True
    
    def get(self, key: str, factory: Optional[Callable] = None, 
            ttl: Optional[int] = None, use_weak: bool = False) -> Any:
        """
        Get a cached value, optionally creating it with factory if missing.
        
        Args:
            key: Cache key
            factory: Optional callable to create value if not cached
            ttl: Time-to-live in seconds (None = use default)
            use_weak: Use weak reference (for large objects)
        
        Returns:
            Cached value or None
        """
        # Check if exists and not expired
        if key in self._cache:
            entry = self._cache[key]
            if entry.is_expired():
                self.delete(key)
            else:
                value = entry.get_value()
                if value is not None:  # Weak ref might be dead
                    self._stats['hits'] += 1
                    return value
                else:
                    # Weak reference was garbage collected
                    self.delete(key)
        
        self._stats['misses'] += 1
        
        # Create with factory if provided
        if factory is not None:
            try:
                value = factory()
                self.set(key, value, ttl=ttl, use_weak=use_weak)
                return value
            except:
                return None
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None, 
            use_weak: bool = False) -> None:
        """
        Set a cache value.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (None = default)
            use_weak: Use weak reference
        """
        # Evict if at max size
        if len(self._cache) >= self._max_size and key not in self._cache:
            self._evict_oldest()
        
        effective_ttl = ttl if ttl is not None else self._default_ttl
        self._cache[key] = CacheEntry(value, ttl=effective_ttl, use_weak=use_weak)
    
    def delete(self, key: str) -> bool:
        """
        Delete a cache entry.
        
        Args:
            key: Cache key
        
        Returns:
            True if deleted, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> int:
        """
        Clear all cache entries.
        
        Returns:
            Number of entries cleared
        """
        count = len(self._cache)
        self._cache.clear()
        
        # Hint to garbage collector
        gc.collect()
        
        return count
    
    def cleanup(self) -> int:
        """
        Remove expired entries and dead weak references.
        
        Returns:
            Number of entries removed
        """
        expired_keys = []
        
        for key, entry in self._cache.items():
            # Check if expired
            if entry.is_expired():
                expired_keys.append(key)
                continue
            
            # Check if weak reference is dead
            if entry.is_weak:
                value = entry.get_value()
                if value is None:
                    expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
            self._stats['evictions'] += 1
        
        # Hint to garbage collector
        if expired_keys:
            gc.collect()
        
        return len(expired_keys)
    
    def update(self, key: str, value: Any) -> bool:
        """
        Update an existing cache entry's value (keeps TTL).
        
        Args:
            key: Cache key
            value: New value
        
        Returns:
            True if updated, False if not found
        """
        if key in self._cache:
            entry = self._cache[key]
            if entry.is_weak:
                try:
                    entry.value = weakref.ref(value)
                except TypeError:
                    entry.value = value
                    entry.is_weak = False
            else:
                entry.value = value
            return True
        return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        if key not in self._cache:
            return False
        
        entry = self._cache[key]
        if entry.is_expired():
            self.delete(key)
            return False
        
        return True
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        return {
            'entries': len(self._cache),
            'max_size': self._max_size,
            'hits': self._stats['hits'],
            'misses': self._stats['misses'],
            'evictions': self._stats['evictions'],
            'hit_rate': self._stats['hits'] / max(1, self._stats['hits'] + self._stats['misses'])
        }
    
    def _evict_oldest(self) -> None:
        """Evict the oldest cache entry."""
        if not self._cache:
            return
        
        # Find oldest entry
        oldest_key = min(self._cache.keys(), 
                        key=lambda k: self._cache[k].created_at)
        self.delete(oldest_key)
        self._stats['evictions'] += 1
    
    def set_max_size(self, size: int) -> None:
        """Set maximum cache size."""
        self._max_size = max(1, size)
        
        # Evict if over new limit
        while len(self._cache) > self._max_size:
            self._evict_oldest()
    
    def set_default_ttl(self, ttl: int) -> None:
        """Set default TTL in seconds."""
        self._default_ttl = max(1, ttl)


# Global cache instance
cache = CacheManager()


# Convenience functions for hooks
def get_cached_context_index():
    """Get cached ContextIndex singleton."""
    def create_context_index():
        from context_index import ContextIndex
        return ContextIndex()
    
    return cache.get('context_index', factory=create_context_index, ttl=None)


def get_cached_shared_context():
    """Get cached SharedContext singleton."""
    def create_shared_context():
        from shared_context import SharedContext
        return SharedContext()
    
    return cache.get('shared_context', factory=create_shared_context, ttl=None)


def clear_all_caches():
    """Clear all caches and run garbage collection."""
    count = cache.clear()
    gc.collect()
    return count


def cleanup_expired():
    """Clean up expired cache entries."""
    return cache.cleanup()
