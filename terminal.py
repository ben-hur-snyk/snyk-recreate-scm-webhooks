from config import Config

from rich import print
from rich.progress import Progress, BarColumn, MofNCompleteColumn, ProgressColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn
from rich.console import Console
from rich.table import Table


class TerminalUI:
    def __init__(self, config: Config):
        self._console = Console()

        self.config = config
        self.progress = TerminalProgress(config)
        self.status = TerminalStatus(config)
        self.table = TerminalTable(config, self._console)

    def print(self, message):
        self._console.print(message)


class TerminalTable:
    def __init__(self, config: Config, console: Console = Console):
        self.config = config
        self._table_instance = None
        self._console = console


    def create(self, title: str):
        self._table_instance = Table(title=title)

    def add_column(self, name: str, style = "white"):
        self._table_instance.add_column(name, style=style)

    def add_row(self, *columns):
        self._table_instance.add_row(*columns)

    def print(self):
        self._console.print(self._table_instance)


class TerminalStatus:
    def __init__(self, config: Config):
        self.config = config
        self._status_instance = None

    def create(self, text: str, spinner: str = "dots3"):
        self._status = Console().status(text, spinner=spinner)
        self._status.start()

    def update(self, text: str):
        self._status.update(text)

    def stop(self):
        self._status.stop()
        self._status = None


class TerminalProgress:
    def __init__(self, config: Config):
        self.config = config
        self._progress_instance = None
        self._tasks = {}

    def create(self, columns: list[str] = []):
        if len(columns) > 0:
            self._create_custom_progress(columns)
        else:
            self._create_default_progress()

    def _create_default_progress(self):self._progress_instance = Progress()

    def add_task(self, task_name: str, total: int):
        self._tasks[task_name] = self._progress_instance.add_task(task_name, total=total)

    def start(self):
        self._progress_instance.start()

    def update(self, task_name: str, advance: int):
        self._progress_instance.update(self._tasks[task_name], advance=advance)

    def stop(self):
        self._progress_instance.stop()
        self._progress_instance = None


    def _create_default_progress(self):
        self._progress_instance = Progress()

    def _create_custom_progress(self, columns):
        cols = []

        for column in columns:
            if column == 'bar':
                cols.append(BarColumn())
            elif column == 'percentage':
                cols.append(TaskProgressColumn())
            elif column == 'time':
                cols.append(TimeElapsedColumn())
            elif column == 'completed':
                cols.append(MofNCompleteColumn())
            elif column == 'description':
                cols.append(TextColumn("{task.description}"))
        
        self._progress_instance = Progress(*cols)


    


    