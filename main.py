import customtkinter as ctk
import ffmpeg
import os
import threading
from options import file_extensions, quality_presets


def convert(input_files, output_path):
    extension = convert_extension_select.get()
    preset = convert_preset_select.get()

    # Get file name w/o extension
    for i, file in enumerate(input_files):
        convert_count_label.configure(text=f'{i+1} of {len(input_files)}')
        filename = os.path.splitext(os.path.basename(file.name))[0]

        # Full output file path
        output_file = os.path.join(output_path, filename + f'.{extension}')

        # Convert
        convert_progress_label.configure(
            text=f'Converting: {filename} to {extension} format')
        (
            ffmpeg.input(file.name)
            .output(output_file, format=extension, preset=preset)
            .run()
        )
    convert_progress_label.configure(text=f'Done!', text_color='#07fc03')
    convert_count_label.configure(text='', text_color='cyan')


def cut(input_file, output_path):

    extension = os.path.splitext(os.path.basename(input_file.name))[1]
    filename = os.path.splitext(os.path.basename(input_file.name))[0]
    begin_time = cut_time_entry_1.get()
    duration_time = cut_time_entry_2.get()
    cut_progress_label.configure(
        text=f'Cutting {filename} from {begin_time} for {duration_time}')
    output_file = os.path.join(output_path, filename + f'.{extension}')

    (
        ffmpeg.input(input_file.name, ss=begin_time, t=duration_time)
        .output(output_file)
        .run()
    )

    cut_progress_label.configure(text='Done!', text_color='#07fc03')


# For convert
def open_files_dialog():
    global convert_file_path
    global file_ext
    convert_file_path = ctk.filedialog.askopenfiles()
    file_ext = os.path.splitext(convert_file_path[0].name)
    file_ext = file_ext[1].replace('.', '')
    print(file_ext)
    detect_extension(file_ext)
    if convert_file_path:
        convert_select_file_label.configure(
            text=f'{len(convert_file_path)} files selected.')


# For cut
def open_file_dialog():
    global cut_file_path
    cut_file_path = ctk.filedialog.askopenfile()
    file_name = os.path.basename(cut_file_path.name)

    if cut_file_path:
        probe = ffmpeg.probe(cut_file_path.name)
        video_info = next(
            (stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        cut_select_file_label.configure(
            text=f"{file_name} selected\n Duration: {video_info.get('duration')} seconds")


def select_convert_output_path():
    global convert_output_path
    convert_output_path = ctk.filedialog.askdirectory()
    if convert_output_path:
        convert_output_path_label.configure(
            text=f'Output path: {convert_output_path}')


def select_cut_output_path():
    global cut_output_path
    cut_output_path = ctk.filedialog.askdirectory()
    if cut_output_path:
        cut_output_path_label.configure(
            text=f'Output path: {cut_output_path}')


def detect_extension(file_ext):
    for key, val in file_extensions.items():
        if file_ext in val:
            ext = key
    convert_extension_select.configure(values=file_extensions[ext])
    convert_preset_select.configure(values=quality_presets)
    convert_button.pack(pady=10)

def time_entry_changed(event):
    # Get the current entry value
    entry = event.widget
    value = entry.get()

    # Remove any non-digit characters
    value = ''.join(filter(str.isdigit, value))

    # Insert colons at appropriate positions
    formatted_value = ':'.join([value[i:i+2] for i in range(0, len(value), 2)])

    # Update the entry field
    entry.delete(0, ctk.END)
    entry.insert(0, formatted_value)

    # Limit input after seconds
    if len(formatted_value) >= 8:
        entry.configure(state=ctk.DISABLED)
    else:
        entry.configure(state=ctk.NORMAL)


def on_entry_key_press(event):
    entry = event.widget
    if event.keysym == 'BackSpace' or event.keysym == 'Delete':
        entry.configure(state=ctk.NORMAL)


# GUI
root = ctk.CTk()
root.geometry('600x600')
root.title('HieNApps Media Converter')

tab = ctk.CTkTabview(root, width=575, height=575)
tab.pack()

convert_tab = tab.add('Convert')
cut_tab = tab.add('Cut')

# Convert tab
convert_select_file_button = ctk.CTkButton(
    convert_tab, text='Select files', command=open_files_dialog)
convert_select_file_button.pack(pady=10)

convert_select_file_label = ctk.CTkLabel(
    convert_tab, text='', text_color='cyan')
convert_select_file_label.pack(pady=10)

convert_select_output_path_button = ctk.CTkButton(
    convert_tab, text='Select output folder', command=select_convert_output_path)
convert_select_output_path_button.pack(pady=10)

convert_output_path_label = ctk.CTkLabel(
    convert_tab, text='', text_color='cyan')
convert_output_path_label.pack(pady=10)

convert_extension_select = ctk.CTkComboBox(
    convert_tab, values=['Select format'], width=200)
convert_extension_select.pack(pady=10)

convert_preset_select = ctk.CTkComboBox(
    convert_tab, values=['Select preset'], width=200)
convert_preset_select.pack(pady=10)

convert_progress_label = ctk.CTkLabel(convert_tab, text='', text_color='cyan')
convert_progress_label.pack(pady=10)

convert_count_label = ctk.CTkLabel(convert_tab, text='', text_color='cyan')
convert_count_label.pack(pady=10)

convert_button = ctk.CTkButton(convert_tab, text='Convert', command=lambda: threading.Thread(
    target=convert, args=(convert_file_path, convert_output_path)).start())

# Cut tab
cut_select_file_button = ctk.CTkButton(
    cut_tab, text='Select files', command=open_file_dialog)
cut_select_file_button.pack(pady=10)

cut_select_file_label = ctk.CTkLabel(cut_tab, text='', text_color='cyan')
cut_select_file_label.pack(pady=10)

cut_select_output_path_button = ctk.CTkButton(
    cut_tab, text='Select output folder', command=select_cut_output_path)
cut_select_output_path_button.pack(pady=10)

cut_output_path_label = ctk.CTkLabel(cut_tab, text='', text_color='cyan')
cut_output_path_label.pack(pady=10)

cut_time_entry_1 = ctk.CTkEntry(
    cut_tab, width=150, placeholder_text='Cut begins at (xx:xx:xx)', text_color='white')
cut_time_entry_1.pack(pady=10)

cut_time_entry_2 = ctk.CTkEntry(
    cut_tab, width=150, placeholder_text='Duration of cut (xx:xx:xx)', text_color='white')
cut_time_entry_2.pack(pady=10)

cut_button = ctk.CTkButton(cut_tab, text='Cut', command=lambda: threading.Thread(
    target=cut, args=(cut_file_path, cut_output_path)).start())
cut_button.pack(pady=10)

cut_time_entry_1.bind(
    '<KeyRelease>', command=time_entry_changed)
cut_time_entry_1.bind(
    '<Key>', command=on_entry_key_press)

cut_time_entry_2.bind(
    '<KeyRelease>', command=time_entry_changed)
cut_time_entry_2.bind(
    '<Key>', command=on_entry_key_press)

cut_progress_label = ctk.CTkLabel(cut_tab, text='', text_color='cyan')
cut_progress_label.pack(pady=10)
# center window on screen
root.update_idletasks()  # Update geometry
x = (root.winfo_screenwidth() - root.winfo_reqwidth()) // 2
y = (root.winfo_screenheight() - root.winfo_reqheight()) // 2
root.geometry("+{}+{}".format(x, y))
root.mainloop()
