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
        idx_list = [0, 1, 2, 3]
        pair_size = len(matrix_pair)
        matrix_size = self.matrix_size
    
        matrix = [[0 for col in range(matrix_size)] for row in range(matrix_size)] 
        for idx in range(pair_size):
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

        norm_val[idx_list[3]] = 1
        norm_val[idx_list[2]] = self.tround(matrix_mean[2], 3)
        norm_val[idx_list[1]] = self.tround(norm_val[idx_list[2]] * matrix_mean[1], 3)
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

        for i in range(4):
            for j in range(4):
                if i == j: continue
                for k in range(4):
                    if i == k: continue
                    if j == k: continue
                    for l in range(4):
                        if i == l: continue
                        if j == l: continue
                        if k == l: continue
                        idx_list = [i, j, k, l]
                        matrix_c = self.step3_matrix_c(matrix_b, idx_list)
                        matrix_mean = self.step4_mean_list(matrix_c)
                        norm_val = self.step5_normalize(matrix_mean, idx_list)
                        normalized_list.append(norm_val)

        df = pd.DataFrame(normalized_list)
        
        #old_consistency = self.tround(df.std().mean(), 4) 
        new_consistency = self.tround(math.sqrt(df.var().sum()), 4)
        #print("old inconsistency: %0.4f" % old_consistency)
        #print("new inconsistency: %0.4f" % new_consistency)
        return new_consistency

def main():
    resp_data = 'CR111,A,40|CR112,B,60|CR114,D,57|CR113,C,43|CR113,C,75|CR111,A,25|CR112,B,38|CR114,D,62|CR111,A,20|CR114,D,80|CR112,B,50|CR113,C,50'
    # resp_data = 'CR111,A,30|CR112,B,70|CR112,B,63|CR114,D,37|CR114,D,83|CR113,C,17|CR111,A,65|CR114,D,35|CR113,C,53|CR111,A,47|CR112,B,79|CR113,C,21'
    
    hi = HdmInconsistency()
    consistency = hi.main_process(resp_data)
    print("consistency: %0.4f" % consistency)

if __name__ == "__main__":
    main()
