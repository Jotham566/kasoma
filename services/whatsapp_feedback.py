"""Concise post-grade feedback with a protected web continuation link (FR-WA-005)."""

from urllib.parse import urlsplit
from uuid import UUID

from services.assessment_contracts import GradeView
from services.config import require_local
from services.whatsapp_format import MAX_MESSAGE_CHARS, RICH_CONTENT


def feedback_text(
    grade: GradeView,
    session_id: UUID,
    position: int,
    app_public_url: str,
    limit: int = MAX_MESSAGE_CHARS,
) -> str:
    """Caller must authorize the owned, submitted grade; no diagnostic feedback is permitted."""
    if not 1 <= position <= 5 or not 1 <= limit <= MAX_MESSAGE_CHARS:
        raise ValueError("Invalid feedback bounds")
    # The UUID selects an owned session after normal web authentication; it is not a token.
    link = application_origin(app_public_url) + "/revise?session=" + str(session_id)
    prefix = f"Answer {position}/5 saved. Points: {grade.points_awarded}/{grade.points_possible}."
    continuation = (
        "Five answers saved." if position == 5 else "Send CONTINUE for the next question."
    )
    suffix = f"Details and worked solution: {link}\n{continuation}\nSend STOP to stop replies."
    minimal = prefix + "\n" + suffix
    if len(minimal) > limit:
        raise ValueError("Feedback exceeds channel limit")
    # Never truncate academic instructions or send rich content as broken text.
    detail = grade.feedback.next_action.strip()
    complete = prefix + "\n" + detail + "\n" + suffix
    return (
        complete
        if detail and not RICH_CONTENT.search(detail) and len(complete) <= limit
        else minimal
    )


def application_origin(app_public_url: str) -> str:
    url = urlsplit(app_public_url)
    require_local(app_public_url, {"web"})
    if (
        url.scheme not in {"http", "https"}
        or url.username is not None
        or url.password is not None
        or url.query
        or url.fragment
        or url.path not in {"", "/"}
        or any(c.isspace() for c in app_public_url)
    ):
        raise ValueError("Invalid public application origin")
    return app_public_url.rstrip("/")
