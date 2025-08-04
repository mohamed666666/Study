#include <iostream>
#include <deque>
using namespace std;

int main() {
    int n, d;
    cin >> n >> d;
    deque<int> dq;
    int t;

    for (int i = 0; i < n; i++) {
        cin >> t;
        dq.push_back(t);
    }

    for (int i = 0; i < d; i++) {
        t = dq.front();     // Get the front element
        dq.pop_front();     // Remove the front element
        dq.push_back(t);    // Push it to the back
    }

    for (auto i : dq) {
        cout << i << " ";
    }

    return 0;
}
