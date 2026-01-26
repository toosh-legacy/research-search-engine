from index import app
from fastapi.testclient import TestClient

def run_tests():
    client = TestClient(app)
    stats = client.get('/api/stats').json()
    print('Total papers in API (stats):', stats.get('total_papers'))

    res = client.get('/api/search?q=machine+learning')
    print('Search status:', res.status_code)
    data = res.json()
    print('Search count:', data.get('count'))
    print('Results returned:', len(data.get('results', [])))
    if data.get('results'):
        print('First title sample:', data['results'][0]['title'][:120])

if __name__ == "__main__":
    run_tests()
