#!/usr/bin/env python
"""
Real-time log viewer (similar to tail -f in Laravel)
"""
import os
import time
import sys

def view_logs(log_file='logs/sms.log', lines=10):
    """View logs in real-time"""
    if not os.path.exists(log_file):
        print(f"❌ Log file {log_file} does not exist!")
        return
    
    print(f"📋 Viewing logs from: {log_file}")
    print("=" * 60)
    
    # Show last N lines
    try:
        with open(log_file, 'r') as f:
            all_lines = f.readlines()
            if all_lines:
                print(f"Last {lines} entries:")
                for line in all_lines[-lines:]:
                    print(line.strip())
            else:
                print("Log file is empty")
    except Exception as e:
        print(f"Error reading log file: {e}")
        return
    
    print("\n" + "=" * 60)
    print("🔄 Watching for new entries... (Press Ctrl+C to stop)")
    print("=" * 60)
    
    # Watch for new entries
    try:
        with open(log_file, 'r') as f:
            # Move to end of file
            f.seek(0, 2)
            
            while True:
                line = f.readline()
                if line:
                    print(line.strip())
                else:
                    time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n👋 Stopped watching logs")

def main():
    """Main function"""
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
    else:
        log_file = 'logs/sms.log'
    
    if len(sys.argv) > 2:
        try:
            lines = int(sys.argv[2])
        except ValueError:
            lines = 10
    else:
        lines = 10
    
    view_logs(log_file, lines)

if __name__ == "__main__":
    main()

