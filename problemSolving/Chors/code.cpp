
// Online C++ compiler to run C++ program online
#include <iostream>
#include<vector>

using namespace std;
int main() {
    // Write C++ code here
    int n,h,x;
    cin>>n>>h>>x;
    vector<int> v;
    int t;
    int c=0;
    while(c<n){
        cin>>t;
        v.push_back(t);
        c++;
    }
    int res=0;
    for (int i=0;i<n;i++){
        if (i>=(n-h) ){
            res+=x;
            continue;
        }
        res+=v[i];
    }
    cout<<res;
    
    
    
    
    return 0;
}
