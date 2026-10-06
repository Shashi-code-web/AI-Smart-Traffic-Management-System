from pydantic import BaseModel


class DiagnosticCheck(BaseModel):
    name: str
    ok: bool
    detail: str


class SystemDiagnostics(BaseModel):
    healthy: bool
    checks: list[DiagnosticCheck]
