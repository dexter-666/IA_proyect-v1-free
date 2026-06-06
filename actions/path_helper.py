# -*- coding: utf-8 -*-
"""
path_helper.py — Robust Windows special folder path resolver for JARVIS.
Handles OneDrive redirection, Spanish localizations, and standard fallbacks.
"""
import os
import ctypes
from pathlib import Path

def get_special_folder(csidl: int) -> Path:
    """Gets the path of a Windows special folder using SHGetFolderPathW."""
    try:
        from ctypes import wintypes
        buf = ctypes.create_unicode_buffer(wintypes.MAX_PATH)
        # CSIDL constants: 0 = CSIDL_DESKTOP, 5 = CSIDL_PERSONAL (Documents)
        if ctypes.windll.shell32.SHGetFolderPathW(None, csidl, None, 0, buf) == 0:
            p = Path(buf.value)
            if p.exists():
                return p
    except Exception:
        pass
    return None

def get_desktop_path() -> Path:
    """Returns the user's actual Desktop path, checking API, OneDrive, and fallbacks."""
    # 1. Try SHGetFolderPathW (CSIDL_DESKTOP = 0)
    p = get_special_folder(0)
    if p:
        return p

    # 2. Try common OneDrive and localized directories
    home = Path.home()
    candidates = [
        home / "OneDrive" / "Desktop",
        home / "OneDrive" / "Escritorio",
        home / "Desktop",
        home / "Escritorio"
    ]
    for c in candidates:
        if c.exists():
            return c
            
    # 3. Fallback to standard environment or home
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        dp = Path(user_profile) / "Desktop"
        if dp.exists():
            return dp
            
    return home

def get_documents_path() -> Path:
    """Returns the user's actual Documents path."""
    # 1. Try SHGetFolderPathW (CSIDL_PERSONAL = 5)
    p = get_special_folder(5)
    if p:
        return p

    # 2. Try common OneDrive and localized directories
    home = Path.home()
    candidates = [
        home / "OneDrive" / "Documents",
        home / "OneDrive" / "Documentos",
        home / "Documents",
        home / "Documentos"
    ]
    for c in candidates:
        if c.exists():
            return c
            
    # 3. Fallback to standard environment or home
    user_profile = os.environ.get("USERPROFILE")
    if user_profile:
        dp = Path(user_profile) / "Documents"
        if dp.exists():
            return dp
            
    return home

def get_downloads_path() -> Path:
    """Returns the user's actual Downloads path."""
    home = Path.home()
    
    # Check registry or standard locations
    candidates = [
        home / "Downloads",
        home / "Descargas",
        home / "OneDrive" / "Downloads",
        home / "OneDrive" / "Descargas"
    ]
    for c in candidates:
        if c.exists():
            return c
            
    return home
