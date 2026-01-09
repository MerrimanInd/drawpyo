from drawpyo.diagram import Object, Edge
import json


def redact_text(text: str | None) -> str | None:
    if text is None:
        return None
    return "".join(ch if ch.isspace() else "X" for ch in text)


def redact_values(diagram, map_file_path):
    id_value_map: dict[str, str] = {}

    for node in diagram.shapes + diagram.edges:
        if isinstance(node, Object):
            if node.value is None:
                continue
            id_value_map[node.id] = node.value
            node.value = redact_text(node.value)

        elif isinstance(node, Edge):
            if node.label is None:
                continue
            id_value_map[node.id] = node.label
            node.label = redact_text(node.label)

    with open(map_file_path, "w", encoding="utf-8") as f:
        json.dump(
            id_value_map,
            f,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )

    return diagram
