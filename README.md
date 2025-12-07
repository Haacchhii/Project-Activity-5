# Network Automation Project - DevNet & Chill
## Project Activity 5: NETCONF/YANG/Python Automation

---

## 📋 Project Overview

This project automates network interface configuration changes for L1 Support Engineers using NETCONF/YANG protocols with Python. The tool connects to Cisco IOS XR devices and performs three critical configuration changes:

1. **Interface Description** - Updates to identify automated management
2. **Interface State** - Enables interface (no shutdown) for operational readiness
3. **MTU Configuration** - Sets to 1500 bytes to prevent fragmentation

After making changes, the tool sends notifications to WebEx Teams for team visibility.

---

## 👥 Team Members

**Team Name**: DevNet & Chill

| Member | Role | Contributions |
|--------|------|---------------|
| Richelle Grace Adarlo | Scrum Leader / Developer | Python script development, DevNet sandbox setup, GitHub repository management |
| Jose Iturralde | Co-Developer | GitHub branch integration, version testing, YANG model debugging |
| Henrick Yurie Mendoza | Tester | WebEx Teams integration, notification system testing |
| Zac Halaman | Tester | QA testing, NETCONF response validation, debugging support |
| Via Mae De Belen | Documentation Lead | Evidence collection, output screenshots, presentation materials |
| Rupery Cyril Garcia | Presenter | NETCONF/YANG research, testing assistance, presentations |

---

## 📁 Project Files

### Core Application
- **`network_automation.py`** - Main Python script with all automation logic

### Documentation
- **`GITHUB_BRANCHES.md`** - Complete branch strategy and Git workflow
- **`TESTING_DOCUMENTATION.md`** - Comprehensive testing phases and results
- **`REQUIREMENTS_COMPLIANCE.md`** - Verification that all requirements are met
- **`README.md`** - This file - project overview and usage guide
- **`for.txt`** - Original project activity requirements and team reflection

---

## 🛠️ Technical Details

### YANG Model
**Cisco-IOS-XR-ifmgr-cfg** (Cisco IOS XR Interface Manager Configuration)

### Platform
- **Device Type**: Cisco IOS XR
- **Protocol**: NETCONF over SSH
- **Port**: 830

### Python Dependencies
```python
ncclient      # NETCONF client library
xmltodict     # XML parsing
requests      # HTTP for WebEx Teams API
```

### Test Environment
- **Sandbox**: sandbox-iosxr-1.cisco.com
- **Interface**: GigabitEthernet0/0/0/0
- **Credentials**: admin / C1sco12345

---

## 🚀 Quick Start

### Installation
```powershell
# Install required packages
pip install ncclient xmltodict requests
```

### Configuration
Edit `network_automation.py` to set your WebEx webhook:
```python
WEBEX_WEBHOOK = "your_webhook_url_here"
```

### Run the Script
```powershell
python network_automation.py
```

### Expected Output
1. Connection to device
2. Display of BEFORE configuration
3. Three configuration changes applied
4. Display of AFTER configuration
5. WebEx Teams notification sent
6. Summary of changes

---

## 📊 Version History

| Version | Description | Branch | Developer |
|---------|-------------|--------|-----------|
| v1.0 | Initial NETCONF connection + description change | feature/netconf-connection | Richelle |
| v1.1 | Added shutdown/no-shutdown control | feature/shutdown-control | Jose |
| v1.2 | Added MTU configuration | feature/mtu-config | Jose |
| v1.3 | WebEx Teams notifications | feature/webex-integration | Henrick |
| v2.0 | Comprehensive YANG error handling | bugfix/yang-errors | Jose |
| v2.1 | Fixed WebEx 204 status code validation | bugfix/webex-response | Via Mae |
| v2.2 | Final production release | main | Team |

---

## 🧪 Testing Summary

### Testing Phases
- **Phase 1**: Individual feature testing (Unit tests)
- **Phase 2**: Integration testing (All features together)
- **Phase 3**: End-to-end validation (Complete workflow)

### Test Results
- **Total Test Cases**: 35
- **Pass Rate**: 100%
- **Bugs Found & Fixed**: 3

### Key Tests
✅ NETCONF connection establishment
✅ Interface description changes
✅ Interface state control (shutdown/no-shutdown)
✅ MTU configuration
✅ WebEx Teams notifications
✅ Error handling and recovery
✅ Configuration persistence

---

## 🐛 Known Issues & Solutions

### Issue #1: YANG Model Compatibility
**Problem**: Shutdown and MTU changes failed with 'bad-element' and 'unknown-element' errors

**Root Cause**: IOS XR requires different YANG structure than IOS XE

**Solution**: 
- Researched Cisco IOS XR documentation
- Updated XML structure to match IOS XR requirements
- Added error detection and handling

**Status**: ✅ RESOLVED (v2.0)

---

### Issue #2: WebEx 204 Status Code
**Problem**: Script reported notification failure even though messages were delivered

**Root Cause**: WebEx API returns 204 (No Content) as success, but script only accepted 200

**Solution**:
- Researched HTTP status code standards
- Updated validation to accept both 200 and 204
- Added documentation explaining 204 is valid success

**Status**: ✅ RESOLVED (v2.1)

---

## 📚 Key Learnings

### Technical Insights
1. **Platform-Specific YANG Models**: Different Cisco platforms (IOS XE vs IOS XR) require different YANG model structures
2. **NETCONF Error Messages**: Provide valuable debugging information - read them carefully
3. **HTTP Standards**: 204 (No Content) is a valid success response
4. **Incremental Testing**: Test simple things first to validate basic connectivity

### Development Process
1. **Feature Branches**: Allow parallel development without conflicts
2. **Incremental Development**: Small changes with frequent testing catch issues early
3. **Error Handling**: Partial failures shouldn't stop entire automation
4. **Documentation**: Essential for team understanding and project continuity

### Team Collaboration
1. **Clear Task Assignment**: Prevents duplicate work
2. **Daily Check-ins**: Short daily meetings more effective than weekly long ones
3. **Code Review**: Multiple perspectives catch different issues
4. **Celebrate Small Wins**: Maintains team morale through challenges

---

## 🎯 Project Objectives Achieved

✅ **Automate Configuration Changes**
- Interface description ✓
- Interface state (no shutdown) ✓
- MTU configuration ✓

✅ **Use NETCONF/YANG**
- NETCONF protocol implementation ✓
- Cisco-IOS-XR-ifmgr-cfg YANG model ✓

✅ **Team Notifications**
- WebEx Teams integration ✓
- Formatted messages with details ✓

✅ **Error Handling**
- Graceful error recovery ✓
- Platform-specific compatibility ✓

✅ **Documentation**
- Complete code documentation ✓
- Testing documentation ✓
- Branch strategy documented ✓

---

## 📖 How to Use This Project

### For Running the Automation
1. Read `network_automation.py` header for requirements
2. Install dependencies: `pip install ncclient xmltodict requests`
3. Configure WebEx webhook (optional)
4. Run: `python network_automation.py`

### For Understanding Development Process
1. Read `GITHUB_BRANCHES.md` for branch workflow
2. Review version history in code header
3. See how features were incrementally developed

### For Understanding Testing
1. Read `TESTING_DOCUMENTATION.md`
2. See what tests were performed
3. Understand how issues were found and fixed

### For Verification
1. Read `REQUIREMENTS_COMPLIANCE.md`
2. Verify all project requirements are met
3. See evidence of each requirement implementation

---

## 🔍 Code Highlights

### Robust Error Handling
```python
try:
    response = connection.edit_config(target='candidate', config=config)
    connection.commit()
    print("✓ Configuration applied successfully")
    return True
except Exception as e:
    print(f"⚠ Error: {e}")
    if 'bad-element' in str(e):
        print("Note: YANG model compatibility issue")
    print("✓ Continuing with remaining changes...")
    return False
```

### WebEx Integration
```python
if response.status_code in [200, 204]:
    print("✓ Notification sent successfully!")
    # 204 No Content is standard WebEx success response
```

### NETCONF Connection
```python
connection = manager.connect(
    host='sandbox-iosxr-1.cisco.com',
    port=830,
    username='admin',
    password='C1sco12345',
    hostkey_verify=False,
    device_params={'name': 'iosxr'}  # Platform-specific
)
```

---

## 🎓 Educational Value

This project demonstrates:
- Real-world network automation
- NETCONF/YANG protocol usage
- Python programming for networking
- Git branching and version control
- Agile development methodology
- Team collaboration and communication
- Problem-solving and debugging
- Technical documentation

---

## 📞 Support & Questions

For questions about this project, contact any team member:
- **Technical Issues**: Jose Iturralde (Co-Developer)
- **WebEx Integration**: Henrick Yurie Mendoza (Integration Lead)
- **Testing Details**: Zac Halaman (QA Lead)
- **Documentation**: Via Mae De Belen (Documentation Lead)
- **Project Overview**: Richelle Grace Adarlo (Scrum Leader)

---

## 🏆 Project Status

**Status**: ✅ COMPLETE AND PRODUCTION-READY

All requirements met, all tests passing, comprehensive documentation provided.

---

## 📝 License & Usage

This project was created for educational purposes as part of Project Activity 5.

**Team**: DevNet & Chill
**Date**: December 2025
**Course**: Network Automation with NETCONF/YANG

---

*"Automation rarely works perfectly on the first attempt, and troubleshooting is a normal part of the development process."*
*- DevNet & Chill Team Reflection*
