class wallet:
    def __init__(self): 
        user_wallet = {"apples" : 0,"bananas" : 0,"oranges" : 0}
    
    def add_funds(self,company_to_add,value_to_add):
        self.user_wallet[company_to_add] += value_to_add
    
    def subtract_funds(self, company, value):
        self.user_wallet[company] -= value


class Database:
    def __init__(self):
        wallets = {'nick': wallet(),'rylee' : wallet(), 'peyton' : wallet()}
    
    def add_new_user(self,username):
        self.wallets[username] = wallet()