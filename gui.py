import tkinter as tk
from tkinter import messagebox, simpledialog
from solver import FutoshikiSolver

from utils import *

class FutoshikiGUI:
    
    '''Constructeur'''
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Futoshiki Solver")
        self.root.resizable(0,0)
        
        # Initialiser le solver avec le fichier
        self.solver = FutoshikiSolver("problems/1.txt")
        self.size = self.solver.size
        self.entries = []  
        self.constraint_labels = {}
        self.selected_cell = None
        
        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.control_frame = tk.Frame(self.main_frame)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
        
        tk.Button(self.control_frame, text="Nouvelle Grille", command=self.new_grid).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Résoudre", command=self.solve_grid).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Vérifier", command=self.verify_grid).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Ajouter Contrainte", command=self.add_constraint).pack(side=tk.LEFT, padx=5)
        tk.Button(self.control_frame, text="Tout Effacer", command=self.effacer_grid).pack(side=tk.LEFT, padx=5)
        # tk.Button(self.control_frame, text="Effacer Sélection", command=self.clear_selection).pack(side=tk.LEFT, padx=5)
        # tk.Button(self.control_frame, text="Exporter DIMACS", command=self.export_dimacs).pack(side=tk.LEFT, padx=5)
        
        self.create_grid()
        
    
    def create_grid(self):
        if hasattr(self, 'grid_frame'):
            self.grid_frame.destroy()
        
        self.grid_frame = tk.Frame(self.main_frame)
        self.grid_frame.pack(pady=10)
        
        self.entries = []
        self.constraint_labels = {}
        
        for i in range(self.size):
            row_entries = []
            for j in range(self.size):
                cell_frame = tk.Frame(self.grid_frame)
                cell_frame.grid(row=i*2, column=j*2)
                
                entry = tk.Entry(cell_frame, width=3, font=('Arial', 16), justify='center')
                entry.pack(padx=5, pady=5)
                
                entry.bind("<Button-1>", lambda e, r=i, c=j: self.select_cell(r, c))
                entry.bind("<Key>", self.check_input)
                
                row_entries.append(entry)
                
                if j < self.size - 1:
                    h_label = tk.Label(self.grid_frame, text=" ", width=1, font=('Arial', 16))
                    h_label.grid(row=i*2, column=j*2+1)
                    self.constraint_labels[(i, j, i, j+1)] = h_label
                
                if i < self.size - 1:
                    v_label = tk.Label(self.grid_frame, text=" ", width=1, font=('Arial', 16))
                    v_label.grid(row=i*2+1, column=j*2)
                    self.constraint_labels[(i, j, i+1, j)] = v_label
            
            self.entries.append(row_entries)
    
    def new_grid(self):
        f = simpledialog.askstring("Grille", "Probleme/Taille ? (p,t)")
        if(f.lower() == "p"):
            filename = simpledialog.askstring("Charger grille", 
                                            "Entrez le nom du fichier (ex: 3.txt):",
                                            initialvalue="problems/1.txt")
            if filename:
                try:
                    self.solver = FutoshikiSolver(filename)
                    self.size = self.solver.size
                    self.create_grid()
                    
                    for i in range(self.size):
                        for j in range(self.size):
                            self.entries[i][j].delete(0, tk.END)
                            if self.solver.cells[i][j] != 0:
                                self.entries[i][j].insert(0, str(self.solver.cells[i][j]))
                    
                    for (i1,j1,i2,j2) in self.solver.constraints:
                        if i1 == i2:  # Contrainte horizontale
                            label_key = (i1, j1, i2, j2)
                            self.constraint_labels[label_key].config(text="<")
                        elif j1 == j2:  # Contrainte verticale
                            label_key = (i1, j1, i2, j2)
                            self.constraint_labels[label_key].config(text="<")
                except Exception as e:
                    messagebox.showerror("Erreur", f"Impossible de charger le fichier: {e}")
        elif(f.lower() == "t"):
            val = simpledialog.askinteger("Taille", "Entrer une taille : (3 ... 9)")
            if  9>= val >= 3: 
                self.size = val
                self.create_grid()
            else:
                messagebox.showerror("Erreur", f"Entrez une valeur valide")
                self.size = 4
                self.create_grid()
        else:
            messagebox.showerror("Erreur", "Entrez une valeur valide")
                
    
    def effacer_grid(self):
        for i in range(self.size):
            for j in range(self.size):
                self.entries[i][j].delete(0, tk.END)
                self.solver.clear_cell(i, j)
        
        for label in self.constraint_labels.values():
            label.config(text=" ")
        
        self.solver.constraints = []
    
    def select_cell(self, row, col):
        self.selected_cell = (row, col)
    
    def check_input(self, event):
        if self.selected_cell is None:
            return
        
        row, col = self.selected_cell
        
        # Vérifier que le 1 <= chiffre <= taille
        if event.char.isdigit() and 1 <= int(event.char) <= self.size:
            self.entries[row][col].delete(0, tk.END)
            self.entries[row][col].insert(0, event.char)
            self.solver.set_value(row, col, int(event.char))
            return "break"  
        elif event.keysym == "BackSpace" or event.keysym == "Delete":
            self.entries[row][col].delete(0, tk.END)
            self.solver.clear_cell(row, col)
            return "break"
        
        return "break"  
    
    def clear_selection(self):
        if self.selected_cell:
            row, col = self.selected_cell
            self.entries[row][col].delete(0, tk.END)
            self.solver.clear_cell(row, col)
    
    def add_constraint(self):
        if not self.selected_cell:
            messagebox.showinfo("Information", "Sélectionnez d'abord une cellule")
            return
        
        row1, col1 = self.selected_cell
        
        direction = simpledialog.askstring("Direction", "Direction de la contrainte (d/D pour droite, b/B pour bas):")
        
        if not direction or direction.lower() not in ["d", "b"]:
            return
        
        # Calculer les coordonnées de la seconde cellule
        if direction.lower() == "d" and col1 < self.size - 1:  # Droite
            row2, col2 = row1, col1 + 1
            label_key = (row1, col1, row2, col2)
        elif direction.lower() == "b" and row1 < self.size - 1:  # Bas
            row2, col2 = row1 + 1, col1
            label_key = (row1, col1, row2, col2)
        else:
            messagebox.showinfo("Information", "Direction invalide pour la contrainte")
            return
        
        constraint_type = simpledialog.askstring("Type de contrainte", "Type de contrainte (< ou >):")
        
        if constraint_type == "<":
            self.solver.add_constraint(row1, col1, row2, col2)
            self.constraint_labels[label_key].config(text="<")
        elif constraint_type == ">":
            self.solver.add_constraint(row2, col2, row1, col1)
            self.constraint_labels[label_key].config(text=">")
        else:
            messagebox.showinfo("Information", "Type de contrainte invalide")
    
    def solve_grid(self):
        for i in range(self.size):
            for j in range(self.size):
                text = self.entries[i][j].get()
                if text.isdigit() and 1 <= int(text) <= self.size:
                    self.solver.set_value(i, j, int(text))
                else:
                    self.solver.clear_cell(i, j)
        
        # ! Résoudre la grille
        solution = self.solver.solve()
        
        if solution is not None:
            for i in range(self.size):
                for j in range(self.size):
                    self.entries[i][j].delete(0, tk.END)
                    self.entries[i][j].insert(0, str(solution[i][j]))
            messagebox.showinfo("Résolution", "Grille résolue avec succès!")
            self.export_dimacs()
        else:
            messagebox.showinfo("Résolution", "Pas de solution possible pour cette grille.")
            
    
    def verify_grid(self):
        # dbrd on recup la solution actuelle
        solution = creerMatrice(self.size, self.size, 0)
        for i in range(self.size):
            for j in range(self.size):
                text = self.entries[i][j].get()
                if text.isdigit() and 1 <= int(text) <= self.size:
                    solution[i][j] = int(text)
                else:
                    messagebox.showinfo("Vérification", f"La cellule ({i+1},{j+1}) est vide ou invalide.")
                    return
        
        # Vérifier la solution
        valid, message = self.solver.verify_solution(solution)
        messagebox.showinfo("Vérification", message)
        
    def export_dimacs(self):
        # Mettre à jour les valeurs de la grille
        for i in range(self.size):
            for j in range(self.size):
                text = self.entries[i][j].get()
                if text.isdigit() and 1 <= int(text) <= self.size:
                    self.solver.set_value(i, j, int(text))
                else:
                    self.solver.clear_cell(i, j)
        
        filename = "clauses.cnf"
        
        if filename:
            max_var, num_clauses = self.solver.save_dimacs(filename)
            messagebox.showinfo(
                "Export DIMACS", 
                f"Fichier DIMACS sauvegardé avec succès.\n"
                f"Variables: {max_var}\n"
                f"Clauses: {num_clauses}"
            )
