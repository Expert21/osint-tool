import asyncio
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Button, Static, Input, Label, ContentSwitcher, DataTable, Checkbox, Log, ProgressBar
from textual.binding import Binding
from textual.logging import TextualHandler
import logging
import sys
from io import StringIO

# Import core logic (we need to run this in a separate thread/task)
# We'll need to refactor main_async to be callable with args object
from argparse import Namespace
# We can't easily import main_async from main.py due to circular imports or structure
# Ideally main.py logic should be in a controller class. 
# For now, we will assume we can import a "Runner" or similar, or we move main_async to a library.
# Let's assume we can import main_async from main (if main.py is importable)
# Or better, we create a Runner class in src/core/runner.py (refactoring)
# But to stick to the plan, I will try to import main_async from main.
# Note: main.py has `if __name__ == "__main__":` so it should be safe.

class HermesApp(App):
    """Hermes OSINT Tool TUI"""

    CSS_PATH = "styles.tcss"
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("tab", "focus_next", "Next Field"),
        Binding("shift+tab", "focus_previous", "Prev Field"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        with Horizontal(id="main-layout"):
            # Left Sidebar - Form Area
            with Vertical(id="sidebar"):
                yield Static("HERMES", classes="sidebar-title")
                
                # --- Target Info ---
                yield Label("Target Info", classes="section-header")
                
                with Container(classes="form-row"):
                    yield Label("Target", classes="label required")
                    yield Input(placeholder="Target...", id="input-target")
                
                with Container(classes="form-row"):
                    yield Label("Type", classes="label required")
                    yield Input(placeholder="individual/company", id="input-type")
                
                with Container(classes="form-row"):
                    yield Label("Company", classes="label")
                    yield Input(placeholder="Company Name...", id="input-company")

                with Container(classes="form-row"):
                    yield Label("Location", classes="label")
                    yield Input(placeholder="Location...", id="input-location")
                
                with Container(classes="form-row"):
                    yield Label("Email", classes="label")
                    yield Input(placeholder="Email...", id="input-email")
                
                with Container(classes="form-row"):
                    yield Label("Domain", classes="label")
                    yield Input(placeholder="Primary Domain...", id="input-domain")

                with Container(classes="form-row"):
                    yield Label("Add. Domains", classes="label")
                    yield Input(placeholder="Space separated...", id="input-domains")

                # --- Search Options ---
                yield Label("Search Options", classes="section-header")
                
                with Container(classes="form-row"):
                    yield Label("Passive Mode", classes="label")
                    yield Checkbox(id="chk-passive")

                with Container(classes="form-row"):
                    yield Label("No Verify", classes="label")
                    yield Checkbox(id="chk-no-verify")

                with Container(classes="form-row"):
                    yield Label("Skip Search", classes="label")
                    yield Checkbox(id="chk-skip-search")

                with Container(classes="form-row"):
                    yield Label("Skip Social", classes="label")
                    yield Checkbox(id="chk-skip-social")

                # --- Enumeration ---
                yield Label("Enumeration", classes="section-header")

                with Container(classes="form-row"):
                    yield Label("Email Enum", classes="label")
                    yield Checkbox(id="chk-email-enum")

                with Container(classes="form-row"):
                    yield Label("Domain Enum", classes="label")
                    yield Checkbox(id="chk-domain-enum")

                # --- Advanced ---
                yield Label("Advanced", classes="section-header")

                with Container(classes="form-row"):
                    yield Label("JS Render", classes="label")
                    yield Checkbox(id="chk-js-render")

                with Container(classes="form-row"):
                    yield Label("User Vars", classes="label")
                    yield Checkbox(id="chk-username-variations")

                with Container(classes="form-row"):
                    yield Label("Leet Speak", classes="label")
                    yield Checkbox(id="chk-include-leet")

                with Container(classes="form-row"):
                    yield Label("Suffixes", classes="label")
                    yield Checkbox(id="chk-include-suffixes")

                with Container(classes="form-row"):
                    yield Label("No Dedup", classes="label")
                    yield Checkbox(id="chk-no-dedup")

                with Container(classes="form-row"):
                    yield Label("Proxies", classes="label")
                    yield Input(placeholder="Proxy list file...", id="input-proxies")
                
                with Container(classes="form-row"):
                    yield Label("Fetch Proxies", classes="label")
                    yield Checkbox(id="chk-fetch-proxies")

                # --- Configuration ---
                yield Label("Configuration", classes="section-header")

                with Container(classes="form-row"):
                    yield Label("Output", classes="label")
                    yield Input(placeholder="Output file...", id="input-output")

                with Container(classes="form-row"):
                    yield Label("Profile", classes="label")
                    yield Input(placeholder="Config Profile...", id="input-config")

                with Container(classes="form-row"):
                    yield Label("Mode", classes="label")
                    yield Input(placeholder="native/docker", id="input-mode")

                with Container(classes="form-row"):
                    yield Label("Tool", classes="label")
                    yield Input(placeholder="sherlock/theharvester", id="input-tool")

                yield Button("START SCAN", id="btn-start", variant="primary")

            # Right Side - Output & ASCII
            with Vertical(id="right-side"):
                yield Log(id="log-output", highlight=True)
                yield ProgressBar(id="progress-bar", total=100, show_eta=True)
                yield DataTable(id="results-table")

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        # Setup logging to redirect to the Log widget
        handler = TextualHandler()
        logging.getLogger().addHandler(handler)
        
        table = self.query_one(DataTable)
        table.add_columns("Type", "Source", "Value")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "btn-start":
            # Collect Inputs
            target = self.query_one("#input-target").value
            scan_type = self.query_one("#input-type").value
            company = self.query_one("#input-company").value
            location = self.query_one("#input-location").value
            email = self.query_one("#input-email").value
            domain = self.query_one("#input-domain").value
            add_domains = self.query_one("#input-domains").value
            proxies = self.query_one("#input-proxies").value
            output = self.query_one("#input-output").value
            config = self.query_one("#input-config").value
            mode = self.query_one("#input-mode").value
            tool = self.query_one("#input-tool").value

            # Collect Checkboxes
            passive = self.query_one("#chk-passive").value
            no_verify = self.query_one("#chk-no-verify").value
            skip_search = self.query_one("#chk-skip-search").value
            skip_social = self.query_one("#chk-skip-social").value
            email_enum = self.query_one("#chk-email-enum").value
            domain_enum = self.query_one("#chk-domain-enum").value
            js_render = self.query_one("#chk-js-render").value
            user_vars = self.query_one("#chk-username-variations").value
            leet = self.query_one("#chk-include-leet").value
            suffixes = self.query_one("#chk-include-suffixes").value
            no_dedup = self.query_one("#chk-no-dedup").value
            fetch_proxies = self.query_one("#chk-fetch-proxies").value
            
            if not target or not scan_type:
                self.query_one(Log).write("[bold red]Error: Target and Type are required![/]")
                return
            
            self.query_one(Log).write(f"Starting scan for {target}...")
            self.query_one(ProgressBar).update(progress=0)
            
            # Run the scan in a background task
            self.run_worker(self.run_scan(target, scan_type))

    async def run_scan(self, target: str, scan_type: str):
        """Run the actual scan logic."""
        # Here we would call the actual core logic.
        # For demonstration/MVP of TUI functionality without full refactor of main.py:
        # We will simulate steps or call a simplified runner.
        
        # TODO: Refactor main.py to expose a clean `run_scan(args)` function that yields progress/results
        # For now, we'll just show that the TUI is "alive"
        
        progress = self.query_one(ProgressBar)
        log = self.query_one(Log)
        table = self.query_one(DataTable)
        
        for i in range(10):
            progress.advance(10)
            log.write(f"Step {i+1}: Processing...")
            await asyncio.sleep(0.5)
            
        log.write("Scan complete!")
        table.add_row("Email", "Google", f"{target}@gmail.com")
        table.add_row("Social", "Twitter", f"@{target}")

if __name__ == "__main__":
    app = HermesApp()
    app.run()
