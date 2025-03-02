# PyQt4 to PyQt5 Migration Guide

## Key Changes Required

1. **Import Statements**:
   - Replace `from PyQt4.QtCore` with `from PyQt5.QtCore`
   - Replace `from PyQt4.QtGui` with either `from PyQt5.QtWidgets` or `from PyQt5.QtGui` depending on the classes
   - Replace `from PyQt4.QtWebKit` with `from PyQt5.QtWebKitWidgets`

2. **Signal/Slot Mechanism**:
   - Replace old-style signals/slots (`SIGNAL`, `connect`) with new-style connections
   - Example: `self.connect(source, SIGNAL('signal()'), target)` becomes `source.signal.connect(target)`

3. **QString Handling**:
   - PyQt5 doesn't have QString class - all strings are Python strings
   - Remove all `QString` conversions

4. **QVariant Handling**:
   - PyQt5 automatically converts to/from Python types - QVariant is rarely needed

5. **Exception Handling**:
   - Update syntax from `except Exception, err` to `except Exception as err`
