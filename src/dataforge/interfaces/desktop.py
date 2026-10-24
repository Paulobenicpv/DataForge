"""Interface desktop local: python -m dataforge.interfaces.desktop."""
import json
import os
import queue
import subprocess
import sys
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from dataforge import __version__
from dataforge.core.config import validate_config
from dataforge.orchestration.pipeline import run


def main():
    root = tk.Tk()
    root.title(f'DataForge {__version__} | Preparação de dados')
    root.geometry('850x840')
    root.minsize(740, 650)
    canvas = tk.Canvas(root, highlightthickness=0)
    scrollbar = ttk.Scrollbar(root, orient='vertical', command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side='right', fill='y')
    canvas.pack(side='left', fill='both', expand=True)
    panel = ttk.Frame(canvas, padding=24)
    window = canvas.create_window((0, 0), window=panel, anchor='nw')
    panel.bind('<Configure>', lambda _: canvas.configure(scrollregion=canvas.bbox('all')))
    canvas.bind('<Configure>', lambda event: canvas.itemconfigure(window, width=event.width))
    root.bind('<MouseWheel>', lambda event: canvas.yview_scroll(int(-event.delta / 120), 'units'))
    ttk.Label(panel, text='DataForge', font=('Segoe UI', 24, 'bold')).pack(anchor='w')
    ttk.Label(panel, text='Prepare sua base e confira as alterações no relatório.').pack(anchor='w', pady=(0, 16))
    paths, labels, controls = {}, {}, []
    messages = queue.Queue()
    state = {'busy': False, 'output': None}
    options = {}
    checkboxes = []
    reset_button = None

    def sync_config():
        selected = bool(paths.get('config'))
        for checkbox in checkboxes:
            checkbox.configure(state='disabled' if selected or state['busy'] else 'normal')
        if reset_button is not None:
            reset_button.configure(state='normal' if selected and not state['busy'] else 'disabled')

    def clear_config():
        paths.pop('config', None)
        labels['config'].configure(text='Não selecionado — usando as opções abaixo')
        sync_config()

    for key, title in [('source', '1. Selecionar base'),
                       ('config', '2. Selecionar regras JSON (opcional)'),
                       ('destination', '3. Selecionar pasta para os resultados')]:
        def choose(k=key):
            if k == 'destination':
                chosen = filedialog.askdirectory(parent=root)
            else:
                types = [('JSON', '*.json')] if k == 'config' else [
                    ('Bases tabulares', '*.csv *.tsv *.txt *.xlsx'), ('Todos os arquivos', '*.*')]
                chosen = filedialog.askopenfilename(parent=root, filetypes=types)
            if chosen:
                paths[k] = chosen
                labels[k].configure(text=chosen)
                sync_config()
        control = ttk.Button(panel, text=title, command=choose)
        control.pack(anchor='w')
        controls.append(control)
        labels[key] = ttk.Label(panel, text='Não selecionado', wraplength=730)
        labels[key].pack(anchor='w', pady=(2, 10))
        if key == 'config':
            reset_button = ttk.Button(panel, text='Limpar configuração JSON', command=clear_config, state='disabled')
            reset_button.pack(anchor='w', pady=(0, 10))

    settings = ttk.LabelFrame(panel, text='Como ler o arquivo', padding=10)
    settings.pack(fill='x', pady=(0, 12))
    separator = tk.StringVar(value='Automático')
    encoding = tk.StringVar(value='utf-8-sig')
    sheet = tk.StringVar()
    for row, (title, variable, values) in enumerate([
        ('Separador CSV', separator, ['Automático', ';', ',', 'Tabulação', '|']),
        ('Codificação CSV', encoding, ['utf-8-sig', 'cp1252', 'latin-1']),
    ]):
        ttk.Label(settings, text=title).grid(row=row, column=0, sticky='w', padx=(0, 12), pady=3)
        control = ttk.Combobox(settings, textvariable=variable, values=values, state='readonly', width=22)
        control.grid(row=row, column=1, sticky='w', pady=3)
        controls.append(control)
    ttk.Label(settings, text='Nome da aba Excel').grid(row=2, column=0, sticky='w', padx=(0, 12), pady=3)
    sheet_entry = ttk.Entry(settings, textvariable=sheet, width=25)
    sheet_entry.grid(row=2, column=1, sticky='w', pady=3)
    controls.append(sheet_entry)
    ttk.Label(settings, text='Vazio = primeira aba. Separe opções CSV das opções Excel.', wraplength=680).grid(
        row=3, column=0, columnspan=2, sticky='w', pady=(6, 0))

    for key, title, default in [('trim', 'Remover espaços nas extremidades dos textos', True),
                                ('normalize_headers', 'Padronizar nomes das colunas', False),
                                ('drop_empty_rows', 'Excluir linhas totalmente vazias', False),
                                ('drop_empty_columns', 'Excluir colunas totalmente vazias', False),
                                ('drop_duplicates', 'Excluir linhas inteiramente repetidas', False)]:
        options[key] = tk.BooleanVar(value=default)
        checkbox = ttk.Checkbutton(panel, text=title, variable=options[key])
        checkbox.pack(anchor='w', pady=2)
        checkboxes.append(checkbox)
    ttk.Label(panel, text='Com JSON selecionado, as regras vêm do arquivo e as caixas ficam desativadas.',
              wraplength=730).pack(anchor='w', pady=10)
    status = tk.StringVar(value='Pronto. O arquivo original será preservado.')
    ttk.Label(panel, textvariable=status, wraplength=730).pack(anchor='w', pady=10)

    def set_busy(busy):
        state['busy'] = busy
        for control in controls:
            control.configure(state='disabled' if busy else 'readonly' if isinstance(control, ttk.Combobox) else 'normal')
        button.configure(state='disabled' if busy else 'normal')
        open_button.configure(state='normal' if not busy and state['output'] else 'disabled')
        sync_config()

    def execute():
        if not paths.get('source') or not paths.get('destination'):
            messagebox.showerror('Seleção incompleta', 'Selecione a base e a pasta para os resultados.', parent=root)
            return
        try:
            cfg = json.loads(Path(paths['config']).read_text(encoding='utf-8-sig')) if paths.get('config') else {
                k: v.get() for k, v in options.items()}
            cfg = validate_config(cfg)
        except (OSError, ValueError) as exc:
            messagebox.showerror('Configuração inválida', str(exc), parent=root)
            return
        sep = {'Automático': None, 'Tabulação': '\t'}.get(separator.get(), separator.get())
        read_options = {'separator': sep, 'encoding': encoding.get(), 'sheet': sheet.get() or 0}
        source = paths['source']
        output = Path(paths['destination']) / ('resultado_' + datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
        set_busy(True)
        status.set('Processando… Aguarde a conclusão para fechar a janela.')

        def worker():
            try:
                report = run(source, output, cfg, **read_options)
                messages.put((report, output, None))
            except Exception as exc:
                messages.put((None, output, str(exc)))
        threading.Thread(target=worker, daemon=True).start()

    def open_result():
        if state['output'] is None:
            return
        try:
            path = str(state['output'])
            if sys.platform == 'win32':
                os.startfile(path)
            else:
                subprocess.Popen(['open' if sys.platform == 'darwin' else 'xdg-open', path])
        except OSError as exc:
            messagebox.showerror('Abrir pasta', str(exc), parent=root)

    def poll():
        try:
            report, output, error = messages.get_nowait()
            if error is not None:
                status.set('Falha no processamento. Confira a mensagem e tente novamente.')
                set_busy(False)
                messagebox.showerror('Falha', error, parent=root)
            else:
                state['output'] = output
                warnings = report['conversion_errors']
                status.set('Concluído com avisos.' if warnings else 'Concluído com sucesso.')
                set_busy(False)
                detail = '\n'.join(f"• {e['column']}: {e['invalid_cells']} valor(es) inválido(s)" for e in warnings)
                message = (f"Salvo em: {output}\nLinhas: {report['before']['rows']} → {report['after']['rows']}"
                           f"\nColunas: {report['after']['columns']}\n")
                if warnings:
                    message += '\nConversões não aplicadas; colunas preservadas:\n' + detail
                (messagebox.showwarning if warnings else messagebox.showinfo)('Resultado', message, parent=root)
        except queue.Empty:
            pass
        root.after(150, poll)

    def close():
        if state['busy']:
            status.set('Processamento em andamento. Aguarde antes de fechar.')
            root.bell()
        else:
            root.destroy()

    actions = ttk.Frame(panel)
    actions.pack(anchor='w')
    button = ttk.Button(actions, text='Analisar, tratar e exportar', command=execute)
    button.pack(side='left')
    open_button = ttk.Button(actions, text='Abrir pasta do resultado', command=open_result, state='disabled')
    open_button.pack(side='left', padx=10)
    root.protocol('WM_DELETE_WINDOW', close)
    poll()
    root.mainloop()


if __name__ == '__main__':
    main()
