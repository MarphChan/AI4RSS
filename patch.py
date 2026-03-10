import os
import logging

filepath = "core/generator.py"

try:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the old block to replace (for generate_daily_news)
    old_str_1 = '''        # Save
        # filepath is already determined above
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)'''

    # Define the new atomic write block
    new_str_1 = '''        # Save using atomic write to avoid locking issues
        # filepath is already determined above
        temp_filepath = filepath + ".tmp"
        try:
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                f.write(final_content)
            os.replace(temp_filepath, filepath)
        except Exception as e:
            logger.error(f"Error saving file {filepath}: {e}")
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except:
                    pass
            raise e'''

    old_str_2 = '''        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)'''

    new_str_2 = '''        # Save using atomic write
        temp_filepath = filepath + ".tmp"
        try:
            with open(temp_filepath, 'w', encoding='utf-8') as f:
                f.write(final_content)
            os.replace(temp_filepath, filepath)
        except Exception as e:
            logger.error(f"Error saving file {filepath}: {e}")
            if os.path.exists(temp_filepath):
                try:
                    os.remove(temp_filepath)
                except:
                    pass
            raise e'''
    
    modified = False
    
    if old_str_1 in content:
        content = content.replace(old_str_1, new_str_1)
        modified = True
        print("Patched generate_daily_news")
    else:
        print("Warning: Could not find code block in generate_daily_news")

    if old_str_2 in content:
        content = content.replace(old_str_2, new_str_2)
        modified = True
        print("Patched generate_daily_news_from_urls")
    else:
        print("Warning: Could not find code block in generate_daily_news_from_urls")

    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print("Successfully updated core/generator.py")
    else:
        print("No changes made to core/generator.py")

except Exception as e:
    print(f"Error: {e}")
