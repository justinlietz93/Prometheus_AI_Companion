#!/usr/bin/env python3
"""
CI Translation Validation Script for Prometheus AI Prompt Generator

This script validates translation files (.ts) for common issues:
1. XML well-formedness
2. Preservation of placeholders
3. Coverage of critical UI elements

Usage:
    python ci_translation_validation.py [options]

Options:
    --ts-dir DIR       Directory containing .ts files (default: current directory)
    --report-file FILE Output report file (default: translation_validation_report.md)
    --critical-only    Only check critical strings
    --verbose          Show detailed information
"""

import os
import sys
import argparse
import xml.etree.ElementTree as ET
import re
from pathlib import Path
from datetime import datetime


# Regular expressions for placeholders
PLACEHOLDER_PATTERNS = [
    r'%\d+',                # Qt style: %1, %2, etc.
    r'{[a-zA-Z0-9_]+}',     # Python style: {variable}
    r'&[A-Za-z]',           # Keyboard shortcuts: &File
]

# Critical contexts that must be translated
CRITICAL_CONTEXTS = [
    'MainWindow',
    'PromptDialog',
    'ErrorDialog',
    'MenuBar',
]


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Validate translation files for CI')
    parser.add_argument('--ts-dir', default='.',
                        help='Directory containing .ts files (default: current directory)')
    parser.add_argument('--report-file', default='translation_validation_report.md',
                        help='Output report file (default: translation_validation_report.md)')
    parser.add_argument('--critical-only', action='store_true',
                        help='Only check critical strings')
    parser.add_argument('--verbose', action='store_true',
                        help='Show detailed information')
    return parser.parse_args()


def validate_xml(ts_file):
    """Check if the TS file is well-formed XML."""
    try:
        ET.parse(ts_file)
        return True, None
    except ET.ParseError as e:
        return False, str(e)


def find_placeholders(text):
    """Find all placeholders in a text."""
    placeholders = []
    if text is None:
        return placeholders
    
    for pattern in PLACEHOLDER_PATTERNS:
        matches = re.findall(pattern, text)
        placeholders.extend(matches)
    
    return placeholders


def validate_placeholders(source_text, translation_text):
    """Check if all placeholders in source are present in translation."""
    if translation_text is None or not translation_text.strip():
        # Skip empty translations
        return True, []
    
    source_placeholders = find_placeholders(source_text)
    translation_placeholders = find_placeholders(translation_text)
    
    missing_placeholders = []
    for placeholder in source_placeholders:
        if placeholder not in translation_placeholders:
            missing_placeholders.append(placeholder)
    
    return len(missing_placeholders) == 0, missing_placeholders


def validate_ts_file(ts_file, critical_only=False):
    """Validate a single TS file for common issues."""
    results = {
        'file': os.path.basename(ts_file),
        'xml_valid': False,
        'xml_error': None,
        'missing_placeholders': [],
        'missing_critical': [],
        'untranslated_count': 0,
        'total_count': 0,
        'completion_percentage': 0,
    }
    
    # Check XML validity
    xml_valid, xml_error = validate_xml(ts_file)
    results['xml_valid'] = xml_valid
    results['xml_error'] = xml_error
    
    if not xml_valid:
        return results
    
    # Parse XML
    tree = ET.parse(ts_file)
    root = tree.getroot()
    
    # Process all translation units
    for context in root.findall('.//context'):
        context_name = context.find('name').text
        is_critical = any(crit in context_name for crit in CRITICAL_CONTEXTS)
        
        # Skip non-critical contexts if critical_only is True
        if critical_only and not is_critical:
            continue
        
        for message in context.findall('message'):
            source = message.find('source')
            translation = message.find('translation')
            
            results['total_count'] += 1
            
            # Check if translated
            is_translated = (translation is not None and 
                            translation.text is not None and 
                            translation.text.strip() != '' and
                            translation.get('type') != 'unfinished')
            
            if not is_translated:
                results['untranslated_count'] += 1
                if is_critical:
                    location = message.find('location')
                    location_str = f"{location.get('filename')}:{location.get('line')}" if location is not None else "unknown"
                    results['missing_critical'].append({
                        'context': context_name,
                        'source': source.text,
                        'location': location_str
                    })
            else:
                # Check placeholders
                placeholder_valid, missing = validate_placeholders(source.text, translation.text)
                if not placeholder_valid:
                    results['missing_placeholders'].append({
                        'context': context_name,
                        'source': source.text,
                        'translation': translation.text,
                        'missing': missing
                    })
    
    # Calculate completion percentage
    if results['total_count'] > 0:
        results['completion_percentage'] = 100 - (results['untranslated_count'] * 100 / results['total_count'])
    
    return results


def generate_report(validation_results, report_file):
    """Generate a markdown report from validation results."""
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Translation Validation Report\n\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Summary table
        f.write("## Summary\n\n")
        f.write("| File | Status | Completion | Issues |\n")
        f.write("|------|--------|------------|--------|\n")
        
        for result in validation_results:
            status = "✅ Valid" if result['xml_valid'] else "❌ Invalid XML"
            issues_count = len(result['missing_placeholders']) + len(result['missing_critical'])
            
            if issues_count > 0:
                status = "⚠️ Has issues"
            
            f.write(f"| {result['file']} | {status} | {result['completion_percentage']:.1f}% | {issues_count} |\n")
        
        # Detailed reports
        for result in validation_results:
            f.write(f"\n## {result['file']}\n\n")
            
            if not result['xml_valid']:
                f.write(f"### ❌ XML Error\n\n")
                f.write(f"```\n{result['xml_error']}\n```\n\n")
                continue
            
            f.write(f"Translation progress: {result['completion_percentage']:.1f}% ({result['total_count'] - result['untranslated_count']}/{result['total_count']})\n\n")
            
            if result['missing_placeholders']:
                f.write("### Missing Placeholders\n\n")
                f.write("| Context | Source | Translation | Missing |\n")
                f.write("|---------|--------|-------------|--------|\n")
                
                for issue in result['missing_placeholders']:
                    f.write(f"| {issue['context']} | {issue['source']} | {issue['translation']} | {', '.join(issue['missing'])} |\n")
            
            if result['missing_critical']:
                f.write("\n### Missing Critical Translations\n\n")
                f.write("| Context | Source | Location |\n")
                f.write("|---------|--------|----------|\n")
                
                for issue in result['missing_critical']:
                    f.write(f"| {issue['context']} | {issue['source']} | {issue['location']} |\n")


def main():
    """Main function."""
    args = parse_args()
    
    # Find TS files
    ts_dir = Path(args.ts_dir)
    ts_files = list(ts_dir.glob('*.ts'))
    
    if not ts_files:
        print(f"No .ts files found in {ts_dir}")
        return 1
    
    # Validate each file
    validation_results = []
    for ts_file in ts_files:
        if args.verbose:
            print(f"Validating {ts_file}...")
        
        result = validate_ts_file(ts_file, args.critical_only)
        validation_results.append(result)
        
        if args.verbose:
            print(f"  Completion: {result['completion_percentage']:.1f}%")
            print(f"  Missing placeholders: {len(result['missing_placeholders'])}")
            print(f"  Missing critical translations: {len(result['missing_critical'])}")
    
    # Generate report
    generate_report(validation_results, args.report_file)
    print(f"Report generated: {args.report_file}")
    
    # Determine exit code
    has_errors = any(not r['xml_valid'] for r in validation_results)
    has_critical_missing = any(len(r['missing_critical']) > 0 for r in validation_results)
    has_placeholder_issues = any(len(r['missing_placeholders']) > 0 for r in validation_results)
    
    if has_errors:
        print("❌ Invalid XML found in translation files")
        return 1
    elif has_critical_missing and not args.critical_only:
        print("⚠️ Missing translations for critical UI elements")
        return 0  # Warning but not failure
    elif has_placeholder_issues:
        print("⚠️ Placeholder issues found")
        return 0  # Warning but not failure
    else:
        print("✅ All translations valid")
        return 0


if __name__ == "__main__":
    sys.exit(main()) 