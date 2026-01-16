# BlenderAdapter.py

import sys
import os
import importlib
import logging
from pathlib import Path

# Configure default logger
log = logging.getLogger("BlenderAdapter")
if not log.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)
    log.setLevel(logging.INFO)


class BlenderConnector:
    """
    BlenderAdapter centralizes:
    - Enhanced Context Handling (safe access to scene/active_object/testing)
    - Session Management (handlers, properties, module reload)
    - Dependency / Path Injection (automatic .venv detection)
    - Logging of session events for safe live development
    """

    def __init__(self, context=None, auto_venv=True):
        # ----- Context Handling -----
        self._injected_context = context
        self._connected = False

        # ----- Session Management -----
        self._handlers = []
        self._properties = []
        self._modules_reloaded = []

        # ----- Dependency Tracking -----
        self._injected_paths = []

        # Initialize connection
        self._connect()

    # ---------------- Context Handling ----------------
    def _connect(self):
        try:
            import bpy  # only import if Blender is running
            self._connected = True
            log.info("Connected to Blender runtime.")
        except Exception:
            self._connected = False
            log.warning("Blender context unavailable (headless or test mode).")

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def context(self):
        if self._injected_context is not None:
            return self._injected_context
        if self._connected:
            import bpy
            return bpy.context
        raise RuntimeError(
            "Blender context unavailable. "
            "Provide an injected context for testing, or run inside Blender."
        )

    @property
    def scene(self):
        ctx = self.context
        if hasattr(ctx, "scene") and ctx.scene is not None:
            return ctx.scene
        raise RuntimeError("Blender context exists, but active scene is missing.")

    @property
    def active_object(self):
        ctx = self.context
        if hasattr(ctx, "active_object") and ctx.active_object is not None:
            return ctx.active_object
        raise RuntimeError("Blender context exists, but there is no active object in the scene.")

    # ---------------- Dependency / Path Injection ----------------
    def inject_path(self, path: str):
        """Add a folder to sys.path for external dependencies."""
        resolved = str(Path(path).resolve())
        if resolved not in sys.path:
            sys.path.insert(0, resolved)
            self._injected_paths.append(resolved)
            log.info(f"Injected path: {resolved}")

    def reload_module(self, module_name: str):
        """Reload a Python module safely for live development."""
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
            if module_name not in self._modules_reloaded:
                self._modules_reloaded.append(module_name)
            log.info(f"Reloaded module: {module_name}")

    # ---------------- Session Management: Handlers ----------------
    def add_handler(self, handler_list, func):
        if func not in handler_list:
            handler_list.append(func)
            self._handlers.append((handler_list, func))
            log.info(f"Added handler {func.__name__}")

    def remove_handlers(self):
        for handler_list, func in self._handlers:
            if func in handler_list:
                handler_list.remove(func)
                log.info(f"Removed handler {func.__name__}")
        self._handlers.clear()

    # ---------------- Session Management: Properties ----------------
    def register_property(self, target, name, prop):
        if not hasattr(target, name):
            setattr(target, name, prop)
            self._properties.append((target, name))
            log.info(f"Registered property {target.__name__}.{name}")

    def unregister_properties(self):
        for target, name in self._properties:
            if hasattr(target, name):
                delattr(target, name)
                log.info(f"Unregistered property {target.__name__}.{name}")
        self._properties.clear()

    # ---------------- Cleanup / Disconnect ----------------
    def disconnect(self):
        """Clean all handlers and properties, reset adapter state."""
        self.remove_handlers()
        self.unregister_properties()
        self._connected = False
        log.info("Disconnected from Blender session.")

    # ---------------- Utility: Reload Addon Safely ----------------
    def reload_development_modules(self):
        """
        Reload only your development modules while keeping .venv and dependencies stable.
        This prevents COM object corruption and dependency conflicts.
        """
        print("🔄 Starting development module reload...")
        
        # Parent development directory - everything under here except .venv
        DEVELOPMENT_ROOT = r"D:\COMPUTATIONAL\Python"
        VENV_PATH = r"D:\COMPUTATIONAL\Python\.venv"
        
        # Convert to normalized paths for comparison
        dev_root = os.path.normpath(DEVELOPMENT_ROOT).lower()
        venv_path = os.path.normpath(VENV_PATH).lower()
        
        modules_to_reload = []
        
        print(f"🎯 Scanning for modules in: {DEVELOPMENT_ROOT}")
        print(f"🛡️  Excluding: {VENV_PATH}")
        
        # Find all modules in development root, but exclude .venv
        for module_name, module in list(sys.modules.items()):
            if hasattr(module, '__file__') and module.__file__:
                module_path = os.path.normpath(os.path.dirname(module.__file__)).lower()
                
                # Check if module is in development root
                if module_path.startswith(dev_root):
                    # But exclude .venv and site-packages
                    if not (module_path.startswith(venv_path) or "site-packages" in module_path):
                        modules_to_reload.append(module_name)
                        print(f"  📦 Found: {module_name}")
        
        # Remove duplicates and sort for clean output
        modules_to_reload = sorted(list(set(modules_to_reload)))
        
        if modules_to_reload:
            print(f"✅ Found {len(modules_to_reload)} development modules to reload")
            
            # Remove development modules from cache
            removed_count = 0
            for module_name in modules_to_reload:
                if module_name in sys.modules:
                    try:
                        del sys.modules[module_name]
                        removed_count += 1
                        print(f"  🗑️  Removed: {module_name}")
                    except Exception as e:
                        print(f"  ❌ Failed to remove {module_name}: {e}")
            
            print(f"🎯 Successfully removed {removed_count} development modules from sys.modules")
            print("🛡️  Protected: .venv and site-packages (kept for stability)")
        else:
            print("📝 No development modules found to reload")
        
        print("🔄 Development module reload completed!")
        return modules_to_reload if modules_to_reload else []