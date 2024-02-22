# Text insertion
place ({user.symbol} | <user.text>) <user.cursorless_destination>:
    user.cursorless_insert(cursorless_destination, symbol or text)

snip {user.snippet} <user.cursorless_destination>:
    user.c_insert_snippet(cursorless_destination, snippet)

# Misc
break line <user.cursorless_target>:
    user.cursorless_command("setSelectionBefore", cursorless_target)
    key("enter")

