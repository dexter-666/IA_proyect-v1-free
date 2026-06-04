import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel
import ui

app = QApplication(sys.argv)
try:
    win = ui.MainWindow("dummy_face.gif")
    
    bento_cards = {
        'Spotify': win._spotify_w,
        'System': win._system_w,
        'Todo': win._todo_w,
        'Notes': win._notes_w,
        'FilesPanel': win._files_panel
    }
    
    for name, card in bento_cards.items():
        print(f"\n===== CARD: {name} =====")
        print(f"Class: {card.__class__.__name__}")
        
        for child in card.findChildren(QWidget):
            cls = child.__class__.__name__
            obj_name = child.objectName()
            text = ""
            if hasattr(child, 'text') and callable(getattr(child, 'text')):
                try:
                    text = child.text()
                except:
                    pass
            
            if isinstance(child, (QPushButton, QLabel)) or text:
                print(f"  {cls} | name={obj_name} | text='{text}'")

    # Also inspect top bar
    print("\n===== TOP BAR / HEADER =====")
    for child in win.children():
        if isinstance(child, QWidget):
            cls = child.__class__.__name__
            obj = child.objectName()
            style = child.styleSheet()[:120] if child.styleSheet() else ""
            print(f"Direct child: {cls} | name={obj} | style_preview={style}")
            
            # Check immediate children of central widget
            if obj == 'myCentralWidget':
                for sub in child.children():
                    if isinstance(sub, QWidget):
                        scls = sub.__class__.__name__
                        sobj = sub.objectName()
                        sstyle = sub.styleSheet()[:120] if sub.styleSheet() else ""
                        print(f"  Central sub: {scls} | name={sobj} | style={sstyle}")
                        
                        # Go one more level
                        for ssub in sub.children():
                            if isinstance(ssub, QWidget):
                                sscls = ssub.__class__.__name__
                                ssobj = ssub.objectName()
                                ssstyle = ssub.styleSheet()[:120] if ssub.styleSheet() else ""
                                txt = ""
                                if hasattr(ssub, 'text') and callable(getattr(ssub, 'text')):
                                    try: txt = ssub.text()
                                    except: pass
                                print(f"    Sub-sub: {sscls} | name={ssobj} | text='{txt}' | style={ssstyle}")
                                
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    app.quit()
