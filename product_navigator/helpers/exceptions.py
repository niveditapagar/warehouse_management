from fastapi import HTTPException


class NotEnoughInfo(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)

class NotFound(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=404, detail=message)

class CreationError(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)

class InsufficientCapacity(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)

class InsufficientQuantity(HTTPException):
    def __init__(self, message: str):
        super().__init__(status_code=400, detail=message)
