# -*- coding: utf-8 -*-
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from PyQt5.QtCore import QObject, pyqtSlot, QUrl
import logging
import os

logger = logging.getLogger(__name__)

class WebEngineBridge(QObject):
    """Bridge between Python and JavaScript"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data = {}
        
    @pyqtSlot(str, str)
    def setData(self, key, value):
        logger.debug(f"JS bridge: setData({key}, {value})")
        self._data[key] = value
        
    @pyqtSlot(str, result=str)
    def getData(self, key):
        logger.debug(f"JS bridge: getData({key})")
        return self._data.get(key, '')
        
    def addToPage(self, page, name='bridge'):
        try:
            from PyQt5.QtWebChannel import QWebChannel
            channel = QWebChannel(page)
            channel.registerObject(name, self)
            page.setWebChannel(channel)
            
            # Inject the web channel
            page.loadFinished.connect(lambda ok: self._inject_webchannel(page) if ok else None)
            return True
        except ImportError:
            logger.warning("QWebChannel not available, using alternate method")
            return False
        
    def _inject_webchannel(self, page):
        script = '''
        new QWebChannel(qt.webChannelTransport, function(channel) {
            window.bridge = channel.objects.bridge;
            document.title = "Bridge connected";
        });
        '''
        page.runJavaScript(script)

class WebEnginePageCompat(QWebEnginePage):
    """Compatibility layer for QWebEnginePage"""
    
    def __init__(self, parent=None):
        super(WebEnginePageCompat, self).__init__(parent)
        self._bridge = WebEngineBridge(self)
        self._bridge.addToPage(self)
        self._javascript_objects = {}
        self._base_url = QUrl.fromLocalFile(os.path.join(os.getcwd(), 'include'))
        
    def mainFrame(self):
        """Emulate old-style API"""
        return self
        
    def addToJavaScriptWindowObject(self, name, obj):
        """Legacy method for compatibility"""
        self._javascript_objects[name] = obj
        
        # Create a property on the bridge for this object
        for attr_name in dir(obj):
            if not attr_name.startswith('_'):
                attr = getattr(obj, attr_name)
                if callable(attr) and hasattr(obj, 'polyFill'):
                    # Register through the bridge
                    setattr(self._bridge, attr_name, lambda *args, method=attr: method(*args))
        
    def setUrl(self, url):
        """Set URL with proper type conversion"""
        if isinstance(url, str):
            if url.startswith('http'):
                url = QUrl(url)
            else:
                # Assume it's a local file path
                url = QUrl.fromLocalFile(url)
                
        super().setUrl(url)
        
    def evaluateJavaScript(self, code):
        """Legacy method for compatibility"""
        return self.runJavaScript(code)
        
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        """Handle JavaScript console messages"""
        log_levels = {
            0: logging.DEBUG,  # Info
            1: logging.WARNING,  # Warning
            2: logging.ERROR,  # Error
        }
        log_level = log_levels.get(level, logging.INFO)
        logger.log(log_level, f"JS: {message} ({sourceID}:{lineNumber})")
