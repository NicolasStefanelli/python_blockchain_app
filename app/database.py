class wallet:
    def __init__(self, is_bank=False): 
        #bank starts with 1000 of each fruit and users start with 300 apples to be exchanged
        if(is_bank == True):
            self.user_wallet =  {"apples" : 1000,"bananas" : 1000,"oranges" : 1000}
        else:
            self.user_wallet = {"apples" : 300,"bananas" : 0,"oranges" : 0}
    
    def add_funds(self,company_to_add,value_to_add):
        self.user_wallet[company_to_add] += value_to_add

    def subtract_funds(self, company, value):
        self.user_wallet[company] -= value
    
    def check_fund(self,company):
       return int(self.user_wallet[company])
    
    def return_companies(self):
        return self.user_wallet.keys()


class Database:
    def __init__(self):
        self.wallets = {'nick': wallet(),'rylee' : wallet(), 'peyton' : wallet(), 'bank':wallet(True)}
    
    def get_users(self):
        return self.wallets.keys()
    
    def add_new_user(self,username):
        self.wallets[username] = wallet()
    
    def get_fund(self,username,company):
        return self.wallets[username].check_fund(company)
    
    def edit_wallet(self,type,amount,author,transaction):
        if(transaction == "SOLD"):
            self.wallets[author].subtract_funds(type,amount)
        elif(transaction == "BOUGHT"):
            self.wallets[author].add_funds(type,amount)
    
    def get_all_companies(self):
        return self.wallets['bank'].return_companies()
        
    def __str__(self):
        return_str = ""
        return_str += "\n----------------\n"
        return_str += "Current Databse standings:\n"
        for user in self.wallets.keys():
            return_str += user + "\n"
            user_wallet = self.wallets[user]
            for company in user_wallet.return_companies():
                return_str += company + " " + str(user_wallet.check_fund(company)) + "\n"
        
        return_str += "\n----------------\n"

        return return_str
        

"""
app = Flask(__name__)

database = Database()

@app.route('/fund_check', methods=['POST'])
def check_funds():
    tx_data = request.get_json()
    required_fields = ["author", "amount","type"]
    #print("Recieved Required Fields")
    for field in required_fields:
        if not tx_data.get(field):
            print("Invalid")
            return "Invalid transaction data", 404
    
    print("check complete")
"""   