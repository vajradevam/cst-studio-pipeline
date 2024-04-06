from __future__ import division 
import customtkinter
from customtkinter import filedialog

import numpy as np
import csv

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

def extract(
        s11_offset_multiplier, 
        gain_offset_multiplier, 
        s11_filename, 
        gain_filename, 
        save_file,
        bool_get_s11,
        bool_get_gain,
        bool_get_freq,
        bool_get_bandwidth):
    
    def interpolated_intercepts(x, y1, y2):
        """Find the intercepts of two curves, given by the same x data"""

        def intercept(point1, point2, point3, point4):
            """find the intersection between two lines
            the first line is defined by the line between point1 and point2
            the first line is defined by the line between point3 and point4
            each point is an (x,y) tuple.

            So, for example, you can find the intersection between
            intercept((0,0), (1,1), (0,1), (1,0)) = (0.5, 0.5)

            Returns: the intercept, in (x,y) format
            """    

            def line(p1, p2):
                A = (p1[1] - p2[1])
                B = (p2[0] - p1[0])
                C = (p1[0]*p2[1] - p2[0]*p1[1])
                return A, B, -C

            def intersection(L1, L2):
                D  = L1[0] * L2[1] - L1[1] * L2[0]
                Dx = L1[2] * L2[1] - L1[1] * L2[2]
                Dy = L1[0] * L2[2] - L1[2] * L2[0]

                x = Dx / D
                y = Dy / D
                return x,y

            L1 = line([point1[0],point1[1]], [point2[0],point2[1]])
            L2 = line([point3[0],point3[1]], [point4[0],point4[1]])

            R = intersection(L1, L2)

            return R

        idxs = np.argwhere(np.diff(np.sign(y1 - y2)) != 0)

        xcs = []
        ycs = []

        for idx in idxs:
            xc, yc = intercept((x[idx], y1[idx]),((x[idx+1], y1[idx+1])), ((x[idx], y2[idx])), ((x[idx+1], y2[idx+1])))
            xcs.append(xc)
            ycs.append(yc)
        return np.array(xcs), np.array(ycs)

    """Open S11 File"""
    with open(s11_filename, "r") as f:
        s11_file = [x for x in f.readlines()]

    """Open Gain File """
    with open(gain_filename, "r") as f:
        gain_file = [x for x in f.readlines()]

    """Extract Headers / Column Names"""
    temp = s11_file[0]
    headers = [x.split("=")[0] for x in temp[15:-2].split("; ")]

    if bool_get_freq: headers.append("freq")
    if bool_get_s11: headers.append("s11")
    if bool_get_gain: headers.append("gain")
    if bool_get_bandwidth: headers.append("bandwidth")

    """Write the Headers to the processed data file"""
    with open(save_file, "a", newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(headers)

    """Get one row of data"""
    def get_one(chunk_s11, chunk_gain):

        """Frequency vs Gain"""
        freqs1 = [float(x[:-1].split('\t')[0]) for x in chunk_gain[3:]]
        gains = [float(x[:-1].split('\t')[1]) for x in chunk_gain[3:]]

        """frequency vs S11"""
        freqs2 = [float(x[:-1].split('\t')[0]) for x in chunk_s11[3:]]
        s11s = [float(x[:-1].split('\t')[1]) for x in chunk_s11[3:]]

        """Get Minimum S11, and respective gain and frequency"""
        min_s11 = min(s11s)
        freq = freqs2[s11s.index(min_s11)]
        gain = np.interp(freq, freqs1, gains)

        """Get the additional data of the row"""
        row = [float(x.split("=")[1]) for x in chunk_s11[0][15:-2].split("; ")]

        """Selective Push of vars can be defined"""
        if bool_get_freq: row.append(freq)
        if bool_get_s11: row.append(min_s11)
        if bool_get_gain: row.append(gain)
        
        """A array of constant -10 with length of same as the
        Number of points in S11 vs Frequencies is used in order
        to calculate the intersection point of the original curve
        with the line y = -10 (90% power transfer). Can also
        change this value to be dynamic."""
        const = []
        for i in range(len(freqs2)):
            const.append(-10)

        """Returns the frequencies which have the exact s11 value of -10;
        and their values"""
        s11_crossers, vals = interpolated_intercepts(np.array(freqs2), np.array(const), np.array(s11s))
        d = [x[0] for x in s11_crossers]
        
        """To find a middle point; there must be even number of points"""
        if len(d) % 2 != 0:
            d = d[:-1]
        
        """Pick two exclusivly and chekc if our frequencies lies between"""
        if bool_get_bandwidth: 
            for i in range(0, len(d), 2):
                if d[i] < freq < d[i + 1]:
                    """importane"""
                    bandwidth = d[i + 1] - d[i]
                    break
            try:
                row.append(bandwidth)
            except UnboundLocalError:
                print(freq, d)

        """Dump the row values in the csv file"""
        with open(save_file, "a", newline='') as f:
            writer = csv.writer(f, delimiter=',')
            writer.writerow(row)

    iters = (len(s11_file) // s11_offset_multiplier)

    for i in range(iters - 1):
        current_s11_data = s11_file[-1 * s11_offset_multiplier:]
        current_gain_data = gain_file[-1 * (gain_offset_multiplier):]

        get_one(current_s11_data, current_gain_data)

        s11_file = s11_file[:-1 * s11_offset_multiplier]
        gain_file = gain_file[:-1 * gain_offset_multiplier]

    return 1

class ChekcBoxFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        # Parameters Checkbox
        self.label_params = customtkinter.CTkLabel(self, text="Parameters")
        self.label_params.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        # Checkboxes
        self.checkbox_s11 = customtkinter.CTkCheckBox(self, text="S11")
        self.checkbox_s11.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="w")

        self.checkbox_gain = customtkinter.CTkCheckBox(self, text="GAIN")
        self.checkbox_gain.grid(row=1, column=1, padx=10, pady=(10, 0), sticky="w")

        self.checkbox_freq = customtkinter.CTkCheckBox(self, text="FREQ")
        self.checkbox_freq.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")

        self.checkbox_bandwidth = customtkinter.CTkCheckBox(self, text="BANDWIDTH")
        self.checkbox_bandwidth.grid(row=2, column=1, padx=10, pady=(10, 0), sticky="w")

        # Offset Labels
        self.label_s11_offset = customtkinter.CTkLabel(self, text="S11 Offset: ")
        self.label_s11_offset.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")

        self.label_gain_offset = customtkinter.CTkLabel(self, text="Gain Offset: ")
        self.label_gain_offset.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="w")

        # Offset Text Boxes
        self.textbox_s11_offset = customtkinter.CTkTextbox(self, height=1, width=80)
        self.textbox_s11_offset.grid(row=3, column=1, padx=10, pady=(10, 0), sticky="w")

        self.textbox_gain_offset = customtkinter.CTkTextbox(self, height=1, width=80)
        self.textbox_gain_offset.grid(row=4, column=1, padx=10, pady=(10, 0), sticky="w")

    def return_checkboxes(self):
        return (self.checkbox_s11, self.checkbox_gain, self.checkbox_freq, self.checkbox_bandwidth)
    
    def return_offset_boxes(self):
        return (self.textbox_s11_offset, self.textbox_gain_offset)

class ButtonFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        self.s11_button = customtkinter.CTkButton(self, text="S11 File", command=self.select_s11_file)
        self.s11_button.grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")

        self.gain_button = customtkinter.CTkButton(self, text="Gain File", command=self.select_gain_file)
        self.gain_button.grid(row=1, column=0, padx=10, pady=(10, 0), sticky="w")

        self.savefile_button = customtkinter.CTkButton(self, text="Result File", command=self.select_result_file)
        self.savefile_button.grid(row=2, column=0, padx=10, pady=(10, 0), sticky="w")
        
        self.s11_file_name = ""
        self.gain_file_name = ""
        self.result_file_name = ""

        # File Text Boxes
        self.text_box_s11 = customtkinter.CTkTextbox(self, height=1, width=200)
        self.text_box_s11.grid(row=3, column=1, padx=10, pady=(10, 0), sticky="w")

        self.text_box_gain = customtkinter.CTkTextbox(self, height=1, width=200)
        self.text_box_gain.grid(row=4, column=1, padx=10, pady=(10, 0), sticky="w")

        self.text_box_result = customtkinter.CTkTextbox(self, height=1, width=200)
        self.text_box_result.grid(row=5, column=1, padx=10, pady=(10, 0), sticky="w")

        # File Labels
        self.label_s11_file = customtkinter.CTkLabel(self, text="S11 File: ")
        self.label_s11_file.grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")

        self.label_gain_file = customtkinter.CTkLabel(self, text="Gain File: ")
        self.label_gain_file.grid(row=4, column=0, padx=10, pady=(10, 0), sticky="w")

        self.label_save_file = customtkinter.CTkLabel(self, text="Save File: ")
        self.label_save_file.grid(row=5, column=0, padx=10, pady=(10, 0), sticky="w")

    def select_s11_file(self):
        self.s11_file_name = filedialog.askopenfilename()
        self.text_box_s11.insert("0.0", text = self.s11_file_name)
        print(self.s11_file_name)

    def select_gain_file(self):
        self.gain_file_name = filedialog.askopenfilename()
        self.text_box_gain.insert("0.0", text = self.gain_file_name)
        print(self.gain_file_name)

    def select_result_file(self):
        self.result_file_name = filedialog.askopenfilename()
        self.text_box_result.insert("0.0", text = self.result_file_name)
        print(self.result_file_name)

    def return_file_names(self):
        return (self.s11_file_name, self.gain_file_name, self.result_file_name)
    
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("CST Studio 2022 Data Pipeline 0.0.1")
        self.geometry("700x500")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure((0, 0), weight=1)

        self.checkbox_frame = ChekcBoxFrame(self)
        self.checkbox_frame.grid(row=0, column=0, padx=10, pady=(10, 10), sticky="news")

        self.button_frame = ButtonFrame(self)
        self.button_frame.grid(row=0, column=1, padx=10, pady=(10, 10), sticky="news")

        self.button_compute = customtkinter.CTkButton(self, text="Calculate", command=self.perform_task)
        self.button_compute.grid(row=1, column=0, padx=10, pady=(10, 10), sticky="news")

        self.label_desc = customtkinter.CTkLabel(self, text="©Vajradevam S., Neptunes Aerospace, 2024")
        self.label_desc.grid(row=1, column=1, padx=10, pady=(10, 10), sticky="we")

    def perform_task(self):

        checkboxes = self.checkbox_frame.return_checkboxes()
        bool_get_s11 = checkboxes[0].get()
        bool_get_gain = checkboxes[1].get()
        bool_get_freq = checkboxes[2].get()
        bool_get_bandwidth = checkboxes[3].get()

        filenames = self.button_frame.return_file_names()

        offset_texboxes = self.checkbox_frame.return_offset_boxes()

        s11_offset = int(offset_texboxes[0].get("1.0","end"))
        gain_offset = int(offset_texboxes[1].get("1.0","end"))

        s11_file_name = filenames[0]
        gain_file_name = filenames[1]
        result_file_name = filenames[2]

        status = extract(
            s11_offset_multiplier=s11_offset,
            gain_offset_multiplier=gain_offset,
            s11_filename=s11_file_name,
            gain_filename=gain_file_name,
            save_file=result_file_name,
            bool_get_s11=bool_get_s11,
            bool_get_gain=bool_get_gain,
            bool_get_freq=bool_get_freq,
            bool_get_bandwidth=bool_get_bandwidth)

app = App()
app.mainloop()