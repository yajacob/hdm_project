import math

from astropy.coordinates.builtin_frames.utils import norm

import pandas as pd


class HdmInconsistency:
    matrix_size = 0
    
    def tround(self, num, place):
        num += pow(0.1, place + 4)
        return round(num, place)
    
    def step1_matrix_a1(self, resp_data):
        temp_list = resp_data.split("|")
        fact_size_dic = {30:6, 20:5, 12:4, 6:3}
        row_size_dic = {6:15, 5:10, 4:6, 3:3}
        matrix_size = fact_size_dic[len(temp_list)]
        self.matrix_size = matrix_size
        print("matrix_size:", matrix_size)
        matrix_pair = [0 for i in range(row_size_dic[matrix_size])]
        list_idx = 0
        temp_dic = {}
        for idx, tl in enumerate(temp_list):
            pair_data = tl.split(",")
    
            res_id = int(pair_data[0][-1:]) - 1
            res_val = int(pair_data[2])
            temp_dic[res_id] = res_val
    
            # second item
            if idx % 2 != 0:
                matrix_pair[list_idx] = temp_dic
                temp_dic = {}
                list_idx += 1
    
        return matrix_pair
    
    def step1_matrix_a2(self, matrix_pair):
        matrix_size = self.matrix_size
        idx_list = []
        if matrix_size == 3:
            idx_list = [0, 1, 2]
        elif matrix_size == 4:
            idx_list = [0, 1, 2, 3]
        elif matrix_size == 5:
            idx_list = [0, 1, 2, 3, 4]
        elif matrix_size == 6:
            idx_list = [0, 1, 2, 3, 4, 5]
        pair_size = len(matrix_pair)
    
        matrix = [[0 for col in range(matrix_size)] for row in range(matrix_size)] 
        for idx in range(pair_size):
            temp_pair = {}
            temp_pair = matrix_pair[idx]
            col1_idx = idx_list[list(temp_pair.keys())[0]]
            col2_idx = idx_list[list(temp_pair.keys())[1]]
            row2_idx = col1_idx
            row1_idx = col2_idx
    
            val1 = list(temp_pair.values())[0]
            val2 = list(temp_pair.values())[1]
            matrix[row1_idx][col1_idx] = val1
            matrix[row2_idx][col2_idx] = val2
        return matrix
    
    def step2_matrix_b(self, matrix_a):
        matrix_size = self.matrix_size
        matrix = [[0 for col in range(matrix_size)] for row in range(matrix_size)]
        
        for i in range(matrix_size):
            for j in range(matrix_size):
                if i == j:
                    matrix[i][j] = 1
                else:
                    matrix[i][j] = self.tround(matrix_a[i][j] / matrix_a[j][i], 3)
        return matrix
    
    def step3_matrix_c(self, matrix_b, idx_list):
        matrix_size = self.matrix_size;
        df = pd.DataFrame(matrix_b)
        matrix_b = df[idx_list].values.tolist()
        matrix = [[0 for col in range(matrix_size - 1)] for row in range(matrix_size)]
        
        for i in range(matrix_size):
            for j in range(matrix_size - 1):
                matrix[i][j] = self.tround(matrix_b[i][j] / matrix_b[i][j + 1], 3)
        return matrix
    
    def step4_mean_list(self, matrix_c):
        matrix_size = self.matrix_size
        matrix_mean = [0 for i in range(matrix_size - 1)]
        
        for i in range(matrix_size - 1):
            temp_sum = 0.0
            for j in range(matrix_size):
                temp_sum += matrix_c[j][i]
            matrix_mean[i] = self.tround(temp_sum / matrix_size, 3)
        
        return matrix_mean
    
    def step5_normalize(self, matrix_mean, idx_list):
        matrix_size = self.matrix_size
        norm_val = [0 for i in range(matrix_size)]

        if matrix_size == 6:
            norm_val[idx_list[5]] = 1
            norm_val[idx_list[4]] = self.tround(matrix_mean[4], 3)
            norm_val[idx_list[3]] = self.tround(matrix_mean[4] * matrix_mean[3], 3)
            norm_val[idx_list[1]] = self.tround(norm_val[idx_list[2]] * matrix_mean[1], 3)
        elif matrix_size == 5:
            norm_val[idx_list[4]] = 1
            norm_val[idx_list[3]] = self.tround(matrix_mean[3], 3)
            norm_val[idx_list[2]] = self.tround(matrix_mean[3] * matrix_mean[2], 3)
            norm_val[idx_list[1]] = self.tround(norm_val[idx_list[2]] * matrix_mean[1], 3)
        elif matrix_size == 4:
            norm_val[idx_list[3]] = 1
            norm_val[idx_list[2]] = self.tround(matrix_mean[2], 3)
            norm_val[idx_list[1]] = self.tround(norm_val[idx_list[2]] * matrix_mean[1], 3)
        elif matrix_size == 3:
            norm_val[idx_list[2]] = 1
            norm_val[idx_list[1]] = self.tround(matrix_mean[1], 3)

        norm_val[idx_list[0]] = self.tround(norm_val[idx_list[1]] * matrix_mean[0], 3)
        
        sum_val = 0.0
        for val in norm_val:
            sum_val += val
            
        for idx, val in enumerate(norm_val):
            norm_val[idx] = self.tround(val / sum_val, 3)
        
        return norm_val

    def main_process(self, resp_data):
        normalized_list = []
        matrix_pair = self.step1_matrix_a1(resp_data)
        matrix_a = self.step1_matrix_a2(matrix_pair)
        matrix_b = self.step2_matrix_b(matrix_a)
        matrix_size = self.matrix_size

        if matrix_size == 3:
            for i in range(matrix_size):
                for j in range(matrix_size):
                    if i == j: continue
                    for k in range(matrix_size):
                        if i == k: continue
                        if j == k: continue
                        idx_list = [i, j, k]
                        matrix_c = self.step3_matrix_c(matrix_b, idx_list)
                        matrix_mean = self.step4_mean_list(matrix_c)
                        norm_val = self.step5_normalize(matrix_mean, idx_list)
                        normalized_list.append(norm_val)
                            
        elif matrix_size == 4:
            for i in range(matrix_size):
                for j in range(matrix_size):
                    if i == j: continue
                    for k in range(matrix_size):
                        if i == k: continue
                        if j == k: continue
                        for l in range(matrix_size):
                            if i == l: continue
                            if j == l: continue
                            if k == l: continue
                            idx_list = [i, j, k, l]
                            matrix_c = self.step3_matrix_c(matrix_b, idx_list)
                            matrix_mean = self.step4_mean_list(matrix_c)
                            norm_val = self.step5_normalize(matrix_mean, idx_list)
                            normalized_list.append(norm_val)

        elif matrix_size == 5:
            for i in range(matrix_size):
                for j in range(matrix_size):
                    if i == j: continue
                    for k in range(matrix_size):
                        if i == k: continue
                        if j == k: continue
                        for l in range(matrix_size):
                            if i == l: continue
                            if j == l: continue
                            if k == l: continue
                            for m in range(matrix_size):
                                if i == m: continue
                                if j == m: continue
                                if k == m: continue
                                if l == m: continue
                                idx_list = [i, j, k, l, m]
                                matrix_c = self.step3_matrix_c(matrix_b, idx_list)
                                matrix_mean = self.step4_mean_list(matrix_c)
                                norm_val = self.step5_normalize(matrix_mean, idx_list)
                                normalized_list.append(norm_val)

        elif matrix_size == 6:
            for i in range(matrix_size):
                for j in range(matrix_size):
                    if i == j: continue
                    for k in range(matrix_size):
                        if i == k: continue
                        if j == k: continue
                        for l in range(matrix_size):
                            if i == l: continue
                            if j == l: continue
                            if k == l: continue
                            for m in range(matrix_size):
                                if i == m: continue
                                if j == m: continue
                                if k == m: continue
                                if l == m: continue
                                for n in range(matrix_size):
                                    if i == n: continue
                                    if j == n: continue
                                    if k == n: continue
                                    if l == n: continue
                                    if m == n: continue
                                    idx_list = [i, j, k, l, m, n]
                                    matrix_c = self.step3_matrix_c(matrix_b, idx_list)
                                    matrix_mean = self.step4_mean_list(matrix_c)
                                    norm_val = self.step5_normalize(matrix_mean, idx_list)
                                    normalized_list.append(norm_val)

        df = pd.DataFrame(normalized_list)
        
        #old_consistency = self.tround(df.std().mean(), 4) 
        new_consistency = self.tround(math.sqrt(df.var().sum()), 4)
        return new_consistency


def main():
    # 4 data
    #resp_data = 'CR111,A,40|CR112,B,60|CR114,D,57|CR113,C,43|CR113,C,75|CR111,A,25|CR112,B,38|CR114,D,62|CR111,A,20|CR114,D,80|CR112,B,50|CR113,C,50'

    # 3 data
    # resp_data = 'CR11,Pink,50|CR12,Blue,50|CR11,Pink,50|CR13,Yellow,50|CR12,Blue,50|CR13,Yellow,50'
    
    # 5 data
    resp_data = 'CR31,test31,12|CR32,test32,88|CR31,test31,70|CR33,test33,30|CR31,test31,17|CR34,test34,83|CR31,test31,76|CR35,test35,24|CR32,test32,17|CR33,test33,83|CR32,test32,24|CR34,test34,76|CR32,test32,19|CR35,test35,81|CR33,test33,23|CR34,test34,77|CR33,test33,5|CR35,test35,95|CR34,test34,22|CR35,test35,78'

    # 6 data
    #resp_data = 'CR21,8GB,13|CR22,16GB,87|CR21,8GB,24|CR23,24GB,76|CR21,8GB,20|CR24,32GB,80|CR21,8GB,29|CR25,64GB,71|CR21,8GB,25|CR26,128GB,75|CR22,16GB,18|CR23,24GB,82|CR22,16GB,26|CR24,32GB,74|CR22,16GB,24|CR25,64GB,76|CR22,16GB,21|CR26,128GB,79|CR23,24GB,15|CR24,32GB,85|CR23,24GB,20|CR25,64GB,80|CR23,24GB,20|CR26,128GB,80|CR24,32GB,19|CR25,64GB,81|CR24,32GB,18|CR26,128GB,82|CR25,64GB,27|CR26,128GB,73'
    
    hi = HdmInconsistency()
    consistency = hi.main_process(resp_data)
    print("consistency: %0.4f" % consistency)

if __name__ == "__main__":
    main()
