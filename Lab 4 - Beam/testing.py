import tkinter as tk
import serial 
import DataCollectionGUI

if __name__ == "__main__":
    root = tk.Tk()
    app = DataCollectionGUI.SerialDataCollector(root)
    root.mainloop()