#!/usr/bin/env python3
"""Enhanced diagnostic script for eMolPat health check - works from any directory"""

import os
import sys
from pathlib import Path

# Add src to path so we can import emolpat modules
sys.path.insert(0, str(Path(__file__).parent / "src"))

from emolpat.domain import InstallRecord, SuiteManifest, SuiteState
from emolpat.health import read_install_record
from emolpat.health_probe import module_available, probe_health
from emolpat.manifest import load_manifest
from emolpat.paths import UserPaths


def print_section(title):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")

def redact_path(text: str) -> str:
    """Redact user-specific paths for privacy"""
    if not text:
        return text
    
    # Replace common user path patterns
    replacements = [
        (os.environ.get('USERNAME', 'user'), '<USER>'),
        (os.environ.get('USERPROFILE', ''), '<USERPROFILE>'),
        (os.environ.get('LOCALAPPDATA', ''), '<LOCALAPPDATA>'),
        (os.environ.get('APPDATA', ''), '<APPDATA>'),
    ]
    
    for old, new in replacements:
        if old and old in text:
            text = text.replace(old, new)
    
    return text

def get_bundled_manifest():
    """Get the bundled manifest from the portal package"""
    try:
        from importlib.resources import as_file, files
        resource = files("emolpat.ui.resources").joinpath("suite-manifest.json")
        with as_file(resource) as manifest_path:
            return load_manifest(manifest_path)
    except Exception as e:  # noqa: BLE001 - diagnostic boundary reports all failures
        print(f"Error loading bundled manifest: {e}")
        return None

def get_network_manifest():
    """Get the network release manifest if available"""
    release_root = os.environ.get("EMOLPAT_RELEASE_ROOT")
    if not release_root:
        return None
    
    manifest_path = Path(release_root) / "manifest.json"
    if not manifest_path.exists():
        return None
    
    try:
        return load_manifest(manifest_path)
    except Exception as e:  # noqa: BLE001 - diagnostic boundary reports all failures
        print(f"Error loading network manifest: {e}")
        return None

def get_retained_manifest(record: InstallRecord | None, paths: UserPaths):
    """Get the retained local manifest if available"""
    if not record:
        return None
    
    retained_path = paths.rollback / record.suite_version / "manifest.json"
    if not retained_path.exists():
        return None
    
    try:
        return load_manifest(retained_path)
    except Exception as e:  # noqa: BLE001 - diagnostic boundary reports all failures
        print(f"Error loading retained manifest: {e}")
        return None

def print_machine_info():
    print_section("Current Machine Diagnostic Information")
    
    print(f"Python Version: {sys.version}")
    print(f"Python Executable: {redact_path(sys.executable)}")
    print(f"Current Working Directory: {redact_path(os.getcwd())}")
    
    # Check environment variables
    env_vars = ['LOCALAPPDATA', 'USERPROFILE', 'APPDATA', 'EMOLPAT_RELEASE_ROOT']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"{var}: {redact_path(value)}")
        else:
            print(f"{var}: NOT SET")

def check_install_record(paths: UserPaths):
    """Check and load install record"""
    print_section("Install Record Check")
    
    install_record_path = paths.install_record
    print(f"Expected location: {redact_path(str(install_record_path))}")
    print(f"Exists: {install_record_path.exists()}")
    
    if not install_record_path.exists():
        print("FEIL: No install record found")
        return None
    
    try:
        record = read_install_record(install_record_path)
        print("OK: Install record loaded successfully")
        print(f"Suite version: {record.suite_version}")
        print(f"Verified at: {record.verified_at}")
        print(f"Manifest SHA256: {record.manifest_sha256[:16]}...")
        
        print("\nModules:")
        for module in record.modules:
            print(f"  - {module.distribution}=={module.version} (import: {module.import_name})")
        
        return record
    except Exception as e:  # noqa: BLE001 - diagnostic boundary reports all failures
        print(f"FEIL: Error reading install record: {e}")
        return None

def check_manifests(record: InstallRecord | None, paths: UserPaths):
    """Check all available manifests"""
    print_section("Manifest Sources")
    
    # 1. Bundled manifest
    print("\n1. BUNDLED PORTAL MANIFEST:")
    bundled = get_bundled_manifest()
    if bundled:
        print(f"  OK: Version: {bundled.suite_version}")
        print(f"  Modules: {[m.id for m in bundled.modules]}")
    else:
        print("  FEIL: Could not load")
    
    # 2. Network manifest
    print("\n2. NETWORK RELEASE MANIFEST:")
    network = get_network_manifest()
    if network:
        print(f"  OK: Version: {network.suite_version}")
        print(f"  Path: {redact_path(os.environ.get('EMOLPAT_RELEASE_ROOT', 'NOT SET'))}")
    else:
        print("  FEIL: Not available or EMOLPAT_RELEASE_ROOT not set")
    
    # 3. Retained manifest
    print("\n3. RETAINED LOCAL MANIFEST:")
    retained = get_retained_manifest(record, paths)
    if retained:
        print(f"  OK: Version: {retained.suite_version}")
        print(f"  Path: {redact_path(str(paths.rollback / record.suite_version))}")
    else:
        print("  FEIL: Not available")
    
    return bundled, network, retained

def check_module_status(record: InstallRecord | None):
    """Check if modules are importable and versions match"""
    print_section("Module Status Check")
    
    if not record:
        print("FEIL: No install record - cannot check modules")
        return
    
    print("Checking distribution versions and imports:\n")
    
    all_ok = True
    for module in record.modules:
        # Check import
        importable = module_available(module.import_name)
        
        # Check version
        try:
            from importlib.metadata import version
            actual_version = version(module.distribution)
            version_match = actual_version == module.version
        except Exception as e:  # noqa: BLE001 - diagnostic boundary reports all failures
            actual_version = f"ERROR: {e}"
            version_match = False
        
        status = "OK" if (importable and version_match) else "FEIL"
        print(f"{status} {module.distribution}")
        print(f"    Expected: {module.version}, Actual: {actual_version}")
        print(f"    Import: {'OK' if importable else 'FAILED'}")
        
        if not (importable and version_match):
            all_ok = False
    
    return all_ok

def run_health_check(manifest: SuiteManifest, paths: UserPaths):
    """Run the actual health check"""
    print_section("Health Check Result")
    
    try:
        health_report = probe_health(manifest, paths)
        
        print(f"State: {health_report.state}")
        print(f"Suite version: {health_report.suite_version}")
        
        if health_report.issues:
            print(f"\nIssues ({len(health_report.issues)}):")
            for issue in health_report.issues:
                print(f"  - {issue}")
        else:
            print("\nOK: No issues detected")
        
        return health_report
    except Exception as e:  # noqa: BLE001 - diagnostic boundary reports all failures
        print(f"FEIL: Error running health check: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    print_section("eMolPat Enhanced Health Check Diagnostic")
    print("This script works from any directory, including Citrix environments")
    
    # Print machine info
    print_machine_info()
    
    # Get paths
    try:
        paths = UserPaths.from_environment(os.environ)
        print(f"\nUserPaths root: {redact_path(str(paths.root))}")
    except Exception as e:  # noqa: BLE001 - diagnostic boundary reports all failures
        print(f"\nFEIL: Error creating UserPaths: {e}")
        return
    
    # Check install record
    record = check_install_record(paths)
    
    # Check manifests
    bundled, _network, _retained = check_manifests(record, paths)
    
    # Check module status
    check_module_status(record)
    
    # Run health check using bundled manifest (same as portal)
    if bundled:
        health_report = run_health_check(bundled, paths)
    else:
        print("\nFEIL: Cannot run health check - no bundled manifest available")
        health_report = None
    
    # Print summary
    print_section("Summary")
    
    if health_report:
        if health_report.state == SuiteState.READY:
            print("OK: PASS - Suite is ready")
            print("   Portal should display: 'Klar til bruk'")
            print("   All application cards should be enabled")
        elif health_report.state == SuiteState.UPDATE_AVAILABLE:
            print("ADVARSEL: UPDATE AVAILABLE - Newer version detected")
        elif health_report.state == SuiteState.REPAIR_REQUIRED:
            print("FEIL: REPAIR REQUIRED - Issues detected")
            print("   Portal will display: 'Ikke klar'")
            print("   Application cards will be disabled")
        elif health_report.state == SuiteState.NOT_INSTALLED:
            print("FEIL: NOT INSTALLED - No valid install record")
        elif health_report.state == SuiteState.UNAVAILABLE:
            print("FEIL: UNAVAILABLE - System error")
        
        if health_report.issues:
            print("\nAction required: Fix the following issues:")
            for issue in health_report.issues:
                print(f"  - {issue}")
    else:
        print("FEIL: FAIL - Could not complete health check")
    
    print("\n" + "="*60)
    print("Diagnostic complete")
    print("="*60)

if __name__ == "__main__":
    main()
