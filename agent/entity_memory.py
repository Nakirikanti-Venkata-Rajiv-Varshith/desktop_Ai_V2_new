import json
from pathlib import Path

from config.settings import DATA_DIR


class EntityMemory:

    @classmethod
    def _normalize_entity(
        cls,
        entity: str
    ) -> str:
        """
        Normalize an entity name before
        storing or retrieving it.
        """

        return (
            entity
            .strip()
            .lower()
        )


    @classmethod
    def _normalize_attribute(
        cls,
        attribute: str
    ) -> str:
        """
        Normalize an attribute name.
        """

        return (
            attribute
            .strip()
            .lower()
        )

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

        entity = cls._normalize_entity(
            entity
        )

        attribute = cls._normalize_attribute(
            attribute
        )

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
                cls._normalize_entity(
                    entity
                )
            )
        )

        if not entity_data:
            return None

        if attribute is None:
            return entity_data

        return entity_data.get(
            cls._normalize_attribute(
                attribute
            )
        )

    @classmethod
    def entity_exists(
        cls,
        entity: str
    ):

        memory = cls.load_memory()

        return (
            cls._normalize_entity(
                entity
            )
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
        entity = cls._normalize_entity(
            entity
        )

        if entity in entities:

            del entities[
                entity
            ]
            cls.save_memory(
                memory
            )