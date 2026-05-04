#!/usr/bin/env python3
"""Test script to verify real data is accessible"""

from backend.predict import get_full_summary

def main():
    summary = get_full_summary()
    if summary:
        print('✅ Real data loaded successfully!')
        print(f'📊 Latest date: {summary["date"]}')
        print(f'📍 Total stations: {summary["total_stations"]}')
        print(f'🌧️  Total rainfall: {summary["total_rainfall_mm"]} mm')
        print(f'📈 Max rainfall: {summary["max_rainfall_mm"]} mm at {summary["max_station"]}')
        print(f'🚨 Danger alerts: {summary["danger_alerts"]}')
        print(f'📊 Districts: {len(summary["district_summary"])}')
    else:
        print('❌ No data found')

if __name__ == "__main__":
    main()