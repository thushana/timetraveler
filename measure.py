#!/usr/bin/env python3
import logging

from core.journey.scheduler import JourneyScheduler

logging.basicConfig(level=logging.INFO)


def main():
    scheduler = JourneyScheduler(debug=True)
    scheduler.process_all_journeys()


if __name__ == "__main__":
    main()
