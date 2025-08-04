
// Online C++ compiler to run C++ program online
#include <iostream>
#include<vector>

using namespace std;
int main() {
    // Write C++ code here
    int n;
    cin>>n;
    vector<int> v;
    int t;
    int c=0;
    while(c<n){
        cin>>t;
        v.push_back(t);
        c++;
    }
    int max=v[0];
    int min=v[0];
    int res=0;
    for (int i=0;i<n;i++){
        if (v[i]>max ){
            res+=1;
            max=v[i];
           
        }
        if(v[i]<min){
            res+=1;
            min=v[i];
          
        }
        
    }
    cout<<res;
    
    
    
    
    return 0;
}
