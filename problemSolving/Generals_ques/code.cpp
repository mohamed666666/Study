// Online C++ compiler to run C++ program online
#include <iostream>
#include <vector>
using namespace std;
int main() {
    // Write C++ code here
    int t,n,c=0;
    cin>>n;
    vector<int>v;
    while(c<n){
        cin>>t;
        v.push_back(t);
        c++;
    }
    int min_index,mn=v[0];
    int max_index,mx=v[1];
    for (int i=0;i<n;i++){
        if(v[i]>mx){
            mx=v[i];
            max_index=i;
        }
        if(v[i]<=mn){
            min_index=i;
            mn=v[i];
        }
    }

    int dead_swap=0;
    if (max_index>min_index){
        dead_swap=1;
        cout<<dead_swap<<endl;
    }
    cout<<((n-min_index-1)+max_index)-dead_swap;
    
    
    
    return 0;
}
