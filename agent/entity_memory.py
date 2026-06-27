import json
from pathlib import Path

from config.settings import DATA_DIR


class EntityMemory:

    MEMORY_FILE = (
        Path(DATA_DIR)
        / "entity_memory.json"
    )

    @classmethod
    def load_memory(cls):

        if not cls.MEMORY_FILE.exists():
            return {
                "entities": {}
            }

        try:

            with open(
                cls.MEMORY_FILE,
                "r",
                encoding="utf-8"
            ) as f:

                return json.load(f)

        except Exception:

            return {
                "entities": {}
            }

    @classmethod
    def save_memory(
        cls,
        memory: dict
    ):

        cls.MEMORY_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            cls.MEMORY_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                memory,
                f,
                indent=4
            )

    @classmethod
    def remember_entity(
        cls,
        entity: str,
        attribute: str,
        value
    ):

        memory = cls.load_memory()

        memory.setdefault(
            "entities",
            {}
        )

        entity = entity.lower()

        memory["entities"].setdefault(
            entity,
            {}
        )

        memory["entities"][
            entity
        ][
            attribute
        ] = value

        cls.save_memory(
            memory
        )

    @classmethod
    def recall_entity(
        cls,
        entity: str,
        attribute: str | None = None
    ):

        memory = cls.load_memory()

        entity_data = (
            memory
            .get(
                "entities",
                {}
            )
            .get(
                entity.lower()
            )
        )

        if not entity_data:
            return None

        if attribute is None:
            return entity_data

        return entity_data.get(
            attribute
        )

    @classmethod
    def entity_exists(
        cls,
        entity: str
    ):

        memory = cls.load_memory()

        return (
            entity.lower()
            in memory.get(
                "entities",
                {}
            )
        )

    @classmethod
    def all_entities(cls):

        return (
            cls.load_memory()
            .get(
                "entities",
                {}
            )
        )

    @classmethod
    def delete_entity(
        cls,
        entity: str
    ):

        memory = cls.load_memory()

        entities = memory.get(
            "entities",
            {}
        )

        if entity.lower() in entities:

            del entities[
                entity.lower()
            ]

            cls.save_memory(
                memory
            )