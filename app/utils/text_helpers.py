def get_status_color(status: str) -> str:
    color = ""
    match status:
        case "downloading":
            color = "#3B82F6"
        case "completed":
            color = "#2C9F4B"
        case "failed":
            color = "#EF4444"
        case "cancelled":
            color = "#F59E0B"
        case _:  # pending actua como default
            color = "#000000"
    return color
