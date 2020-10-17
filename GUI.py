import network
import socket
from tkinter import *
from tkinter import scrolledtext
import threading
import parser

itemnamelist = [] 

cm = network.connectionManager()

def add_button():
	print(listenerbindentry.get())
	if selected.get() == 0 and listenerbindentry.get() == "":
		incominglistener = threading.Thread(target = cm.inbound, args = ())
		incominglistener.start()
	elif selected.get() == 0 and listenerbindentry.get():
		cm.setbindip(listenerbindentry.get())
		incominglistener = threading.Thread(target = cm.inbound, args = ())
		incominglistener.start()
	elif selected.get() == 1:
		cm.outbound(socket.gethostname(), 1234)

	instantiate_button.configure(state="disabled")


def add_item():
	pass

def refresh():
	global itemnamelist

	while True:
		
		network.connectionManager.waitevent()

		label1['text'] = parser.iplist
		itemnamelist = getitemnamelist()
		destroyall()
		createitemlist()
		updateoptionlist()
		
def getitemnamelist():
	lst = []
	for item in parser.itemlist.values():
		lst.append(item['name'])
	return lst

threading.Thread(target = refresh, args = ()).start()

root = Tk()
root.title("Peer-to-Peer Shop")
root.geometry('720x450')

frame1 = LabelFrame(root, text="Configuration", padx=50, pady=5)
frame1.pack()
frame2 = LabelFrame(root, text="Inventory", padx=5, pady=5)

selected = IntVar()

listenerbindlabel = Label(frame1, text="Listener Bind Address [Ethernet Port]: ")
listenerbindlabel.grid(row=0, column=1, padx=5)
listenerbindentry = Entry(frame1, width=10)
listenerbindentry.grid(row=0, column=2, padx=5)
outgoinglabel = Label(frame1, text="Outgoing Address [Ethernet Port of Peer]: ")
outgoinglabel.grid(row=1, column=1, padx=5)
outgoingentry = Entry(frame1, width=10)
outgoingentry.grid(row=1, column=2, padx=5)
rad1 = Radiobutton(frame1, value=0, variable=selected)
rad2 = Radiobutton(frame1, value=1, variable=selected)
rad1.grid(row=0, column=0)
rad2.grid(row=1, column=0)

instantiate_button = Button(frame1,text='Instantiate Application',command=add_button)
instantiate_button.grid(row=0, column=3, padx=10, rowspan=2)

def destroyall():
	for child in frame2.winfo_children():
		child.destroy()

def createitemlist():

	itemid = Label(frame2, text="ID", width=5, bg="skyblue").grid(row=0,column=0)
	itemname = Label(frame2, text="Name", width=55, bg="skyblue").grid(row=0,column=1)
	itemqty = Label(frame2, text="Quantity", width=10, bg="skyblue").grid(row=0,column=2)
	itemprice = Label(frame2, text="Price", width=15, bg="skyblue").grid(row=0, column=3)

	row = 1
	column = 0
	for item in parser.itemlist.values():

		column = 0

		itemlabel = Label(frame2, text=item['itemid'], bg="white", width=5)
		itemlabel.grid(row=row, column=column)
		column += 1

		itemlabel = Label(frame2, text=item['name'], bg="white", width=55)
		itemlabel.grid(row=row, column=column)
		column += 1

		itemlabel = Label(frame2, text=item['qty'], bg="white", width=10)
		itemlabel.grid(row=row, column=column)
		column += 1

		itemlabel = Label(frame2, text=item['price'], bg="white", width=15)
		itemlabel.grid(row=row, column=column)

		row += 1

frame2.pack(fill="both",padx=5,pady=5)

frame3 = LabelFrame(root, text="Purchase", padx=5, pady=5)
frame3.pack(fill="x",padx=5,pady=5)

selecteditem = StringVar(frame3)
selecteditem.set("None")

itemnamelist = getitemnamelist()

selectitem = OptionMenu(frame3, selecteditem, "None")
selectitem.configure(width=45)
selectitem.grid(row=0, column=0, columnspan=2)

def updateoptionlist():
	selectitem.children["menu"].delete(0,"end")
	for v in itemnamelist:
		selectitem.children["menu"].add_command(label=v, command=lambda veh=v:selecteditem.set(veh))
	selecteditem.set("None")

updateoptionlist()

qtygenlabel = Label(frame3, text="Enter Quantity: ", padx=5,pady=5)
qtygenlabel.grid(row=1, column=0)

qtyentry = Entry(frame3, width = 10)
qtyentry.grid(row=1, column=1)

def buy():
	global buybutton

	qty = int(qtyentry.get())
	if qty > 0:
		check = parser.createtnx(selecteditem.get(), qty)

		if check != False:

			buybutton.configure(state="disabled")
			network.broadcastData(check)
			buybutton.configure(state="normal")
			
		else:
			print("GUI Error: Failed to create transaction")
	else:
		print("GUI Error: QTY entered is incorrect")

buybutton = Button(frame3, bg="green", text="Buy", font="Arial", command=buy)
buybutton.grid(row=2, column=0, columnspan=2)

def create_additem_window():
	window = Toplevel(root)
	window.title("Add Item")

	itemnamelabel = Label(window, text="Enter Item Name: ", padx=5,pady=5)
	itemnamelabel.grid(row=0, column=0)

	itemnameentry = Entry(window, width = 10)
	itemnameentry.grid(row=0, column=1, padx=5, pady=5)

	itemqtylabel = Label(window, text="Enter Quantity: ", padx=5,pady=5)
	itemqtylabel.grid(row=1, column=0)

	itemqtyentry = Entry(window, width = 10)
	itemqtyentry.grid(row=1, column=1,  padx=5, pady=5)

	itempricelabel = Label(window, text="Enter Price: ", padx=5,pady=5)
	itempricelabel.grid(row=2, column=0)

	itempriceentry = Entry(window, width = 10)
	itempriceentry.grid(row=2, column=1, padx=5, pady=5)

	def additemnow():
		ret = parser.createitem(itemnameentry.get(), int(itemqtyentry.get()), int(itempriceentry.get()))
		if ret != False:
			network.broadcastData(ret)
		else:
			print("GUI Error: Error creating an item")
		window.destroy()

	add = Button(window, text="Add Item!", bg = "skyblue", command=additemnow).grid(row=3,column=0,columnspan=2)

b = Button(root, text="Add Item", command=create_additem_window)
b.pack()

label1 = Label(root, text = parser.iplist)
label1.pack()

root.mainloop()