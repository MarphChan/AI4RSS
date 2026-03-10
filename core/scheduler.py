import schedule
import time
import threading
import logging
from datetime import datetime
from core.config_manager import config_manager
from core.generator import news_generator
from core.pusher import pusher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self._stop_event = threading.Event()
        self._thread = None
        self.is_running = False
        self._last_fetch_time = None
        self._last_push_time = None

    def start(self):
        """Start the scheduler in a background thread."""
        if self.is_running:
            return
        
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self.is_running = True
        logger.info("Scheduler service started.")

    def stop(self):
        """Stop the scheduler."""
        if not self.is_running:
            return
            
        self._stop_event.set()
        if self._thread:
            self._thread.join()
        self.is_running = False
        logger.info("Scheduler service stopped.")

    def _run_loop(self):
        """Main loop running in thread."""
        # Initial schedule setup
        self._refresh_schedule()
        
        last_config_check = time.time()
        
        while not self._stop_event.is_set():
            # Check for config changes every minute
            if time.time() - last_config_check > 60:
                self._refresh_schedule()
                last_config_check = time.time()
            
            schedule.run_pending()
            time.sleep(1)

    def _refresh_schedule(self):
        """Reload schedule from config."""
        config = config_manager.config["system"]
        fetch_time = config.get("fetch_time", "08:00")
        push_time = config.get("push_time", "09:30")

        # Only refresh if schedule times have changed
        if fetch_time == self._last_fetch_time and push_time == self._last_push_time:
            return

        schedule.clear()
        
        # Schedule Fetch
        schedule.every().day.at(fetch_time).do(self._job_fetch)
        logger.info(f"Scheduled auto-fetch at {fetch_time}")
        
        # Schedule Push
        schedule.every().day.at(push_time).do(self._job_push)
        logger.info(f"Scheduled auto-push at {push_time}")

        self._last_fetch_time = fetch_time
        self._last_push_time = push_time

    def _job_fetch(self):
        """Execute fetch job."""
        logger.info("Starting scheduled fetch job...")
        try:
            news_generator.generate_daily_news()
            logger.info("Scheduled fetch completed.")
        except Exception as e:
            logger.error(f"Scheduled fetch failed: {e}")

    def _job_push(self):
        """Execute push job."""
        logger.info("Starting scheduled push job...")
        try:
            # Load today's news
            content = news_generator.load_daily_news()
            if not content:
                logger.warning("No news found for auto-push.")
                return

            # Check status (optional: enforce 'reviewed' status?)
            # For MVP, we push whatever is there if it exists.
            # But let's check if already pushed?
            # pusher logic doesn't check status, but we can update file after push.
            
            success = pusher.push(content)
            if success:
                logger.info("Scheduled push successful.")
            else:
                logger.error("Scheduled push failed.")
        except Exception as e:
            logger.error(f"Scheduled push error: {e}")

# Global instance
scheduler_service = SchedulerService()
