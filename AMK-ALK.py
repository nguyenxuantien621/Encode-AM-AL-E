from pysat.solvers import Solver
from math import comb

def solve_exactly_k(n, k):
    solver = Solver(name='g3')
    
    def R(i, j):
        return n + (i * k + j)  # Chỉ số cho R
    
    
    for i in range(1, n + 1):
        # (1) X_i -> R_{i,1}  
        if i <= n-1:
            solver.add_clause([-i, R(i, 1)])
        
        # (5) ¬X_i -> ¬R_{i,i}  (với i <= k)
        if i <= k:
            solver.add_clause([i, -R(i, i)])  # ¬X_i ∨ ¬R_{i,i}
    
    for i in range(2, n + 1):
        for j in range(1, k + 1):
            # (2) R_{i-1,j} -> R_{i,j}
            solver.add_clause([-R(i-1, j), R(i, j)])
            
            # (4) ¬X_i ∧ ¬R_{i-1,j} -> ¬R_{i,j}

            solver.add_clause([i, R(i-1, j), -R(i, j)])
            
            # (6) ¬R_{i-1,j-1} -> ¬R_{i,j}  (với j >= 2)
            if j >= 2:
                solver.add_clause([R(i-1, j-1), -R(i, j)])
                 # (3) X_i ∧ R_{i-1,j-1} -> R_{i,j}
            solver.add_clause([-i, -R(i-1, j-1), R(i, j)])
       
    #  (7) ALK
    if k == 1:
        # R_{n-1,1} ∨ X_n
        solver.add_clause([R(n-1, 1), n])
    else:
        # R_{n-1,k} ∨ (X_n ∧ R_{n-1,k-1})
        solver.add_clause([R(n-1, k), n])
        solver.add_clause([R(n-1, k), R(n-1, k-1)])
    
    #  (8) AMK
    for i in range(k + 1, n + 1):
        # X_i -> ¬R_{i-1,k}  <=> ¬X_i ∨ ¬R_{i-1,k}
        solver.add_clause([-i, -R(i-1, k)])
    
    # ===== LIỆT KÊ KẾT QUẢ =====
    count = 0
    seen = set()
    
    print(f"Danh sách các cách chọn ĐÚNG {k} người từ {n} người:")
    
    for model in solver.enum_models():
        # Lấy các biến X (1..n) có giá trị TRUE
        selected = tuple(sorted([v for v in model if 1 <= v <= n]))
        
        if selected not in seen:
            seen.add(selected)
            if len(selected) == k:  # Chỉ in nếu đúng k
                print(f"Cách {count + 1}: {list(selected)}")
                count += 1
    
    solver.delete()
    print(f"\nTổng cộng: {count} cách (C({n},{k}) = {comb(n, k)})")

# Chạy thử
solve_exactly_k(7,3)