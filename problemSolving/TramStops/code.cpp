// Online C++ compiler to run C++ program online
#include <iostream>
#include<algorithm>
#include<vector>
using namespace std;
int main() {
    // Write C++ code here
    int n,c=0;
    int entr=0;
    int leav=0;
    int capacity=0;
    int remain=0;
    cin >>n;
    while(c<n){
        cin>>leav;
        cin>>entr;
        remain+=entr-leav;
        capacity=max(capacity,remain);
        c++;
    }
    cout<<capacity;

    return 0;
}
