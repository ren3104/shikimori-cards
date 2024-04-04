from shikithon import ShikimoriAPI
from shikithon.models import History

from typing import Callable


class Check:
    async def check(self, api: ShikimoriAPI, history: History) -> bool:
        raise NotImplementedError

    async def __call__(self, api: ShikimoriAPI, history: History) -> bool:
        return await self.check(api, history)

    def __invert__(self) -> "InvertCheck":
        return InvertCheck(self)

    def __and__(self, other: "Check") -> "AndCheck":
        if isinstance(self, AndCheck):
            self._checks.append(other)
            return self
        return AndCheck(self, other)

    def __or__(self, other: "Check") -> "OrCheck":
        if isinstance(self, OrCheck):
            self._checks.append(other)
            return self
        return OrCheck(self, other)
    

class InvertCheck(Check):
    def __init__(self, check: Check) -> None:
        self._check = check

    async def check(self, api: ShikimoriAPI, history: History) -> bool:
        return not await self._check(api, history)


class AndCheck(Check):
    def __init__(self, *checks: Check) -> None:
        self._checks = list(checks)

    async def check(self, api: ShikimoriAPI, history: History) -> bool:
        for check in self._checks:
            if not await check(api, history):
                return False
        return True


class OrCheck(Check):
    def __init__(self, *checks: Check) -> None:
        self._checks = list(checks)

    async def check(self, api: ShikimoriAPI, history: History) -> bool:
        for check in self._checks:
            if await check(api, history):
                return True
        return False
    

class FuncCheck(Check):
    def __init__(self, func: Callable[[History], bool]) -> None:
        self._func = func
    
    async def check(self, api: ShikimoriAPI, history: History) -> bool:
        return self._func(history)
