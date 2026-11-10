import os
import time
import shutil

def audit_and_cleanup(force=False):
    print("-> Running post-upload audit and storage optimization...")
    assets_dir = "assets"
    
    if not os.path.exists(assets_dir):
        return

    # Target heavy temporary build files for cleanup
    cleaned_count = 0
    current_time = time.time()
    two_days_in_seconds = 2 * 86400  # 48 hours

    for item in os.listdir(assets_dir):
        item_path = os.path.join(assets_dir, item)
        
        # Clean up temporary frame folders and raw downloads older than 2 days (or immediately if forced after upload audit)
        is_temp_artifact = "broll_frames" in item or "downloaded_raw" in item or "processed_broll" in item
        
        if is_temp_artifact:
            file_age = current_time - os.path.getmtime(item_path)
            if force or file_age > two_days_in_seconds:
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
                cleaned_count += 1

    print(f"SUCCESS: Storage audit complete. Cleared {cleaned_count} temporary build artifacts to keep Mac optimized.")

if __name__ == "__main__":
    audit_and_cleanup(force=True)
