"""Garmin Connect data synchronization."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

try:
    from garminconnect import Garmin
    GARMIN_AVAILABLE = True
except ImportError:
    GARMIN_AVAILABLE = False
    Garmin = None

from ..models.health import GarminActivityDay

logger = logging.getLogger(__name__)


class GarminSync:
    """Handles syncing data from Garmin Connect."""

    def __init__(self, username: str, password: str):
        """Initialize Garmin client.

        Args:
            username: Garmin Connect username
            password: Garmin Connect password
        """
        self.client = Garmin(username, password)
        self.client.login()
        logger.info(f"Authenticated with Garmin as {username}")

    def get_activity_data(
        self,
        days_back: int = 7,
    ) -> List[GarminActivityDay]:
        """
        Fetch daily activity data for the last N days.

        Args:
            days_back: Number of days to fetch (default: 7)

        Returns:
            List of GarminActivityDay objects
        """
        activities = []

        # Get daily summaries for the requested period
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)

        logger.info(f"Fetching Garmin data from {start_date} to {end_date}")

        try:
            # Fetch daily stats
            stats = self.client.get_stats(start_date.isoformat())

            if isinstance(stats, dict):
                # Extract data for each day
                for day_data in stats.get("dailyStepData", []):
                    try:
                        activity_date = datetime.strptime(
                            day_data.get("calendarDate"), "%Y-%m-%d"
                        ).date()

                        if activity_date < start_date:
                            continue

                        # Get detailed daily summary
                        daily_summary = self.client.get_daily_summary(activity_date.isoformat())

                        activity = self._parse_daily_summary(activity_date, daily_summary)
                        activities.append(activity)
                        logger.info(f"Fetched activity for {activity_date}")

                    except Exception as e:
                        logger.warning(f"Failed to parse day data: {e}")
                        continue

        except Exception as e:
            logger.error(f"Error fetching Garmin data: {e}")
            raise

        return sorted(activities, key=lambda x: x.date)

    def _parse_daily_summary(
        self,
        activity_date: datetime.date,
        daily_summary: dict,
    ) -> GarminActivityDay:
        """Parse daily summary from Garmin API response."""

        # Handle nested structure from Garmin API
        summary = daily_summary if isinstance(daily_summary, dict) else {}

        # Extract heart rate data
        hr_avg = None
        hr_max = None
        if "dailyHeartRateData" in summary:
            hr_data = summary["dailyHeartRateData"][0] if summary["dailyHeartRateData"] else {}
            hr_avg = hr_data.get("restingHeartRate") or hr_data.get("lastNightAverage")
            hr_max = hr_data.get("lastNightMaxHr")

        # Extract sleep data (in seconds)
        sleep_seconds = None
        sleep_quality = None
        if "sleepData" in summary and summary["sleepData"]:
            sleep_data = summary["sleepData"][0]
            # Convert milliseconds to seconds
            sleep_seconds = int(sleep_data.get("sleepTimeSeconds", 0))
            sleep_quality = sleep_data.get("sleepQualityTypeName")

        # Extract stress level and body battery
        stress_level = None
        body_battery = None
        if "stressData" in summary and summary["stressData"]:
            stress_data = summary["stressData"][0]
            stress_level = stress_data.get("stressLevel")

        if "bodyBatteryData" in summary and summary["bodyBatteryData"]:
            battery_data = summary["bodyBatteryData"][0]
            body_battery = battery_data.get("bodyBatteryChargedValue")

        activity = GarminActivityDay(
            date=activity_date,
            steps=summary.get("totalSteps"),
            active_minutes=summary.get("totalActiveMinutes"),
            calories=summary.get("totalCalories"),
            heart_rate_avg=hr_avg,
            heart_rate_max=hr_max,
            sleep_seconds=sleep_seconds,
            sleep_quality=sleep_quality,
            stress_level=stress_level,
            body_battery=body_battery,
        )

        return activity

    def get_weight_data(self, days_back: int = 30) -> List[dict]:
        """
        Fetch weight data if synced to Garmin.

        Args:
            days_back: Number of days to fetch (default: 30)

        Returns:
            List of weight measurements
        """
        try:
            # Garmin may not have a dedicated weight endpoint in the library
            # This would need to be customized based on API availability
            logger.info("Weight data fetch not yet implemented")
            return []
        except Exception as e:
            logger.warning(f"Could not fetch weight data: {e}")
            return []
