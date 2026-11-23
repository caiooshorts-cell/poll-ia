"""DevPilot PC — assistente local de programação com Ollama."""

from __future__ import annotations

import json
import queue
import threading
import urllib.error
import urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

OLLAMA = "http://127.0.0.1:11434"
MAX_CONTEXT_CHARS = 32_000
ALLOWED_EXTENSIONS = {
    ".py", ".js", ".ts", ".tsx", ".jsx", ".html", ".css", ".json", ".md",
    ".go", ".rs", ".java", ".c", ".cpp", ".h", ".cs", ".php", ".rb", ".sql",
    ".yml", ".yaml", ".toml", ".sh", ".ps1",
}

SYSTEM_PROMPT = """Você é DevPilot, um especialista em programação para PC.
Responda em português, de forma direta e prática. Priorize código correto, seguro,
testável e fácil de manter. Ao sugerir alterações, explique onde aplicar e forneça
blocos de código completos. Nunca afirme ter executado ou modificado algo no PC.
"""


class DevPilot(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("DevPilot PC — IA para programação")
        self.geometry("1120x760")
        self.minsize(820, 580)
        self.configure(bg="#111827")
        self.context_parts: list[str] = []
        self.events: queue.Queue[tuple[str, str]] = queue.Queue()
        self.model = tk.StringVar(value="qwen2.5-coder:7b")
        self.status = tk.StringVar(value="Verificando Ollama…")
        self._build_ui()
        self.after(100, self._drain_events)
        threading.Thread(target=self._load_models, daemon=True).start()

    def _build_ui(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background="#111827")
        style.configure("TLabel", background="#111827", foreground="#e5e7eb")
        style.configure("TButton", padding=7)

        sidebar = tk.Frame(self, bg="#172033", width=245)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        tk.Label(sidebar, text="DevPilot", font=("Segoe UI", 20, "bold"), bg="#172033", fg="#67e8f9").pack(anchor="w", padx=18, pady=(22, 2))
        tk.Label(sidebar, text="IA local para programação", bg="#172033", fg="#94a3b8").pack(anchor="w", padx=18, pady=(0, 22))

        tk.Label(sidebar, text="MODELO OLLAMA", bg="#172033", fg="#94a3b8", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=18)
        self.model_box = ttk.Combobox(sidebar, textvariable=self.model, state="normal")
        self.model_box.pack(fill="x", padx=18, pady=(5, 20))

        ttk.Button(sidebar, text="Adicionar arquivo", command=self.add_file).pack(fill="x", padx=18, pady=4)
        ttk.Button(sidebar, text="Adicionar pasta", command=self.add_folder).pack(fill="x", padx=18, pady=4)
        ttk.Button(sidebar, text="Limpar contexto", command=self.clear_context).pack(fill="x", padx=18, pady=4)
        ttk.Separator(sidebar).pack(fill="x", padx=18, pady=18)
        tk.Label(sidebar, text="ATALHOS", bg="#172033", fg="#94a3b8", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=18, pady=(0, 6))
        for label, prompt in [("Explicar código", "Explique o código selecionado ou enviado."), ("Encontrar bug", "Analise o contexto e encontre possíveis bugs."), ("Revisar código", "Faça uma revisão técnica objetiva do contexto.")]:
            ttk.Button(sidebar, text=label, command=lambda p=prompt: self.quick_prompt(p)).pack(fill="x", padx=18, pady=3)
        self.context_label = tk.Label(sidebar, text="Nenhum contexto", bg="#172033", fg="#94a3b8", wraplength=205, justify="left")
        self.context_label.pack(side="bottom", anchor="w", padx=18, pady=20)

        main = tk.Frame(self, bg="#111827")
        main.pack(side="left", fill="both", expand=True, padx=18, pady=16)
        top = tk.Frame(main, bg="#111827")
        top.pack(fill="x")
        tk.Label(top, text="Conversa", font=("Segoe UI", 16, "bold"), bg="#111827", fg="#f8fafc").pack(side="left")
        tk.Label(top, textvariable=self.status, bg="#111827", fg="#94a3b8").pack(side="right")

        self.chat = tk.Text(main, wrap="word", state="disabled", bg="#0b1220", fg="#e5e7eb", insertbackground="#fff", relief="flat", padx=16, pady=14, font=("Cascadia Code", 10))
        self.chat.pack(fill="both", expand=True, pady=(14, 12))
        self.chat.tag_configure("user", foreground="#67e8f9", font=("Segoe UI", 10, "bold"))
        self.chat.tag_configure("assistant", foreground="#a7f3d0", font=("Segoe UI", 10, "bold"))
        self.chat.tag_configure("text", foreground="#e5e7eb")
        self._append("assistant", "DevPilot pronto. Escolha um modelo local e pergunte sobre o seu código.\n\n")

        bottom = tk.Frame(main, bg="#111827")
        bottom.pack(fill="x")
        self.input = tk.Text(bottom, height=4, wrap="word", bg="#1f2937", fg="#f8fafc", insertbackground="#fff", relief="flat", padx=12, pady=10, font=("Segoe UI", 11))
        self.input.pack(side="left", fill="x", expand=True)
        self.input.bind("<Control-Return>", lambda _event: self.send())
        ttk.Button(bottom, text="Enviar\nCtrl+Enter", command=self.send).pack(side="left", padx=(10, 0), fill="y")

    def _request(self, endpoint: str) -> dict:
        request = urllib.request.Request(f"{OLLAMA}{endpoint}")
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode())

    def _load_models(self) -> None:
        try:
            models = [item["name"] for item in self._request("/api/tags").get("models", [])]
            self.events.put(("models", json.dumps(models)))
        except (urllib.error.URLError, TimeoutError, OSError):
            self.events.put(("status", "Ollama não encontrado em localhost:11434"))

    def _drain_events(self) -> None:
        while not self.events.empty():
            kind, content = self.events.get()
            if kind == "models":
                models = json.loads(content)
                self.model_box["values"] = models
                if models:
                    self.model.set(models[0])
                    self.status.set(f"{len(models)} modelo(s) local(is) disponível(is)")
                else:
                    self.status.set("Nenhum modelo instalado no Ollama")
            elif kind == "status":
                self.status.set(content)
            elif kind == "chunk":
                self._append("text", content)
            elif kind == "done":
                self._append("text", "\n\n")
                self.status.set("Pronto")
                self.input.configure(state="normal")
            elif kind == "error":
                self._append("text", f"\n[Erro: {content}]\n\n")
                self.status.set("Não foi possível gerar a resposta")
                self.input.configure(state="normal")
        self.after(80, self._drain_events)

    def _append(self, tag: str, text: str) -> None:
        self.chat.configure(state="normal")
        if tag in ("user", "assistant"):
            text = ("Você: " if tag == "user" else "DevPilot: ") + text
        self.chat.insert("end", text, tag)
        self.chat.configure(state="disabled")
        self.chat.see("end")

    def add_file(self) -> None:
        path = filedialog.askopenfilename(title="Escolha um arquivo de código")
        if path:
            self._read_context_file(Path(path))

    def _read_context_file(self, path: Path) -> None:
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            self.context_parts.append(f"\n--- Arquivo: {path.name} ---\n{content}")
            self._update_context_label()
        except OSError as error:
            messagebox.showerror("DevPilot", f"Não foi possível ler o arquivo:\n{error}")

    def add_folder(self) -> None:
        folder = filedialog.askdirectory(title="Escolha uma pasta de projeto")
        if not folder:
            return
        count = 0
        for path in Path(folder).rglob("*"):
            if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS and not any(part in {"node_modules", ".git", "dist", "build", ".venv"} for part in path.parts):
                if sum(map(len, self.context_parts)) > MAX_CONTEXT_CHARS:
                    break
                self._read_context_file(path)
                count += 1
        self.status.set(f"{count} arquivo(s) de contexto adicionados")

    def clear_context(self) -> None:
        self.context_parts.clear()
        self._update_context_label()

    def _update_context_label(self) -> None:
        size = sum(map(len, self.context_parts))
        self.context_label.config(text=f"Contexto: {len(self.context_parts)} arquivo(s)\n{size:,} caracteres")

    def quick_prompt(self, prompt: str) -> None:
        self.input.delete("1.0", "end")
        self.input.insert("1.0", prompt)
        self.input.focus_set()

    def send(self) -> None:
        prompt = self.input.get("1.0", "end").strip()
        if not prompt:
            return
        if not self.model.get().strip():
            messagebox.showwarning("DevPilot", "Escolha ou informe um modelo do Ollama.")
            return
        self.input.delete("1.0", "end")
        self.input.configure(state="disabled")
        self._append("user", prompt + "\n\n")
        self._append("assistant", "")
        self.status.set("Gerando resposta…")
        threading.Thread(target=self._generate, args=(prompt,), daemon=True).start()

    def _generate(self, prompt: str) -> None:
        context = "".join(self.context_parts)
        if len(context) > MAX_CONTEXT_CHARS:
            context = context[:MAX_CONTEXT_CHARS] + "\n[contexto cortado]"
        full_prompt = prompt + (f"\n\nContexto do projeto:\n{context}" if context else "")
        payload = {"model": self.model.get().strip(), "prompt": full_prompt, "system": SYSTEM_PROMPT, "stream": True}
        try:
            request = urllib.request.Request(f"{OLLAMA}/api/generate", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(request, timeout=180) as response:
                for line in response:
                    data = json.loads(line.decode())
                    if data.get("response"):
                        self.events.put(("chunk", data["response"]))
            self.events.put(("done", ""))
        except Exception as error:
            self.events.put(("error", str(error)))


if __name__ == "__main__":
    DevPilot().mainloop()
