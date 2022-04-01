import collections
import numpy as np
import pandas as pd

word_list_filename = "https://slc.is/data/wordles.txt"
word_relation_table_filename1 = "word_relation_table_int8_1.pk"
word_relation_table_filename2 = "word_relation_table_int8_2.pk"

class wordle:
    def __init__(self,first_flg,left_word=None):
        if first_flg:
            self.words = pd.read_table(word_list_filename, header = None)[0]
        else:
            self.words = left_word

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

        self.left_word_bool = self.words.apply(self.check_word_available,o_list = self.o_list,p_list = self.p_list)
        self.left_word = self.words[self.left_word_bool]
        return self.left_word 

    def calc_aic(self,row):
        c = collections.Counter(row)
        c_np = np.array(list(c.values()))
        prob = c_np/c_np.sum()
        return -(prob * np.log2(prob)).sum()

    def suggest_best_word(self):
        word_relation_table1 = pd.read_pickle(word_relation_table_filename1)
        word_relation_table2 = pd.read_pickle(word_relation_table_filename2)
        self.word_relation_table = pd.concat((word_relation_table1,word_relation_table2))[self.left_word.to_list()]
        aic_list = self.word_relation_table.apply(self.calc_aic,axis = 1)
        aic_dict = {k: v for k, v in aic_list.items()}
        aic_sorted = sorted(aic_dict.items(), key=lambda x:x[1],reverse=True)
        return aic_sorted[0]

def wordle_solver(available_words, first_flag, previous_suggested_word):
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

    print("calculating......")
    a = wordle(first_flg=first_flag,left_word = available_words)
    available_words = a.print_candidate(input_word= input_word,res=res)
    suggested_word = a.suggest_best_word()[0]

    left_length = len(available_words)
    if left_length == 1:
        print("the answer is " + str(available_words.to_list()[0]))
    elif left_length == 0:
        print("something wrong")
    else:
        print("candidate words are")
        print(*(available_words.to_list()))
        print("suggested word is " + str(suggested_word))
    return available_words,left_length,str(suggested_word)

def calc_word_relation_table(filename = "word_relation_table.csv"):
    words = pd.read_table(word_list_filename, header = None)[0]
    relation_list = []
    
    def ret(inp,ans):
        ret = 0
        tmp = []
        ans_list = {}
        for i in range(5):
            if ans[i] in ans_list:
                ans_list[ans[i]] += 1
            else:
                ans_list[ans[i]] = 1

        for i in range(5):
            if inp[i] == ans[i]:
                ret += 2 * 3**i
                ans_list[inp[i]] -= 1
                tmp.append(i)

        for i in range(5):
            if inp[i] in ans_list and i not in tmp and ans_list[inp[i]] != 0:
                ret += 1 * 3**i
                ans_list[inp[i]] -= 1
        return ret

    for ans in words:
        relation_list.append(words.apply(ret,ans = ans).rename(ans))
    ret_table = pd.concat(relation_list,axis=1)
    ret_table.to_csv(filename)
    
def main():
    first_word = "tares"
    print("suggested word is " + first_word)
    a = wordle_solver(0,True,first_word)
    for i in range(5):
        if a[1] <=1:
            break
        else:
            a = wordle_solver(a[0],False,a[2])

if __name__ == "__main__":
    main()