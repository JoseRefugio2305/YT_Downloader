import app.utils.constants as C


def get_status_color(status: str) -> str:
    color = ""
    match status:
        case C.STATUS_DOWNLOADING:
            color = C.STATUS_COLORS[C.STATUS_DOWNLOADING]
        case C.STATUS_COMPLETED:
            color = C.STATUS_COLORS[C.STATUS_COMPLETED]
        case C.STATUS_FAILED:
            color = C.STATUS_COLORS[C.STATUS_FAILED]
        case C.STATUS_CANCELLED:
            color = C.STATUS_COLORS[C.STATUS_CANCELLED]
        case _:  # pending actua como default
            color = C.STATUS_COLORS[C.STATUS_PENDING]
    return color
