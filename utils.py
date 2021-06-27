import json
import gzip
import base64
import uuid
from discord import Message, User


def list_chunk(lst, n):
    return [lst[i : i + n] for i in range(0, len(lst), n)]


def dump_data(data):
    step1 = json.dumps(data, separators=(",", ":"))
    step2 = gzip.compress(step1.encode())
    step3 = base64.b85encode(step2).decode()
    return step3


def make_buttons(elements, data):
    if len(elements) * 100 - 10 < len(data):
        raise ValueError

    splited_elements = list_chunk(elements, 5)
    splited_data = list_chunk("PSTA_" + data + "_PEND", 100)

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


def parse_components(raw_components):
    components = []

    for row in raw_components:
        for component in row["components"]:
            components.append(
                {"label": component["label"], "id": component["custom_id"]}
            )

    return components


def parse_msg(data, state):
    channel = state._get_guild_channel(data)
    message = Message(channel=channel, data=data["message"], state=state)

    if data.get("user"):
        user = User(state=state, data=data["user"])
    else:
        user = User(state=state, data=data["member"]["user"])

    custom_id = data["data"]["custom_id"]
    components = parse_components(data["message"]["components"])

    interaction_id = data["id"]
    interaction_token = data["token"]

    return message, user, custom_id, components, interaction_id, interaction_token


def parse_data(components):
    step1 = "".join(map(lambda x: x["id"], components))
    index = step1.find("_PEND")

    if not step1.startswith("PSTA_") or index == -1:
        return None

    step2 = step1[5:index]
    step3 = base64.b85decode(step2)
    step4 = gzip.decompress(step3)
    step5 = json.loads(step4)
    return step5
