# compile_translations.py
import os
import struct

def msgfmt(po_path, mo_path):
    with open(po_path, 'rb') as f:
        lines = f.read().decode('utf-8').splitlines()

    msgs = {}
    msgid = None
    msgstr = None
    collecting = None
    for line in lines:
        line = line.strip()
        if line.startswith('msgid '):
            msgid = eval(line[6:])
            collecting = 'id'
        elif line.startswith('msgstr '):
            msgstr = eval(line[7:])
            collecting = 'str'
            if msgid is not None:
                msgs[msgid] = msgstr
                msgid = None
                msgstr = None

    keys = sorted(msgs.keys())
    ids = strs = b''
    offsets = []
    for k in keys:
        idb = k.encode('utf-8') + b'\x00'
        strb = msgs[k].encode('utf-8') + b'\x00'
        offsets.append((len(ids), len(idb), len(strs), len(strb)))
        ids += idb
        strs += strb

    keystart = 7 * 4 + 16 * len(keys)
    idofs = []
    strofs = []
    cur = 0
    for o in offsets:
        idofs.append((o[1], o[0]))
        strofs.append((o[3], len(ids) + o[2]))

    kcount = len(keys)
    header = struct.pack("Iiiiiii",
                         0x950412de, 0, kcount, 7*4, keystart, 0, 0)
    table = b''
    for i in range(kcount):
        table += struct.pack("ii", idofs[i][0], idofs[i][1])
    for i in range(kcount):
        table += struct.pack("ii", strofs[i][0], strofs[i][1])

    data = header + table + ids + strs
    with open(mo_path, 'wb') as f:
        f.write(data)

if __name__ == "__main__":
    base = os.path.join(os.path.dirname(__file__), "locales")
    for lang in os.listdir(base):
        po = os.path.join(base, lang, "LC_MESSAGES", "messages.po")
        mo = os.path.join(base, lang, "LC_MESSAGES", "messages.mo")
        if os.path.exists(po):
            print("Compiling", po, "->", mo)
            msgfmt(po, mo)
