import json
import csv
import logging

logger = logging.getLogger("OSINT_Tool")

def generate_report(results, output_file):
    """
    Generates a report from the results.
    Supports JSON and CSV formats based on file extension.
    """
    if output_file.endswith('.json'):
        _generate_json_report(results, output_file)
    elif output_file.endswith('.csv'):
        _generate_csv_report(results, output_file)
    else:
        logger.warning("Unknown file extension. Defaulting to JSON.")
        _generate_json_report(results, output_file + ".json")

def _generate_json_report(results, output_file):
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=4)
        logger.info(f"JSON report saved to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save JSON report: {e}")

def _generate_csv_report(results, output_file):
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Module", "Source/Platform", "Title/Status", "URL", "Description/Details"])
            
            # Process Search Engine Results
            if 'search_engines' in results:
                for item in results['search_engines']:
                    writer.writerow([
                        "Search Engine",
                        item.get('source', 'N/A'),
                        item.get('title', 'N/A'),
                        item.get('url', 'N/A'),
                        item.get('description', 'N/A')
                    ])
            
            # Process Social Media Results
            if 'social_media' in results:
                for item in results['social_media']:
                    writer.writerow([
                        "Social Media",
                        item.get('platform', 'N/A'),
                        item.get('status', 'N/A'),
                        item.get('url', 'N/A'),
                        ""
                    ])
        logger.info(f"CSV report saved to {output_file}")
    except Exception as e:
        logger.error(f"Failed to save CSV report: {e}")
