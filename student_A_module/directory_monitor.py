import os
import time
from pathlib import Path
from datetime import datetime

# Configuration
MONITOR_DIR = "../test_directory"
LOG_FILE = "../logs/directory_changes.log"
CHECK_INTERVAL = 5 # seconds

def setup_logging():
	"""Initialize log file with header"""
	log_dir = os.path.dirname(LOG_FILE)
	if not os.path.exists(log_dir):
		os.makedirs(log_dir)
		print(f"Created log directory: {log_dir}")

	with open(LOG_FILE,'a') as f:
		f.write(f"\n{'='*60}\n")
		f.write(f"Directory Monitoring Session Started\n")
		f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
		f.write(f"Monitoring: {os.path.abspath(MONITOR_DIR)}\n")
		f.write(f"{'='*60}\n\n")

	print(f"Logging to: {os.path.abspath(LOG_FILE)}")

def get_directory_snapshot(directory):
	"""
	Scan directory and return current state of all files

	Returns:
		dict: {filename: filepath} for all files in directory
	"""
	snapshot = {}

	try:
		# Check if directory exists
		if not os.path.exists(directory):
			print(f"Warning: Directory {directory} does not exist!")
			return snapshot

		# Scan all items in directory
		for item in os.listdir(directory):
			item_path = os.path.join(directory, item)

			# Only track regular files (not subdirectories for now)
			if os.path.isfile(item_path):
				snapshot[item] = item_path

		print(f"Scanned directory: Found {len(snapshot)} files")
		return snapshot

	except Exception as e:
		print(f"Error scanning directory: {e}")
		return snapshot

def get_file_metadata(filepath):
	"""
	Extract metadata from a file using os.stat()

	Returns:
		dict: File metadata including size, timestamps, permissions
	"""
	try:
		stat_info = os.stat(filepath)

		metadata = {
			'filename': os.path.basename(filepath),
			'filepath': filepath,
			'size_bytes': stat_info.st_size,
			'permissions': oct(stat_info.st_mode)[-3:],
			'owner_uid': stat_info.st_uid,
			'group_gid': stat_info.st_gid,
			'modified_time': datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
			'access_time': datetime.fromtimestamp(stat_info.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
			'created_time': datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
		}

		return metadata

	except Exception as e:
		print(f"Error getting metadata for {filepath}: {e}")
		return None

def log_file_creation(filepath):
	"""Log details of a newly created file"""
	metadata = get_file_metadata(filepath)

	if metadata:
		log_message = f"""
[FILE CREATED] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  Filename: {metadata['filename']}
  Path: {metadata['filepath']}
  Size: {metadata['size_bytes']} bytes
  Permissions: {metadata['permissions']}
  Owner UID: {metadata['owner_uid']}
  Group GID: {metadata['group_gid']}
  Modified: {metadata['modified_time']}
  Accessed: {metadata['access_time']}
  Created: {metadata['created_time']}
{'-'*60}
"""


	# Write to log file
	with open(LOG_FILE,'a') as f:
		f.write(log_message)

	# Print to console
	print(f"/ Detected new file: {metadata['filename']} ({metadata['size_bytes']} bytes)")

def detect_file_creation(old_snapshot, new_snapshot):
	"""
	Compare two snapshots to find newly created files

	Args:
		old_snapshot: Previous directory state
		new_snapshot: Current directory state
	"""
	new_files = set(new_snapshot.keys()) - set(old_snapshot.keys())

	if new_files:
		print(f"\n New Found {len(new_files)} new file(s)!")
		for filename in new_files:
			filepath = new_snapshot[filename]
			log_file_creation(filepath)

	return len(new_files)

def main():
	"""Main monitoring loop"""
	print("="*60)
	print("Directory Monitoring System")
	print("Student A Module")
	print("="*60)
	print(f"\nMonitoring directory: {os.path.abspath(MONITOR_DIR)}")
	print(f"Check interval: {CHECK_INTERVAL} seconds")
	print(f"Press Ctrl+C to stop\n")

	setup_logging()

	# Get initial snapshot
	print("\nTaking initial snapshot...")
	previous_snapshot = get_directory_snapshot(MONITOR_DIR)
	print(f"Initial files: {list(previous_snapshot.keys())}\n")

	print("Monitoring started. Waiting for changes...\n")

	try:
		while True:
			time.sleep(CHECK_INTERVAL)

			# Get current state
			current_snapshot = get_directory_snapshot(MONITOR_DIR)

			# Detect changes
			new_file_count = detect_file_creation(previous_snapshot, current_snapshot)

			# Update snapshot
			previous_snapshot = current_snapshot

			# Show we are still running
			if new_file_count == 0:
				print(f"[{datetime.now().strftime('%H:%M:%S')}] Monitoring...(no changes)")

	except KeyboardInterrupt:
		print("\n\nMonitoring stopped by user.")
		print(f"Check log file: {os.path.abspath(LOG_FILE)}")
		print("="*60)

if __name__ =="__main__":
	main()
