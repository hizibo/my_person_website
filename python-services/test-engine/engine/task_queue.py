"""
任务队列
asyncio 实现，支持并发控制、优先级抢占、超时自动终止
"""
import asyncio
import uuid
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Callable, Awaitable


class TaskStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PASS = "pass"
    FAIL = "fail"
    STOPPED = "stopped"
    TIMEOUT = "timeout"


class TaskPriority(str, Enum):
    P0 = "P0"  # 可抢占
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


@dataclass
class Task:
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    status: TaskStatus = TaskStatus.QUEUED
    priority: TaskPriority = TaskPriority.P1
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    result: dict = field(default_factory=dict)
    logs: list = field(default_factory=list)
    _cancel_flag: bool = field(default=False, repr=False)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status.value,
            "priority": self.priority.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "result": self.result,
            "duration_ms": int((self.finished_at - self.started_at) * 1000) if self.started_at and self.finished_at else 0,
        }


class TaskQueue:
    def __init__(self, max_concurrent: int = 3, max_size: int = 100, timeout: int = 3600):
        self.max_concurrent = max_concurrent
        self.max_size = max_size
        self.timeout = timeout
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._running: dict[str, asyncio.Task] = {}
        self._tasks: dict[str, Task] = {}
        self._subscribers: dict[str, list[asyncio.Queue]] = {}

    @property
    def running_count(self) -> int:
        return len(self._running)

    @property
    def queued_count(self) -> int:
        return self._queue.qsize()

    def _priority_key(self, task: Task) -> tuple:
        order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
        return (order.get(task.priority.value, 9), task.created_at)

    async def submit(self, task: Task, coro_factory: Callable[[Task], Awaitable]) -> str:
        if self._queue.qsize() >= self.max_size:
            raise ValueError(f"任务队列已满（最大 {self.max_size}）")

        # P0 可抢占：如果有 P1/P2/P3 正在运行且有空位不够
        if task.priority == TaskPriority.P0 and self.running_count >= self.max_concurrent:
            # 尝试找最低优先级任务抢占
            lowest = None
            for tid, asyncio_task in self._running.items():
                t = self._tasks.get(tid)
                if t and t.priority != TaskPriority.P0:
                    if lowest is None or self._priority_key(t) > self._priority_key(lowest):
                        lowest = t
            if lowest:
                await self.cancel(lowest.id)
                self._queue.put_nowait((self._priority_key(lowest), lowest))

        self._tasks[task.id] = task
        await self._queue.put((self._priority_key(task), task))

        # 启动调度
        asyncio.create_task(self._schedule(coro_factory))
        return task.id

    async def _schedule(self, coro_factory: Callable[[Task], Awaitable]):
        while self.running_count < self.max_concurrent and not self._queue.empty():
            _, task = await self._queue.get()
            if task._cancel_flag:
                continue

            task.status = TaskStatus.RUNNING
            task.started_at = time.time()
            self._tasks[task.id] = task

            async def runner(t: Task):
                try:
                    await asyncio.wait_for(coro_factory(t), timeout=self.timeout)
                except asyncio.TimeoutError:
                    t.status = TaskStatus.TIMEOUT
                    t.finished_at = time.time()
                    self._tasks[t.id] = t
                    self._notify(t)
                except asyncio.CancelledError:
                    t.status = TaskStatus.STOPPED
                    t.finished_at = time.time()
                    self._tasks[t.id] = t
                    self._notify(t)
                except Exception as e:
                    t.status = TaskStatus.FAIL
                    t.finished_at = time.time()
                    t.result["error"] = str(e)
                    self._tasks[t.id] = t
                    self._notify(t)
                finally:
                    self._running.pop(t.id, None)
                    asyncio.create_task(self._schedule(coro_factory))

            self._running[task.id] = asyncio.create_task(runner(task))

    async def cancel(self, task_id: str) -> bool:
        task = self._tasks.get(task_id)
        if not task:
            return False

        if task.status == TaskStatus.QUEUED:
            task._cancel_flag = True
            task.status = TaskStatus.STOPPED
            task.finished_at = time.time()
            self._tasks[task_id] = task
            self._notify(task)
            return True

        if task.status == TaskStatus.RUNNING:
            asyncio_task = self._running.get(task_id)
            if asyncio_task:
                asyncio_task.cancel()
            return True

        return False

    def get(self, task_id: str) -> Optional[Task]:
        return self._tasks.get(task_id)

    def list_tasks(self) -> list[dict]:
        return [t.to_dict() for t in self._tasks.values()]

    # ---- WebSocket 推送 ----
    def subscribe(self, task_id: str) -> asyncio.Queue:
        sub = asyncio.Queue()
        self._subscribers.setdefault(task_id, []).append(sub)
        return sub

    def unsubscribe(self, task_id: str, sub: asyncio.Queue):
        subs = self._subscribers.get(task_id, [])
        if sub in subs:
            subs.remove(sub)

    def _notify(self, task: Task):
        for sub in self._subscribers.get(task.id, []):
            try:
                sub.put_nowait(task.to_dict())
            except asyncio.QueueFull:
                pass


# 全局单例
_queue_instance: Optional[TaskQueue] = None


def get_queue(max_concurrent: int = 3, max_size: int = 100, timeout: int = 3600) -> TaskQueue:
    global _queue_instance
    if _queue_instance is None:
        _queue_instance = TaskQueue(
            max_concurrent=max_concurrent,
            max_size=max_size,
            timeout=timeout,
        )
    return _queue_instance
