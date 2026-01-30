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
		f.write(f"\n{'='*70}\n")
		f.write(f"Directory Monitoring Session Started\n")
		f.write(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
		f.write(f"Monitoring: {os.path.abspath(MONITOR_DIR)}\n")
		f.write(f"{'='*70}\n\n")

	print(f"Logging to: {os.path.abspath(LOG_FILE)}")

def get_directory_snapshot(directory):
	"""
	Scan directory and return current state of all files with metadata

	Returns:
		dict: {filename: metadata_dict}
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
				metadata = get_file_metadata(item_path)
				if metadata:
					snapshot[item] = metadata

		return snapshot

	except Exception as e:
		print(f"Error scanning directory: {e}")
		return snapshot

def get_file_metadata(filepath):
	"""Extract complete metadata from a file"""
	try:
		stat_info = os.stat(filepath)

		metadata = {
			'filename': os.path.basename(filepath),
			'filepath': filepath,
			'size_bytes': stat_info.st_size,
			'permissions': oct(stat_info.st_mode)[-3:],
			'owner_uid': stat_info.st_uid,
			'group_gid': stat_info.st_gid,
			'modified_time': stat_info.st_mtime,
			'access_time': stat_info.st_atime,
			'created_time': stat_info.st_ctime,
			'modified_time_str': datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
			'access_time_str': datetime.fromtimestamp(stat_info.st_atime).strftime('%Y-%m-%d %H:%M:%S'),
			'created_time_str': datetime.fromtimestamp(stat_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
		}

		return metadata

	except Exception as e:
		print(f"Error getting metadata for {filepath}: {e}")
		return None

def log_file_creation(metadata):
	"""Log details of a newly created file"""
	log_message = f"""
[FILE CREATED] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
  Filename: {metadata['filename']}
  Path: {metadata['filepath']}
  Size: {metadata['size_bytes']} bytes
  Permissions: {metadata['permissions']}
  Owner UID: {metadata['owner_uid']}
  Group GID: {metadata['group_gid']}
  Modified: {metadata['modified_time_str']}
  Accessed: {metadata['access_time_str']}
  Created: {metadata['created_time_str']}
{'-'*70}
"""


	# Write to log file
	with open(LOG_FILE,'a') as f:
		f.write(log_message)

	# Print to console
	print(f"/ Detected new file: {metadata['filename']} ({metadata['size_bytes']} bytes)")

def log_file_deletion(filename, timestamp):
	"""Log file deletion event"""
	log_message = f"""
[FILE DELETED] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
   Filename: {filename}
   Detected at: {timestamp}
{'-'*70}
"""

	with open(LOG_FILE, 'a') as f:
		f.write(log_message)

	print(f"x DELETED: {filename}")

def log_file_modification(filename, old_meta, new_meta):
	"""Log file modification with before/after values"""
	changes = []

	# Check size change
	if old_meta['size_bytes'] != new_meta['size_bytes']:
		changes.append(f"Size: {old_meta['size_bytes']} bytes --> {new_meta['size_bytes']} bytes")

	# Check permission change
	if old_meta['permissions'] != new_meta['permissions']:
		changes.append(f"Permissions: {old_meta['permissions']} --> {new_meta['permissions']}")

	# Check modification time (allowing 1 second tolerance)
	if abs(old_meta['modified_time'] - new_meta['modified_time']) > 1:
		changes.append(f"Modified time: {old_meta['modified_time_str']} --> {new_meta['modified_time_str']}")

	if changes:
		log_message = f"""
[FILE MODIFIED] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
   Filename: {filename}
   Changes:
"""
		log_message += "\n".join(changes)
		log_message += f"\n{'-'*70}\n"

		with open(LOG_FILE, 'a') as f:
			f.write(log_message)

		print(f"MODIFIED: {filename}")
		for change in changes:
			print(f" {change.strip()}")

		return True

	return False

def detect_file_creation(old_snapshot, new_snapshot):
	"""Detect newly created files"""
	new_files = set(new_snapshot.keys()) - set(old_snapshot.keys())

	if new_files:
		print(f"\n New Found {len(new_files)} new file(s)!")
		for filename in new_files:
			log_file_creation(new_snapshot[filename])

	return len(new_files)

def detect_file_deletion(old_snapshot, new_snapshot):
	"""Detect deleted files"""
	deleted_files = set(old_snapshot.keys()) - set(new_snapshot.keys())

	if deleted_files:
		print(f"\n Found {len(deleted_files)} deleted file(s)!")
		timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		for filename in deleted_files:
			log_file_deletion(filename, timestamp)

	return len(deleted_files)

def detect_file_modification(old_snapshot, new_snapshot):
	"""Detect modified files by comparing metadata"""
	common_files = set(old_snapshot.keys()) & set(new_snapshot.keys())
	modified_count = 0

	if common_files:
		for filename in common_files:
			old_meta = old_snapshot[filename]
			new_meta = new_snapshot[filename]

			if log_file_modification(filename, old_meta, new_meta):
				modified_count += 1

	if modified_count > 0:
		print(f"\n Found {modified_count} modified file(s)!")

	return modified_count

def main():
	"""Main monitoring loop"""
	print("="*70)
	print("Directory Monitoring System")
	print("Student A Module")
	print("="*70)
	print(f"\nMonitoring directory: {os.path.abspath(MONITOR_DIR)}")
	print(f"Check interval: {CHECK_INTERVAL} seconds")
	print(f"\nFeatures:")
	print("File creation detection")
	print("File deletion detection")
	print("File modification detection")
	print(f"\nPress Ctrl+C to stop\n")

	setup_logging()

	# Get initial snapshot
	print("Taking initial snapshot...")
	previous_snapshot = get_directory_snapshot(MONITOR_DIR)
	print(f"Initial files: {list(previous_snapshot.keys())}\n")

	print("Monitoring started. Waiting for changes...\n")

	check_count = 0

	try:
		while True:
			time.sleep(CHECK_INTERVAL)
			check_count += 1

			# Get current state
			current_snapshot = get_directory_snapshot(MONITOR_DIR)

			# Detect changes
			created = detect_file_creation(previous_snapshot, current_snapshot)
			deleted = detect_file_deletion(previous_snapshot, current_snapshot)
			modified = detect_file_modification(previous_snapshot, current_snapshot)

			# Update snapshot
			previous_snapshot = current_snapshot

			# Show status
			total_changes = created + deleted + modified
			if total_changes == 0:
				print(f"[Check {check_count} - {datetime.now().strftime('%H:%M:%S')}] No changes detected")

	except KeyboardInterrupt:
		print("\n" + "="*70)
		print(f"Monitoring stopped by user")
		print(f"Total checks performed: {check_count}")
		print(f"Total runtime: {check_count * CHECK_INTERVAL} seconds")
		print(f"Log file: {os.path.abspath(LOG_FILE)}")
		print("="*70)

if __name__ == "__main__":
	main()
