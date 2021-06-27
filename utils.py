import json
import gzip
import base64
import uuid


def list_chunk(lst, n):
    return [lst[i : i + n] for i in range(0, len(lst), n)]


def dump_data(data):
    step1 = json.dumps(data, separators=(",", ":"))
    step2 = gzip.compress(step1.encode())
    step3 = base64.b85encode(step2).decode()
    return step3


def make_buttons(elements, data):
    if len(elements) * 100 - 5 < len(data):
        raise ValueError

    splited_elements = list_chunk(elements, 5)
    splited_data = list_chunk("POLL_" + data, 100)

    splited_data.reverse()
    components = []

    for i in splited_elements:
        buttons = []

        for j in i:
            try:
                custom_id = splited_data.pop()
            except IndexError:
                custom_id = uuid.uuid4().hex

            buttons.append(
                {
                    "type": 2,
                    "style": 1,
                    "custom_id": custom_id,
                    "label": j,
                }
            )

        components.append({"type": 1, "components": buttons})
    return components
