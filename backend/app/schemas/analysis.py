from pydantic import BaseModel


class AnalyzeResponse(BaseModel):
    analysis_id: str
    delegate_id: str
    filename: str
    risk_level: str
    result: dict


class EmbeddingStatsResponse(BaseModel):
    delegate_id: str
    document_count: int
    centroid: list[float]
    normal_range: dict
    cluster_points: list[dict]

