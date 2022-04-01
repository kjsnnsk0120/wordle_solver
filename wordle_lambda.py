import pandas as pd

if __name__ == "lambda_function":
    import numpy as np
    import collections
    word_list_filename = "/mnt/efs/lib/wordles.txt"
    word_relation_table_filename = "/mnt/efs/lib/word_relation_table_int8.pickle"

elif __name__ == "__main__":
    import requests
    import json
    word_list_filename = "https://slc.is/data/wordles.txt"
    api_endpoint = "https://thtok2ua96.execute-api.ap-northeast-1.amazonaws.com/wordle_solver"

data_init = pd.read_table(word_list_filename,header = None)[0]
data_init.index = data_init.tolist()

class wordle:
    def __init__(self,first_flg,left_word=None):
        data_init = pd.read_table(word_list_filename, header = None)[0]
        self.words_length = len(data_init)
        if int(first_flg):
            self.data = data_init
        else:
            d = []
            for i in range(len(data_init)-1,-1,-1):
                if left_word & 1<<i:
                    d.append(True)
                else:
                    d.append(False)
            self.use_list_bool = d
            self.data = data_init[d]

        self.word_dict = {chr(i):5 for i in range(97,123)}

    def check_word_available(self, word, o_list, p_list):
        w_counter = {}
        for w in word:
            if w in w_counter:
                w_counter[w] += 1
            else:
                w_counter[w] = 1
        for w in w_counter:
            if w_counter[w] > self.word_dict[w]:
                return False
        for i in o_list:
            if o_list[i] != word[i]:
                return False
        for i,p in p_list.items():
            if p not in word:
                return False
            if p == word[i]:
                return False
        return True

    def print_candidate(self,input_word,res):
        tmp = ""
        self.o_list = {}
        self.p_list = {}
        word_counter = collections.Counter(input_word)
        for i in range(5):
            if res[i] == "o":
                self.o_list.update({i:input_word[i]})
                tmp += input_word[i]
            if res[i] == "-":
                self.p_list.update({i:input_word[i]})
                tmp += input_word[i]
        used_counter = collections.Counter(tmp)
        for w in input_word:
            if w in used_counter and used_counter[w] != word_counter[w]:
                self.word_dict[w] = used_counter[w]
            elif w not in used_counter:
                self.word_dict[w] = 0

        self.available_list = self.data.apply(self.check_word_available,o_list = self.o_list,p_list = self.p_list)
        self.data = self.data[self.available_list]
        c = 0
        available_list_limited = self.available_list[self.available_list].index
        for aa in available_list_limited:
            c += 1<<(self.words_length-aa-1)
        self.available_int = c
        return self.available_int

    def calc_aic(self,row):
        c = collections.Counter(row)
        c_np = np.array(list(c.values()))
        prob = c_np/c_np.sum()
        return -(prob * np.log2(prob)).sum()

    def suggest_best_word(self):
        self.ret_table = pd.read_pickle(word_relation_table_filename)[self.data.to_list()]
        ans = self.ret_table.apply(self.calc_aic,axis = 1)
        ans = {k: v for k, v in ans.items()}
        ans_sorted = sorted(ans.items(), key=lambda x:x[1],reverse=True)
        return ans_sorted[0]

def lambda_handler(event, context):
    inpt_params = event['queryStringParameters']
    available_int = int(inpt_params["available_int"])
    first_flag = inpt_params["first_flag"]
    input_word = inpt_params["input_word"]
    res = inpt_params["res"]
    a = wordle(first_flg=first_flag,left_word = available_int)
    available_int = a.print_candidate(input_word= input_word,res=res)
    suggested_word = a.suggest_best_word()[0]
    return_params = {"available_int" : str(available_int), "suggested_word" : str(suggested_word)}
    return return_params

def wordle_solver_cliant(available_int, first_flag, previous_suggested_word):
    while(True):
        input_word = input("input your word : ")
        if len(input_word)==0:
            input_word = previous_suggested_word
            break
        elif len(input_word) == 5:
            break

    while(True):
        res = input("input its response : ")
        if len(res)== 5 and res.count("o") + res.count("-")+res.count("x")==5:
            break

    params = {"available_int":available_int, "first_flag": first_flag, "input_word": input_word, "res":res}
    print("calculating......")
    result = json.loads(requests.get(api_endpoint,params = params).text)
    available_int = int(result["available_int"])
    suggested_word = result["suggested_word"]

    data_init = pd.read_table("wordles.txt",header = None)[0]
    d = []
    for i in range(len(data_init)-1,-1,-1):
        if available_int & 1<<i:
            d.append(True)
        else:
            d.append(False)

    left_length = len(data_init[d])
    if left_length == 1:
        print("the answer is " + str(data_init[d].to_list()[0]))
    elif left_length == 0:
        print("something wrong")
    else:
        print("candidate words are")
        print(*(data_init[d].to_list()))
        print("suggested word is " + str(suggested_word))
    return available_int,left_length,str(suggested_word)
    
def cliant_main():
    first_word = "tares"
    print("suggested word is " + first_word)
    a = wordle_solver_cliant(0,1,first_word)
    for i in range(5):
        if a[1] <=1:
            break
        else:
            a = wordle_solver_cliant(a[0],0,a[2])

if __name__ == "__main__": #on lambda: __name__ = "lambda_function"
    cliant_main()

    