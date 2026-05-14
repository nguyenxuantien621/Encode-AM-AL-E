import math
from pysat.solvers import Glucose3

# QUẢN LÝ ID 
class IDManager:
    def __init__(self, start_id):
        self.dictionary_id = {}
        self.next_id = start_id

    def get_id(self, label, width, block_idx, pos, current_sum): 
        key = f"{label}_W{width}_B{block_idx}_P{pos}_S{current_sum}"
        if key not in self.dictionary_id:
            self.dictionary_id[key] = self.next_id
            self.next_id += 1
        return self.dictionary_id[key]

#  BIẾN CHÍNH
def get_var_id(day, shift_type):
    shift_map = {'D': 0, 'E': 1, 'N': 2, 'O': 3}
    return (day * 4) + shift_map[shift_type] + 1

#  AMK
def AMK(g, block, number_block, k, label, width, id_manager):
    w = len(block)
    for j in range(0, w - 1): 
        Xij = block[j]
        Rij1 = id_manager.get_id(label, width, number_block, j, 0)
        g.add_clause([-Xij, Rij1])
        
    for j in range(1, w - 1): 
        for s in range(0, min(j, k)): 
            Rijm1s = id_manager.get_id(label, width, number_block, j - 1, s)
            Rijs = id_manager.get_id(label, width, number_block, j, s)
            g.add_clause([-Rijm1s, Rijs]) 

    for j in range(1, w - 1):
        for s in range(1, min(j + 1, k)):
            Xij = block[j]
            Rijm1sm1 = id_manager.get_id(label, width, number_block, j - 1, s - 1)
            Rijs = id_manager.get_id(label, width, number_block, j, s)
            g.add_clause([-Xij, -Rijm1sm1, Rijs])
    
    for j in range(0, k): 
        Xij = block[j]
        Rijj = id_manager.get_id(label, width, number_block, j, j)
        g.add_clause([Xij, -Rijj]) 

    for j in range(1, w - 1):
        for s in range(1, min(j + 1, k)):
            Rijm1sm1 = id_manager.get_id(label, width, number_block, j - 1, s - 1)
            Rijs = id_manager.get_id(label, width, number_block, j, s)
            g.add_clause([Rijm1sm1, -Rijs]) 

    for j in range(1, w - 1):
        for s in range(0, min(j, k)):
            Xij = block[j]
            Rijm1s = id_manager.get_id(label, width, number_block, j - 1, s)
            Rijs = id_manager.get_id(label, width, number_block, j, s)
            g.add_clause([Xij, Rijm1s, -Rijs])

    for j in range(k, w): 
        Xij = block[j]
        Rijm1k = id_manager.get_id(label, width, number_block, j - 1, k - 1)
        g.add_clause([-Xij, -Rijm1k])

def connect_areas(g, area1_idx, area2_idx, k, width, label, id_manager):
    bid_bwd = 2 * area1_idx + 1
    bid_fwd = 2 * area2_idx + 0
    for j in range(2, width + 1):
        for p in range(1, k + 1):
            j1, s1 = (width - j), (k - p)
            j2, s2 = (j - 2), (p - 1)
            if s1 >= 0 and s2 >= 0:
                R_var1 = id_manager.get_id(label, width, bid_bwd, j1, s1)
                R_var2 = id_manager.get_id(label, width, bid_fwd, j2, s2)
                g.add_clause([-R_var1, -R_var2])

def sc_amk_Ladder(g, vars_list, k, width, label, id_manager):
    n_areas = math.ceil(len(vars_list) / width)
    for i in range(n_areas):
        start, end = i * width, min((i + 1) * width, len(vars_list))
        area = vars_list[start:end]
        if i != 0:
            AMK(g, area, 2 * i + 0, k, label, width, id_manager)
        if i != n_areas - 1:
            AMK(g, area[::-1], 2 * i + 1, k, label, width, id_manager)
    for i in range(n_areas - 1):
        connect_areas(g, i, i + 1, k, width, label, id_manager)

# Ex-one
def add_exactly_one_constraint(g, var_list):
    g.add_clause(var_list)
    for i in range(len(var_list)):
        for j in range(i + 1, len(var_list)):
            g.add_clause([-var_list[i], -var_list[j]])

#  RÀNG BUỘC CHO EN (Evening/Night)
def get_en_vars(g, total_days, id_manager):
    en_vars = []
    for d in range(total_days):
        en_id = id_manager.next_id
        id_manager.next_id += 1
        e_id = get_var_id(d, 'E')
        n_id = get_var_id(d, 'N')
        # Logic: EN_d -> (E_d v N_d) và ngược lại
        g.add_clause([-en_id, e_id, n_id])
        g.add_clause([-e_id, en_id])
        g.add_clause([-n_id, en_id])
        en_vars.append(en_id)
    return en_vars

# Main để chạy thử
def main():
    solver = Glucose3()
    days = 28
    max_main_id = days * 4
    id_manager = IDManager(max_main_id + 1)

    # Ràng buộc 1: Mỗi ngày đúng 1 ca 
    for d in range(days):
        day_vars = [get_var_id(d, s) for s in ['D', 'E', 'N', 'O']]
        add_exactly_one_constraint(solver, day_vars)

    #  các tập biến mục tiêu
    not_off = [-get_var_id(d, 'O') for d in range(days)]
    evening = [get_var_id(d, 'E') for d in range(days)]
    night = [get_var_id(d, 'N') for d in range(days)]
    not_evening = [-v for v in evening]
    not_night = [-v for v in night]
    en_vars = get_en_vars(solver, days, id_manager)
    not_en_vars = [-v for v in en_vars]

   
    # 2. Max 6 work / 7 days
    sc_amk_Ladder(solver, not_off, 6, 7, "not_O", id_manager)
    # 3. At least 4 off / 14 days => Max 10 work / 14 days
    sc_amk_Ladder(solver, not_off, 10, 14, "not_O", id_manager)
    # 4. At least 4 evening / 14 days => Max 10 not_evening / 14 days
    sc_amk_Ladder(solver, not_evening, 10, 14, "not_E", id_manager)
    # 5. At most 8 evening / 14 days
    sc_amk_Ladder(solver, evening, 8, 14, "E", id_manager)
    # 6. At least 20 work / 28 days => Max 8 off / 28 days
    off_vars = [get_var_id(d, 'O') for d in range(days)]
    sc_amk_Ladder(solver, off_vars, 8, 28, "O", id_manager)
    # 7. At most 4 night / 14 days
    sc_amk_Ladder(solver, night, 4, 14, "N", id_manager)
    # 8. At least 1 night / 14 days => Max 13 not_night / 14 days
    sc_amk_Ladder(solver, not_night, 13, 14, "not_N", id_manager)
    # 9. At least 2 E/N / 7 days => Max 5 not_EN / 7 days
    sc_amk_Ladder(solver, not_en_vars, 5, 7, "not_EN", id_manager)
    # 10. At most 4 E/N / 7 days
    sc_amk_Ladder(solver, en_vars, 4, 7, "EN", id_manager)
    # 11. Night shifts not successive
    for d in range(days - 1):
        solver.add_clause([-get_var_id(d, 'N'), -get_var_id(d+1, 'N')])
        #Test
    for d in range(5):
     solver.add_clause([get_var_id(d, 'N')])
    # GIẢI VÀ IN KẾT QUẢ
    if solver.solve():
        print(">>> KẾT QUẢ: SAT (Đã tìm thấy lịch trực thỏa mãn)")
        model = solver.get_model()
        for d in range(days):
            for s in ['D', 'E', 'N', 'O']:
                if model[get_var_id(d, s) - 1] > 0:
                    print(f"Ngày {d+1:02d}: Ca {s}")
    else:
        print(">>> KẾT QUẢ: UNSAT (Không có lịch trực nào thỏa mãn các ràng buộc trên)")

if __name__ == "__main__":
    main()