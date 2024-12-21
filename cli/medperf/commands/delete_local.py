from typing import Type
from medperf.entities.interface import Entity
from medperf.exceptions import CleanExit
from medperf.entities.cube import Cube
from medperf.entities.dataset import Dataset
from medperf.entities.result import Result
from medperf.entities.benchmark import Benchmark
from medperf.utils import remove_path
import medperf.config as config


class EntityDelete:
    @staticmethod
    def run(entity_id: int, entity_class: Type[Entity]):
        entity_delete = EntityDelete(entity_id, entity_class)
        entity_delete.prepare()
        entity_delete.prompt_validate()
        entity_delete.delete()

    def __init__(self, entity_id: int, entity_class: Type[Entity]):
        self.entity_id = entity_id
        self.entity_class = entity_class

    def prepare(self):
        if self.entity_class == Cube:
            self.entity = Cube.get(self.entity_id, local_only=True)
            self.entity_class = "Cube"
        elif self.entity_class == Dataset:
            self.entity = Dataset.get(self.entity_id, local_only=True)
            self.entity_class = "Dataset"
        elif self.entity_class == Result:
            self.entity = Result.get(self.entity_id, local_only=True)
            self.entity_class = "Result"
        elif self.entity_class == Benchmark:
            self.entity = Benchmark.get(self.entity_id, local_only=True)
            self.entity_class = "Benchmark"

    def view_entity(self, entity_dict):
        msg = (
            f"Details:\n\tType: {self.entity_class}\n\tUID: {entity_dict['UID']}\n\tName: {entity_dict['Name']}"
            + f"\n\tState: {entity_dict['State']}\n\tRegistered: {entity_dict['Registered']}"
        )
        config.ui.print(msg)

    def prompt(self, msg):
        ui = config.ui
        ui.print_highlight(msg)
        return ui.prompt("").strip()

    def prompt_validate(self):
        ui = config.ui
        entity_dict = self.entity.display_dict()
        self.view_entity(entity_dict)
        confirm = (
            f"I confirm deleting the {self.entity_class} with UID {entity_dict['UID']}"
        )
        msg = (
            f"Are you sure you want to delete the above {self.entity_class}?"
            + f"\nNote: This will delete the {self.entity_class} 'Locally' from your PC,"
            + " and the action is irreversible."
            + f"\nIf so, please type '{confirm}'."
            + " Otherwise, type 'N' (Case Sensitive): "
        )

        user_input = self.prompt(msg)
        while user_input not in [confirm, "N"]:
            ui.print("Invalid input.")
            user_input = self.prompt(msg)

        if user_input != confirm:
            raise CleanExit("Deletion aborted.")

    def delete(self):
        remove_path(self.entity.path)
