from datetime import datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, validator


class ParagraphBase(BaseModel):
    text: str = Field(..., min_length=1, description="The paragraph text")


class ParagraphCreate(ParagraphBase):
    pass


class ParagraphResponse(ParagraphBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class FetchResponse(BaseModel):
    paragraph: ParagraphResponse
    message: str = "Paragraph fetched and stored successfully"


class SearchRequest(BaseModel):
    words: List[str] = Field(..., min_items=1, max_items=50, description="List of words to search for")
    operator: Literal["and", "or"] = Field(..., description="Search operator: 'and' or 'or'")
    
    @validator('words')
    def validate_words(cls, v):
        if not v:
            raise ValueError("At least one word must be provided")
        
        # Remove empty strings and duplicates
        words = list(set(word.strip().lower() for word in v if word.strip()))
        if not words:
            raise ValueError("At least one non-empty word must be provided")
        
        return words


class SearchResponse(BaseModel):
    paragraphs: List[ParagraphResponse]
    total_count: int
    search_terms: List[str]
    operator: str


class WordDefinition(BaseModel):
    word: str
    frequency: int
    definition: Optional[str] = None
    pronunciation: Optional[str] = None
    part_of_speech: Optional[str] = None


class DictionaryResponse(BaseModel):
    words: List[WordDefinition]
    total_paragraphs_analyzed: int
    message: str = "Top 10 most frequent words with definitions"


class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime
    database_connected: bool
    version: str = "1.0.0"


class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)