from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class Metadata(BaseModel):
    """Parsed link metadata."""

    url: str = Field(..., description="Canonical URL after redirects.")
    title: Optional[str] = Field(None, description="Page title.")
    description: Optional[str] = Field(None, description="Page description.")
    image: Optional[str] = Field(None, description="Primary image URL (absolute).")
    site_name: Optional[str] = Field(None, description="Site name.")
    type: Optional[str] = Field(None, description="Content type (e.g., 'website').")
    twitter_card: Optional[str] = Field(None, description="Twitter card type.")
    raw: Dict[str, Any] = Field(default_factory=dict, description="All source data for debugging.")

    model_config = {
        "extra": "forbid",
    }


Metadata.update_forward_refs()
