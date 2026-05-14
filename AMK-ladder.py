import math
from pysat.solvers import Glucose3

# Quản lý ID 
class IDManager:
    def __init__(self, start_id):
        self.dictionary_id = {}
        self.next_id = start_id

    def get_id(self, block_idx, pos, current_sum):
        # Tạo key duy nhất 
        key = f"B{block_idx}_P{pos}_S{current_sum}"
        if key not in self.dictionary_id:
            self.dictionary_id[key] = self.next_id
            self.next_id += 1
        return self.dictionary_id[key]

#  AMK 
def AMK(g, block, number_block, k, id_manager):
    w = len(block)
    
    # 1.
    for j in range(0, w - 1): 
        Xij = block[j]
        Rij1 = id_manager.get_id(number_block, j, 0)
        g.add_clause([-Xij, Rij1])
        
    # 2.
    for j in range(1, w - 1): 
        for s in range(0, min(j, k)): 
            Rijm1s = id_manager.get_id(number_block, j - 1, s)
            Rijs = id_manager.get_id(number_block, j, s)
            g.add_clause([-Rijm1s, Rijs]) 

    # 3.
    for j in range(1, w - 1):
        for s in range(1, min(j + 1, k)):
            Xij = block[j]
            Rijm1sm1 = id_manager.get_id(number_block, j - 1, s - 1)
            Rijs = id_manager.get_id(number_block, j, s)
            g.add_clause([-Xij, -Rijm1sm1, Rijs])
    
    # 4.
    for j in range(0, k): 
        Xij = block[j]
        Rijj = id_manager.get_id(number_block, j, j)
        g.add_clause([Xij, -Rijj]) 

    # 5.
    for j in range(1, w - 1):
        for s in range(1, min(j + 1, k)):
            Rijm1sm1 = id_manager.get_id(number_block, j - 1, s - 1)
            Rijs = id_manager.get_id(number_block, j, s)
            g.add_clause([Rijm1sm1, -Rijs]) 

    # 6.
    for j in range(1, w - 1):
        for s in range(0, min(j, k)):
            Xij = block[j]
            Rijm1s = id_manager.get_id(number_block, j - 1, s)
            Rijs = id_manager.get_id(number_block, j, s)
            g.add_clause([Xij, Rijm1s, -Rijs])

    # 7. (Ràng buộc At-Most-K)
    for j in range(k, w): 
        Xij = block[j]
        Rijm1k = id_manager.get_id(number_block, j - 1, k - 1)
        g.add_clause([-Xij, -Rijm1k])

#  Chia Area
def get_area(vars_list, width, number):
    start = width * number
    end = min(start + width, len(vars_list))
    return vars_list[start:end]

#  Định danh Block 
def get_block_num(area_idx, is_forward):
    return 2 * area_idx + (0 if is_forward else 1)

#  Encoding cho từng Area 
def encode_area(g, area, area_idx, k, n_areas, width, id_manager):
    # Block xuôi 
    if area_idx != 0:
        bid_fwd = get_block_num(area_idx, True)
        AMK(g, area, bid_fwd, k, id_manager)
    
    # Block ngược 
    if area_idx != n_areas - 1:
        bid_bwd = get_block_num(area_idx, False)
        AMK(g, area[::-1], bid_bwd, k, id_manager)

#  Nối các Area 
def connect_areas(g, area1_idx, area2_idx, k, width, id_manager):
    bid_bwd = get_block_num(area1_idx, False) 
    bid_fwd = get_block_num(area2_idx, True)  

    for j in range(2, width + 1):
        for p in range(1, k + 1):
            j1, s1 = (width - j), (k - p)
            j2, s2 = (j - 2), (p - 1)

            if s1 >= 0 and s2 >= 0:
                R_var1 = id_manager.get_id(bid_bwd, j1, s1)
                R_var2 = id_manager.get_id(bid_fwd, j2, s2)
                g.add_clause([-R_var1, -R_var2])

#  Hàm thực thi chính 
def sc_amk_Ladder(g, vars_list, k, width):
    n_areas = math.ceil(len(vars_list) / width)
    id_manager = IDManager(max(vars_list) + 1)

    for i in range(n_areas):
        area = get_area(vars_list, width, i)
        encode_area(g, area, i, k, n_areas, width, id_manager)
 
    for i in range(n_areas - 1):
        connect_areas(g, i, i + 1, k, width, id_manager)

# --- VÍ DỤ CHẠY THỬ ---
def main():
    solver = Glucose3()
    
    # Bài toán: 10 biến, Cửa sổ width=4, At-most-k=2
    my_vars = list(range(1, 11))
    k = 2
    width = 4
    
    sc_amk_Ladder(solver, my_vars, k, width)
    
    # Test
    solver.add_clause([1])
    solver.add_clause([2])
    
    
    
    if solver.solve():
        print(">>> Kết quả: SAT")
        model = solver.get_model()
        # Chỉ in ra các biến chính để dễ theo dõi
        true_vars = [v for v in model if 0 < v <= max(my_vars)]
        print(f"Bóng đèn được bật: {true_vars}")
    else:
        print(">>> Kết quả: UNSAT (Vi phạm ràng buộc cửa sổ!)")

if __name__ == "__main__":
    main()