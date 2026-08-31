from pydantic import BaseModel


class InvestigationRequest(BaseModel):
    case_id: str


class InvestigationResponse(BaseModel):
    investigation_id: str
    case_id: str
    status: str