def creerMatrice(N, M, value):
    Mat = []
    for i in range(N):
        row = []
        for j in range(M):
            row.append(value);
        Mat.append(row)
    return Mat
        
def afficherMatrice(Mat, N, M):
    for i in range(N):
        for j in range(M):
            print(Mat[i][j], end=" ")
        print()
        
def chargerMatrice(filename):
    mat = []
    constraints = []
    with open(filename, "r") as f:
        size = int(f.readline())
        for _ in range(size):
            row = list(map(int, f.readline().strip().split()))
            mat.append(row)
        
        for line in f:
            line = line.strip()
            if line:
                parts = list(map(int, line.split()))
                if len(parts) == 4:
                    constraints.append(tuple(parts))
    return mat, constraints, size