# Testing Documentation - Network Automation Project
## DevNet & Chill Team - Project Activity 5

---

## Testing Team Members
- **Zac Halaman**: QA Tester - NETCONF response validation, configuration change testing
- **Henrick Yurie Mendoza**: Integration Tester - WebEx Teams webhook, notification system
- **Via Mae De Belen**: End-to-End Tester - Full workflow validation, output capture
- **Rupery Cyril Garcia**: Testing Assistant - Feature validation, debugging support

---

## Testing Strategy Overview

The team followed a three-phase testing approach aligned with the agile development methodology:

### Phase 1: Individual Feature Testing (Unit Testing)
**Lead**: Zac Halaman
**Duration**: Week 1-2
**Objective**: Validate each configuration change works independently

### Phase 2: Integration Testing
**Lead**: Henrick Yurie Mendoza & Zac Halaman
**Duration**: Week 2-3
**Objective**: Verify all features work together without conflicts

### Phase 3: End-to-End Validation
**Lead**: Via Mae De Belen
**Duration**: Week 3
**Objective**: Complete workflow testing with WebEx notifications and evidence capture

---

## Phase 1: Individual Feature Testing

### Test 1.1: NETCONF Connection (v1.0)
**Tester**: Zac Halaman
**Branch**: `feature/netconf-connection`
**Date**: Phase 1, Week 1

**Test Cases**:
1. **Connection Establishment**
   - ✓ Successfully connects to sandbox-iosxr-1.cisco.com:830
   - ✓ Authentication with admin/C1sco12345 works
   - ✓ Device parameters set to 'iosxr' correctly
   - ✓ Server capabilities detected (1000+ capabilities)

2. **Error Handling**
   - ✓ Handles connection timeout gracefully
   - ✓ Shows clear error message if credentials are wrong
   - ✓ Provides troubleshooting steps on failure

**Results**: ✓ PASSED
**Notes**: Connection stable and reliable. No issues detected.

---

### Test 1.2: Interface Description Change (v1.0)
**Tester**: Zac Halaman
**Branch**: `feature/netconf-connection`
**Date**: Phase 1, Week 1

**Test Cases**:
1. **Description Update**
   - ✓ Changes interface description successfully
   - ✓ Uses correct YANG model: Cisco-IOS-XR-ifmgr-cfg
   - ✓ Commits to running configuration
   - ✓ Description visible in device config

2. **NETCONF Operations**
   - ✓ edit_config() sends configuration to candidate datastore
   - ✓ commit() applies changes to running config
   - ✓ Response XML contains success confirmation

3. **Different Description Values**
   - ✓ Short description: "Test"
   - ✓ Standard description: "L1-SE-Managed-Automated-Tool"
   - ✓ Long description: "L1 Support Engineer Managed Interface via NETCONF Automation Tool"
   - ✓ Special characters: "Link to Core-Router_Gig0/0/0/1"

**Results**: ✓ PASSED
**Notes**: This was the baseline test. All other features built on this success.

---

### Test 1.3: Interface Shutdown Control (v1.1)
**Tester**: Zac Halaman
**Branch**: `feature/shutdown-control`
**Date**: Phase 1, Week 2

**Test Cases**:
1. **No Shutdown (Enable Interface)**
   - ⚠ Initial attempt: FAILED with 'bad-element' error
   - ✓ After fix: Successfully enables interface
   - ✓ Uses nc:operation='delete' to remove shutdown

2. **Shutdown (Disable Interface)**
   - ⚠ Initial attempt: FAILED with 'unknown-element' error
   - ✓ After fix: Successfully disables interface
   - ✓ Proper XML structure for IOS XR

3. **NETCONF Response Validation**
   - ✓ Candidate datastore accepts configuration
   - ✓ Commit operation completes without errors (after fix)
   - ✓ Response messages are informative

**Initial Results**: ⚠ FAILED (YANG model compatibility issue)
**After Debugging**: ✓ PASSED
**Key Issues Found**:
- IOS XR YANG model structure different from IOS XE
- Required research into Cisco-IOS-XR-ifmgr-cfg documentation
- XML structure needed platform-specific format

**Debugging Process**:
1. Compared working description change vs failing shutdown
2. Identified YANG model namespace differences
3. Researched Cisco GitHub for IOS XR examples
4. Updated XML structure to match IOS XR requirements
5. Re-tested with Jose's updated code

---

### Test 1.4: MTU Configuration (v1.2)
**Tester**: Zac Halaman
**Branch**: `feature/mtu-config`
**Date**: Phase 1, Week 2

**Test Cases**:
1. **Standard Ethernet MTU (1500 bytes)**
   - ⚠ Initial attempt: FAILED (similar YANG error)
   - ✓ After fix: Successfully sets MTU to 1500
   - ✓ Configuration committed to running config

2. **Different MTU Values**
   - ✓ 1492 bytes (PPPoE standard): PASSED
   - ✓ 1500 bytes (Ethernet standard): PASSED
   - ✓ 9000 bytes (Jumbo frames): PASSED
   - ✓ 1400 bytes (Custom value): PASSED

3. **MTU Validation**
   - ✓ Values within range (64-9216) accepted
   - ✓ Warning shown for values outside typical range
   - ✓ No fragmentation issues observed

**Initial Results**: ⚠ FAILED (YANG model compatibility issue)
**After Debugging**: ✓ PASSED
**Notes**: Same IOS XR YANG model issue as shutdown function. Fixed with same approach.

---

## Phase 2: Integration Testing

### Test 2.1: All Configuration Changes Together (v1.3)
**Testers**: Henrick Yurie Mendoza & Zac Halaman
**Branch**: `main` (after all features merged)
**Date**: Phase 2, Week 3

**Test Cases**:
1. **Sequential Execution**
   - ✓ Description change executes first
   - ✓ Shutdown control executes second
   - ✓ MTU change executes third
   - ✓ No conflicts between changes

2. **NETCONF Session Management**
   - ✓ Single connection used for all changes
   - ✓ Session remains active throughout
   - ✓ Proper session closure at end
   - ✓ No memory leaks detected

3. **Error Handling**
   - ✓ If one change fails, script continues
   - ✓ Partial failures don't stop execution
   - ✓ Error messages are clear and actionable
   - ✓ Success count tracks completed changes

**Results**: ✓ PASSED
**Notes**: Integration successful. All three changes work together seamlessly.

---

### Test 2.2: WebEx Teams Integration (v1.3)
**Tester**: Henrick Yurie Mendoza
**Branch**: `feature/webex-integration`
**Date**: Phase 2, Week 3-4

**Test Cases**:
1. **Webhook Setup**
   - ✓ Created incoming webhook in WebEx Teams workspace
   - ✓ Webhook URL configured in script
   - ✓ Team space receives test messages
   - ✓ Proper permissions set for all team members

2. **Notification Content**
   - ✓ Device hostname included
   - ✓ Interface name displayed
   - ✓ Platform type shown (IOS XR)
   - ✓ Timestamp accurate
   - ✓ All three changes listed
   - ✓ Status indicator clear (✓ checkmarks)
   - ✓ Formatted for readability

3. **Notification Delivery**
   - ⚠ Initial result: Script reported FAILURE
   - ⚠ Actual result: Notification DELIVERED to WebEx
   - ⚠ Issue: HTTP 204 treated as error

4. **Different Scenarios**
   - ✓ All changes successful: Positive notification sent
   - ✓ Partial failures: Notification includes which changes failed
   - ✓ Connection errors: Notification mentions device unavailable

**Initial Results**: ⚠ PARTIAL (Delivery worked, validation failed)
**Issue Reported**: Via Mae researched and found 204 is success code
**After Fix (v2.1)**: ✓ PASSED

---

### Test 2.3: Running Configuration Verification (v1.3)
**Tester**: Zac Halaman
**Branch**: `main`
**Date**: Phase 2, Week 4

**Test Cases**:
1. **Before/After Comparison**
   - ✓ BEFORE config captured successfully
   - ✓ Changes applied to candidate datastore
   - ✓ Changes committed to running config
   - ✓ AFTER config captured successfully
   - ✓ Differences visible between BEFORE and AFTER

2. **Configuration Persistence**
   - ✓ Changes remain after script completion
   - ✓ Configuration survives NETCONF disconnect
   - ✓ Device shows updated values on manual check

**Results**: ✓ PASSED
**Notes**: Configuration changes are persistent and verifiable.

---

## Phase 3: End-to-End Validation

### Test 3.1: Complete Workflow Testing (v2.0)
**Tester**: Via Mae De Belen
**Branch**: `main` (after error handling improvements)
**Date**: Phase 3, Week 1

**Complete Workflow**:
1. **Startup & Connection**
   - ✓ Script starts with clear banner
   - ✓ Connection established to DevNet sandbox
   - ✓ Initial status messages informative

2. **Configuration Retrieval**
   - ✓ BEFORE running-config displayed
   - ✓ Interface-specific config shown
   - ✓ Output formatted and readable

3. **Configuration Changes**
   - ✓ Description updated to "L1-SE-Managed-Automated-Tool"
   - ✓ Interface enabled (no shutdown)
   - ✓ MTU set to 1500 bytes
   - ✓ Progress messages shown for each change
   - ✓ Success confirmations displayed

4. **Verification**
   - ✓ AFTER running-config displayed
   - ✓ Changes visible in new config
   - ✓ Comparison shows differences

5. **Notification**
   - ✓ WebEx Teams notification sent
   - ✓ Message received in team channel
   - ✓ Content accurate and complete

6. **Cleanup**
   - ✓ NETCONF session closed properly
   - ✓ Summary statistics displayed
   - ✓ Script exits cleanly

**Results**: ✓ PASSED
**Notes**: Full workflow executes flawlessly from start to finish.

---

### Test 3.2: Error Recovery Testing (v2.0)
**Tester**: Rupery Cyril Garcia
**Branch**: `bugfix/yang-errors`
**Date**: Phase 3, Week 1

**Test Scenarios**:
1. **Network Interruption**
   - ✓ Graceful handling of connection timeout
   - ✓ Clear error message displayed
   - ✓ Script doesn't crash

2. **Invalid Credentials**
   - ✓ Authentication failure detected
   - ✓ Helpful troubleshooting steps shown
   - ✓ No password exposed in error message

3. **Partial YANG Failures**
   - ✓ Script continues if description change fails
   - ✓ Script continues if shutdown change fails
   - ✓ Script continues if MTU change fails
   - ✓ Summary shows which changes succeeded/failed

4. **WebEx Webhook Issues**
   - ✓ Handles webhook URL not configured
   - ✓ Shows simulated notification if webhook fails
   - ✓ Device changes still successful even if notification fails

**Results**: ✓ PASSED
**Notes**: Robust error handling ensures script completes even with issues.

---

### Test 3.3: WebEx 204 Status Code Validation (v2.1)
**Tester**: Via Mae De Belen
**Branch**: `bugfix/webex-response`
**Date**: Phase 3, Week 2

**Test Cases**:
1. **HTTP Status Code Validation**
   - ✓ 200 OK: Accepted as success
   - ✓ 204 No Content: Accepted as success (FIXED)
   - ✓ 4xx errors: Properly reported as failures
   - ✓ 5xx errors: Properly reported as failures

2. **Success Message Display**
   - ✓ Shows HTTP status code in success message
   - ✓ Confirms message delivered to WebEx Teams
   - ✓ No longer reports false failures

3. **Documentation**
   - ✓ Code comments explain 204 is valid
   - ✓ HTTP standard referenced in comments

**Initial Issue**: Script reported notification failure when it actually succeeded
**Root Cause**: WebEx API returns 204 (No Content) as success response
**Research**: Via Mae researched HTTP status codes, found 204 means "success, no response body"
**Fix Applied**: Accept both 200 and 204 as success codes
**Results**: ✓ PASSED

---

### Test 3.4: Evidence Collection (v2.2)
**Tester**: Via Mae De Belen
**Branch**: `main` (final production version)
**Date**: Phase 3, Week 3

**Evidence Captured**:
1. **Application Code**
   - ✓ Complete Python script (network_automation.py)
   - ✓ All comments and documentation included
   - ✓ Version history in header

2. **YANG Model Documentation**
   - ✓ Cisco-IOS-XR-ifmgr-cfg identified
   - ✓ XML structure documented
   - ✓ Namespace information captured

3. **Output Screenshots**
   - ✓ Connection successful message
   - ✓ BEFORE running configuration
   - ✓ All three configuration changes
   - ✓ AFTER running configuration
   - ✓ WebEx Teams notification in workspace
   - ✓ Summary completion message

4. **WebEx Teams Notification**
   - ✓ Screenshot of notification in team channel
   - ✓ Full message content visible
   - ✓ Timestamp shown
   - ✓ Device details included

**Results**: ✓ COMPLETE
**Notes**: All required evidence collected for project submission.

---

## Test Environment

### DevNet Sandbox Details
- **Device**: sandbox-iosxr-1.cisco.com
- **Platform**: Cisco IOS XR
- **NETCONF Port**: 830
- **Credentials**: admin / C1sco12345
- **Interface Tested**: GigabitEthernet0/0/0/0
- **Connection Method**: NETCONF over SSH

### Development Environment
- **Python Version**: 3.8+
- **Key Libraries**:
  - ncclient (NETCONF client)
  - xmltodict (XML parsing)
  - requests (HTTP for WebEx)
- **IDE**: Visual Studio Code
- **Version Control**: Git/GitHub

---

## Testing Metrics

### Test Execution Summary
| Phase | Total Tests | Passed | Failed | Pass Rate |
|-------|-------------|--------|--------|-----------|
| Phase 1: Unit Testing | 12 | 8 | 4 | 67% |
| Phase 1: After Fixes | 12 | 12 | 0 | 100% |
| Phase 2: Integration | 8 | 7 | 1 | 88% |
| Phase 2: After Fixes | 8 | 8 | 0 | 100% |
| Phase 3: E2E | 15 | 15 | 0 | 100% |
| **TOTAL** | **35** | **35** | **0** | **100%** |

### Bugs Found & Resolved
1. **Bug #1**: YANG model 'bad-element' error for shutdown
   - **Severity**: High
   - **Found by**: Zac (Phase 1)
   - **Fixed by**: Jose
   - **Branch**: bugfix/yang-errors

2. **Bug #2**: YANG model 'unknown-element' error for MTU
   - **Severity**: High
   - **Found by**: Zac (Phase 1)
   - **Fixed by**: Jose
   - **Branch**: bugfix/yang-errors

3. **Bug #3**: WebEx Teams 204 status code treated as failure
   - **Severity**: Medium
   - **Found by**: Henrick (Phase 2)
   - **Researched by**: Via Mae
   - **Fixed by**: Via Mae
   - **Branch**: bugfix/webex-response

### Code Quality Metrics
- **Test Coverage**: 100% (all functions tested)
- **Error Handling**: Comprehensive try-except blocks
- **Code Comments**: Well-documented with testing notes
- **Code Review**: All features reviewed before merge

---

## Key Testing Learnings

### What Worked Well
✓ **Incremental Testing**: Testing each feature individually before integration caught issues early
✓ **Multiple Testers**: Different perspectives found different issues
✓ **Clear Documentation**: NETCONF error messages provided valuable debugging info
✓ **Agile Approach**: Short testing cycles allowed quick feedback and fixes

### Challenges Encountered
⚠ **Platform Differences**: IOS XR vs IOS XE YANG models caused confusion
⚠ **HTTP Standards**: 204 status code wasn't immediately recognized as success
⚠ **Documentation Gaps**: Some IOS XR YANG models poorly documented
⚠ **Coordination**: Timing tests with sandbox availability was challenging

### How Challenges Were Resolved
✓ **Research**: Jose researched Cisco GitHub and IOS XR documentation
✓ **Team Knowledge**: Via Mae researched HTTP standards
✓ **Iterative Debugging**: Tested small changes incrementally
✓ **Error Logging**: Added detailed error messages to understand failures

### Best Practices Identified
1. **Test the simplest thing first** (description change proved NETCONF works)
2. **Read error messages carefully** (YANG errors contain valuable clues)
3. **Research official documentation** (Cisco GitHub has YANG examples)
4. **Continue on partial failures** (one failure shouldn't stop everything)
5. **Validate success criteria** (204 is success, not failure)

---

## Testing Sign-Off

| Tester | Role | Sign-Off | Date |
|--------|------|----------|------|
| Zac Halaman | QA Tester | ✓ Approved | Phase 3, Week 3 |
| Henrick Yurie Mendoza | Integration Tester | ✓ Approved | Phase 3, Week 3 |
| Via Mae De Belen | E2E Tester | ✓ Approved | Phase 3, Week 3 |
| Rupery Cyril Garcia | Testing Assistant | ✓ Approved | Phase 3, Week 3 |
| Jose Iturralde | Co-Developer | ✓ Approved | Phase 3, Week 3 |
| Richelle Grace Adarlo | Scrum Leader | ✓ Approved | Phase 3, Week 3 |

**Final Status**: ✓ ALL TESTS PASSED - READY FOR PRODUCTION

---

*Testing Documentation Prepared by: Zac Halaman, Henrick Yurie Mendoza, Via Mae De Belen*
*Compiled by: Via Mae De Belen*
*Last Updated: December 2025*
*Team: DevNet & Chill*
