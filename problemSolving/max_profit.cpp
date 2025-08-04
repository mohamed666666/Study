// Online C++ compiler to run C++ program online
#include <iostream>
#include<vector>
#include<algorithm>
using namespace std;

class Solution {
  public:
    int maximumProfit(vector<int> &prices) {
        // code her
        int buy = 0;
        int sell = 0;
        int buy_index = -1;
        int sell_index = -1;
        for(int i=0;i<prices.size()-1;i++){
            if (prices[i+1]>prices[i]){
                cout<<"the buy index"<<prices[i]<<endl;
                buy_index=i;
                buy+=prices[i];
            }
            if ((prices[buy_index] < prices[i])&&(true) ){
                sell+=prices[i];
                sell_index=i;
            }
            
        }
        return sell-buy;
    }
    
    
    vector<int> slice(vector<int> vec,int start,int end){
        vector<int> result;
        for (int i =start ; i<end;i++){
            result.push_back(vec[i]);
        }
        return result;
    }
    
    int min_number(vector<int> vec){
        return *min_element(vec.begin(), vec.end());
    }
    
    int max_number(vector<int> vec){
        return *max_element(vec.begin(), vec.end());
    }
};

int main() {
    // Write C++ code here
    std::cout << "Try programiz.pro"<<endl;
    vector<int> test={75,200,100 , 180 ,160,310,40,570,695};
    Solution sol;

    int start_index=1;
    int end_index=5;
    int min=sol.maximumProfit(test);
   // cout<<"max profit :" <<min<<endl;
    //cout<<"min element"<<(200+180+310+695)-(75+100+160+40)<<endl;
  //  vector<int> vec2=sol.slice(test,start_index,end_index);
    //for (int i =0 ;i<vec2.size();i++){
      //  cout<<vec2[i]<<endl;
    //}
 
 
 
 
 
 
    return 0;
}
