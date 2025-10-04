"""
Background tasks support
"""

from typing import Callable, List, Any, Tuple
import asyncio
import inspect


class BackgroundTasks:
    """
    يدير background tasks
    ينفذ tasks بعد إرسال الـ response
    """
    
    def __init__(self):
        self.tasks: List[Tuple[Callable, tuple, dict]] = []
    
    def add_task(self, func: Callable, *args, **kwargs):
        """
        إضافة task للـ queue
        
        Args:
            func: الـ function المراد تنفيذها
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        self.tasks.append((func, args, kwargs))
    
    async def execute_all(self):
        """
        تنفيذ جميع tasks
        ينفذ tasks بشكل async بعد إرسال الـ response
        """
        for func, args, kwargs in self.tasks:
            try:
                if inspect.iscoroutinefunction(func):
                    await func(*args, **kwargs)
                else:
                    # Run sync function in executor
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(None, lambda: func(*args, **kwargs))
            except Exception as e:
                # Log error but don't fail
                # In production, you'd want proper logging here
                print(f"Background task error: {e}")
