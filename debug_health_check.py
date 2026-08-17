#!/usr/bin/env python3
"""Comprehensive diagnostic script for cross-machine health check differences"""

import json
import os
import sys
from pathlib import Path

# Add src to path so we can import emolpat modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from emolpat.domain import InstallRecord, SuiteManifest, SuiteState
from emolpat.health import read_install_record, evaluate_health
from emolpat.health_probe import probe_health, module_available
from emolpat.manifest import load_manifest
from emolpat.paths import UserPaths

def print_section(title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")

def get_install_record_info(record):
    if record is None:
        return "No install record found"
    
    info = f"""Install Record:
  Suite Version: {record.suite_version}
  Manifest SHA256: {record.manifest_sha256}
  Verified At: {record.verified_at}
  Modules:
"""
    for module in record.modules:
        info += f"    - {module.distribution}=={module.version} (import: {module.import_name})\n"
    return info

def get_manifest_info(manifest):
    if manifest is None:
        return "No manifest found"
    
    info = f"""Manifest:
  Schema Version: {manifest.schema_version}
  Suite Version: {manifest.suite_version}
  Python Requires: {manifest.python_requires}
  Modules:
"""
    for module in manifest.modules:
        info += f"    - {module.id}: {module.distribution}=={module.version} (import: {module.import_name})\n"
    return info

def print_machine_info():
    print_section("Current Machine Diagnostic Information")
    
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {sys.executable}")
    print(f"Current Working Directory: {os.getcwd()}")
    
    # Check LOCALAPPDATA
    localappdata = os.environ.get("LOCALAPPDATA")
    print(f"LOCALAPPDATA: {localappdata}")
    
    # Check USERPROFILE
    userprofile = os.environ.get("USERPROFILE")
    print(f"USERPROFILE: {userprofile}")
    
    # Check HOMEPATH/HOMEUSERPROFILE
    homepath = os.environ.get("HOMEPATH")
    homeuserprofile = os.environ.get("HOMEDRIVE") + os.environ.get("HOMEPATH", "")
    print(f"HOMEPATH: {homepath}")
    print(f"HOMEUSERPROFILE: {homeuserprofile}")
    
    # Try to find the install record path
    possible_paths = [
        Path(localappdata) / "eMolPat" / "install-record.json" if localappdata else None,
        Path(userprofile) / "AppData" / "Local" / "eMolPat" / "install-record.json" if userprofile else None,
        Path.home() / "AppData" / "Local" / "eMolPat" / "install-record.json",
        Path.cwd() / "eMolPat" / "install-record.json",
        Path.cwd().parent / "eMolPat" / "install-record.json",
    ]
    
    print(f"\nLooking for install-record.json in:")
    for path in possible_paths:
        if path is None:
            continue
        exists = path.exists()
        print(f"  {path} - {'EXISTS' if exists else 'NOT FOUND'}")
        
        if exists:
            try:
                # Try to read the install record
                with open(path, 'r') as f:
                    content = json.load(f)
                print(f"    Content: {json.dumps(content, indent=4)}")
            except Exception as e:
                print(f"    Error reading: {e}")

def print_health_check_details(record, manifest, health_report):
    print_section("Health Check Details")
    
    if health_report is None:
        print("No health report generated")
        return
    
    print(f"Health Report State: {health_report.state}")
    print(f"Suite Version: {health_report.suite_version}")
    print(f"Issues: {len(health_report.issues)}")
    
    if health_report.issues:
        print("\nDetailed Issues:")
        for issue in health_report.issues:
            print(f"  - {issue}")
    
    # Show module status
    if record:
        print(f"\nModule Status Check:")
        for module in record.modules:
            # Check if module is importable
            importable = module_available(module.import_name)
            print(f"  - {module.distribution}=={module.version} (import: {module.import_name}) - {'IMPORTABLE' if importable else 'NOT IMPORTABLE'}")
            
            # Try to get version
            try:
                from importlib.metadata import version
                actual_version = version(module.distribution)
                print(f"    Expected: {module.version}, Actual: {actual_version}, Match: {actual_version == module.version}")
            except Exception as e:
                print(f"    Error getting version: {e}")

def main():
    print_section("eMolPat Cross-Machine Health Check Diagnostic")
    
    # Print machine information
    print_machine_info()
    
    # Try to locate the install record
    possible_record_paths = []
    localappdata = os.environ.get("LOCALAPPDATA")
    if localappdata:
        possible_record_paths.append(Path(localappdata) / "eMolPat" / "install-record.json")
    
    userprofile = os.environ.get("USERPROFILE")
    if userprofile:
        possible_record_paths.append(Path(userprofile) / "AppData" / "Local" / "eMolPat" / "install-record.json")
    
    possible_record_paths.append(Path.home() / "AppData" / "Local" / "eMolPat" / "install-record.json")
    
    # Load install record
    record = None
    for path in possible_record_paths:
        if path.exists():
            print_section(f"Found install record at: {path}")
            try:
                record = read_install_record(path)
                print(f"Successfully loaded install record")
                print(record)
                break
            except Exception as e:
                print(f"Error loading install record: {e}")
                record = None
    
    if record is None:
        print("\n❌ No install record found on this machine")
        return
    
    # Try to locate the manifest
    # First try to get it from the record if possible
    # This is tricky because the record doesn't store the full path
    
    # Try common locations
    manifest_candidates = [
        Path.cwd() / "release" / "manifest.json",
        Path.cwd().parent / "release" / "manifest.json",
        Path.cwd() / "src" / "emolpat" / "ui" / "resources" / "suite-manifest.json",
        Path(localappdata) / "eMolPat" / "release" / "manifest.json" if localappdata else None,
        Path(userprofile) / "AppData" / "Local" / "eMolPat" / "release" / "manifest.json" if userprofile else None,
    ]
    
    manifest = None
    manifest_path = None
    
    for candidate in manifest_candidates:
        if candidate is None or not Path(candidate).exists():
            continue
            
        try:
            manifest = load_manifest(Path(candidate))
            manifest_path = candidate
            print_section(f"Trying manifest at: {candidate}")
            print(f"Successfully loaded manifest: suite_version={manifest.suite_version}")
            print(f"Modules: {[m.id for m in manifest.modules]}")
            break
        except Exception as e:
            print(f"Error loading manifest: {e}")
            continue
    
    if manifest is None:
        print("\n❌ Could not load manifest")
        return
    
    # Run health check
    print_section("Running Health Check")
    try:
        # Use environment variables to construct UserPaths
        paths = UserPaths.from_environment(os.environ)
        print(f"UserPaths: {paths}")
        
        health_report = probe_health(manifest, paths)
        print_health_check_details(record, manifest, health_report)
        
    except Exception as e:
        print(f"Error during health check: {e}")
        import traceback
        traceback.print_exc()
    
    # Print summary
    print_section("Summary")
    if health_report:
        if health_report.state == SuiteState.READY:
            print("✅ Machine health check PASSED - Suite is ready")
        elif health_report.state == SuiteState.UPDATE_AVAILABLE:
            print("⚠️  Machine health check shows UPDATE AVAILABLE")
        elif health_report.state == SuiteState.REPAIR_REQUIRED:
            print("❌ Machine health check shows REPAIR REQUIRED")
        elif health_report.state == SuiteState.NOT_INSTALLED:
            print("❌ Machine health check shows NOT INSTALLED")
        elif health_report.state == SuiteState.UNAVAILABLE:
            print("❌ Machine health check shows UNAVAILABLE")
        
        if health_report.issues:
            print("\nIssues found:")
            for issue in health_report.issues:
                print(f"  - {issue}")
    else:
        print("❌ No health report was generated")

if __name__ == "__main__":
    main()