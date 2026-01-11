def is_navigation_event(event):
    return event.type in {
        'MIDDLEMOUSE',
        'WHEELUPMOUSE',
        'WHEELDOWNMOUSE',
        'TRACKPADPAN',
        'TRACKPADZOOM',
    }