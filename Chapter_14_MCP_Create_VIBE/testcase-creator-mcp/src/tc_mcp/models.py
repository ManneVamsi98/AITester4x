"""Pydantic models: enums, test case records, filters, drafts and changes."""

from __future__ import annotations

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, Field


class Priority(str, Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"
    Highest = "Highest"


class TestType(str, Enum):
    Functional = "Functional"
    Negative = "Negative"
    UI_UX = "UI/UX"
    API = "API"
    Boundary = "Boundary"
    Regression = "Regression"
    Security = "Security"
    Accessibility = "Accessibility"
    Performance = "Performance"


class Status(str, Enum):
    Ready = "Ready"
    Automated = "Automated"
    Draft = "Draft"
    Deprecated = "Deprecated"


Browser = Literal["Chrome 148", "Firefox 141", "Safari 19", "Edge 148"]
Device = Literal["desktop", "mobile (Android)", "mobile (iOS)", "tablet"]

BROWSERS: list[str] = ["Chrome 148", "Firefox 141", "Safari 19", "Edge 148"]
DEVICES: list[str] = ["desktop", "mobile (Android)", "mobile (iOS)", "tablet"]
PRIORITIES: list[str] = [p.value for p in Priority]
TEST_TYPES: list[str] = [t.value for t in TestType]
STATUSES: list[str] = [s.value for s in Status]


class TestCase(BaseModel):
    """A single normalized test case row."""

    issue_key: str
    summary: str
    description: str
    priority: Priority
    module: str
    feature: str
    labels: list[str] = Field(default_factory=list)
    test_type: TestType
    preconditions: str
    steps: list[str] = Field(default_factory=list)
    expected_result: str
    browser: str
    device: str
    status: Status
    scenario_id: str = ""

    def to_compact(self) -> dict:
        return {
            "key": self.issue_key,
            "summary": self.summary,
            "module": self.module,
            "feature": self.feature,
            "priority": self.priority.value,
            "test_type": self.test_type.value,
            "status": self.status.value,
            "browser": self.browser,
            "device": self.device,
        }

    def to_full(self) -> dict:
        row = self.to_compact()
        row.update(
            {
                "description": self.description,
                "preconditions": self.preconditions,
                "steps": self.steps,
                "expected_result": self.expected_result,
                "labels": self.labels,
            }
        )
        return row

    @property
    def live(self) -> bool:
        return self.status != Status.Deprecated


class TestFilter(BaseModel):
    """Shared filter applied by search, stats, effort estimation and export."""

    __test__ = False

    module: Optional[str] = None
    modules: Optional[list[str]] = None
    feature: Optional[str] = None
    priority: Optional[list[Priority]] = None
    min_priority: Optional[Priority] = None
    max_priority: Optional[Priority] = None
    test_type: Optional[list[TestType]] = None
    browser: Optional[Browser] = None
    device: Optional[Device] = None
    status: Optional[list[Status]] = None
    label: Optional[str] = None
    include_deprecated: bool = False
    include_duplicates: bool = True


class TestCaseDraft(BaseModel):
    """A new test case to be validated and added to the overlay."""

    summary: str
    description: str
    priority: Priority
    module: str
    test_type: TestType
    preconditions: str
    steps: list[str]
    expected_result: str
    browser: Browser = "Chrome 148"
    device: Device = "desktop"
    labels: list[str] = Field(default_factory=list)


class TestCaseChanges(BaseModel):
    """Fields that may be updated on an existing test case."""

    status: Optional[Status] = None
    priority: Optional[Priority] = None
    steps: Optional[list[str]] = None
    expected_result: Optional[str] = None
    summary: Optional[str] = None
    description: Optional[str] = None
    browser: Optional[Browser] = None
    device: Optional[Device] = None
