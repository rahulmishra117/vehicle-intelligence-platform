import re

from app.inspections.repository import InspectionRepository


CATEGORIES = {
    "engine": ("engine", "motor", "oil leak", "overheating"),
    "transmission": ("transmission", "gearbox", "clutch"),
    "brakes": ("brake", "brakes"),
    "body": ("body", "dent", "paint", "rust", "accident"),
    "electrical": ("electrical", "battery", "alternator", "wiring"),
    "tyres": ("tyre", "tyres", "tire", "tires"),
    "suspension": ("suspension", "shock absorber"),
}


class NaturalLanguageQueryService:
    """Auditable natural-language parser for inspection-domain questions."""

    def __init__(self, repository: InspectionRepository):
        self.repository = repository

    def execute(self, query: str, limit: int = 20) -> dict:
        intent, filters = self.interpret(query)
        results = self.repository.search(filters, limit)
        return {
            "answer": self._answer(intent, results),
            "interpretation": {"intent": intent, "filters": filters},
            "results": results,
            "count": len(results),
        }

    def interpret(self, query: str) -> tuple[str, dict]:
        text = query.lower().strip()
        filters: dict[str, str | int] = {}
        vehicle = re.search(r"\b(?:vehicle|car)?\s*#?([a-z]{2,10}-?\d{2,10})\b", text, re.I)
        if vehicle:
            filters["vehicle_id"] = vehicle.group(1).upper()
        for decision in ("rejected", "approved", "review"):
            if decision in text:
                filters["decision"] = decision
                break
        for severity in ("critical", "major", "minor"):
            if severity in text:
                filters["severity"] = severity
                break
        for category, aliases in CATEGORIES.items():
            if any(re.search(rf"\b{re.escape(alias)}\b", text) for alias in aliases):
                filters["category"] = category
                break

        if any(word in text for word in ("why", "reason")):
            intent = "explain_decision"
        elif any(word in text for word in ("summarize", "summary", "overview")):
            intent = "summarize_inspection"
        else:
            intent = "search_inspections"
        return intent, filters

    @staticmethod
    def _answer(intent: str, results: list[dict]) -> str:
        if not results:
            return "No inspections matched the interpreted filters."
        if intent == "explain_decision" and len(results) == 1:
            item = results[0]
            blocking = [issue for issue in item["issues"] if issue["severity"] in ("major", "critical")]
            reasons = "; ".join(f'{issue["component"]}: {issue["description"]}' for issue in blocking)
            reasons = reasons or item["notes"] or "No explicit rejection reason was recorded."
            return f'{item["vehicle_id"]} was marked {item["decision"]}. Key reasons: {reasons}'
        if intent == "summarize_inspection" and len(results) == 1:
            item = results[0]
            cost = sum(issue["repair_cost"] for issue in item["issues"])
            severities = ", ".join(issue["severity"] for issue in item["issues"]) or "none"
            return (f'{item["vehicle_id"]}: {item["year"]} {item["make"]} {item["model"]}, '
                    f'{item["decision"]} with {len(item["issues"])} issue(s) '
                    f'({severities}); estimated repairs INR {cost:,.0f}.')
        return f"Found {len(results)} matching inspection(s)."

