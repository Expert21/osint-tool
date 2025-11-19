import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger("OSINT_Tool")


def generate_html_report(results: Dict[str, Any], output_file: str):
    """
    Generate a beautiful HTML report with embedded CSS and charts.
    
    Args:
        results: Results dictionary
        output_file: Output file path
    """
    logger.info(f"Generating HTML report: {output_file}")
    
    target = results.get('target', 'Unknown')
    target_type = results.get('target_type', 'Unknown')
    stats = results.get('statistics', {})
    
    # Calculate percentages for charts
    total_results = stats.get('total_unique', 0)
    high_quality = stats.get('high_quality_results', 0)
    avg_score = stats.get('avg_quality_score', 0)
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT Report - {target}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.1em; opacity: 0.9; }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s;
        }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .stat-number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 10px 0;
        }}
        .stat-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .section {{
            padding: 30px;
        }}
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 12px;
            border-bottom: 1px solid #eee;
        }}
        tr:hover {{ background: #f8f9fa; }}
        .quality-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: bold;
        }}
        .quality-high {{ background: #28a745; color: white; }}
        .quality-medium {{ background: #ffc107; color: #333; }}
        .quality-low {{ background: #dc3545; color: white; }}
        .email-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 10px;
            margin-top: 15px;
        }}
        .email-item {{
            background: #f8f9fa;
            padding: 10px 15px;
            border-radius: 5px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 OSINT Report</h1>
            <p><strong>Target:</strong> {target} ({target_type})</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Results</div>
                <div class="stat-number">{total_results}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">High Quality</div>
                <div class="stat-number">{high_quality}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Score</div>
                <div class="stat-number">{avg_score:.1f}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Duplicates Removed</div>
                <div class="stat-number">{stats.get('duplicates_removed', 0)}</div>
            </div>
        </div>
"""
    
    # Email Enumeration Section
    if 'emails' in results and results['emails']:
        emails = results['emails']
        html_content += f"""
        <div class="section">
            <h2>📧 Email Enumeration</h2>
            <p><strong>{emails.get('valid_format_count', 0)}</strong> potential email addresses generated</p>
            <div class="email-list">
"""
        for email in emails.get('emails_generated', [])[:30]:
            html_content += f'                <div class="email-item">{email}</div>\n'
        
        html_content += """            </div>
        </div>
"""
    
    # Social Media Section
    social_media = results.get('social_media', [])
    if social_media:
        html_content += """
        <div class="section">
            <h2>👥 Social Media Profiles</h2>
            <table>
                <thead>
                    <tr>
                        <th>Platform</th>
                        <th>Status</th>
                        <th>URL</th>
                        <th>Quality Score</th>
                    </tr>
                </thead>
                <tbody>
"""
        for profile in social_media:
            score = profile.get('quality_score', 0)
            badge_class = 'quality-high' if score >= 70 else ('quality-medium' if score >= 40 else 'quality-low')
            
            html_content += f"""                    <tr>
                        <td><strong>{profile.get('platform', 'N/A')}</strong></td>
                        <td>{profile.get('status', 'N/A')}</td>
                        <td><a href="{profile.get('url', '#')}" target="_blank">{profile.get('url', 'N/A')}</a></td>
                        <td><span class="quality-badge {badge_class}">{score}/100</span></td>
                    </tr>
"""
        
        html_content += """                </tbody>
            </table>
        </div>
"""
    
    # Search Results Section
    search_results = results.get('search_engines', [])
    if search_results:
        html_content += """
        <div class="section">
            <h2>🔍 Search Engine Results</h2>
            <table>
                <thead>
                    <tr>
                        <th>Source</th>
                        <th>Title</th>
                        <th>URL</th>
                        <th>Quality Score</th>
                    </tr>
                </thead>
                <tbody>
"""
        for result in search_results[:30]:
            score = result.get('quality_score', 0)
            badge_class = 'quality-high' if score >= 70 else ('quality-medium' if score >= 40 else 'quality-low')
            
            html_content += f"""                    <tr>
                        <td>{result.get('source', 'N/A')}</td>
                        <td>{result.get('title', 'N/A')[:80]}</td>
                        <td><a href="{result.get('url', '#')}" target="_blank">View</a></td>
                        <td><span class="quality-badge {badge_class}">{score}/100</span></td>
                    </tr>
"""
        
        html_content += """                </tbody>
            </table>
        </div>
"""
    
    # Footer
    html_content += """
        <div class="footer">
            <p>Generated by OSINT Tool | Advanced Open Source Intelligence Gathering</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"✓ HTML report saved to {output_file}")
