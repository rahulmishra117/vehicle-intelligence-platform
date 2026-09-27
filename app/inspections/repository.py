import sqlite3

from app.db.database import Database
from app.inspections.schemas import InspectionCreate


class InspectionRepository:
    def __init__(self, database: Database):
        self.database = database

    def create(self, payload: InspectionCreate) -> dict:
        with self.database.connection() as connection:
            cursor = connection.execute(
                """INSERT INTO inspections
                (vehicle_id, make, model, year, odometer_km, inspector, decision, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (payload.vehicle_id, payload.make, payload.model, payload.year,
                 payload.odometer_km, payload.inspector, payload.decision.value, payload.notes),
            )
            inspection_id = cursor.lastrowid
            connection.executemany(
                """INSERT INTO issues
                (inspection_id, category, component, severity, description, repair_cost)
                VALUES (?, ?, ?, ?, ?, ?)""",
                [(inspection_id, issue.category.lower(), issue.component, issue.severity.value,
                  issue.description, issue.repair_cost) for issue in payload.issues],
            )
        return self.get(inspection_id)

    def get(self, inspection_id: int) -> dict | None:
        with self.database.connection() as connection:
            row = connection.execute("SELECT * FROM inspections WHERE id = ?", (inspection_id,)).fetchone()
            return self._hydrate(connection, row) if row else None

    def latest_for_vehicle(self, vehicle_id: str) -> dict | None:
        with self.database.connection() as connection:
            row = connection.execute(
                "SELECT * FROM inspections WHERE vehicle_id = ? ORDER BY inspected_at DESC, id DESC LIMIT 1",
                (vehicle_id,),
            ).fetchone()
            return self._hydrate(connection, row) if row else None

    def search(self, filters: dict, limit: int = 20) -> list[dict]:
        clauses, params = [], []
        issue_filters = {key: filters[key] for key in ("category", "severity", "component") if key in filters}
        for key in ("vehicle_id", "decision", "make", "year"):
            if key in filters:
                clauses.append(f"i.{key} = ?")
                params.append(filters[key])
        for key, value in issue_filters.items():
            if key == "component":
                clauses.append("lower(x.component) LIKE ?")
                params.append(f"%{str(value).lower()}%")
            else:
                clauses.append(f"lower(x.{key}) = ?")
                params.append(str(value).lower())
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"""SELECT DISTINCT i.* FROM inspections i
                  LEFT JOIN issues x ON x.inspection_id = i.id
                  {where} ORDER BY i.inspected_at DESC, i.id DESC LIMIT ?"""
        params.append(limit)
        with self.database.connection() as connection:
            rows = connection.execute(sql, params).fetchall()
            return [self._hydrate(connection, row) for row in rows]

    @staticmethod
    def _hydrate(connection: sqlite3.Connection, row: sqlite3.Row) -> dict:
        inspection = dict(row)
        issues = connection.execute(
            "SELECT * FROM issues WHERE inspection_id = ? ORDER BY id", (row["id"],)
        ).fetchall()
        inspection["issues"] = [
            {key: value for key, value in dict(issue).items() if key != "inspection_id"}
            for issue in issues
        ]
        return inspection

