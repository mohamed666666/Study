#include <iostream>
#include <algorithm>
#include <vector>
using namespace std;
int main() {
    // Write C++ code here
    int n;
    cin>>n;
    vector<int> a;
    int t;
    int c=0;
    while(c<n){
        cin>>t;
        a.push_back(t);
        c++;
    }
    sort(a.begin(),a.end());
    for(int i:a){
        cout<<i<<" ";
    }

    return 0;
}
