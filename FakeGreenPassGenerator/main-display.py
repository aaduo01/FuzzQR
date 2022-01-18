#
# Display for FakeGreenPass generation
# --------------------


#from watchdog.observers import Observer
#from watchdog.events import FileSystemEventHandler

from qrgen import *
from passgen import *
from datetime import datetime

import sys
import argparse
import json
import pyqrcode
import tkinter as tk
import os

update_time = 500
fuzzer_file = "../QRCodeFuzzer/data/fuzzer.json"
qr_imgs = []
qr_files = []


# ---------------- EDIT EVENT HANDLER ----------------
#class MyHandler(FileSystemEventHandler):
class FileHandler():
    def __init__(self):
        self.fuzzer = []
        self.initialize()
        self.iterator = 0

    def next(self):
        if not self.hasNotNext():
            self.iterator += 1

    def hasNotNext(self):
        return len(qr_files) <= self.iterator
        
    def currentFilename(self):
        return qr_files[self.iterator]

    def initialize(self):
        # Initialize JSON file
        fuzzer = {}
        fuzzer["status"] = 0
        fuzzer["file"] = "Starting"
        fuzzer["size"] = len(qr_files)
        f = open(fuzzer_file, 'w', encoding='utf-8')
        json.dump(fuzzer, f, ensure_ascii=False, indent=4)
        f.close()
        self.fuzzer = fuzzer

    def checker(self):

        # currentTime = os.path.getmtime(fuzzer_file)

        # Read JSON file
        f = open(fuzzer_file, 'r', encoding='utf-8')
        string = f.read()
        try: 
            # Decode from JSON
            fuzzer = json.loads(string)

            if fuzzer["status"] == 1 & fuzzer["status"] != self.fuzzer["status"]:

                # Set "status" back to 0 and update file name
                fuzzer["status"] = 0
                fuzzer["file"] = qr_files[self.iterator]

                # Update JSON file
                f = open(fuzzer_file, 'w', encoding='utf-8')
                json.dump(fuzzer, f, ensure_ascii=False, indent=4)
                f.close()


                # Update value
                self.fuzzer = fuzzer
                print("> Ok:", qr_files[self.iterator])

                return True
        except:
            # JSON decoding throws some errors, but then works, dunno why
            pass

        return False
        


# --------------------- MAIN ---------------------
def main():   
    
    opt = cmd()
    payloads = get_words(opt)


    for i, _ in enumerate(payloads):
        qr_files.append(fuzz_type[opt.list] + "-" + str(i))

    file = FileHandler()

    def gengp():
        msg = get_cose(get_pass(payloads[file.iterator]))
        msg = add_cose_key(msg, PRIVKEY)
        msg = flynn(msg.encode(), HEADER)
        msg = b45(msg)
        msg = b"HC1:" + msg
        print("RAW Certificate: ", msg)
        print("-"*20)
        return msg

    def close():
        print("Done")
        window.destroy()


    def update():
        if not file.checker():
            if file.hasNotNext():
                print("End of QR codes, closing in 10 seconds...")
                window.after(10000, close)
            else:
                window.after(update_time, update)
        else:
            gp = gengp()
            img2 = genqr(gp)
            panel.config(image=img2)
            panel.image = img2 #IPER MEGA IMPORTANT
            file.next()
            window.after(update_time, update)

    def genqr(text="test"):
        qrcode = pyqrcode.create(text)
        return tk.BitmapImage(data = qrcode.xbm(scale=4))

    

    window = tk.Tk()
    window.title("Display FakeGreenPass")
    window.geometry("600x600")
    window.configure(background='white')

    img = genqr("test")
    panel = tk.Label(window, image = img)
    panel.pack(side = "bottom", fill = "both", expand = "yes")

    window.after(update_time, update)
    window.mainloop()

def cmd():
    parser = argparse.ArgumentParser(
        description="Display FakeGreenPass while scanning with Appium-controlled app",
        usage=f"main-display.py -l [number]\nusage: main-display.py -w [/path/to/custom/wordlist]\n\nPayload lists: \n {fuzz_type}"
    )
    sgroup = parser.add_argument_group("Options available")
    sgroup.add_argument(
        "--list",
        "-l",
        type=int,
        help="Set wordlist to use",
        choices=fuzz_type.keys(),
    )
    opt = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    return opt


if __name__ == "__main__":
    main()