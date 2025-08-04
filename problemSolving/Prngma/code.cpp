
// Online C++ compiler to run C++ program online
#include <iostream>
#include<vector>
#include <numeric>
#include <string>
#include <cctype> // Required for tolower()
#include <algorithm> 
using namespace std;
int main() {
    // Write C++ code here
    int n;
    string str;
    cin>>n;
    cin>>str;
     for(int i=0;i<n;i++){
        str[i]=tolower(str[i]);
    }
    sort(str.begin(),str.end());
   
    str.erase(unique(str.begin(), str.end()), str.end());
  
    std::string lower(26,' ');
	std::iota(lower.begin(), lower.end(), 'a');
   
    if(str==lower){
        cout<<"YES\n";
    }
    else{
        cout<<"NO\n";
    }
        
    
    
    return 0;
}




