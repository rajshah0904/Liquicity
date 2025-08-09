"""
Performance Optimization Module
Advanced caching, connection pooling, and optimization techniques
for high-performance crypto payment processing
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal
import aioredis
import aiohttp
from functools import wraps
import hashlib
import pickle
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import threading
from collections import defaultdict, OrderedDict
import weakref

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    HYBRID = "hybrid"

class OptimizationLevel(Enum):
    BASIC = "basic"
    ADVANCED = "advanced"
    AGGRESSIVE = "aggressive"

@dataclass
class CacheConfig:
    strategy: CacheStrategy
    max_size: int = 1000
    ttl: int = 300  # 5 minutes
    cleanup_interval: int = 60  # 1 minute
    compression: bool = True
    serialization: str = "json"  # json, pickle, msgpack

@dataclass
class PerformanceMetrics:
    request_count: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    avg_response_time: float = 0.0
    error_rate: float = 0.0
    throughput: float = 0.0
    memory_usage: float = 0.0

class LRUCache:
    """
    Least Recently Used cache implementation
    """
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.lock = threading.Lock()
    
    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key in self.cache:
                # Move to end (most recently used)
                self.cache.move_to_end(key)
                return self.cache[key]
            return None
    
    def put(self, key: str, value: Any):
        with self.lock:
            if key in self.cache:
                # Update existing
                self.cache.move_to_end(key)
                self.cache[key] = value
            else:
                # Add new
                self.cache[key] = value
                if len(self.cache) > self.max_size:
                    # Remove least recently used
                    self.cache.popitem(last=False)
    
    def clear(self):
        with self.lock:
            self.cache.clear()
    
    def size(self) -> int:
        return len(self.cache)

class AsyncConnectionPool:
    """
    Async connection pool for HTTP and database connections
    """
    
    def __init__(self, max_connections: int = 100, max_keepalive: int = 20):
        self.max_connections = max_connections
        self.max_keepalive = max_keepalive
        self.session = None
        self.redis_pool = None
        self._lock = asyncio.Lock()
    
    async def get_http_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session with connection pooling"""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=self.max_connections,
                limit_per_host=20,
                keepalive_timeout=30,
                enable_cleanup_closed=True
            )
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={"User-Agent": "Liquicity-Payment-API/1.0"}
            )
        return self.session
    
    async def get_redis_pool(self, redis_url: str) -> aioredis.Redis:
        """Get or create Redis connection pool"""
        if self.redis_pool is None:
            self.redis_pool = aioredis.from_url(
                redis_url,
                max_connections=self.max_connections,
                encoding="utf-8",
                decode_responses=True
            )
        return self.redis_pool
    
    async def close(self):
        """Close all connections"""
        if self.session and not self.session.closed:
            await self.session.close()
        if self.redis_pool:
            await self.redis_pool.close()

class PerformanceOptimizer:
    """
    Main performance optimization service
    """
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache = LRUCache(config.max_size)
        self.connection_pool = AsyncConnectionPool()
        self.metrics = PerformanceMetrics()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.process_executor = ProcessPoolExecutor(max_workers=4)
        
        # Cache for different data types
        self.caches = {
            "gas_estimates": LRUCache(500),
            "wallet_sessions": LRUCache(1000),
            "transaction_data": LRUCache(2000),
            "bridge_responses": LRUCache(1000),
            "user_data": LRUCache(5000),
        }
        
        # Background tasks
        self.background_tasks = []
        self.running = True
        
        # Start background cleanup
        asyncio.create_task(self._cleanup_cache())
        asyncio.create_task(self._update_metrics())
    
    async def _cleanup_cache(self):
        """Background cache cleanup task"""
        while self.running:
            await asyncio.sleep(self.config.cleanup_interval)
            
            # Clean expired entries
            current_time = time.time()
            for cache_name, cache in self.caches.items():
                # This would implement TTL cleanup for TTL strategy
                pass
    
    async def _update_metrics(self):
        """Background metrics update task"""
        while self.running:
            await asyncio.sleep(60)  # Update every minute
            
            # Calculate cache hit rate
            total_requests = self.metrics.cache_hits + self.metrics.cache_misses
            if total_requests > 0:
                hit_rate = self.metrics.cache_hits / total_requests
                logger.info(f"Cache hit rate: {hit_rate:.2%}")
    
    def cache_decorator(self, cache_name: str, ttl: int = None):
        """
        Decorator for caching function results
        """
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Try to get from cache
                cached_result = self.caches[cache_name].get(cache_key)
                if cached_result is not None:
                    self.metrics.cache_hits += 1
                    return cached_result
                
                # Cache miss, execute function
                self.metrics.cache_misses += 1
                result = await func(*args, **kwargs)
                
                # Store in cache
                self.caches[cache_name].put(cache_key, result)
                
                return result
            return wrapper
        return decorator
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate unique cache key"""
        key_data = {
            "func": func_name,
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    async def batch_process(self, items: List[Any], processor: Callable, batch_size: int = 10):
        """
        Process items in batches for better performance
        """
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_tasks = [processor(item) for item in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)
        return results
    
    async def parallel_process(self, items: List[Any], processor: Callable, max_workers: int = 10):
        """
        Process items in parallel using thread pool
        """
        loop = asyncio.get_event_loop()
        tasks = []
        
        for item in items:
            task = loop.run_in_executor(self.executor, processor, item)
            tasks.append(task)
        
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def optimize_gas_estimation(self, chain_id: str, from_address: str, to_address: str, amount: str):
        """
        Optimized gas estimation with caching and parallel processing
        """
        cache_key = f"gas_{chain_id}_{from_address}_{to_address}_{amount}"
        
        # Check cache first
        cached_estimate = self.caches["gas_estimates"].get(cache_key)
        if cached_estimate:
            return cached_estimate
        
        # Get gas estimates from multiple sources in parallel
        gas_sources = [
            self._get_etherscan_gas(chain_id),
            self._get_eth_gas_station_gas(chain_id),
            self._get_chainlink_gas(chain_id),
        ]
        
        gas_estimates = await asyncio.gather(*gas_sources, return_exceptions=True)
        
        # Filter out errors and calculate optimal estimate
        valid_estimates = [est for est in gas_estimates if not isinstance(est, Exception)]
        
        if valid_estimates:
            # Use median for stability
            optimal_estimate = self._calculate_optimal_gas(valid_estimates)
            
            # Cache the result
            self.caches["gas_estimates"].put(cache_key, optimal_estimate)
            
            return optimal_estimate
        
        # Fallback to default estimate
        return self._get_default_gas_estimate(chain_id)
    
    async def _get_etherscan_gas(self, chain_id: str):
        """Get gas estimate from Etherscan API"""
        try:
            session = await self.connection_pool.get_http_session()
            async with session.get(f"https://api.etherscan.io/api?module=gastracker&action=gasoracle") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "source": "etherscan",
                        "safe": int(data["result"]["SafeGasPrice"]),
                        "standard": int(data["result"]["ProposeGasPrice"]),
                        "fast": int(data["result"]["FastGasPrice"])
                    }
        except Exception as e:
            logger.warning(f"Etherscan gas estimation failed: {e}")
            return None
    
    async def _get_eth_gas_station_gas(self, chain_id: str):
        """Get gas estimate from ETH Gas Station"""
        try:
            session = await self.connection_pool.get_http_session()
            async with session.get("https://ethgasstation.info/api/ethgasAPI.json") as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "source": "ethgasstation",
                        "safe": int(data["safe"] / 10),
                        "standard": int(data["average"] / 10),
                        "fast": int(data["fast"] / 10)
                    }
        except Exception as e:
            logger.warning(f"ETH Gas Station estimation failed: {e}")
            return None
    
    async def _get_chainlink_gas(self, chain_id: str):
        """Get gas estimate from Chainlink oracle"""
        # This would integrate with Chainlink gas oracle
        return None
    
    def _calculate_optimal_gas(self, estimates: List[Dict]) -> Dict:
        """Calculate optimal gas estimate from multiple sources"""
        if not estimates:
            return {"gas_price": 20, "gas_limit": 21000}
        
        # Calculate median for each gas level
        safe_prices = [est["safe"] for est in estimates if "safe" in est]
        standard_prices = [est["standard"] for est in estimates if "standard" in est]
        fast_prices = [est["fast"] for est in estimates if "fast" in est]
        
        return {
            "gas_price": self._median(standard_prices) if standard_prices else 20,
            "gas_limit": 21000,  # Default gas limit
            "safe": self._median(safe_prices) if safe_prices else 15,
            "standard": self._median(standard_prices) if standard_prices else 20,
            "fast": self._median(fast_prices) if fast_prices else 25
        }
    
    def _median(self, values: List[int]) -> int:
        """Calculate median of values"""
        if not values:
            return 0
        sorted_values = sorted(values)
        n = len(sorted_values)
        if n % 2 == 0:
            return (sorted_values[n//2 - 1] + sorted_values[n//2]) // 2
        else:
            return sorted_values[n//2]
    
    def _get_default_gas_estimate(self, chain_id: str) -> Dict:
        """Get default gas estimate for chain"""
        defaults = {
            "ethereum": {"gas_price": 20, "gas_limit": 21000},
            "polygon": {"gas_price": 30, "gas_limit": 21000},
            "base": {"gas_price": 0.001, "gas_limit": 21000},
            "solana": {"gas_price": 0.00025, "gas_limit": 1}
        }
        return defaults.get(chain_id, {"gas_price": 20, "gas_limit": 21000})
    
    async def optimize_transaction_building(self, transaction_data: Dict[str, Any]):
        """
        Optimize transaction building process
        """
        # Parallel processing for transaction components
        tasks = [
            self._optimize_gas_estimation(transaction_data),
            self._validate_addresses(transaction_data),
            self._check_balance(transaction_data),
            self._get_nonce(transaction_data)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        gas_estimate, address_validation, balance_check, nonce = results
        
        if isinstance(gas_estimate, Exception):
            gas_estimate = self._get_default_gas_estimate(transaction_data.get("chain_id", "ethereum"))
        
        return {
            "gas_estimate": gas_estimate,
            "address_valid": not isinstance(address_validation, Exception),
            "sufficient_balance": not isinstance(balance_check, Exception),
            "nonce": nonce if not isinstance(nonce, Exception) else 0
        }
    
    async def _optimize_gas_estimation(self, transaction_data: Dict[str, Any]):
        """Optimized gas estimation for transaction"""
        return await self.optimize_gas_estimation(
            transaction_data.get("chain_id", "ethereum"),
            transaction_data.get("from_address", ""),
            transaction_data.get("to_address", ""),
            transaction_data.get("amount", "0")
        )
    
    async def _validate_addresses(self, transaction_data: Dict[str, Any]):
        """Validate addresses in parallel"""
        from_address = transaction_data.get("from_address", "")
        to_address = transaction_data.get("to_address", "")
        chain_id = transaction_data.get("chain_id", "ethereum")
        
        # Validate both addresses in parallel
        tasks = [
            self._validate_single_address(from_address, chain_id),
            self._validate_single_address(to_address, chain_id)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return all(not isinstance(r, Exception) for r in results)
    
    async def _validate_single_address(self, address: str, chain_id: str):
        """Validate single address"""
        # This would implement address validation logic
        return True
    
    async def _check_balance(self, transaction_data: Dict[str, Any]):
        """Check balance asynchronously"""
        # This would implement balance checking logic
        return True
    
    async def _get_nonce(self, transaction_data: Dict[str, Any]):
        """Get nonce asynchronously"""
        # This would implement nonce retrieval logic
        return 0
    
    async def optimize_bridge_api_calls(self, api_calls: List[Dict[str, Any]]):
        """
        Optimize Bridge API calls with batching and caching
        """
        # Group API calls by type for batching
        grouped_calls = defaultdict(list)
        for call in api_calls:
            grouped_calls[call["type"]].append(call)
        
        # Process each group in parallel
        tasks = []
        for call_type, calls in grouped_calls.items():
            if call_type == "transfer":
                task = self._batch_transfer_calls(calls)
            elif call_type == "balance":
                task = self._batch_balance_calls(calls)
            else:
                task = self._process_single_calls(calls)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Flatten results
        all_results = []
        for result in results:
            if isinstance(result, list):
                all_results.extend(result)
            else:
                all_results.append(result)
        
        return all_results
    
    async def _batch_transfer_calls(self, calls: List[Dict[str, Any]]):
        """Batch transfer API calls"""
        # This would implement batch transfer logic
        return [{"status": "success"} for _ in calls]
    
    async def _batch_balance_calls(self, calls: List[Dict[str, Any]]):
        """Batch balance API calls"""
        # This would implement batch balance logic
        return [{"balance": "100.00"} for _ in calls]
    
    async def _process_single_calls(self, calls: List[Dict[str, Any]]):
        """Process single API calls in parallel"""
        tasks = [self._make_api_call(call) for call in calls]
        return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _make_api_call(self, call: Dict[str, Any]):
        """Make individual API call"""
        # This would implement actual API call logic
        return {"status": "success"}
    
    def get_performance_metrics(self) -> PerformanceMetrics:
        """Get current performance metrics"""
        return self.metrics
    
    async def cleanup(self):
        """Cleanup resources"""
        self.running = False
        await self.connection_pool.close()
        self.executor.shutdown(wait=True)
        self.process_executor.shutdown(wait=True)

# Initialize performance optimizer
performance_optimizer = PerformanceOptimizer(
    CacheConfig(
        strategy=CacheStrategy.HYBRID,
        max_size=5000,
        ttl=300,
        compression=True
    )
) 