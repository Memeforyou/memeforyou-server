import asyncio
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static, Log, TabbedContent, TabPane
from textual.containers import Vertical
from loguru import logger
from downloader.DLmanager import managed_download
from preps.captioner import captioner_operation
from preps.embedder import embedder_operation
from preps.dblite import export_json, get_status_counts
from preps.init_sqlite import init_db

class PrepTUI(App):
    """A Textual app to manage the meme data preparation pipeline."""

    TITLE = "Meme-for-You: Data Prep Pipeline"
    CSS_PATH = "preppipe.css"

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent(initial="dashboard"):
            with TabPane("Dashboard", id="dashboard"):
                yield Static("Loading status...", id="status_display")
                yield Button("Refresh Status", id="refresh_status")
            with TabPane("Pipeline Controls", id="controls"):
                yield Button("Initialize Database", id="init_db", variant="primary")
                yield Button("Download New Memes", id="download", variant="primary")
                yield Button("Run Captioner", id="caption", variant="primary")
                yield Button("Run Embedder", id="embed", variant="primary")
                yield Button("Run Full Pipeline", id="run_all", variant="success")
                yield Button("Export to JSON", id="export", variant="warning")
            with TabPane("Logs", id="logs"):
                yield Log(id="log_viewer")
        yield Footer()

    def on_mount(self) -> None:
        log_widget = self.query_one(Log)
        logger.remove()
        logger.add(lambda msg: log_widget.write(msg), format="{time:HH:mm:ss} | {level} | {message}", enqueue=True)
        logger.add(lambda msg: print(msg, end=""), format="{time:HH:mm:ss} | {level} | {message}", enqueue=True)
        self.call_later(self.update_status)

    # --- Worker methods ---
    async def update_status(self):
        status_widget = self.query_one("#status_display")
        status_widget.update("Fetching status...")
        try:
            counts = get_status_counts()
            status_text = (
                f"PENDING: {counts['PENDING']}\n"
                f"CAPTIONED: {counts['CAPTIONED']}\n"
                f"READY: {counts['READY']}"
            )
            status_widget.update(status_text)
            logger.info("Status updated.")
        except Exception as e:
            status_widget.update("Error fetching status")
            logger.error(f"Failed to fetch status: {e}")

    def run_init_db_worker(self):
        loop = asyncio.get_running_loop()
        async def task():
            try:
                logger.info("Initializing database...")
                try:
                    await loop.run_in_executor(None, init_db)
                    logger.success("Database initialized.")
                except Exception as e:
                    logger.error(f"Database initialization failed: {e}")
                await self.update_status()
            except Exception as e:
                # Catch unexpected errors in the task itself
                logger.exception(f"Unexpected error in init_db_worker: {e}")
        self.run_worker(task, exclusive=True)

    def run_download_worker(self):
        loop = asyncio.get_running_loop()
        async def task():
            logger.info("Starting download process...")
            try:
                await loop.run_in_executor(None, managed_download)
                logger.success("Download complete.")
            except Exception as e:
                logger.error(f"Download failed: {e}")
            await self.update_status()
        self.run_worker(task, exclusive=True)

    def run_caption_worker(self):
        loop = asyncio.get_running_loop()
        async def task():
            try:
                logger.info("Starting captioner...")
                try:
                    await loop.run_in_executor(None, captioner_operation)
                    logger.success("Captioning complete.")
                except Exception as e:
                    logger.error(f"Captioner failed: {e}")
                await self.update_status()
            except Exception as e:
                logger.exception(f"Unexpected error in caption_worker: {e}")
        self.run_worker(task, exclusive=True)

    def run_embed_worker(self):
        loop = asyncio.get_running_loop()
        async def task():
            try:
                logger.info("Starting embedder...")
                try:
                    await loop.run_in_executor(None, embedder_operation)
                    logger.success("Embedding complete.")
                except Exception as e:
                    logger.error(f"Embedder failed: {e}")
                await self.update_status()
            except Exception as e:
                logger.exception(f"Unexpected error in embed_worker: {e}")
        self.run_worker(task, exclusive=True)

    def run_full_pipeline_worker(self):
        loop = asyncio.get_running_loop()
        async def task():
            try:
                logger.info("Running full pipeline...")
                try:
                    await loop.run_in_executor(None, managed_download)
                    await loop.run_in_executor(None, captioner_operation)
                    await loop.run_in_executor(None, embedder_operation)
                    logger.success("Full pipeline complete.")
                except Exception as e:
                    logger.error(f"Full pipeline failed: {e}")
                await self.update_status()
            except Exception as e:
                logger.exception(f"Unexpected error in full_pipeline_worker: {e}")
        self.run_worker(task, exclusive=True)

    def run_export_worker(self):
        loop = asyncio.get_running_loop()
        async def task():
            try:
                logger.info("Exporting database to JSON...")
                try:
                    await loop.run_in_executor(None, export_json)
                    logger.success("Export complete.")
                except Exception as e:
                    logger.error(f"Export failed: {e}")
            except Exception as e:
                logger.exception(f"Unexpected error in export_worker: {e}")
        self.run_worker(task, exclusive=True)

    # --- Button handlers ---
    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh_status":
            await self.update_status()
        elif event.button.id == "init_db":
            self.run_init_db_worker()
        elif event.button.id == "download":
            self.run_download_worker()
        elif event.button.id == "caption":
            self.run_caption_worker()
        elif event.button.id == "embed":
            self.run_embed_worker()
        elif event.button.id == "run_all":
            self.run_full_pipeline_worker()
        elif event.button.id == "export":
            self.run_export_worker()

if __name__ == "__main__":
    app = PrepTUI()
    app.run()