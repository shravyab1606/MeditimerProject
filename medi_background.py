from PIL import Image,ImageTk
def login_screen(self):
    self.clear()
    self.root.geometry("900x500")
    self.root.configure(bg="#b3d9ff")  # soft blue background

    # ---------- RIGHT SIDE IMAGE ----------
    try:
        img = Image.open("medicine_bg.jpg")
        img = img.resize((450, 500))
        self.login_bg = ImageTk.PhotoImage(img)
        tk.Label(self.root, image=self.login_bg).place(x=450, y=0)
    except:
        tk.Label(self.root, text="Image not found!", fg="red", bg="#b3d9ff").place(x=600, y=250)

    # ---------- LEFT SIDE LOGIN BOX ----------
    box = tk.Frame(self.root, bg="white", width=420, height=430)
    box.place(x=30, y=40)

    # App title
    tk.Label(box, text="💊 MediTimer Login", bg="white",
             font=("Comic Sans MS", 24, "bold"), fg="#0066cc").place(x=60, y=20)

    # Username label + entry
    tk.Label(box, text="Username", bg="white", font=("Helvetica", 14)).place(x=40, y=110)
    u = tk.Entry(box, font=("Helvetica", 12), width=28)
    u.place(x=40, y=140)

    # Password label + entry
    tk.Label(box, text="Password", bg="white", font=("Helvetica", 14)).place(x=40, y=190)
    p = tk.Entry(box, show="*", font=("Helvetica", 12), width=28)
    p.place(x=40, y=220)

    # Button hover effect
    def glow_in(e):
        login_btn["background"] = "#3399ff"

    def glow_out(e):
        login_btn["background"] = "#0066cc"

    # LOGIN BUTTON
    login_btn = tk.Button(box, text="Login", font=("Comic Sans MS", 14, "bold"),
                          width=15, bg="#0066cc", fg="white", cursor="hand2",
                          command=lambda: self.do_login(u.get(), p.get()))
    login_btn.place(x=110, y=270)
    login_btn.bind("<Enter>", glow_in)
    login_btn.bind("<Leave>", glow_out)

    # Signup switch
    tk.Button(box, text="Signup Instead?", bg="white", fg="#0066cc",
              bd=0, cursor="hand2", font=("Helvetica", 11),
              command=self.signup_screen).place(x=135, y=330)