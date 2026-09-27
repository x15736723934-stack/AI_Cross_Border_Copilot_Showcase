"""Safe, deterministic workflow used by the public portfolio edition.

The production-oriented private edition replaces these demo handlers with an
OpenAI-compatible gateway and persists checkpoints per project.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


STEPS = (
    ("positioning", "产品定位"),
    ("persona", "用户画像"),
    ("selling_points", "卖点提炼"),
    ("keywords", "关键词分析"),
    ("listing", "Listing 草稿"),
    ("profit", "利润测算"),
    ("advice", "运营建议"),
    ("report", "Launch Report"),
)


@dataclass(frozen=True)
class ProjectInput:
    name: str
    product: str
    platform: str
    marketplace: str
    price: float


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_run(project: ProjectInput) -> dict[str, Any]:
    """Create a traceable input snapshot instead of reading mutable UI state."""
    return {
        "run_id": uuid4().hex[:12],
        "status": "pending",
        "current_step": None,
        "completed_steps": [],
        "progress": 0,
        "input_snapshot": asdict(project),
        "outputs": {},
        "events": [],
        "updated_at": _now(),
    }


def run_next(state: dict[str, Any]) -> dict[str, Any]:
    """Advance one idempotent demo step and append an observable audit event."""
    completed = set(state["completed_steps"])
    remaining = [(key, label) for key, label in STEPS if key not in completed]
    if not remaining:
        state["status"] = "completed"
        state["current_step"] = None
        state["progress"] = 100
        return state

    key, label = remaining[0]
    project = state["input_snapshot"]
    state["status"] = "running"
    state["current_step"] = key
    state["outputs"][key] = _demo_output(key, project)
    state["completed_steps"].append(key)
    state["progress"] = round(100 * len(state["completed_steps"]) / len(STEPS))
    state["events"].append(
        {"step": key, "label": label, "status": "completed", "timestamp": _now()}
    )
    state["updated_at"] = _now()
    if len(state["completed_steps"]) == len(STEPS):
        state["status"] = "completed"
        state["current_step"] = None
    return state


def _demo_output(step: str, project: dict[str, Any]) -> str:
    product = project["product"] or "示例产品"
    outputs = {
        "positioning": f"为 {project['marketplace']} 市场建立 {product} 的差异化定位。",
        "persona": "核心用户：重视效率、品质与售后体验的线上消费者。",
        "selling_points": "围绕使用场景、关键参数与可信证据组织卖点。",
        "keywords": f"{product}, compact {product}, {product} for home",
        "listing": f"{product} | 场景化标题与结构化卖点草稿",
        "profit": f"售价 ${project['price']:.2f}；利润由本地确定性公式计算。",
        "advice": "先以小预算验证转化，再按搜索词表现迭代内容与投放。",
        "report": "已汇总定位、用户、内容、关键词、利润和运营建议。",
    }
    return outputs[step]

