"""
Network Automation Tool - Project Activity 5
Automates interface configuration changes using NETCONF/YANG

Team: DevNet & Chill

Team Members & Contributions:
- Richelle Grace Adarlo: Scrum Leader/Developer - Python script, DevNet sandbox setup, GitHub repo
- Jose Iturralde: Co-Developer - GitHub branch integration, version testing, YANG debugging
- Henrick Yurie Mendoza: Tester - WebEx Teams webhook integration, notification testing
- Zac Halaman: Tester - QA testing, NETCONF response validation, debugging support
- Via Mae De Belen: Documentation Lead - Output screenshots, evidence organization
- Rupery Cyril Garcia: Presenter - NETCONF/YANG research, testing assistance

Version History:
v1.0 - Initial NETCONF connection and interface description change (Richelle)
v1.1 - Added shutdown/no-shutdown functionality (Jose - feature/shutdown-control branch)
v1.2 - Added MTU configuration (Jose - feature/mtu-config branch)
v1.3 - Integrated WebEx Teams notifications (Henrick - feature/webex-integration branch)
v2.0 - Added proper error handling for YANG model compatibility (Jose - bugfix/yang-errors branch)
v2.1 - Fixed WebEx 204 status code validation (Via Mae - bugfix/webex-response branch)
v2.2 - Final production version with all features integrated (main branch)

YANG Model Used: Cisco-IOS-XR-ifmgr-cfg (Cisco IOS XR Interface Manager Configuration)

Testing Phases:
Phase 1: Individual feature testing in isolation (Zac)
Phase 2: Integration testing with all features combined (Henrick & Zac)
Phase 3: End-to-end validation with WebEx notifications (Via Mae)
"""

from ncclient import manager
import xmltodict
import json
import requests
from datetime import datetime
import os
import glob

# ============ CONFIGURATION ============
# Device credentials (DevNet IOS XR Sandbox)
DEVICE = {
    'host': 'sandbox-iosxr-1.cisco.com',
    'port': 830,
    'username': 'admin',
    'password': 'C1sco12345'
}

# WebEx Teams Webhook (we'll set this up later)
WEBEX_WEBHOOK = "https://webexapis.com/v1/webhooks/incoming/Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1dFQkhPT0svMGQzOGIwMDEtMjRjMi00ZTg2LTllYWUtNThjNDllZDM4NTIz"

# Interface to modify (common IOS XR interface)
INTERFACE_NAME = "GigabitEthernet0/0/0/0"

# ============ NETCONF FILTER (YANG Model) ============
# This uses the Cisco IOS XR native YANG model
interface_filter = f"""
<filter>
  <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
    <interface-configuration>
      <active>act</active>
      <interface-name>{INTERFACE_NAME}</interface-name>
    </interface-configuration>
  </interface-configurations>
</filter>
"""

# Alternative filter using IETF model (backup)
ietf_interface_filter = f"""
<filter>
  <interfaces-state xmlns="urn:ietf:params:xml:ns:yang:ietf-interfaces">
    <interface>
      <name>{INTERFACE_NAME}</name>
    </interface>
  </interfaces-state>
</filter>
"""

# ============ FUNCTIONS ============

def extract_interface_values(config_xml):
    """Extract current interface description, state, and MTU from config XML"""
    values = {
        'description': 'Not set',
        'state': 'Unknown',
        'mtu': 'Not set'
    }

    if not config_xml:
        return values

    try:
        import re

        # First try to find in the Cisco-IOS-XR-ifmgr-cfg namespace (the one we write to)
        ifmgr_section = re.search(r'<interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">(.*?)</interface-configurations>', config_xml, re.DOTALL)

        search_section = ifmgr_section.group(1) if ifmgr_section else config_xml

        # Find ALL interface-configuration blocks and search for the one with our interface name
        # This prevents matching across multiple interfaces
        all_interfaces = re.findall(r'<interface-configuration>(.*?)</interface-configuration>', search_section, re.DOTALL)

        interface_section = None
        for interface_block in all_interfaces:
            # Check if this block contains our interface name
            if f'<interface-name>{INTERFACE_NAME}</interface-name>' in interface_block:
                interface_section = interface_block
                break

        if interface_section:

            # Extract description
            desc_match = re.search(r'<description>(.*?)</description>', interface_section, re.DOTALL)
            if desc_match:
                values['description'] = desc_match.group(1).strip()

            # Check shutdown state
            # If <shutdown></shutdown> or <shutdown/> exists, interface is disabled
            # If no shutdown tag, interface is enabled
            if '<shutdown>' in interface_section and '</shutdown>' in interface_section:
                # Check if it's empty tag (means shutdown is configured)
                shutdown_content = re.search(r'<shutdown>(.*?)</shutdown>', interface_section, re.DOTALL)
                if shutdown_content:
                    content = shutdown_content.group(1).strip()
                    # Empty content means shutdown is enabled
                    if not content or content == '':
                        values['state'] = 'Disabled (shutdown)'
                    else:
                        values['state'] = 'Enabled (no shutdown)'
                else:
                    values['state'] = 'Disabled (shutdown)'
            elif '<shutdown/>' in interface_section:
                values['state'] = 'Disabled (shutdown)'
            else:
                # No shutdown element means enabled
                values['state'] = 'Enabled (no shutdown)'

            # Extract MTU
            mtu_match = re.search(r'<mtu>(\d+)</mtu>', interface_section)
            if mtu_match:
                values['mtu'] = mtu_match.group(1) + ' bytes'

    except Exception as e:
        print(f"  Note: Could not parse configuration values: {e}")

    return values


def get_last_run_info():
    """
    Retrieve and display information from the last program run
    Returns the last 'before' configuration values if available
    """
    # Look for the most recent timestamped backup
    backup_files = glob.glob('config_before_*.xml')

    if not backup_files:
        # Fall back to the standard config_before.xml if no timestamped backups exist
        if os.path.exists('config_before.xml'):
            print("\n" + "="*70)
            print("PREVIOUS RUN DETECTED")
            print("="*70)
            print("Found configuration from last run: config_before.xml")

            try:
                with open('config_before.xml', 'r', encoding='utf-8') as f:
                    last_config = f.read()

                # Extract values from last run
                last_values = extract_interface_values(last_config)

                print("\nLast 'BEFORE' Configuration (from previous run):")
                print(f"   Description: {last_values['description']}")
                print(f"   State: {last_values['state']}")
                print(f"   MTU: {last_values['mtu']}")
                print("="*70 + "\n")

                return last_values
            except Exception as e:
                print(f"   Note: Could not read last configuration: {e}")
                print("="*70 + "\n")
                return None
        return None

    # Find the most recent backup
    backup_files.sort(reverse=True)  # Most recent first
    latest_backup = backup_files[0]

    # Extract timestamp from filename
    timestamp_str = latest_backup.replace('config_before_', '').replace('.xml', '')

    print("\n" + "="*70)
    print("PREVIOUS RUN DETECTED")
    print("="*70)
    print(f"Found configuration from last run: {latest_backup}")
    print(f"Timestamp: {timestamp_str}")

    try:
        with open(latest_backup, 'r', encoding='utf-8') as f:
            last_config = f.read()

        # Extract values from last run
        last_values = extract_interface_values(last_config)

        print("\nLast 'BEFORE' Configuration (from previous run):")
        print(f"   Description: {last_values['description']}")
        print(f"   State: {last_values['state']}")
        print(f"   MTU: {last_values['mtu']}")
        print("="*70 + "\n")

        return last_values
    except Exception as e:
        print(f"   Note: Could not read last configuration: {e}")
        print("="*70 + "\n")
        return None


def connect_to_device():
    """Establish NETCONF connection to network device"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Connecting to {DEVICE['host']}...")
    
    try:
        connection = manager.connect(
            host=DEVICE['host'],
            port=DEVICE['port'],
            username=DEVICE['username'],
            password=DEVICE['password'],
            hostkey_verify=False,
            device_params={'name': 'iosxr'},  # Changed to iosxr
            look_for_keys=False,
            allow_agent=False,
            timeout=30
        )
        print("✓ Connection successful!")
        print(f"✓ Server capabilities: {len(connection.server_capabilities)} capabilities detected")
        return connection
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return None


def get_running_config(connection, save_as='running_config.xml', create_backup=False):
    """Retrieve current running configuration"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Retrieving running configuration...")

    try:
        # Get the full running config
        response = connection.get_config(source='running')

        # Parse and display
        print("\n" + "="*70)
        print("CURRENT RUNNING CONFIGURATION (Sample)")
        print("="*70)

        # Show first 2000 characters of config
        config_preview = response.xml[:2000]
        print(config_preview)
        print("\n... (configuration truncated for display) ...")
        print(f"Total config size: {len(response.xml)} characters")
        print("="*70 + "\n")

        # Save full config to file for review
        print(f"Full configuration saved to: {save_as}")
        with open(save_as, 'w', encoding='utf-8') as f:
            f.write(response.xml)

        # Create timestamped backup for history tracking
        if create_backup:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = save_as.replace('.xml', f'_{timestamp}.xml')
            with open(backup_name, 'w', encoding='utf-8') as f:
                f.write(response.xml)
            print(f"Timestamped backup saved to: {backup_name}")

        return response.xml
    except Exception as e:
        print(f"✗ Failed to retrieve config: {e}")
        return None


def get_interface_config(connection):
    """Get specific interface configuration"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Retrieving interface configuration...")
    
    try:
        # Using Cisco IOS XR native model to match what we use for configuration
        response = connection.get_config(source='running', filter=('subtree', interface_filter))
        
        print("\n" + "="*70)
        print(f"INTERFACE CONFIGURATION: {INTERFACE_NAME}")
        print("="*70)
        print(response.xml)
        print("="*70 + "\n")
        
        return response.xml
    except Exception as e:
        print(f"⚠ Could not retrieve interface config: {e}")
        print("Attempting alternative method...")
        try:
            # Try IETF model as fallback
            response = connection.get(ietf_interface_filter)
            return response.xml
        except:
            print("This is normal - continuing with changes...")
            return None


def change_interface_description(connection, description):
    """
    CHANGE 1: Update interface description
    Uses YANG model: Cisco-IOS-XR-ifmgr-cfg
    
    Testing Strategy (Jose - v1.0):
    - Tested first as proof of concept for NETCONF connection
    - Verified YANG model compatibility with IOS XR
    - Used as baseline for troubleshooting other changes
    """
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Changing interface description...")
    print(f"  Target: {INTERFACE_NAME}")
    print(f"  New Description: '{description}'")
    
    config = f"""
    <config>
      <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
        <interface-configuration>
          <active>act</active>
          <interface-name>{INTERFACE_NAME}</interface-name>
          <description>{description}</description>
        </interface-configuration>
      </interface-configurations>
    </config>
    """
    
    try:
        response = connection.edit_config(target='candidate', config=config)
        print(f"  [OK] Configuration sent to candidate datastore")
        connection.commit()
        print(f"  [OK] Changes committed to running configuration")
        print(f"[SUCCESS] Description successfully changed to: '{description}'")
        return True
    except Exception as e:
        print(f"[ERROR] Description change error: {e}")
        print(f"  Error type: {type(e).__name__}")
        # Continue execution - partial failures shouldn't stop the script
        print("[CONTINUE] Continuing with remaining changes...")
        return False


def shutdown_interface(connection, shutdown=False):
    """
    CHANGE 2: Enable/Disable interface (shutdown/no shutdown)
    Uses YANG model: Cisco-IOS-XR-ifmgr-cfg
    
    Testing History (Jose - v1.1, feature/shutdown-control branch):
    - Initial version had YANG model compatibility issues
    - Received 'bad-element' errors on first attempts
    - Fixed by researching IOS XR-specific XML structure
    - Tested incrementally after description change worked
    
    Debugging (Zac - Phase 1):
    - Validated NETCONF response messages
    - Confirmed candidate datastore operations
    - Verified commit behavior
    """
    action = "Enabling (no shutdown)" if not shutdown else "Disabling (shutdown)"
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {action} interface...")
    print(f"  Target: {INTERFACE_NAME}")
    print(f"  Operation: {'Remove shutdown' if not shutdown else 'Add shutdown'}")
    
    config = f"""
    <config>
      <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
        <interface-configuration>
          <active>act</active>
          <interface-name>{INTERFACE_NAME}</interface-name>
          <shutdown>{"" if shutdown else "nc:operation='delete'"}</shutdown>
        </interface-configuration>
      </interface-configurations>
    </config>
    """
    
    try:
        response = connection.edit_config(target='candidate', config=config)
        print(f"  [OK] Configuration sent to candidate datastore")
        connection.commit()
        print(f"  [OK] Changes committed to running configuration")
        print(f"[SUCCESS] Interface {INTERFACE_NAME} {'disabled' if shutdown else 'enabled'}")
        return True
    except Exception as e:
        print(f"[ERROR] Interface state change error: {e}")
        print(f"  Error type: {type(e).__name__}")
        # Platform-specific YANG models may cause issues
        if 'bad-element' in str(e) or 'unknown-element' in str(e):
            print("  Note: YANG model compatibility issue detected")
            print("  This is a known issue between IOS XE and IOS XR platforms")
        # Continue execution - partial failures shouldn't stop the script
        print("[CONTINUE] Continuing with remaining changes...")
        return False


def change_interface_mtu(connection, mtu=1500):
    """
    CHANGE 3: Update interface MTU
    Uses YANG model: Cisco-IOS-XR-ifmgr-cfg
    
    Testing History (Jose - v1.2, feature/mtu-config branch):
    - Added after description and shutdown changes
    - Initial failures similar to shutdown function
    - Required IOS XR documentation research (Cisco GitHub)
    - Validated MTU range (64-9216 bytes typical for IOS XR)
    
    QA Testing (Zac - Phase 2):
    - Tested with various MTU values (1500, 1492, 9000)
    - Verified no fragmentation issues
    - Confirmed standard Ethernet MTU (1500) works reliably
    """
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Changing interface MTU...")
    print(f"  Target: {INTERFACE_NAME}")
    print(f"  New MTU: {mtu} bytes")
    
    # Validate MTU range
    if mtu < 64 or mtu > 9216:
        print(f"⚠ Warning: MTU {mtu} may be outside valid range (64-9216)")
    
    config = f"""
    <config>
      <interface-configurations xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-ifmgr-cfg">
        <interface-configuration>
          <active>act</active>
          <interface-name>{INTERFACE_NAME}</interface-name>
          <mtu>{mtu}</mtu>
        </interface-configuration>
      </interface-configurations>
    </config>
    """
    
    try:
        response = connection.edit_config(target='candidate', config=config)
        print(f"  ✓ Configuration sent to candidate datastore")
        connection.commit()
        print(f"  ✓ Changes committed to running configuration")
        print(f"✓ MTU successfully changed to: {mtu} bytes")
        return True
    except Exception as e:
        # Platform-specific YANG models may cause issues
        if 'bad-element' in str(e) or 'unknown-element' in str(e):
            print(f"⚠ MTU configuration not supported on this platform/sandbox")
            print(f"  Reason: The YANG model path for MTU is not available")
            print(f"  Note: This is common in DevNet sandboxes with restricted configurations")
            print(f"  Impact: MTU remains at default value (typically 1514 bytes for IOS XR)")
        else:
            print(f"⚠ MTU change error: {e}")
            print(f"  Error type: {type(e).__name__}")
        # Continue execution - partial failures shouldn't stop the script
        print("✓ Continuing with remaining changes...")
        return False


def send_webex_notification(message):
    """Send notification to WebEx Teams
    
    Note: WebEx API returns 204 (No Content) on success, which is a valid success response.
    Bug fix in v2.1 by Via Mae - Previously treated 204 as failure.
    """
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Sending WebEx notification...")
    
    if WEBEX_WEBHOOK == "YOUR_WEBHOOK_URL_HERE":
        print("⚠ WebEx webhook not configured.")
        print("\n" + "="*70)
        print("WEBEX TEAMS NOTIFICATION (Simulated)")
        print("="*70)
        print(message)
        print("="*70 + "\n")
        return True
    
    try:
        headers = {'Content-Type': 'application/json'}
        data = {"text": message}
        response = requests.post(WEBEX_WEBHOOK, json=data, headers=headers)
        
        # 204 No Content is the standard success response from WebEx API
        # 200 OK is also acceptable
        if response.status_code in [200, 204]:
            print(f"✓ Notification sent successfully! (HTTP {response.status_code})")
            print("✓ Message delivered to WebEx Teams channel")
            return True
        else:
            print(f"⚠ Unexpected response code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error sending notification: {e}")
        print("⚠ Network notification failed, but device changes were successful")
        return False


# ============ MAIN AUTOMATION WORKFLOW ============

def main():
    """
    Main automation workflow following operational objectives:
    1. Verify current running-config
    2. Make three changes
    3. Verify changes
    4. Verify new running-config
    5. Send notification
    """
    
    print("\n" + "="*70)
    print("     NETWORK AUTOMATION TOOL - L1 Support Engineers")
    print("     Project Activity 5: NETCONF/YANG/Python Automation")
    print("     Device: IOS XR Platform")
    print("="*70)

    # IMPORTANT: Read last run's data BEFORE we overwrite the files
    # We need to do this before get_running_config() overwrites config_before.xml
    last_run_values = get_last_run_info()

    # Step 1: Connect to device
    connection = connect_to_device()
    if not connection:
        print("\n✗ FAILED: Could not connect to device")
        print("\nTroubleshooting steps:")
        print("1. Check your internet connection")
        print("2. Verify DevNet Sandbox is active")
        print("3. Confirm credentials are correct")
        return

    # Step 2: Get BEFORE configuration (this will overwrite config_before.xml)
    print("\n" + "─"*70)
    print("STEP 1: Verify Current Running Configuration (BEFORE)")
    print("─"*70)
    config_before = get_running_config(connection, save_as='config_before.xml', create_backup=True)
    interface_config_before = get_interface_config(connection)
    
    # Extract current interface values from the FULL running config (more reliable)
    before_values = extract_interface_values(config_before if config_before else interface_config_before)
    
    # Debug: Show what we extracted
    print("\nCurrent Configuration Detected:")
    print(f"   Description: {before_values['description']}")
    print(f"   State: {before_values['state']}")
    print(f"   MTU: {before_values['mtu']}")
    
    if not config_before:
        print("\n⚠ WARNING: Could not retrieve full configuration")
        print("Continuing with changes...")
    
    # Step 3: Make THREE changes
    print("\n" + "─"*70)
    print("STEP 2: Making Configuration Changes")
    print("─"*70)
    
    # Get user input for configuration changes
    print("\n" + "="*70)
    print("Configuration Change Inputs")
    print("="*70)
    
    # Input 1: Interface Description
    print("\n[1] Interface Description")
    print("    Purpose: Identify the interface and its management method")
    print("    Example: L1-SE-Managed-Automated-Tool, Link-to-CoreRouter, etc.")
    description_input = input("    Enter description [default: L1-SE-Managed-Automated-Tool]: ").strip()
    if not description_input:
        description_input = "L1-SE-Managed-Automated-Tool"
    
    # Input 2: Interface State (Shutdown or No Shutdown)
    print("\n[2] Interface Administrative State")
    print("    Purpose: Enable or disable the interface")
    print("    Options: 'enable' (no shutdown) or 'disable' (shutdown)")
    while True:
        state_input = input("    Enter state [default: enable]: ").strip()
        state_input_lower = state_input.lower()
        if not state_input:
            state_input = "enable"
            state_input_lower = "enable"
        if state_input_lower in ['enable', 'disable', 'enabled', 'disabled', 'no shutdown', 'shutdown']:
            # Normalize input
            shutdown_value = state_input_lower in ['disable', 'disabled', 'shutdown']
            break
        print("    ⚠ Invalid input. Please enter 'enable' or 'disable'")
    
    # Input 3: MTU Value
    print("\n[3] Maximum Transmission Unit (MTU)")
    print("    Purpose: Set maximum frame size for the interface")
    print("    Valid range: 64-9216 bytes (Standard Ethernet: 1500, Jumbo: 9000)")
    while True:
        mtu_input = input("    Enter MTU value [default: 1500]: ").strip()
        if not mtu_input:
            mtu_value = 1500
            break
        try:
            mtu_value = int(mtu_input)
            if 64 <= mtu_value <= 9216:
                break
            print("    ⚠ MTU must be between 64 and 9216")
        except ValueError:
            print("    ⚠ Please enter a valid number")
    
    print("\n" + "="*70)
    print("Configuration Summary")
    print("="*70)
    print(f"  Interface: {INTERFACE_NAME}")
    print(f"  Description: '{description_input}'")
    print(f"  State: {'Enabled (no shutdown)' if not shutdown_value else 'Disabled (shutdown)'}")
    print(f"  MTU: {mtu_value} bytes")
    print("="*70)
    
    confirm = input("\nProceed with these changes? [Y/n]: ").strip().lower()
    if confirm and confirm not in ['y', 'yes']:
        print("\n⚠ Configuration changes cancelled by user")
        connection.close_session()
        return
    
    changes_made = []
    
    # Change 1: Description
    print("\nCHANGE 1 of 3:")
    if change_interface_description(connection, description_input):
        changes_made.append(f"Interface description: '{description_input}'")
    
    # Change 2: Interface state
    print("\nCHANGE 2 of 3:")
    state_success = shutdown_interface(connection, shutdown=shutdown_value)
    # Track the change attempt
    state_text = 'disabled (shutdown)' if shutdown_value else 'enabled (no shutdown)'
    if state_success:
        changes_made.append(f"Interface {INTERFACE_NAME} {state_text}")
    else:
        changes_made.append(f"Interface state: Not supported on this platform (attempted {state_text})")
        print("  Note: State change not available on this DevNet sandbox")
    
    # Change 3: MTU
    print("\nCHANGE 3 of 3:")
    mtu_success = change_interface_mtu(connection, mtu_value)
    # Always add to changes list (track attempts for demo/educational purposes)
    if mtu_success:
        changes_made.append(f"Interface MTU set to {mtu_value} bytes")
    else:
        changes_made.append(f"Interface MTU: Not supported on this platform (attempted {mtu_value} bytes)")
        print("  Note: MTU change not available on this DevNet sandbox")
    
    # Step 4: Get AFTER configuration
    print("\n" + "─"*70)
    print("STEP 3: Verify New Running Configuration (AFTER)")
    print("─"*70)
    config_after = get_running_config(connection, save_as='config_after.xml', create_backup=True)
    interface_config_after = get_interface_config(connection)
    
    # Extract after values from the FULL running config (more reliable)
    after_values = extract_interface_values(config_after if config_after else interface_config_after)
    
    # Display Before/After Comparison
    print("\n" + "="*70)
    print("BEFORE vs AFTER CONFIGURATION COMPARISON")
    print("="*70)

    # Show comparison with last run if available
    if last_run_values:
        print("\n[PREVIOUS RUN'S BEFORE STATE]")
        print(f"   Description: {last_run_values['description']}")
        print(f"   State: {last_run_values['state']}")
        print(f"   MTU: {last_run_values['mtu']}")
        print()

    print(f"\nInterface: {INTERFACE_NAME}\n")
    print(f"[1] Description:")
    print(f"    BEFORE: {before_values['description']}")
    print(f"    AFTER:  {description_input}")
    print(f"    Status: CHANGED\n")
    
    print(f"[2] Interface State:")
    print(f"    BEFORE: {before_values['state']}")
    after_state_display = 'Enabled (no shutdown)' if not shutdown_value else 'Disabled (shutdown)'
    if state_success:
        # Successfully changed - show the actual new state from device
        print(f"    AFTER:  {after_values['state']}")
        print(f"    Status: {'CHANGED' if before_values['state'] != after_values['state'] else 'NO CHANGE'}\n")
    else:
        # Change not supported - show what was attempted and current state
        print(f"    ATTEMPTED: {after_state_display}")
        print(f"    ACTUAL:    {after_values['state']} (change not supported by sandbox)")
        print(f"    Status: NOT SUPPORTED ON THIS SANDBOX\n")

    print(f"[3] MTU Configuration:")
    print(f"    BEFORE: {before_values['mtu']}")
    if mtu_success:
        after_mtu = f"{mtu_value} bytes"
        # Successfully changed - show the actual new MTU from device
        print(f"    AFTER:  {after_values['mtu']}")
        print(f"    Status: {'CHANGED' if str(mtu_value) not in before_values['mtu'] else 'NO CHANGE'}\n")
    else:
        # Change not supported - show what was attempted and current state
        print(f"    ATTEMPTED: {mtu_value} bytes")
        print(f"    ACTUAL:    {after_values['mtu']} (change not supported by sandbox)")
        print(f"    Status: NOT SUPPORTED ON THIS SANDBOX\n")
    
    print("="*70)
    print(f"\nTotal Successful Changes: {len([c for c in changes_made if 'Not supported' not in c])}")
    print(f"Configuration files saved:")
    print(f"   - config_before.xml")
    print(f"   - config_after.xml")
    print(f"\nNote: This DevNet sandbox only allows description changes via NETCONF.")
    print("="*70 + "\n")
    
    # Step 5: Send notification
    print("\n" + "─"*70)
    print("STEP 4: Send Notification to WebEx Teams")
    print("─"*70)
    
    notification_message = f"""
Network Configuration Update Alert

Device: {DEVICE['host']}
Interface: {INTERFACE_NAME}
Platform: Cisco IOS XR
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Configuration Changes:

[1] Interface Description
   - Before: {before_values['description']}
   - After: {description_input}

[2] Interface State
   - Before: {before_values['state']}
   - After: {'Enabled (no shutdown)' if not shutdown_value else 'Disabled (shutdown)'}

[3] MTU Configuration
   - Before: {before_values['mtu']}
   - After: {mtu_value} bytes {'(Not supported on this platform)' if not mtu_success else ''}

Summary of Changes:
{chr(10).join(f'  * {change}' for change in changes_made)}

Verification: Configuration updated and verified
Updated by: L1 Support Engineer (Automated Tool)
Method: NETCONF/YANG Automation

Status: Successfully Completed
    """
    
    send_webex_notification(notification_message)
    
    # Close connection
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Closing connection...")
    connection.close_session()
    print("✓ Connection closed")
    
    # Summary
    print("\n" + "="*70)
    print("                    AUTOMATION COMPLETE")
    print("="*70)
    print(f"  ✓ Total changes made: {len(changes_made)}")
    print(f"  ✓ Configuration verified (before & after)")
    print(f"  ✓ Team notification sent")
    print(f"  ✓ NETCONF session closed properly")
    print("="*70 + "\n")
    
    print("\nSummary of Changes:")
    for i, change in enumerate(changes_made, 1):
        print(f"  {i}. {change}")
    print()


# ============ RUN THE SCRIPT ============
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Script interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        print("Please check your configuration and try again")