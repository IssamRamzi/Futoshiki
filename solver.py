from pysat.solvers import Glucose3
from utils import creerMatrice, afficherMatrice, chargerMatrice

class FutoshikiSolver:
    
    '''
        self.size : taille de la grille
        self.cells : matrice avec les cases
        self.constraints : contraintes du jeu de la forme (i1, j1, i2, j2) ou (i1,j1) < (i2,j2)        
    '''
    
    
    '''Constructeur'''
    def __init__(self, filename):

        # self.size = size
        # self.cells = creerMatrice(self.size, self.size, 0)
        # afficherMatrice(self.cells, self.size, self.size)
        # self.constraints = []  

        self.cells, self.constraints, self.size = chargerMatrice(filename)
        afficherMatrice(self.cells, self.size, self.size)

    '''Ajoute une contrainte'''
    def add_constraint(self, row1, col1, row2, col2):
        self.constraints.append((row1, col1, row2, col2))
    
    '''Donne la valeur <value> a une case'''
    def set_value(self, row, col, value):
        """Fixe une valeur initiale dans la grille"""
        if 0 <= row < self.size and 0 <= col < self.size and 1 <= value <= self.size:
            self.cells[row][col] = value
            return True
        return False
    
    '''Enleve la valeur d'une case'''
    def clear_cell(self, row, col):
        if 0 <= row < self.size and 0 <= col < self.size:
            self.cells[row][col] = 0
            return True
        return False
        
        
    """Encode une variable (row, col, val) en un entier unique pour le satsolver"""
    def encode_var(self, row, col, val):
        return row * self.size * self.size + col * self.size + val
        
    """Decode un entier en coordonnées (row, col, val) cad l'inverse de la fonction d'avant"""
    def decode_var(self, var):
        var -= 1  
        val = var % self.size + 1
        var //= self.size
        col = var % self.size
        row = var // self.size
        return row, col, val
    
    """Résout le problème Futoshiki avec un satsolver"""
    def solve(self):
        solver = Glucose3()
        n = self.size
        
        # Chaque cellule doit avoir exactement une valeur
        for i in range(n):
            for j in range(n):
                # Au moins une valeur par cellule
                solver.add_clause([self.encode_var(i, j, val) for val in range(1, n+1)])
                
                # Au plus une valeur par cellule
                for val1 in range(1, n+1):
                    for val2 in range(val1+1, n+1):
                        solver.add_clause([-self.encode_var(i, j, val1), -self.encode_var(i, j, val2)])
        
        # Valeurs uniques par ligne
        for i in range(n):
            for val in range(1, n+1):
                for j1 in range(n):
                    for j2 in range(j1+1, n):
                        solver.add_clause([-self.encode_var(i, j1, val), -self.encode_var(i, j2, val)])
        
        # Valeurs uniques par colonne
        for j in range(n):
            for val in range(1, n+1):
                for i1 in range(n):
                    for i2 in range(i1+1, n):
                        solver.add_clause([-self.encode_var(i1, j, val), -self.encode_var(i2, j, val)])
        
        # Fixer les valeurs initiales
        for i in range(n):
            for j in range(n):
                if self.cells[i][j] != 0:
                    solver.add_clause([self.encode_var(i, j, self.cells[i][j])])
        
        # Ajouter les contraintes d'inégalités
        for i1, j1, i2, j2 in self.constraints:
            for val1 in range(1, n+1):
                for val2 in range(1, n+1):
                    if val1 >= val2:  # Si val1 n'est pas strictement inférieur à val2
                        solver.add_clause([-self.encode_var(i1, j1, val1), -self.encode_var(i2, j2, val2)])
        
        # Résoudre le problème
        if solver.solve():
            model = solver.get_model()
            solution = creerMatrice(n, n, 0)
            
            for var in model:
                if var > 0:  # Variables positives SEULEMENT
                    row, col, val = self.decode_var(var)
                    if 0 <= row < n and 0 <= col < n and 1 <= val <= n:
                        solution[row][col] = val
            self.save_solution(solution)
            return solution
        else:
            return None
    
    """Vérifie si une solution proposée est valide"""
    def verify_solution(self, solution):
        n = self.size
        
        # Valeurs entre 1 et n
        for i in range(n):
            for j in range(n):
                if solution[i][j] < 1 or solution > n:
                    return False, "Certaines valeurs sont hors limites"
        
        # Valeurs uniques dans chaque ligne
        for i in range(n):
            if len(set(solution[i])) != n:
                return False, f"La ligne {i+1} contient des valeurs dupliquées"
        
        # Valeurs uniques dans chaque colonne
        for j in range(n):
            if len(set(solution[:, j])) != n:
                return False, f"La colonne {j+1} contient des valeurs dupliquée"
        
        # Inégalités
        for i1, j1, i2, j2 in self.constraints:
            if solution[i1, j1] >= solution[i2, j2]:
                return False, f"Contrainte non respectée: ({i1+1},{j1+1}) < ({i2+1},{j2+1})"
        
        # Verifier que les valeurs initiales sont conservées
        for i in range(n):
            for j in range(n):
                if self.cells[i][j] != 0 and self.cells[i][j] != solution[i][j]:
                    return False, f"La valeur initiale à ({i+1},{j+1}) n'est pas respectée"
        
        return True, "La solution est correcte"
        
    """Sauvegarde la solutions du probleme dans un fichier TEXT"""
    def save_solution(self, solution):
        with open("solution.txt", "w+") as f:
            f.write(f"Solutoin de la grille de taille {self.size}x{self.size}\n")
            for i in range(self.size):
                for j in range(self.size):
                    f.write(str(solution[i][j]) + " ")
                f.write('\n')
        
                

    """Sauvegarde le problème actuel au format DIMACS CNF"""
    def save_dimacs(self, filename):
        n = self.size
        clauses = []
        
        # Chaque cellule doit avoir exactement une valeur
        for i in range(n):
            for j in range(n):
                # Au moins une valeur par cellule
                clauses.append([self.encode_var(i, j, val) for val in range(1, n+1)])
                
                # Au plus une valeur par cellule
                for val1 in range(1, n+1):
                    for val2 in range(val1+1, n+1):
                        clauses.append([-self.encode_var(i, j, val1), -self.encode_var(i, j, val2)])
        
        # Valeurs uniques par ligne
        for i in range(n):
            for val in range(1, n+1):
                for j1 in range(n):
                    for j2 in range(j1+1, n):
                        clauses.append([-self.encode_var(i, j1, val), -self.encode_var(i, j2, val)])
        
        # Valeurs uniques par colonne
        for j in range(n):
            for val in range(1, n+1):
                for i1 in range(n):
                    for i2 in range(i1+1, n):
                        clauses.append([-self.encode_var(i1, j, val), -self.encode_var(i2, j, val)])
        
        # Fixer les valeurs initiales
        for i in range(n):
            for j in range(n):
                if self.cells[i][j] != 0:
                    clauses.append([self.encode_var(i, j, self.cells[i][j])])
        
        # Contraintes d'inégalités
        for i1, j1, i2, j2 in self.constraints:
            for val1 in range(1, n+1):
                for val2 in range(1, n+1):
                    if val1 >= val2:  # Si val1 n'est pas strictement inférieur à val2
                        clauses.append([-self.encode_var(i1, j1, val1), -self.encode_var(i2, j2, val2)])
        
        # Calculer le nombre de variables et de clauses
        max_var = n * n * n
        num_clauses = len(clauses)
        
        # Ecrire le fichier DIMACS
        with open(filename, 'w') as f:
            # En-tête DIMACS
            f.write(f"c Futoshiki {n}x{n}\n")
            f.write(f"p cnf {max_var} {num_clauses}\n")
            
            # Écrire les clauses
            for clause in clauses:
                f.write(" ".join(map(str, clause)) + " 0\n")
                
        return max_var, num_clauses